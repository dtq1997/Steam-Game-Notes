# 🎮 Steam Game Notes — Steam 笔记管理器

一个功能丰富的桌面工具，用于以编程方式管理 Steam 游戏笔记（Steam Notes）。支持 AI 批量生成游戏说明、富文本编辑、Steam Cloud 直接上传，以及多账号管理。

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/Version-5.3.2-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 核心功能

### 🤖 AI 批量生成游戏说明
- 调用 AI 为 Steam 库中的游戏自动撰写客观的"游戏说明"笔记，帮助好友快速判断游戏是否适合自己
- 支持多种 AI 提供商：**Anthropic (Claude)**、**OpenAI (GPT)**、**DeepSeek** 及任意 OpenAI 兼容 API
- **多令牌管理**：保存多组 API Key，在生成时自由切换
- **智能信息源**：自动获取 Steam 商店详情 + 玩家评测 + 好评率，作为 AI 参考上下文
- **Claude 联网搜索**：使用 Anthropic 官方 API 时可启用 Web Search 获取更多信息
- **批量任务生命周期**：支持暂停 / 继续 / 停止，关闭后可从断点恢复
- 每条 AI 笔记自动添加模型名称和确信度声明

### 📝 富文本编辑器
- 所见即所得（WYSIWYG）编辑，支持 Steam 笔记全部富文本标签（粗体、斜体、标题、列表、链接、代码块等）
- 可切换源码模式直接编辑 BBCode
- 支持任意深度的标签嵌套

### ☁️ Steam Cloud 直接上传
- 通过 Steamworks API (`ISteamRemoteStorage::FileWrite`) 直接上传笔记到 Steam Cloud
- **延迟上传机制**：所有改动先保存本地并标记 dirty，用户确认后再批量上传
- **持久化 dirty 检测**：重启程序后通过文件哈希自动检测未上传的改动
- **账号安全检测**：连接时自动核验 Steam 登录账号与程序选择的账号是否一致

### 📦 导入导出
- **批量导出**：将多个游戏的笔记合并导出为结构化文本，可在其他账号导入还原
- **逐条导出**：每条笔记保存为独立 `.txt` 文件
- **导入冲突处理**：支持 AI 冲突检测和字面重复检测两种模式，可逐一对比处理
- **笔记去重**：扫描所有笔记中的重复项

### 🔍 搜索与筛选
- 双模式搜索：按游戏名 / AppID 或按笔记内容搜索
- 多维度筛选：全部 / 有笔记 / 无笔记 / AI 处理过 / 按 AI 模型 / 按确信度 / 有改动
- 按 Steam 收藏夹（分类）筛选游戏

### 👥 多账号支持
- 启动时自动扫描所有本地 Steam 账号
- 支持扫描他人游戏库（家庭共享场景）

## 📋 前置要求

- **Python 3.8+**
- **Tkinter**（通常随 Python 一起安装）
- **Steam 客户端**（使用 Cloud 上传功能时需要正在运行）

### 可选依赖

- **Steam Web API Key**：用于在线扫描游戏库、获取游戏名称（[申请地址](https://steamcommunity.com/dev/apikey)）
- **AI API Key**：用于 AI 批量生成功能（支持 Anthropic / OpenAI / DeepSeek 等）

## 🚀 使用方法

```bash
python main.py
```

### 基本操作流程

1. 启动程序，自动检测 Steam 安装路径和账号
2. 在左侧笔记列表浏览/编辑笔记，右侧面板进行管理操作
3. 如需 AI 生成：点击「🤖 AI 批量生成」，配置 API Key 后选择游戏批量生成
4. 如需上传到云端：点击「☁️ 连接 Steam Cloud」，然后上传有改动的笔记

### Steam Cloud 上传流程

1. 确保 Steam 客户端正在运行
2. 点击「☁️ 连接 Steam Cloud」
3. 编辑/生成笔记（改动自动标记为 dirty）
4. 点击「☁️ 全部上传」或逐条上传

## 🗂️ Steam 笔记存储机制

笔记文件存储在 Steam 本地目录中：

```
<Steam安装目录>/userdata/<用户ID>/2371090/remote/notes_<游戏AppID>
```

其中 `2371090` 是 Steam Notes 功能的固定 AppID。每个笔记文件是一个 JSON 文件，包含笔记 ID、时间戳、标题和富文本内容。

## ⚙️ 配置文件

程序配置保存在 `~/.steam_notes_gen/config.json`，包括：

- AI 令牌列表（多组 API Key / 模型 / 提供商）
- Steam Web API Key
- 游戏名称缓存
- 自定义系统提示词
- 上传哈希记录（用于 dirty 检测）

## 🖥️ 跨平台支持

| 平台 | 状态 |
|------|------|
| Windows | ✅ 完整支持 |
| macOS | ✅ 完整支持 |
| Linux | ✅ 完整支持 |
| WSL | ✅ 支持 |

## 📄 许可证

MIT License

## 👤 作者

**dtq1997**

- Steam: [steamcommunity.com/id/dtq1997](https://steamcommunity.com/id/dtq1997/)
- Email: 919130201@qq.com / dtq1997@pku.edu.cn
