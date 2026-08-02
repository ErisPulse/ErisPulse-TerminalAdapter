<div align="center">

<img src=".github/assets/logo.png" width="180" alt="ErisPulse TerminalAdapter" />

# ErisPulse TerminalAdapter

**The terminal is the chat — develop and test your Bot with zero platform setup.**

A terminal adapter for [ErisPulse](https://github.com/ErisPulse/ErisPulse). Each line you type in the terminal is emitted as a private message, and the bot's replies are printed back to stdout. Handy for developing and testing handlers without registering a real platform.

<p>
  <a href="https://pypi.org/project/ErisPulse-TerminalAdapter/"><img src="https://img.shields.io/pypi/v/ErisPulse-TerminalAdapter?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/ErisPulse-TerminalAdapter/"><img src="https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/ErisPulse/ErisPulse-TerminalAdapter"><img src="https://img.shields.io/github/stars/ErisPulse/ErisPulse-TerminalAdapter?style=for-the-badge&logo=github&color=brightgreen" alt="Stars"></a>
  <a href="https://pepy.tech/project/ErisPulse-TerminalAdapter"><img src="https://img.shields.io/pepy/dt/ErisPulse-TerminalAdapter?style=for-the-badge&color=blue" alt="Downloads"></a>
  <a href="https://github.com/ErisPulse/ErisPulse"><img src="https://img.shields.io/badge/Powered_by-ErisPulse-FF6B9D?style=for-the-badge&logo=bookstack&logoColor=white" alt="ErisPulse"></a>
</p>

[English](#english) | [简体中文](#简体中文)

</div>

---

<a id="english"></a>

## English

### Features

- **Zero config** — no platform account or token needed, install and run
- **One line, one message** — every line typed in the terminal becomes a private message that triggers command / module handlers
- **Replies printed to stdout** — the bot's SendDSL replies are printed with a `[Bot]` prefix
- **Standard actions work** — `get_user_info` / `get_self_info` / `get_friend_list` return mock data so framework standard actions keep working
- **Readable rendering** — non-text segments (image / voice / file / mention ...) render as readable placeholders
- **i18n aware** — welcome / goodbye / hint messages follow the framework's `i18n` language

### Install

```bash
pip install ErisPulse-TerminalAdapter
```

Requires ErisPulse >= 2.7.0.

### Configuration

`config.toml`:

```toml
[TerminalAdapter]
bot_id = "terminal_bot"
bot_name = "TerminalBot"
user_id = "terminal_user"
user_name = "User"
prompt = "> "
reply_prefix = "[Bot] "
echo_input = false
```

| Field | Default | Description |
|------|---------|-------------|
| `bot_id` | `terminal_bot` | Bot user ID |
| `bot_name` | `TerminalBot` | Bot nickname |
| `user_id` | `terminal_user` | Mocked user ID (the terminal user chatting with the bot) |
| `user_name` | `User` | Mocked user nickname |
| `prompt` | `> ` | Input prompt |
| `reply_prefix` | `[Bot] ` | Prefix prepended to each bot reply line (empty for none) |
| `echo_input` | `false` | Echo user input (useful for piped input) |

The adapter registers under platform name `terminal` and exposes a single private-chat session (no groups).

### Usage

After `epsdk run`, the terminal becomes the chat:

```
> Terminal adapter started. Type a message to chat with the Bot. Ctrl+C / EOF to quit.
> Use /help to list commands.

> /hello
[Bot] Hello, User!
> ping
[Bot] ...
```

You can also pipe input in, which is handy for automated testing:

```bash
echo "/hello" | epsdk run main.py
```

Non-text segments render as placeholders (`[image: url]`, `[voice: url]`, `@user_id`, ...). Group-related actions are unsupported (no groups in a terminal).

### Notes

- `stdin` is read in a worker thread, so on shutdown the reader only returns after the next line or EOF (Ctrl+D / Ctrl+Z).
- Welcome / goodbye / hint messages follow the framework's `i18n` language setting.

---

<a id="简体中文"></a>

## 简体中文

### 特性

- **零配置即用** —— 不需要注册任何平台账号、不需要 token，装上就能跑
- **一行一消息** —— 终端里每输入一行即一条私聊消息，直接触发命令 / 模块处理器
- **回复即打印** —— Bot 通过 SendDSL 回复的内容带 `[Bot]` 前缀打印到 stdout
- **标准动作可用** —— `get_user_info` / `get_self_info` / `get_friend_list` 等返回模拟数据，框架标准动作照常工作
- **多段渲染** —— 非文本消息段（图片 / 语音 / 文件 / @ 等）渲染成可读占位符
- **i18n 跟随** —— 欢迎语 / 退出语跟随框架 `i18n` 语言设置

### 安装

```bash
pip install ErisPulse-TerminalAdapter
```

需要 ErisPulse >= 2.7.0。

### 配置

`config.toml`：

```toml
[TerminalAdapter]
bot_id = "terminal_bot"
bot_name = "TerminalBot"
user_id = "terminal_user"
user_name = "User"
prompt = "> "
reply_prefix = "[Bot] "
echo_input = false
```

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `bot_id` | `terminal_bot` | Bot 的用户 ID |
| `bot_name` | `TerminalBot` | Bot 昵称 |
| `user_id` | `terminal_user` | 模拟用户的 ID（与 Bot 对话的终端用户）|
| `user_name` | `User` | 模拟用户昵称 |
| `prompt` | `> ` | 输入提示符 |
| `reply_prefix` | `[Bot] ` | Bot 回复的行前缀（留空则不加前缀）|
| `echo_input` | `false` | 是否回显用户输入（管道输入场景下开启）|

适配器注册的平台名为 `terminal`，只有一个私聊会话，没有群组概念。

### 使用

`epsdk run` 启动后，终端就是聊天窗口：

```
> 终端适配器已启动。直接输入消息即可与 Bot 对话，Ctrl+C 或 EOF 退出。
> 输入 /help 查看可用命令。

> /hello
[Bot] Hello, User!
> ping
[Bot] ...
```

也可以通过管道喂入，便于自动化测试：

```bash
echo "/hello" | epsdk run main.py
```

非文本消息段会渲染成占位符（`[image: url]`、`[voice: url]`、`@user_id` 等）。群组相关操作不支持（终端无群组）。

### 说明

- `stdin` 在独立线程中读取，关闭时需等到下一行或 EOF（Ctrl+D / Ctrl+Z）才会退出。
- 欢迎语 / 退出语 / 提示语跟随框架 `i18n` 语言设置。

---

<div align="center">

**Related** · [ErisPulse](https://github.com/ErisPulse/ErisPulse) · [Documentation](https://www.erisdev.com) · [Issues](https://github.com/ErisPulse/ErisPulse-TerminalAdapter/issues)

</div>
