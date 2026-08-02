"""TerminalAdapter：把命令行标准输入/输出作为消息通道，用于本地开发调试。

终端输入的每一行即一条私聊消息，Bot 的回复通过 SendDSL 打印到终端。
"""

from __future__ import annotations

import asyncio
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from ErisPulse.Core import BaseAdapter, SendDSL
from ErisPulse.Core.Bases import BaseConfig, BaseI18n, I18nKey


class TerminalAdapter(BaseAdapter):
    """终端适配器：命令行即聊天会话，用于本地开发调试。"""

    _platform = "terminal"

    @dataclass
    class ConfigClass(BaseConfig):
        bot_id: str = field(
            default="terminal_bot",
            metadata={
                "description": "Bot 的用户 ID",
                "ui": {"widget": "text", "group": "basic", "order": 1},
            },
        )
        bot_name: str = field(
            default="TerminalBot",
            metadata={
                "description": "Bot 昵称",
                "ui": {"widget": "text", "group": "basic", "order": 2},
            },
        )
        user_id: str = field(
            default="terminal_user",
            metadata={
                "description": "模拟用户的 ID（与 Bot 对话的终端用户）",
                "ui": {"widget": "text", "group": "basic", "order": 3},
            },
        )
        user_name: str = field(
            default="User",
            metadata={
                "description": "模拟用户昵称",
                "ui": {"widget": "text", "group": "basic", "order": 4},
            },
        )
        prompt: str = field(
            default="> ",
            metadata={
                "description": "输入提示符",
                "ui": {"widget": "text", "group": "ui", "order": 5},
            },
        )
        reply_prefix: str = field(
            default="[Bot] ",
            metadata={
                "description": "Bot 回复的行前缀（留空则不加前缀）",
                "ui": {"widget": "text", "group": "ui", "order": 6},
            },
        )
        echo_input: bool = field(
            default=False,
            metadata={
                "description": "是否回显用户输入（管道输入场景下开启）",
                "ui": {"widget": "switch", "group": "ui", "order": 7},
            },
        )

    class I18nClass(BaseI18n):
        welcome: I18nKey = I18nKey(
            default="Terminal adapter started. Type a message to chat with the Bot. Ctrl+C / EOF to quit.",
            zh_CN="终端适配器已启动。直接输入消息即可与 Bot 对话，Ctrl+C 或 EOF 退出。",
            zh_TW="終端介面卡已啟動。直接輸入訊息即可與 Bot 對話，Ctrl+C 或 EOF 退出。",
            en="Terminal adapter started. Type a message to chat with the Bot. Ctrl+C / EOF to quit.",
            ja="ターミナルアダプターが起動しました。メッセージを入力して Bot と会話できます。Ctrl+C / EOF で終了。",
            ru="Терминальный адаптер запущен. Введите сообщение для общения с ботом. Ctrl+C / EOF — выход.",
        )
        goodbye: I18nKey = I18nKey(
            default="Terminal adapter stopped.",
            zh_CN="终端适配器已停止。",
            zh_TW="終端介面卡已停止。",
            en="Terminal adapter stopped.",
            ja="ターミナルアダプターを停止しました。",
            ru="Терминальный адаптер остановлен.",
        )
        input_hint: I18nKey = I18nKey(
            default="Use /help to list commands.",
            zh_CN="输入 /help 查看可用命令。",
            zh_TW="輸入 /help 查看可用指令。",
            en="Use /help to list commands.",
            ja="/help でコマンド一覧を表示。",
            ru="Введите /help для списка команд.",
        )

    class Send(SendDSL):
        """终端发送 DSL：把 OB12 消息段渲染为文本打印到 stdout。"""

        def Raw_ob12(self, message, **kwargs):

            async def _do_send():
                segments = self._apply_modifiers(message)
                text = self._adapter._render_segments(segments)
                self._adapter._output(text)
                return self._adapter.make_response(
                    message_id=str(uuid.uuid4()),
                    data={"text": text, **self.send_context},
                )

            return asyncio.create_task(_do_send())

    def __init__(self, sdk=None):
        super().__init__(sdk)
        self._running = False
        self._read_task: asyncio.Task | None = None

    async def start(self) -> None:
        """启动适配器：上线 Bot、打印欢迎语、启动 stdin 读取循环"""
        cfg = self.cfg
        self._running = True

        await self.emit_meta("connect", cfg.bot_id, user_name=cfg.bot_name, avatar="")

        try:
            from ErisPulse import i18n

            say = i18n.t
        except Exception:

            def say(key, default=None):
                return default or key

        self._write_raw("\n")
        self._output_raw(say("TerminalAdapter.welcome"))
        self._output_raw(say("TerminalAdapter.input_hint"))
        self._write_raw("\n")

        self._read_task = asyncio.create_task(self._read_loop())
        self.logger.info("TerminalAdapter 已启动")

    async def shutdown(self) -> None:
        """关闭适配器：停止读取、下线 Bot"""
        self._running = False
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except (asyncio.CancelledError, Exception):
                pass

        cfg = self.cfg
        try:
            from ErisPulse import i18n

            self._output_raw(i18n.t("TerminalAdapter.goodbye"))
        except Exception:
            pass

        await self.emit_meta("disconnect", cfg.bot_id)
        self.logger.info("TerminalAdapter 已关闭")

    def on_config_update(self, old_config, new_config):
        """配置热更新回调"""
        self.logger.info("TerminalAdapter 配置已热更新")

    async def call_api(self, endpoint: str, **params: Any) -> dict:
        """模拟常用平台 API，使框架标准动作可用。"""
        cfg = self.cfg

        if endpoint == "get_self_info":
            return self.make_response(data={"user_id": cfg.bot_id, "user_name": cfg.bot_name, "platform": "terminal"})
        if endpoint == "get_user_info":
            uid = str(params.get("user_id", cfg.user_id))
            is_bot = uid == cfg.bot_id
            return self.make_response(
                data={
                    "user_id": uid,
                    "user_name": cfg.bot_name if is_bot else cfg.user_name,
                    "user_displayname": cfg.bot_name if is_bot else cfg.user_name,
                    "platform": "terminal",
                }
            )
        if endpoint in ("get_friend_list", "get_user_list"):
            return self.make_response(data=[{"user_id": cfg.user_id, "user_name": cfg.user_name}])
        if endpoint == "get_group_list":
            return self.make_response(data=[])  # 终端无群组
        if endpoint in ("get_group_info", "get_group_member_info", "get_group_member_list"):
            return self.make_error(retcode=10002, message="终端适配器不支持群组操作")
        if endpoint == "send_message":
            return self.make_response(message_id=str(uuid.uuid4()))
        if endpoint == "delete_message":
            return self.make_response()  # 终端无法撤回，返回成功

        return self.make_error(retcode=10002, message=f"终端适配器不支持 {endpoint}")

    async def _read_loop(self) -> None:
        """异步读取 stdin：每行作为一条私聊消息 emit 给框架。"""
        loop = asyncio.get_running_loop()
        cfg = self.cfg

        while self._running:
            try:
                self._write_raw(cfg.prompt)
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    # EOF（无更多输入）
                    break
                text = line.rstrip("\r\n")
                if not text:
                    continue
                if cfg.echo_input:
                    self._output_raw(f"< {text}")
                await self._handle_input(text)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.warning(f"读取 stdin 失败: {e}")
                await asyncio.sleep(0.5)

    async def _handle_input(self, text: str) -> None:
        """把一行文本构造为 OB12 message 事件并 emit"""
        cfg = self.cfg
        try:
            from ErisPulse.Core.adapter import adapter as adapter_mgr
        except ImportError:
            self.logger.error("无法访问 adapter manager")
            return

        event = {
            "id": str(uuid.uuid4()),
            "time": int(time.time()),
            "type": "message",
            "detail_type": "private",
            "platform": "terminal",
            "self": {
                "platform": "terminal",
                "user_id": cfg.bot_id,
                "user_name": cfg.bot_name,
            },
            "user_id": cfg.user_id,
            "message": [{"type": "text", "data": {"text": text}}],
            "alt_message": text,
            "terminal_raw": {"text": text},
            "terminal_raw_type": "stdin_line",
        }
        await adapter_mgr.emit(event)

    @staticmethod
    def _render_segments(segments: list[dict]) -> str:
        parts: list[str] = []
        for seg in segments:
            seg_type = seg.get("type", "")
            data = seg.get("data", {}) or {}
            if seg_type == "text":
                parts.append(str(data.get("text", "")))
            elif seg_type == "image":
                parts.append(f"[image: {data.get('file', '')}]")
            elif seg_type == "audio":
                parts.append(f"[voice: {data.get('file', '')}]")
            elif seg_type == "video":
                parts.append(f"[video: {data.get('file', '')}]")
            elif seg_type == "file":
                parts.append(f"[file: {data.get('file', '')}]")
            elif seg_type == "mention":
                parts.append(f"@{data.get('user_id', '')}")
            elif seg_type == "mention_all":
                parts.append("@all")
            elif seg_type == "reply":
                parts.append(f"[reply:{data.get('message_id', '')}]")
            else:
                parts.append(f"[{seg_type}]")
        return "".join(parts)

    def _output(self, text: str) -> None:
        """带 Bot 前缀地输出一段文本（多行逐行加前缀）"""
        prefix = self.cfg.reply_prefix or ""
        for line in str(text).split("\n"):
            self._write_raw(prefix + line + "\n")

    def _output_raw(self, text: str) -> None:
        """原样输出一段文本（不加前缀，自动换行）"""
        if text:
            self._write_raw(str(text) + "\n")

    @staticmethod
    def _write_raw(s: str) -> None:
        """底层写 stdout"""
        try:
            sys.stdout.write(s)
            sys.stdout.flush()
        except Exception:
            pass


__all__ = ["TerminalAdapter"]
