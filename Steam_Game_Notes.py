"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     STEAM NOTES GENERATOR v5.3.2                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
================================================================================
【AI 协作系统提示词 / System Prompt for AI Maintainers】
如果你（AI）正在处理此文件，请务必遵守以下开发者习惯与规则：

【元规则 - 最高优先级】
0. 【提示词协作】：允许 AI 根据与用户的交流情况，自发在本导言区增加或修改提示词，
   但每次增加或修改提示词前必须先与用户讨论并获得同意。
   AI 必须严格遵照本导言区的所有提示词运作，本导言区规则优先级最高。
   【主动更新】：如果用户提出的需求反映了某些更具一般性的要求，AI 应主动将其整合
   为新的规则添加到本导言区，并在回复中明确告知用户具体修改了哪些内容。
   【及时响应】：当用户明确要求修改导言区内容时，AI 必须立即配合执行修改，
   不得拖延或遗漏。导言区是用户与 AI 之间的"协作契约"，保持其准确和最新
   是最高优先级任务之一。

【项目目标】
本程序用于以编程方式生成/修改 Steam 笔记 (Steam Notes)。
核心用途：由 AI 撰写客观的"游戏说明"笔记，帮助用户的 Steam 好友快速判断
库中的游戏是否适合自己。详见下方【AI 撰写游戏说明笔记的指引】。
也可用于手动创建其他类型的笔记（攻略、日志等），通过本脚本写入 Steam 笔记
文件，使其在 Steam 客户端中可见。

【Steam 笔记存储机制 - 关键技术细节】
1. 本地路径:
   <Steam安装目录>/userdata/<用户ID>/2371090/remote/
   其中 2371090 是 Steam Notes 功能的固定 AppID

2. 文件命名:
   - 每个游戏对应: notes_<游戏AppID>  (如 notes_570 = Dota 2)
   - 非 Steam 游戏: notes_shortcut_<游戏名>
   - 没有文件扩展名

3. 文件格式: JSON
   {
     "notes": [
       {
         "id": "<8位随机十六进制字符串>",
         "appid": <游戏AppID数字>,
         "ordinal": 0,
         "time_created": <Unix时间戳秒>,
         "time_modified": <Unix时间戳秒>,
         "title": "笔记标题",
         "content": "[p]正文（支持富文本标签如 [h1][b][list] 等）[/p]"
       }
     ]
   }

4. 云同步:
   - 使用 Steam Cloud 同步 (AppID 2371090 的 remote 目录)
   - 本程序通过 Steamworks API (ISteamRemoteStorage::FileWrite) 直接上传
   - 在主界面点击「☁️ 连接 Steam Cloud」后，保存即自动上传到云端
   - 需要 Steam 客户端正在运行，且库中有至少一个已安装游戏（需要 libsteam_api）

【确保云同步的操作流程】
1. 启动 Steam → 2. 打开本程序 → 3. 点击「连接 Steam Cloud」→ 4. 正常编辑，保存即上传

【AI 撰写游戏说明笔记的指引】
本程序的核心用途之一是为用户 Steam 库中的游戏生成"游戏说明"笔记。
这些说明的目标读者是：登上用户账号的随机好友，他们不一定了解独立游戏或单机游戏。
说明的目的是：让读者快速判断这个游戏是否符合自己的兴趣。

⚠️ 撰写游戏说明时必须遵守以下规则（最高优先级）：

1. 【客观描述】：不能照抄游戏商店页面的商业化宣传语。必须客观地告诉读者这个
   游戏是什么、玩起来是什么感觉。
2. 【"现在打开会怎样"】：必须具体描述"如果我现在立刻打开这个游戏，前几分钟
   会看到什么、做什么"——要写到读者脑中能浮现画面，而非"上手难度适中"
   "需要一定学习成本"等模糊概括。这是最重要的信息之一。
3. 【认知资源与时间需求】：必须说明这个游戏消耗的认知资源如何（需要全神贯注
   还是可以边看视频边玩）、是否需要大段连续时间、每局/每次游玩大概需要多久。
4. 【网络口碑】：必须提及这个游戏在网络上是否受欢迎、大致评价如何。
5. 【缺点与不适人群】：必须有一定篇幅介绍缺点，以及明确说明不适合什么样的人玩。
6. 【不用术语、说人话】：禁止使用读者可能不懂的术语而不加解释。例如不能直接说
   "ASCII 风格画面"或"1-bit 风格"，而应该用没玩过游戏的人都能理解的语言描述
   （如"画面几乎完全由彩色文字符号构成——你的角色是一个@，怪物是字母，墙壁
   是#号"）。术语不必刻意回避或删除，解释清楚即可。
7. 【无需强调性价比】：这些游戏默认已在用户库中，属于免费可玩，绝对禁止提及
   任何与价格相关的内容（价格、售价、原价、打折、性价比、定价等）。即使参考资料
   （如 Steam 评测）中大量讨论价格，AI 也必须完全忽略这些信息。
8. 【格式与富文本】：AI 生成的笔记采用"标题=内容"模式——输出纯文本单行，
   禁止换行和 BBCode 标签，同时作为笔记标题和内容显示。这样用户在 Steam 客户端
   的笔记列表中无需点进去就能看到全部说明。所有信息应融入一段连贯自然的叙述中，
   禁止使用分段式小标题（如"初次打开的体验："、"认知资源："等）。
   可适度使用 emoji（📌✅⚠️🗺️⚔️📝🎯）但要克制。建议 200-500 字。
   手动创建的笔记仍可使用 BBCode 富文本标签。
9. 【AI 声明前缀】：每条 AI 生成的笔记必须自动在开头添加固定前缀：
   "🤖AI: ⚠️ 以下内容由 {实际模型名} 生成，该模型对以下内容的确信程度：{X}。"
   前缀必须以 "🤖AI:" 开头，这是程序识别 AI 笔记的唯一标志。
   其中模型名从 API 响应中提取，确信程度由 AI 根据自身对该游戏的了解程度
   自评为：很高 / 较高 / 中等 / 较低 / 很低。此声明由程序自动拼接，
   无需在系统提示词中要求 AI 输出。

【Steam 笔记富文本标签参考】
Steam 笔记 content 字段支持以下富文本标签（类似 BBCode）：
- [p]段落文本[/p]          — 段落（所有正文文本都应包裹在 [p] 中）
- [h1]标题[/h1]            — 一级标题
- [h2]标题[/h2]            — 二级标题
- [h3]标题[/h3]            — 三级标题
- [b]粗体[/b]              — 粗体文本
- [i]斜体[/i]              — 斜体文本
- [u]下划线[/u]            — 下划线文本
- [strike]删除线[/strike]  — 删除线文本
- [list][*]项目一[*]项目二[/list] — 无序列表
- [olist][*]第一[*]第二[/olist]   — 有序列表
- [hr]                     — 水平分隔线
- [code]代码[/code]        — 代码块
- [url]链接[/url]          — URL 链接
- [url=链接]文本[/url]     — 带显示文本的 URL 链接
⚠️ 注意：AI 生成笔记内容时，正文必须使用 [p]...[/p] 包裹，
  否则在 Steam 客户端中可能显示异常。

【富文本编辑器设计原则】
1. 程序中所有笔记编辑和显示区域都使用富文本（WYSIWYG）模式，而非源码模式。
   用户看到的是渲染后的效果（粗体、斜体、标题等），而非 [b][/b] 等标签源码。
2. 编辑器提供工具栏按钮，对应 Steam 笔记支持的所有富文本功能（粗体、斜体、
   下划线、删除线、标题 H1/H2/H3、段落、无序列表、有序列表、分隔线、代码块）。
3. 底层存储仍使用 Steam 原生 BBCode 标签格式，编辑器负责双向转换：
   - 加载时：BBCode → 富文本渲染显示
   - 保存时：富文本 → BBCode 源码写入文件
4. 编辑器需提供"源码模式"切换按钮，方便高级用户直接编辑 BBCode 源码。
5. 笔记查看器提供"原始文本/富文本"就地切换按钮，用于调试富文本渲染。
6. 【嵌套标签】：BBCode 解析必须支持任意深度的标签嵌套，例如
   [b][i]text[/i][/b]、[list][*][b][url=...]text[/url][/b][/list] 等。
   内联标签解析器（_insert_inline）必须递归调用以正确渲染嵌套结构。
7. 【URL 标签】：必须支持 [url]链接[/url] 和 [url=链接]文本[/url] 两种格式，
   url= 属性值可能带引号（如 [url="..."]），解析时需去除引号。

【导入导出设计原则】
1. 导入操作永远不覆盖已有笔记，导入的内容始终追加在已有笔记之后。
   UI 中不提供"覆盖"选项，以防止误操作。
2. 导出分两种模式：
   - 【单条导出】：在笔记查看页面中选中一条笔记后导出为独立 txt 文件，
     文件名为笔记标题（不可作为文件名的字符自动转义），内容为富文本源码。
   - 【批量导出】：在主界面选择一个、多个或全部游戏，将所有笔记导出为
     一个结构化 txt 文件（含 AppID 和笔记分隔标记）。
3. 导入也分两种对应模式：
   - 【单条导入】：选择一个 txt 文件，作为一条笔记导入到指定 AppID 下。
     文件名自动成为笔记标题。
   - 【批量导入】：选择批量导出格式的 txt 文件，按其中的 AppID 信息
     自动分发到对应游戏下，无需手动指定 AppID。

【开发规范】
1. 【逻辑稳定性】：核心功能（JSON 读写、笔记文件操作）严禁在非必要情况下改动。
2. 【改动确认】：在尝试重构现有功能或大规模调整 UI 前，必须获得用户明确许可。
3. 【UI 习惯】：与 Steam_Library_Manager 保持一致的风格。
4. 【反馈机制】：操作完成后必须显示明确的成功/失败反馈。
5. 【UI 文本风格】：
   - ✅ 表示成功，❌ 表示失败
   - 按钮: emoji + 动宾结构
   - 关键信息: 红色高亮
6. 【账号管理】：启动时自动扫描所有 Steam 账号，支持多账号切换。
7. 【窗口大小】：自适应内容大小，禁止固定 geometry()。
8. 【跨平台】：支持 Windows / macOS / Linux / WSL。
9. 【增量修改】：修改代码时必须以原始文件为基础进行增量编辑（如逐处替换），
   严禁整体重新生成文件。这样既节省 token，也避免引入无关变更或丢失已有功能。
10.【UI 按钮布局】：当按钮较多时应分多行排列，确保所有按钮在窗口中可见，
   不被挤出可视区域。功能切换类按钮（如"原始文本/富文本"）应就地切换状态，
   而非弹出新窗口。
11.【调试信息规范】：
   - 所有调试/诊断信息窗口中的文本必须可选中、可复制（不得使用 DISABLED 状态
     阻止文本选择），同时必须提供"📋 复制"按钮一键复制全部内容到剪贴板。
   - 调试信息应包含完整的请求/响应链路：输入参数、请求 URL（隐藏敏感信息）、
     HTTP 状态码、响应体预览、解析结果摘要、错误 Traceback 等。
   - API Key 等敏感信息在调试输出中必须脱敏（仅显示前6位...后4位）。
12.【版本管理】：每次生成新版本文件时，必须递增版本号并在导言区更新日志中
   添加对应条目，版本号格式为 vX.Y 或 vX.Y.Z。
13.【配置持久化】：AI 令牌配置保存为 ai_tokens 列表（每项含 name/key/provider/
   model/api_url），并通过 ai_active_token_index 记录默认令牌。向后兼容旧版
   单 Key 配置（ai_api_key/ai_provider/ai_model/ai_api_url）。
   AI 批量生成窗口提供令牌选择下拉框，用户可自由切换不同令牌。
   Steam Web API Key 和 Steam 配置仍在主界面统一管理。
14.【AI 笔记识别】：AI 生成的笔记以固定前缀 "🤖AI:" 开头。程序通过检测此前缀
   自动识别哪些笔记由 AI 处理过。同时兼容旧版 v2.x 的前缀 "⚠️ 以下内容由"。
   AI 处理过的笔记在列表中显示蓝色，
   未处理的显示默认颜色。可从前缀中提取模型名实现按 AI 模型分类。
15.【笔记创建统一性】：无论是手动创建还是 AI 批量生成，笔记文件的创建都必须
   使用相同的 create_note/write_notes 方法，确保 JSON 格式、时间戳、
   文件结构完全一致。这保证了 Steam Cloud 能正确识别和同步所有笔记。
16.【Steam 分类集成】：AI 批量生成支持按 Steam 收藏夹（分类）筛选游戏，
   通过读取 cloud-storage-namespace-1.json 获取用户收藏夹列表。
17.【延迟上传与 dirty 状态跟踪】：所有笔记改动（新建、编辑、删除、移动、AI
   生成、导入等）仅写入本地文件并标记 dirty。只有用户显式点击上传按钮后才调用
   Steamworks API 上传到 Steam Cloud。主界面游戏列表中，dirty 的条目需要有明显
   标识（颜色 + 图标），并提供每行单独上传按钮和全局批量上传按钮。
18.【列表行内操作按钮】：主界面右侧游戏列表的每个条目右侧提供行内小按钮（如
   📋 复制 AppID），点击后直接执行操作，不弹出额外确认窗口，减少操作步骤。
19.【批量任务生命周期】：AI 批量生成支持暂停/继续/停止。暂停后剩余队列持久化到
   配置文件，关闭窗口后再打开可继续。停止则立即中断并清空队列。关闭窗口时若有
   未上传的笔记，提示用户是否一键上传（自动尝试连接 Steam Cloud）。

【更新日志】
2026-02-09  v5.3.2 — 手动标记已同步功能：
                    - 【标记已同步】右键菜单新增「✅ 标记为已同步」选项，
                      可手动消除因历史残留导致的虚假 dirty 标记（如从云端下载
                      的笔记被误判为有改动），支持单选和多选操作
2026-02-09  v5.3.1 — 右侧面板紧凑化 + 上传按钮宽度修复 + 关于作者按钮：
                    - 【右侧面板紧凑化】右侧控制面板内边距、按钮宽度、间距全面缩减，
                      Cloud 状态文本和路径标签限制宽度，大幅减少无意义空白
                    - 【上传按钮宽度修复】工具栏「☁️全部」按钮宽度从 6 增至 9，
                      修复显示 dirty 数目时文本被截断的问题
                    - 【关于作者按钮】右侧面板底部新增「ℹ️ 关于」按钮，
                      点击弹出作者信息窗口（含联系方式和 Steam 主页链接），
                      不占用主界面空间
2026-02-09  v5.3 — 主界面 UI 大幅重排 + 导入冲突双模式 + 笔记去重：
                    - 【主界面重排】笔记列表移至左侧（仿 Steam 界面布局），
                      控制按钮区移至右侧，消除大片空白，布局更紧凑合理
                    - 【导入冲突双模式】批量导入时新增两种冲突检测模式：
                      ① AI 冲突检测（原有）：检测导入文件中 AI 笔记与已有 AI 笔记的冲突
                      ② 字面重复检测（新增）：检测导入笔记标题/内容是否与已有笔记完全重复
                      导入窗口新增模式选择，用户可按需切换
                    - 【笔记去重】主界面新增「🔍 去重」按钮，扫描所有笔记中的重复项
                      （按标题+内容完全匹配），列出重复笔记供用户选择删除
2026-02-09  v5.2.1 — Cloud 断开清理状态 + 账号不匹配拒绝连接：
                    - 【断开清理】断开 Steam Cloud 时，shutdown 后立即清空
                      remote_storage 和 logged_in_friend_code，避免残留状态
                    - 【账号不匹配拒绝连接】连接 Steam Cloud 时若检测到登录账号与程序
                      选择的账号不一致，立即 shutdown 并拒绝连接（而非连接后仅警告），
                      主界面和 AI 批量生成窗口均适用
2026-02-09  v5.2 — 导入确认窗口优化 + 游戏名称扫描重做 + 导出 AI 筛选 + Cloud 账号检测
                    + 导入 AI 冲突处理 + 持久化 dirty 检测：
                    - 【导入确认窗口】批量导入大量笔记时，结果摘要从 messagebox 改为
                      可滚动的 Toplevel 窗口，确认按钮始终可见，不再因内容过多而溢出屏幕
                    - 【游戏名称扫描重做】新增 fetch_all_steam_app_names() 方法，通过
                      ISteamApps/GetAppList/v2/ 一次性获取 Steam 全量应用名称列表
                      （无需 API Key，约 15 万条），缓存到本地配置文件，作为游戏名称
                      解析的主要数据源；不再依赖按账号扫描的 GetOwnedGames，
                      任何 AppID 都能正确显示游戏名
                    - 【导出 AI 筛选】修复筛选 AI 笔记后导出仍会导出所有笔记的问题；
                      导出对话框新增「🤖 仅导出 AI 笔记」复选框，当主界面筛选为
                      AI 相关时自动勾选；export_batch 和 export_individual_files 方法
                      新增 note_filter 参数支持按条件过滤导出
                    - 【Cloud 账号不匹配检测】修复为小号生成的笔记上传后出现在大号的严重
                      Bug：连接 Steam Cloud 时通过 Steamworks API (SteamUser::GetSteamID)
                      检测当前登录的 Steam 账号，若与程序选择的账号不一致则弹出醒目警告；
                      主界面和 AI 批量生成窗口的 Cloud 状态栏均显示红色「账号不匹配」提示；
                      关闭 AI 窗口自动上传前也会检查并确认
                    - 【导入 AI 笔记冲突处理】批量导入时若导入文件中的 AI 笔记与目标
                      AppID 已有 AI 笔记冲突，弹出冲突处理窗口：可选「全部替换/全部追加/
                      跳过 AI/逐一处理」；逐一处理模式下左右两栏对比已有和导入的 AI 笔记，
                      逐个游戏选择替换/追加/跳过；import_batch 重构为 parse → detect →
                      apply 三步流程，新增 parse_batch_file 和 apply_batch_import 方法
                    - 【持久化 dirty 检测】上传笔记到 Cloud 后记录文件 MD5 哈希到配置文件，
                      重启程序时通过对比本地文件哈希与上次上传的哈希，自动检测哪些笔记
                      需要重新上传；彻底解决「关闭程序后丢失 dirty 状态」的问题
2026-02-09  v5.1 — 主界面大幅优化 + 游戏名称显示 + 搜索功能：
                    - 【游戏名称显示】笔记列表显示游戏名而非 AppID，名称缓存持久化到
                      配置文件，启动时后台线程自动通过 Steam Store API 解析未知名称
                    - 【双模式搜索】右侧列表新增搜索栏，支持两种模式切换：
                      ① 按游戏名/AppID 搜索 ② 按笔记内容搜索
                    - 【主界面精简】移除冗余帮助文本、AppID 速查表、路径信息框，
                      按钮布局紧凑化，Cloud 状态合并为单行，整体高度大幅缩减
2026-02-09  v5.0.1 — 系统提示词优化（"现在打开会怎样"具体化）：
                    - 规则第2条大幅强化：要求 AI 描述"打开后会看到什么界面、做什么
                      操作、遇到什么状况"，而非"上手难度适中"等模糊概括；
                      增加正面示例和❌负面禁止示例，配合自查清单同步更新
2026-02-09  v5.0 — AI 批量生成：暂停/继续/停止 + 关闭时上传提示：
                    - 【暂停/继续】生成过程中可随时暂停，剩余队列自动保存到配置文件，
                      关闭窗口后重新打开可从断点继续；暂停期间按钮变为「▶️ 继续」
                    - 【停止】立即中断当前生成任务并清空队列
                    - 【关闭时上传提示】关闭 AI 批量生成窗口时若检测到未上传的笔记，
                      弹窗询问是否一键上传到 Steam Cloud；选「是」时自动尝试连接
                      Steam Cloud（若尚未连接），连接失败则返回窗口
                    - 新增开发规范第 19 条【批量任务生命周期】
2026-02-09  v4.9 — AI 批量生成窗口 UI 布局紧凑化：
                    - 【布局优化】AI 批量生成窗口整体布局大幅紧凑化，减少冗余间距和
                      重复标题，令牌信息与 Cloud 状态合并为单行显示，Steam API 状态
                      与 Steam ID 输入合并为单行，分类筛选与刷新按钮同行，
                      扫描/全选/调试按钮合并为单行，AI 筛选移至游戏数量信息同行，
                      减小窗口最小尺寸，确保在较小屏幕上也能完整显示所有控件
2026-02-09  v4.8 — 多令牌管理 + 斜体修复 + AI 页面 Cloud 连接：
                    - 【多令牌管理】API Key 配置页面全面重构，支持保存和管理多个
                      AI 令牌（每个令牌含名称、提供商、模型、API URL、Key），
                      在 AI 批量生成页面可通过下拉框自由切换令牌，适应不同开销需求
                    - 【AI 页面 Cloud 连接】将 Steam Cloud 连接/断开按钮添加到
                      AI 批量生成页面，生成完成后可直接连接并上传，无需返回主界面
                    - 【斜体渲染修复】富文本编辑器使用显式字体族名解析，修复部分
                      平台下斜体样式无视觉效果的问题（italic font 未正确渲染）
                    - 配置结构新增 ai_tokens 列表和 ai_active_token_index，
                      保持与旧单 Key 配置的向后兼容
2026-02-09  v4.7 — AI 提示词强化 + 批量生成界面增强：
                    - 【提示词强化 - 禁止提及价格】规则第7条大幅强化措辞，增加
                      负面示例和明确禁止词列表（原价/打折/性价比/售价等），
                      并在 user_msg 末尾 reminder 中重复强调，防止 Steam 评论中的
                      大量性价比讨论"污染" AI 输出
                    - 【批量生成 - 有改动筛选】AI 筛选器新增「☁️ 有改动」选项，
                      与主界面筛选器完全一致，方便快速查看刚生成/修改过的笔记
                    - 【批量生成 - 云同步按钮】底部按钮栏新增「☁️上传选中」和
                      「☁️全部上传」两个云同步按钮，生成满意后可直接上传到
                      Steam Cloud，无需返回主界面操作
2026-02-09  v4.6 — 导出功能增强 + 全选：
                    - 【全选按钮】主界面工具栏新增「✅全选」按钮，一键选中当前筛选项
                      下的所有游戏（再次点击取消全选），方便批量操作上千条笔记
                    - 【双模式导出】导出按钮改为弹窗选择两种模式：
                      ① 逐条导出：每条笔记保存为独立 .txt 文件（文件名=标题，内容=BBCode）
                      ② 合并导出：所有笔记写入单个结构化 .txt 文件，可在其他账号上导入还原
                    - 新增 SteamNotesManager.export_individual_files() 方法，支持同名去重
                    - 右键菜单新增单个游戏导出入口，多选时也使用新导出对话框
2026-02-09  v4.5.1 — AI 格式遵守修复 + UI 细节优化：
                    - 【提示词强化】评测等参考资料用明确边界标记包裹，
                      并在 user_msg 末尾重复关键格式要求（reminder 技巧），
                      防止大量参考资料"淹没"系统提示词导致 AI 不遵守格式
                    - 【配置文件夹快捷入口】AI 配置页面的路径文字变为可点击链接，
                      点击直接打开 ~/.steam_notes_gen/ 目录
                    - 【确信度筛选修复】筛选下拉框始终显示全部 5 个等级
                      （很高/较高/中等/较低/很低），不再只显示当前数据中存在的等级
                    - 【批量生成 - 图例精简】移除 AI 筛选行的拥挤图例说明
                    - 【笔记预览修复】双击预览窗口现在只显示 AI 笔记（无 AI 笔记时
                      回退显示手动笔记）；修复 scrollbar 父级错误导致关闭按钮冻结；
                      窗口大小自适应内容长度
2026-02-09  v4.5 — AI 信息源大幅增强（评测接入 + 联网搜索 + 代理兼容修复）：
                    - 【Steam 评测接入】新增 get_game_reviews_from_steam() 方法，
                      通过 Steam appreviews API 获取「最有帮助」的玩家评测文本，
                      使用 purchase_type=steam 过滤，并排除 received_for_free 的评测
                    - 【好评率】从评测 API 的 query_summary 中提取好评率、评价等级
                      （如"特别好评"、"褒贬不一"）和评价总数，写入 AI 参考上下文
                    - 新增 format_review_context() 方法，将评测摘要格式化为 AI 可参考文本，
                      包含好评/差评各取最有帮助的若干条（截取前300字），中英文各取一批
                    - 【Claude 联网搜索】Anthropic 提供商新增可选的 Web Search 功能，
                      在底部按钮栏勾选「🔍 联网搜索」后，Claude 可自行上网搜索游戏信息
                      （需 Anthropic 官方 API + 额外费用 $10/1000次搜索）
                    - 使用第三方代理（自定义URL）时自动禁用联网搜索并给出说明
                    - _call_anthropic() 支持 web_search_20250305 工具和对应 beta header
                    - generate_note() 新增 use_web_search 参数
                    - 【代理兼容性修复】使用第三方代理（new-api/one-api 等）时，
                      自动添加 Authorization: Bearer 认证头，兼容需要 Bearer Token
                      格式的代理服务（修复"未提供令牌"401错误）
                    - 响应解析同时兼容 Anthropic 格式和 OpenAI 格式（choices[0].message）
                    - 【确信度 emoji】全局引入 CONFIDENCE_EMOJI 映射（🟢很高 🔵较高 🟡中等 🟠较低 🔴很低），
                      在主界面和 AI 批量生成界面的游戏列表中，AI 处理过的游戏名后显示确信度 emoji
                    - 【批量生成 - 确信度筛选】AI 筛选选中"AI处理过"或具体模型时，
                      自动显示确信度二级筛选下拉框（与主界面一致）
                    - 【批量生成 - 双击预览笔记】双击游戏列表中的条目，弹出笔记预览窗口，
                      清晰展示 AI 笔记正文、确信度、模型信息；手动笔记也一并显示
                    - 【UI 优化】全局选项（跳过已有AI笔记、联网搜索）移至底部按钮栏，
                      在"从Steam库选择"和"手动输入AppID"两种模式下均可见
                    - 简化笔记覆盖逻辑：取消勾选"跳过已有AI笔记"时，自动替换旧AI笔记
                    - 401 错误时给出具体排查建议并停止后续生成（避免浪费时间）
2026-02-09  v4.4 — 确信度筛选 + 列表多选导出 + 游戏名修复：
                    - 修复游戏名称不显示的 bug：刷新时强制重建缓存，
                      在线扫描失败时输出简短提示而非静默吞没
                    - 新增 extract_ai_confidence_from_note() 函数，从 AI 笔记标题解析确信度
                    - scan_ai_notes 返回结果新增 confidences 字段
                    - 筛选「AI 处理过」或具体模型时，自动出现确信度二级筛选下拉框
                    - 列表改为多选模式（selectmode=extended），支持 Ctrl/Shift 多选
                    - 列表上方工具栏新增「📤 批量导出」按钮，直接导出选中的游戏笔记
                    - 移除旧版「📤 批量导出」按钮及其弹窗（功能已整合到列表工具栏）
2026-02-09  v4.3 — 主界面 UI 优化 + 游戏名称解析：
                    - 游戏名称：优先使用 Steam Web API 在线解析游戏名（需配置 API Key），
                      结果缓存至 _game_name_cache 避免重复请求；本地扫描作为 fallback
                    - 列表上方新增紧凑工具栏（📋复制ID / ☁️上传选中 / ☁️全部上传），
                      列表下方仅保留 🔄刷新 和 📋查看，整体更窄更紧凑
                    - Treeview 列宽收窄（#0: 340→280），减少右侧面板整体宽度
                    - 新增 UI 提示文本：「☁️ 上传后仍需等待 Steam 自动同步到云端」
2026-02-09  v4.2 — Steam 进程监控 + 列表性能优化：
                    - 新增 Steam 进程后台监控：连接 Cloud 后每 5 秒检测 Steam 是否在运行，
                      一旦检测到 Steam 关闭，自动断开 Cloud 连接并更新界面状态
                    - SteamCloudUploader 新增 is_steam_running() 静态方法（跨平台）
                    - 右侧游戏列表从 Canvas+Frame-per-row 改为 ttk.Treeview 实现，
                      大幅减少 widget 数量，数百条目也能流畅滚动
                    - 行内按钮（📋 ☁️）改为底部按钮 + 右键菜单，保留全部功能
2026-02-09  v4.1 — 延迟上传 + 行内操作按钮：
                    - 所有笔记改动仅写入本地，标记 dirty，不自动上传
                    - 主界面游戏列表改为 Canvas 滚动列表，每行带行内按钮
                    - 每行右侧 📋 按钮一键复制 AppID（无弹窗）
                    - dirty 条目显示 ☁️ 上传按钮和黄色高亮
                    - 底部新增「☁️ 全部上传」批量上传按钮
                    - 筛选器新增「☁️ 有改动」选项
                    - 导言区新增规则 #17 延迟上传 和 #18 行内操作按钮
2026-02-09  v4.0 — Steam Cloud 直接上传（重大改进）：
                    - 通过 Steamworks API (ISteamRemoteStorage::FileWrite) 直接上传笔记到 Steam Cloud
                    - 主界面新增「☁️ 连接 Steam Cloud」按钮，连接后保存即自动上传
                    - 自动搜索已安装 Steam 游戏中的 libsteam_api 动态库
                    - 移除旧版「删除该笔记以触发云同步」机制（不再需要手动操作）
                    - 移除"⚠️ 需要云同步"筛选器和红色标记（不再需要）
                    - 保存笔记后不再关闭重开窗口，交互更流畅
                    - 删除全部笔记时同步从 Steam Cloud 删除
                    - 新增 SteamCloudUploader 类，封装 Steamworks API 调用
2026-02-08  v3.5 — AI 批量生成功能优化（家庭共享支持）：
                    - 打开 AI 批量生成窗口时自动触发在线扫描（如已配置 Steam API Key 和 Steam ID）
                    - 【核心改进】收藏夹筛选改为交集逻辑：选择收藏夹后，只显示"该收藏夹中且被扫描用户拥有的游戏"
                    - 这样在扫描家庭组成员时，选择自己的收藏夹，就只会显示该成员拥有的游戏
                    - 避免在家庭组成员没有的游戏上浪费 AI token
                    - 统计信息更清晰：显示"收藏夹共 X 款，该用户拥有 Y 款"
2026-02-08  v3.4 — 多项界面改进：
                    - 修复保存提示词时的参数错误
                    - AI批量生成窗口打开时自动扫描本地游戏库
                    - 主界面笔记列表显示游戏名称而不仅仅是AppID
                    - 需要云同步的游戏支持点击复制AppID（右键菜单）
2026-02-08  v3.2 — 新增筛选功能：
                    - 主界面筛选器新增"⚠️ 需要云同步"选项
                    - 可快速筛选出所有需要在 Steam 内手动触发云同步的游戏
                    - 新增UI提示标签说明红色代表需要云同步
2026-02-08  v3.1 — 云同步触发机制增强：
                    - 修改、删除、上移、下移笔记后立刻刷新显示同步触发笔记
                    - 保存修改后立刻关闭并重开窗口以显示同步触发笔记
                    - 禁止在程序内删除云同步触发笔记（第一条提醒笔记受保护）
                    - 禁止移动云同步触发笔记或将其他笔记移动到第一位（保护第一位置）
                    - delete_note、move_note 方法现在会自动调用 _insert_sync_trigger_note
                    - move_note 方法新增保护逻辑，防止破坏同步触发笔记的第一位置
2026-02-08  v3.0 — 云同步触发机制：每次创建/修改笔记后自动在 appid 列表开头
                    插入特殊笔记"删除该笔记以触发云同步"，并在游戏列表中标红
                    显示需要在 Steam 内手动处理的游戏，解决云同步延迟问题
2026-02-06  v2.0 — 带 GUI 的完整版本，参考 Steam_Library_Manager 架构
                    自动扫描 Steam 路径和账号
                    支持创建/查看/编辑/删除笔记
2026-02-06  v2.1 — 富文本编辑器（WYSIWYG）: 所有编辑和显示区域均渲染富文本，
                    工具栏支持全部 Steam 笔记标签，可切换源码模式
                    重新设计导入导出: 单条导出/批量导出 + 对应两种导入模式
                    导入操作始终追加，不再提供覆盖选项
2026-02-06  v2.2 — 修复富文本编辑器 bug:
                    - 修复加粗/斜体/下划线等内联样式被段落 tag 覆盖的问题
                      (使用 tag_raise 确保内联样式优先级高于块级样式)
                    - 无选区点击内联格式按钮时，进入"预设模式"——
                      后续输入的文字自动带该格式，而非静默无反应
                    新增 URL 自动识别: 编辑器和显示区域自动检测 URL 并高亮为
                    可点击链接（蓝色下划线，鼠标变手型）
                    新增 🤖 AI 批量生成: 调用 Anthropic API (Claude) 为 Steam
                    库中的游戏批量生成"游戏说明"笔记，遵循导言区撰写指引
2026-02-07  v2.2.1 — 修复 [url] / [url=...] BBCode 标签未被解析的 bug:
                      之前 [url][/url] 标签会作为纯文本显示，现在正确解析并渲染
                      为可点击链接，支持 [url]链接[/url] 和 [url=链接]文本[/url]
                      修复 [url="..."] 带引号属性未正确解析的问题
                      修复嵌套内联标签不渲染的问题（如 [b][i]text[/i][/b]）:
                      _insert_inline 改为递归实现，支持任意深度嵌套
                      修复列表项中的内联标签（[b][url]等）不渲染的问题
                      标题和顶级内联 token 也支持嵌套内联标签
                      列表项解析时自动去除 [p]...[/p] 包裹
                      "📄 原始文本"改为就地切换（非弹窗），点击切换原始/富文本
                      按钮区改为双行布局，确保上移/下移按钮始终可见
                      斜体样式增加颜色区分以提升可辨识度
                      导言区新增开发规范 #9 增量修改 和 #10 按钮布局规则
                      导言区富文本编辑器设计原则新增嵌套标签和 URL 标签规则
2026-02-07  v2.2.2 — 修复列表项 [/*] 闭合标签未被正确处理的 bug:
                      列表项中 [p][b]...[/b][/p][/*] 格式现在正确解析，
                      先去除 [/*] 再去除 [p]...[/p] 包裹，内联标签正常渲染
                      修复 [*] 和 [/*] 标签在顶层解析器中导致的文本丢失问题
                      调整标题字号以匹配 Steam 客户端实际显示效果:
                      H1: 18→22, H2: 15→17, H3: 13→14
2026-02-07  v2.3   — AI 批量生成功能增强:
                      新增系统提示词显示/编辑区域（可展开/收起/恢复默认）
                      采用"标题=内容"模式: AI 输出纯文本单行，同时作为笔记标题和内容，
                      在 Steam 笔记列表中无需点进去即可看到全部说明
                      移除"笔记标题"输入框（不再需要固定标题）
                      自动去除 AI 输出中的换行和残留 BBCode 标签
                      generate_note 方法新增 system_prompt 参数支持自定义提示词
                      更新系统提示词: 禁止分段式小标题，要求连贯叙述风格
                      更新导言区 AI 撰写指引第 8 条以反映新格式要求
2026-02-07  v2.4   — AI 批量生成功能增强 — 游戏库扫描:
                      新增 SteamAccountScanner.scan_library() 方法，
                      扫描 steamapps/appmanifest_*.acf 获取用户库中所有已安装游戏
                      支持多库目录（通过 libraryfolders.vdf 发现额外 Steam 库文件夹）
                      AI 批量生成窗口新增双模式切换:
                        模式1「📚 从 Steam 库选择游戏」— 扫描库后以列表展示，
                        支持全选/取消全选/多选/搜索筛选
                        模式2「✏️ 手动输入 AppID」— 保留原有手动输入方式
                      列表显示实时已选数量，搜索框支持按游戏名或 AppID 即时筛选
2026-02-07  v2.5   — 游戏库扫描大幅增强:
                      新增 scan_library_online() 方法，通过 Steam Web API
                      (IPlayerService/GetOwnedGames) 获取用户完整游戏库，
                      包含未安装的游戏和免费游戏，结果远比本地扫描完整
                      支持输入任意 Steam ID / 好友代码扫描他人的库（如家庭共享来源）
                      好友代码（32位）自动转换为 Steam 64位 ID
                      在线扫描为主要方式，本地扫描保留为 fallback
                      AI 声明前缀: 每条生成的笔记自动添加
                      "⚠️ 以下内容由 {模型名} 生成，该模型对以下内容的确信程度：{X}"
                      确信程度由 AI 根据自身对该游戏的了解程度自评
                      (很高/较高/中等/较低/很低)，从 API 响应中解析实际模型名
                      导言区新增【AI 声明前缀】规则
2026-02-07  v2.6   — 调试信息可复制:
                      调试信息窗口中的文本现在可以直接选中复制，
                      不再需要截图（修复 Text widget DISABLED 阻止选择的问题）
                      API Key 持久化:
                      主界面新增「🔑 API Key 设置」，可保存 Anthropic API Key 和
                      Steam Web API Key 到本地配置文件（~/.steam_notes_gen/config.json），
                      保存后全局使用，无需每次输入；支持查看、清除已保存的 Key
                      AI 生成前自动获取游戏详情:
                      在调用 AI 之前，自动通过 Steam Store API (appdetails) 获取游戏的
                      完整信息（开发商、发行商、类型标签、功能特性、官方简介、Metacritic
                      评分、评价数、发行日期等），作为补充上下文传给 AI，大幅提升
                      冷门/独立游戏说明的准确性
                      新增 get_game_details_from_steam() 和 format_game_context() 方法
                      导言区新增开发规范 #11 调试信息规范 和 #12 版本管理规则
2026-02-07  v2.7   — 多 AI 提供商支持:
                      重构 SteamAIGenerator 类，支持 Anthropic (Claude)、OpenAI (GPT)、
                      DeepSeek 及任意 OpenAI 兼容 API（自定义 URL）
                      输入 API Key 后自动根据前缀检测提供商（sk-ant- → Anthropic,
                      sk- → OpenAI），并自动切换可用模型列表
                      新增"自定义 (OpenAI 兼容)"模式，支持填写任意 API URL
                      AI 批量生成窗口 UI 大幅重排:
                      采用 PanedWindow 左右+上下分割布局，左列 API 设置+提示词，
                      右列游戏列表，下方进度区。设置最小窗口尺寸 900×700，
                      游戏列表和按钮不再被挤压截断。搜索框与状态信息同行显示，
                      操作按钮分两行排列确保全部可见
2026-02-08  v2.8   — 所有提供商支持自定义 API URL:
                      任何提供商（Anthropic / OpenAI / DeepSeek）均可覆盖默认 API URL，
                      支持第三方中转服务（如 CC-max 等）使用 Anthropic 格式端点
                      自定义 URL 输入框在所有提供商下均可见（带默认值占位提示），
                      留空时使用官方默认地址，填写后覆盖
                      自动检测提供商逻辑优化: 非 sk-ant- 开头的 Key 不再自动切换提供商，
                      避免中转服务 Key 被误判
2026-02-08  v3.0   — 重大功能更新:
                      【持久化配置】主界面 API Key 设置升级为完整的 AI 配置管理:
                      提供商、模型、自定义 URL 均可保存到本地配置文件，
                      AI 批量生成窗口不再重复显示 API 配置，仅显示提示词和游戏列表
                      【AI 前缀识别】AI 生成的笔记强制以固定前缀 "🤖AI:" 开头，
                      程序自动扫描识别 AI 处理过的笔记，后续批量生成默认跳过，
                      可选择重新生成覆盖；AI 处理过的笔记在列表中显示蓝色，
                      鼠标悬停可查看是哪个 AI 模型处理的
                      【Steam 分类筛选】AI 批量生成支持按 Steam 收藏夹/分类筛选游戏，
                      通过读取 cloud-storage-namespace-1.json 获取用户收藏夹列表，
                      选择分类后只处理该分类内的游戏
                      【AI 筛选器】主界面和 AI 生成界面新增 AI 处理状态筛选器：
                      可一键过滤已处理/未处理的游戏，按不同 AI 模型分类查看，
                      双击即可打开查看笔记
                      【配置布局优化】AI 生成界面更紧凑：API 状态显示为只读摘要，
                      Steam API Key 和 ID 也仅显示配置状态提示
                      【笔记创建统一性】AI 生成笔记使用与手动创建完全相同的
                      create_note 方法，确保文件格式和云同步行为一致
2026-02-08  v3.0.1 — 修复 AI 笔记识别不兼容旧格式:
                      新增 AI_NOTE_PREFIX_LEGACY 支持，同时识别旧版 "⚠️ 以下内容由"
                      和新版 "🤖AI:" 两种前缀，确保已有 AI 笔记能被正确检测
                      修复 Steam 分类筛选与游戏库取交集的问题:
                      选择分类后显示该分类内的所有 AppID（不再要求游戏在库中），
                      分类中的游戏如果在库中则显示游戏名，否则显示 "AppID xxx"
                      恢复 Steam ID 输入框:
                      AI 批量生成窗口恢复 Steam ID 输入框，允许填写家庭组其他成员 ID
                      以扫描其游戏库（适用于家庭共享场景）
================================================================================
"""

import json
import os
import re
import time
import random
import string
import platform
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import tkinter.font as tkfont
from datetime import datetime

# AI 批量生成所需（可选依赖，缺失时禁用 AI 功能）
try:
    import urllib.request
    import urllib.error
    import ssl
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


def _get_ssl_context():
    """获取 SSL 上下文，macOS Python 安装后未运行证书脚本时自动 fallback"""
    try:
        # 先尝试正常的默认上下文（有系统证书）
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        pass
    # fallback: 使用未验证的上下文（仍然加密，但不验证服务端证书）
    ctx = ssl._create_unverified_context()
    return ctx


def _urlopen(req, timeout=30):
    """封装 urlopen，自动处理 SSL 证书问题"""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            # macOS Python 未安装证书，使用未验证上下文重试
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise


# ═══════════════════════════════════════════════════════════════════════════════
#  Steam Cloud 上传器 (通过 Steamworks API 直接上传)
# ═══════════════════════════════════════════════════════════════════════════════

import ctypes
import glob
import hashlib
import subprocess
import tempfile

class SteamCloudUploader:
    """通过 Steamworks SDK 的 ISteamRemoteStorage::FileWrite 直接上传文件到 Steam Cloud。
    
    原理：加载任意已安装 Steam 游戏中的 libsteam_api.dylib/.so/.dll，
    调用与 Steam 笔记程序内部相同的 FileWrite API，使 Steam 客户端认为
    是应用内写入，从而触发云同步。
    """
    
    def __init__(self):
        self.dll = None
        self.remote_storage = None
        self.initialized = False
        self._dylib_path = None
        self._work_dir = None
        self._init_error = None
        self.logged_in_friend_code = None  # 当前登录的 Steam 账号 32 位 ID
    
    def auto_init(self, steam_path: str, app_id: str = "2371090") -> tuple:
        """自动查找 dylib 并初始化 Steam API。
        Returns: (success: bool, message: str)
        """
        # 1. 查找 dylib
        dylib = self._find_dylib(steam_path)
        if not dylib:
            self._init_error = "未找到 libsteam_api"
            return False, "未找到 libsteam_api.dylib/.so/.dll"
        self._dylib_path = dylib
        
        # 2. 创建临时目录写 steam_appid.txt
        self._work_dir = tempfile.mkdtemp(prefix="steam_cloud_")
        with open(os.path.join(self._work_dir, "steam_appid.txt"), "w") as f:
            f.write(app_id)
        
        # 3. 初始化
        old_cwd = os.getcwd()
        os.chdir(self._work_dir)
        try:
            return self._do_init()
        finally:
            os.chdir(old_cwd)
    
    def _find_dylib(self, steam_path: str) -> str:
        """在 Steam 安装目录中搜索 libsteam_api"""
        system = platform.system()
        if system == "Darwin":
            name = "libsteam_api.dylib"
        elif system == "Linux":
            name = "libsteam_api.so"
        else:
            name = "steam_api.dll"
        
        common = os.path.join(steam_path, "steamapps", "common")
        if os.path.isdir(common):
            for found in glob.glob(os.path.join(common, "**", name), recursive=True):
                return found
        
        # macOS: 也搜索 /Applications/Steam.app
        if system == "Darwin":
            for found in glob.glob(
                os.path.join("/Applications/Steam.app", "**", name), recursive=True
            ):
                return found
        return None
    
    def _do_init(self) -> tuple:
        """加载 dylib 并初始化 Steam API"""
        try:
            self.dll = ctypes.CDLL(self._dylib_path)
        except OSError as e:
            self._init_error = f"加载 dylib 失败: {e}"
            return False, self._init_error
        
        # 尝试新版 Init (SDK 1.58+)
        ok = False
        try:
            func = self.dll.SteamInternal_SteamAPI_Init
            func.restype = ctypes.c_int
            err_msg = ctypes.create_string_buffer(1024)
            result = func(None, ctypes.byref(err_msg))
            ok = (result == 0)
            if not ok:
                err = err_msg.value.decode("utf-8", errors="replace")
                self._init_error = f"Init 失败: {err}"
        except AttributeError:
            # 尝试旧版
            try:
                func = self.dll.SteamAPI_Init
                func.restype = ctypes.c_bool
                ok = func()
                if not ok:
                    self._init_error = "SteamAPI_Init 返回 false"
            except AttributeError:
                self._init_error = "找不到 Init 函数"
                return False, self._init_error
        
        if not ok:
            return False, self._init_error
        
        # 获取 ISteamRemoteStorage
        for ver in ["v016", "v014", "v013"]:
            try:
                func = getattr(self.dll, f"SteamAPI_SteamRemoteStorage_{ver}")
                func.restype = ctypes.c_void_p
                ptr = func()
                if ptr:
                    self.remote_storage = ptr
                    self.initialized = True
                    # 获取当前登录的 Steam 账号
                    self._detect_logged_in_user()
                    return True, f"OK ({ver})"
            except AttributeError:
                continue
        
        self._init_error = "无法获取 RemoteStorage 接口"
        return False, self._init_error

    def _detect_logged_in_user(self):
        """通过 Steamworks API 获取当前登录的 Steam 账号 ID"""
        if not self.dll:
            return
        try:
            # 获取 ISteamUser 接口
            steam_user = None
            for ver in ["v023", "v021", "v020"]:
                try:
                    func = getattr(self.dll, f"SteamAPI_SteamUser_{ver}")
                    func.restype = ctypes.c_void_p
                    ptr = func()
                    if ptr:
                        steam_user = ptr
                        break
                except AttributeError:
                    continue
            if not steam_user:
                return
            # 调用 GetSteamID 获取 64 位 Steam ID
            get_id_func = self.dll.SteamAPI_ISteamUser_GetSteamID
            get_id_func.restype = ctypes.c_uint64
            get_id_func.argtypes = [ctypes.c_void_p]
            steam_id64 = get_id_func(steam_user)
            if steam_id64 and steam_id64 > 76561197960265728:
                self.logged_in_friend_code = str(
                    steam_id64 - 76561197960265728)
        except Exception:
            pass  # 检测失败不影响主功能
    
    def file_write(self, filename: str, data: bytes) -> bool:
        """调用 ISteamRemoteStorage::FileWrite 上传文件到 Steam Cloud"""
        if not self.initialized:
            return False
        try:
            func = self.dll.SteamAPI_ISteamRemoteStorage_FileWrite
            func.restype = ctypes.c_bool
            func.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                             ctypes.c_void_p, ctypes.c_int32]
            result = func(self.remote_storage, filename.encode("utf-8"),
                          data, len(data))
            # 跑一次回调确保数据发出
            try:
                self.dll.SteamAPI_RunCallbacks()
            except:
                pass
            return result
        except Exception:
            return False
    
    def file_delete(self, filename: str) -> bool:
        """调用 ISteamRemoteStorage::FileDelete 从 Steam Cloud 删除文件"""
        if not self.initialized:
            return False
        try:
            func = self.dll.SteamAPI_ISteamRemoteStorage_FileDelete
            func.restype = ctypes.c_bool
            func.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
            result = func(self.remote_storage, filename.encode("utf-8"))
            try:
                self.dll.SteamAPI_RunCallbacks()
            except:
                pass
            return result
        except Exception:
            return False
    
    @staticmethod
    def is_steam_running() -> bool:
        """检测 Steam 客户端是否正在运行（跨平台）"""
        system = platform.system()
        try:
            if system == "Windows":
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq steam.exe"],
                    capture_output=True, text=True, timeout=5)
                return "steam.exe" in result.stdout.lower()
            elif system == "Darwin":
                result = subprocess.run(
                    ["pgrep", "-x", "steam_osx"],
                    capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
                # fallback: 也检查 Steam Helper 进程
                result = subprocess.run(
                    ["pgrep", "-f", "Steam.app"],
                    capture_output=True, timeout=5)
                return result.returncode == 0
            else:  # Linux
                result = subprocess.run(
                    ["pgrep", "-x", "steam"],
                    capture_output=True, timeout=5)
                return result.returncode == 0
        except Exception:
            return True  # 检测失败时保守地认为 Steam 在运行

    def shutdown(self):
        if self.initialized:
            try:
                self.dll.SteamAPI_Shutdown()
            except:
                pass
            self.initialized = False
            self.remote_storage = None
            self.logged_in_friend_code = None


# ═══════════════════════════════════════════════════════════════════════════════
#  Steam 账号扫描器
# ═══════════════════════════════════════════════════════════════════════════════

NOTES_APPID = "2371090"

# AI 生成笔记的固定前缀标志 — 用于识别哪些笔记是 AI 处理过的
AI_NOTE_PREFIX = "🤖AI:"
# 旧版前缀关键词（v2.x 使用），仍需识别
AI_NOTE_LEGACY_KEYWORD = "以下内容由"

def is_ai_note(note: dict) -> bool:
    """检测一条笔记是否为 AI 生成
    核心逻辑：标题中包含「以下内容由...生成」即为 AI 笔记。
    也兼容新版 🤖AI: 前缀。
    """
    title = note.get("title", "")
    if not title:
        return False
    # 最可靠的方式：只要标题里出现"以下内容由"就是 AI 笔记
    if AI_NOTE_LEGACY_KEYWORD in title and "生成" in title:
        return True
    # 新版前缀（去掉变体选择符后匹配）
    clean = title.replace('\ufe0e', '').replace('\ufe0f', '')
    if clean.startswith("🤖AI:"):
        return True
    return False

def extract_ai_model_from_note(note: dict) -> str:
    """从 AI 笔记标题中提取模型名。
    找「以下内容由 XXX 生成」中的 XXX，这就是模型名。
    """
    title = note.get("title", "")
    if not title:
        return ""
    m = re.search(r'以下内容由\s*(.+?)\s*生成', title)
    return m.group(1).strip() if m else ""

def extract_ai_confidence_from_note(note: dict) -> str:
    """从 AI 笔记标题中提取确信程度。
    找「确信程度：X」中的 X（很高/较高/中等/较低/很低）。
    """
    title = note.get("title", "")
    if not title:
        return ""
    m = re.search(r'确信程度[：:]\s*(很高|较高|中等|较低|很低)', title)
    return m.group(1) if m else ""


# AI 确信度对应 emoji（用于列表显示，直观表示 AI 自评可靠程度）
CONFIDENCE_EMOJI = {
    "很高": "🟢",
    "较高": "🔵",
    "中等": "🟡",
    "较低": "🟠",
    "很低": "🔴",
}


class SteamAccountScanner:
    """Steam 账号扫描器：自动发现系统中所有 Steam 账号及笔记路径"""

    @staticmethod
    def get_steam_paths():
        """获取所有可能的 Steam 安装路径"""
        system = platform.system()
        paths = []

        # 检测 WSL
        is_wsl = False
        if system == "Linux":
            try:
                with open("/proc/version", "r") as f:
                    if "microsoft" in f.read().lower():
                        is_wsl = True
            except:
                pass

        if system == "Windows":
            possible = [
                os.path.expandvars(r"%ProgramFiles(x86)%\Steam"),
                os.path.expandvars(r"%ProgramFiles%\Steam"),
                r"C:\Steam", r"D:\Steam", r"E:\Steam",
                r"D:\Program Files (x86)\Steam",
                r"D:\Program Files\Steam",
                r"E:\Program Files (x86)\Steam",
                r"E:\Program Files\Steam",
            ]
            # 尝试注册表
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\WOW6432Node\Valve\Steam")
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                winreg.CloseKey(key)
                if install_path and install_path not in possible:
                    paths.append(install_path)
            except:
                pass
            paths.extend(possible)

        elif system == "Darwin":
            home = os.path.expanduser("~")
            paths = [
                os.path.join(home, "Library/Application Support/Steam"),
            ]

        elif system == "Linux":
            home = os.path.expanduser("~")
            paths = [
                os.path.join(home, ".steam/steam"),
                os.path.join(home, ".local/share/Steam"),
                os.path.join(home, ".steam"),
            ]
            if is_wsl:
                for drive in "cdefgh":
                    paths.extend([
                        f"/mnt/{drive}/Program Files (x86)/Steam",
                        f"/mnt/{drive}/Program Files/Steam",
                        f"/mnt/{drive}/Steam",
                    ])

        return [p for p in paths if os.path.exists(p)]

    @staticmethod
    def _get_persona_name(userdata_path, friend_code):
        """尝试从配置文件获取用户昵称"""
        localconfig_path = os.path.join(userdata_path, "config", "localconfig.vdf")
        if os.path.exists(localconfig_path):
            try:
                with open(localconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                match = re.search(r'"PersonaName"\s+"([^"]+)"', content)
                if match:
                    return match.group(1)
            except:
                pass
        return f"Steam 用户 {friend_code}"

    @staticmethod
    def scan_accounts():
        """扫描所有 Steam 账号及其笔记目录"""
        accounts = []
        seen_ids = set()
        steam_paths = SteamAccountScanner.get_steam_paths()

        for steam_path in steam_paths:
            userdata_path = os.path.join(steam_path, "userdata")
            if not os.path.exists(userdata_path):
                continue

            try:
                for entry in os.listdir(userdata_path):
                    entry_path = os.path.join(userdata_path, entry)
                    if not os.path.isdir(entry_path) or not entry.isdigit():
                        continue

                    friend_code = entry
                    if friend_code in seen_ids:
                        continue
                    seen_ids.add(friend_code)

                    notes_dir = os.path.join(entry_path, NOTES_APPID, "remote")
                    persona_name = SteamAccountScanner._get_persona_name(
                        entry_path, friend_code
                    )

                    # 计算已有笔记数量
                    notes_count = 0
                    if os.path.exists(notes_dir):
                        notes_count = len([
                            f for f in os.listdir(notes_dir)
                            if f.startswith("notes_") and os.path.isfile(
                                os.path.join(notes_dir, f))
                        ])

                    accounts.append({
                        'friend_code': friend_code,
                        'userdata_path': entry_path,
                        'notes_dir': notes_dir,
                        'persona_name': persona_name,
                        'steam_path': steam_path,
                        'notes_count': notes_count,
                    })
            except PermissionError:
                continue

        return accounts

    @staticmethod
    def scan_library(steam_path: str) -> list:
        """扫描本地 Steam 库中所有已安装的游戏 (通过 appmanifest 文件)

        仅包含本地已安装游戏，作为在线扫描的 fallback。
        Returns: [{app_id: str, name: str}, ...] 按游戏名排序
        """
        games = {}

        # 收集所有 steamapps 目录（包括主目录和额外库文件夹）
        steamapps_dirs = []
        primary_steamapps = os.path.join(steam_path, "steamapps")
        if os.path.isdir(primary_steamapps):
            steamapps_dirs.append(primary_steamapps)
        # 大小写变体 (Linux)
        primary_lower = os.path.join(steam_path, "SteamApps")
        if os.path.isdir(primary_lower) and primary_lower != primary_steamapps:
            steamapps_dirs.append(primary_lower)

        # 读取 libraryfolders.vdf 以发现额外库目录
        for sa_dir in list(steamapps_dirs):
            lf_path = os.path.join(sa_dir, "libraryfolders.vdf")
            if os.path.exists(lf_path):
                try:
                    with open(lf_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    # 匹配 "path" "..." 条目
                    for m in re.finditer(r'"path"\s+"([^"]+)"', content):
                        extra_path = m.group(1).replace("\\\\", "\\")
                        extra_sa = os.path.join(extra_path, "steamapps")
                        if os.path.isdir(extra_sa) and extra_sa not in steamapps_dirs:
                            steamapps_dirs.append(extra_sa)
                except Exception:
                    pass

        # 扫描所有 steamapps 目录中的 appmanifest 文件
        for sa_dir in steamapps_dirs:
            try:
                for fname in os.listdir(sa_dir):
                    if not fname.startswith("appmanifest_") or not fname.endswith(".acf"):
                        continue
                    fpath = os.path.join(sa_dir, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        aid_m = re.search(r'"appid"\s+"(\d+)"', content)
                        name_m = re.search(r'"name"\s+"([^"]+)"', content)
                        if aid_m:
                            aid = aid_m.group(1)
                            name = name_m.group(1) if name_m else f"AppID {aid}"
                            # 过滤掉 Steam 自身和一些工具类 AppID
                            if aid not in games and aid not in (
                                "228980",  # Steamworks Common Redistributables
                                "250820",  # SteamVR
                                "1007",    # Steam Client
                            ):
                                games[aid] = name
                    except Exception:
                        continue
            except PermissionError:
                continue

        # 按游戏名排序返回
        result = [{'app_id': aid, 'name': name} for aid, name in games.items()]
        result.sort(key=lambda x: x['name'].lower())
        return result

    @staticmethod
    def scan_library_online(steam_id: str, api_key: str) -> tuple:
        """通过 Steam Web API 获取用户拥有的所有游戏（含家庭共享等）

        Returns: (games_list, debug_info) — 永远不抛异常，所有错误记入 debug_info
        """
        import traceback as _tb
        debug_lines = []
        debug_lines.append(f"[输入] steam_id = '{steam_id}'")
        debug_lines.append(f"[输入] api_key = '{api_key[:6]}...{api_key[-4:]}'"
                           if len(api_key) > 10 else f"[输入] api_key = '(长度={len(api_key)})'")

        # 如果传入的是32位好友代码（Steam3 AccountID），转换为64位 Steam ID
        # 64位 Steam ID 始终 >= 76561197960265728（17位数字）
        # 32位 AccountID 最大约 43 亿（10位数字），远小于此值
        sid = steam_id.strip()
        debug_lines.append(f"[处理] 去空格后 sid = '{sid}'")
        debug_lines.append(f"[处理] sid.isdigit() = {sid.isdigit()}")

        if sid.isdigit():
            sid_int = int(sid)
            debug_lines.append(f"[处理] sid 数值 = {sid_int}")
            if sid_int < 76561197960265728:  # 不是64位ID，视为32位好友代码
                old_sid = sid
                sid = str(sid_int + 76561197960265728)
                debug_lines.append(f"[转换] 32位→64位: {old_sid} → {sid}")
            else:
                debug_lines.append(f"[转换] 已是64位ID，无需转换")
        else:
            debug_lines.append(f"[警告] sid 不是纯数字！无法转换")

        url = (f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
               f"?key={api_key}&steamid={sid}"
               f"&include_appinfo=1&include_played_free_games=1"
               f"&include_free_sub=1&skip_unvetted_apps=0")

        # URL 中隐藏 API key 用于调试显示
        debug_url = url.replace(api_key, api_key[:6] + "..." + api_key[-4:]) \
                    if len(api_key) > 10 else url
        debug_lines.append(f"[请求] URL = {debug_url}")

        req = urllib.request.Request(url, headers={
            "User-Agent": "SteamNotesGen/2.8"
        })

        try:
            with _urlopen(req, timeout=30) as resp:
                status_code = resp.getcode()
                raw_body = resp.read().decode("utf-8")
                debug_lines.append(f"[响应] HTTP {status_code}")
                debug_lines.append(f"[响应] body 长度 = {len(raw_body)} 字符")
                body_preview = raw_body[:500]
                debug_lines.append(f"[响应] body 预览 = {body_preview}")

                data = json.loads(raw_body)
        except Exception as e:
            debug_lines.append(f"[错误] {type(e).__name__}: {e}")
            if hasattr(e, 'code'):
                debug_lines.append(f"[错误] HTTP 状态码: {e.code}")
                try:
                    err_body = e.read().decode("utf-8")[:500]
                    debug_lines.append(f"[错误] 响应内容: {err_body}")
                except Exception:
                    pass
            debug_lines.append(f"[Traceback]\n{_tb.format_exc()}")
            return [], "\n".join(debug_lines)

        response_obj = data.get("response", {})
        debug_lines.append(f"[解析] data 顶层键 = {list(data.keys())}")
        debug_lines.append(f"[解析] response 键列表 = {list(response_obj.keys())}")
        debug_lines.append(f"[解析] response.game_count = {response_obj.get('game_count', '(不存在)')}")

        games_data = response_obj.get("games", [])
        debug_lines.append(f"[解析] games 数组长度 = {len(games_data)}")

        if not games_data:
            debug_lines.append(f"[注意] games 为空！完整 response 内容 = {json.dumps(response_obj, ensure_ascii=False)[:500]}")

        if games_data:
            for i, g in enumerate(games_data[:3]):
                debug_lines.append(f"[样本] games[{i}] = {g}")

        result = []
        for g in games_data:
            aid = str(g.get("appid", ""))
            name = g.get("name", f"AppID {aid}")
            if aid:
                result.append({'app_id': aid, 'name': name})

        result.sort(key=lambda x: x['name'].lower())
        debug_lines.append(f"[结果] 最终返回 {len(result)} 款游戏")

        return result, "\n".join(debug_lines)

    @staticmethod
    def get_collections(userdata_path: str) -> list:
        """从 cloud-storage-namespace-1.json 获取用户的 Steam 收藏夹列表

        Returns: [{'name': str, 'app_ids': [int, ...], 'is_dynamic': bool}, ...]
        """
        json_path = os.path.join(userdata_path, "config", "cloudstorage",
                                 "cloud-storage-namespace-1.json")
        if not os.path.exists(json_path):
            return []
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return []

        collections = []
        for entry in data:
            key = entry[0] if isinstance(entry, list) else ""
            meta = entry[1] if isinstance(entry, list) and len(entry) > 1 else {}
            if not key.startswith("user-collections."):
                continue
            if meta.get("is_deleted") is True or "value" not in meta:
                continue
            try:
                val_obj = json.loads(meta['value'])
                is_dynamic = "filterSpec" in val_obj
                app_ids = [int(x) for x in val_obj.get("added", []) if str(x).isdigit()]
                collections.append({
                    "name": val_obj.get("name", "未命名"),
                    "app_ids": app_ids,
                    "is_dynamic": is_dynamic,
                })
            except Exception:
                continue
        collections.sort(key=lambda c: c['name'].lower())
        return collections

    @staticmethod
    def fetch_all_steam_app_names() -> dict:
        """通过 ISteamApps/GetAppList/v2/ 一次性获取 Steam 全量应用名称列表

        无需 API Key，返回 {app_id_str: name_str, ...} 字典。
        约 15 万条记录，跳过名称为空的条目。
        失败时返回空字典。
        """
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "SteamNotesGen/5.2"
            })
            with _urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            apps = data.get("applist", {}).get("apps", [])
            result = {}
            for app in apps:
                aid = str(app.get("appid", ""))
                name = app.get("name", "")
                if aid and name:  # 跳过空名称的条目
                    result[aid] = name
            return result
        except Exception as e:
            print(f"[游戏名称] 全量列表获取失败: {e}")
            return {}


# ═══════════════════════════════════════════════════════════════════════════════
#  Steam 笔记管理器 (核心逻辑)
# ═══════════════════════════════════════════════════════════════════════════════

class SteamNotesManager:
    """Steam 笔记的核心读写逻辑"""

    def __init__(self, notes_dir: str, cloud_uploader: SteamCloudUploader = None,
                 uploaded_hashes: dict = None):
        self.notes_dir = notes_dir
        self.cloud_uploader = cloud_uploader
        self._dirty_apps = set()  # 有本地改动但尚未上传至云的 app_id 集合
        self._uploaded_hashes = uploaded_hashes or {}  # {app_id: md5} 持久化上传记录
        # 启动时根据持久化哈希重建 dirty 状态
        self._rebuild_dirty_from_hashes()

    @staticmethod
    def _gen_id():
        """生成 8 位随机十六进制 ID，与 Steam 原生格式一致"""
        return ''.join(random.choices('0123456789abcdef', k=8))

    @staticmethod
    def _wrap_content(text: str) -> str:
        """将纯文本包裹为 [p]...[/p] 格式（如果尚未包裹）"""
        stripped = text.strip()
        # 如果已经包含富文本标签，不做处理
        if stripped.startswith('[p]') or stripped.startswith('[h1]') or \
           stripped.startswith('[h2]') or stripped.startswith('[h3]') or \
           stripped.startswith('[list]') or stripped.startswith('[olist]'):
            return stripped
        # 按段落分割并包裹
        paragraphs = stripped.split('\n\n')
        wrapped = []
        for p in paragraphs:
            p = p.strip()
            if p:
                wrapped.append(f'[p]{p}[/p]')
        return ''.join(wrapped) if wrapped else f'[p]{stripped}[/p]'

    def _build_entry(self, app_id: str, title: str, content: str) -> dict:
        """构建一条符合 Steam 原生格式的笔记条目"""
        now = int(time.time())
        return {
            "id": self._gen_id(),
            "appid": int(app_id) if app_id.isdigit() else app_id,
            "ordinal": 0,
            "time_created": now,
            "time_modified": now,
            "title": title,
            "content": self._wrap_content(content),
        }

    def _get_note_file(self, app_id: str) -> str:
        return os.path.join(self.notes_dir, f"notes_{app_id}")

    def read_notes(self, app_id: str) -> dict:
        """读取指定游戏的笔记文件"""
        path = self._get_note_file(app_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"notes": []}

    def write_notes(self, app_id: str, data: dict):
        """写入笔记文件（仅本地），并标记为需要上传到云"""
        os.makedirs(self.notes_dir, exist_ok=True)
        path = self._get_note_file(app_id)
        content = json.dumps(data, ensure_ascii=False, indent=2)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self._dirty_apps.add(app_id)

    def cloud_upload(self, app_id: str) -> bool:
        """上传指定 app 的笔记到 Steam Cloud，成功后清除 dirty 标记并记录哈希"""
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            return False
        path = self._get_note_file(app_id)
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        filename = f"notes_{app_id}"
        if self.cloud_uploader.file_write(filename, content.encode("utf-8")):
            self._dirty_apps.discard(app_id)
            # 记录上传后的文件哈希，用于跨会话检测 dirty
            self._uploaded_hashes[app_id] = self._compute_file_hash(path)
            return True
        return False

    def cloud_upload_all_dirty(self) -> tuple:
        """上传所有有改动的笔记到云，返回 (成功数, 失败数)"""
        ok = fail = 0
        for app_id in list(self._dirty_apps):
            if self.cloud_upload(app_id):
                ok += 1
            else:
                fail += 1
        return ok, fail

    def is_dirty(self, app_id: str) -> bool:
        return app_id in self._dirty_apps

    def dirty_count(self) -> int:
        return len(self._dirty_apps)

    @staticmethod
    def _compute_file_hash(filepath: str) -> str:
        """计算文件内容的 MD5 哈希"""
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _rebuild_dirty_from_hashes(self):
        """根据持久化的上传哈希与本地文件对比，重建 dirty 状态"""
        if not os.path.exists(self.notes_dir):
            return
        for f in os.listdir(self.notes_dir):
            fp = os.path.join(self.notes_dir, f)
            if not os.path.isfile(fp) or not f.startswith("notes_"):
                continue
            app_id = f.replace("notes_", "")
            local_hash = self._compute_file_hash(fp)
            stored_hash = self._uploaded_hashes.get(app_id, "")
            if not stored_hash or local_hash != stored_hash:
                self._dirty_apps.add(app_id)

    def mark_as_synced(self, app_id: str) -> bool:
        """手动将指定 app 标记为已同步（记录当前文件哈希，清除 dirty 状态）"""
        path = self._get_note_file(app_id)
        if not os.path.exists(path):
            return False
        self._uploaded_hashes[app_id] = self._compute_file_hash(path)
        self._dirty_apps.discard(app_id)
        return True

    def get_uploaded_hashes(self) -> dict:
        """返回当前上传哈希表（供外部持久化）"""
        return dict(self._uploaded_hashes)

    def create_note(self, app_id: str, title: str, content: str) -> dict:
        """创建一条笔记（始终追加）"""
        entry = self._build_entry(app_id, title, content)
        data = self.read_notes(app_id)
        data["notes"].append(entry)
        self.write_notes(app_id, data)
        return self.read_notes(app_id)

    def update_note(self, app_id: str, index: int, title: str, content: str):
        """更新指定索引的笔记"""
        data = self.read_notes(app_id)
        notes = data.get("notes", [])
        if 0 <= index < len(notes):
            notes[index]["title"] = title
            notes[index]["content"] = self._wrap_content(content)
            notes[index]["time_modified"] = int(time.time())
            self.write_notes(app_id, data)
            return True
        return False

    def delete_note(self, app_id: str, index: int) -> bool:
        """删除指定索引的笔记
        
        Returns: True if deleted, False if invalid index
        """
        data = self.read_notes(app_id)
        notes = data.get("notes", [])
        if 0 <= index < len(notes):
            notes.pop(index)
            self.write_notes(app_id, data)
            return True
        return False

    def delete_all_notes(self, app_id: str) -> bool:
        """删除指定游戏的所有笔记"""
        path = self._get_note_file(app_id)
        if os.path.exists(path):
            os.remove(path)
            self._dirty_apps.discard(app_id)
            # 同时从 Steam Cloud 删除
            if self.cloud_uploader and self.cloud_uploader.initialized:
                self.cloud_uploader.file_delete(f"notes_{app_id}")
            return True
        return False

    def move_note(self, app_id: str, index: int, direction: int) -> bool:
        """移动笔记顺序。direction: -1=上移, +1=下移
        
        Returns: True if moved, False if invalid move
        """
        data = self.read_notes(app_id)
        notes = data.get("notes", [])
        new_index = index + direction
        
        # 检查索引是否有效
        if not (0 <= index < len(notes) and 0 <= new_index < len(notes)):
            return False
        
        # 执行移动
        notes[index], notes[new_index] = notes[new_index], notes[index]
        self.write_notes(app_id, data)
        return True

    def list_all_games(self) -> list:
        """列出所有有笔记的游戏 [{app_id, note_count, file_path}]"""
        if not os.path.exists(self.notes_dir):
            return []
        result = []
        for f in sorted(os.listdir(self.notes_dir)):
            fp = os.path.join(self.notes_dir, f)
            if not os.path.isfile(fp) or not f.startswith("notes_"):
                continue
            app_id = f.replace("notes_", "")
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                notes_list = data.get("notes", [])
                count = len(notes_list)
            except:
                count = 0
            result.append({
                'app_id': app_id,
                'note_count': count,
                'file_path': fp,
            })
        return result

    # ── 批量导出格式标记 ──
    BATCH_EXPORT_HEADER = "# Steam Notes Batch Export"
    BATCH_APP_HEADER = "===APP_ID:"
    BATCH_NOTE_SEP = "---===NOTE_SEPARATOR===---"

    def export_single_note(self, app_id: str, note_index: int, output_path: str):
        """导出单条笔记为独立文件，内容为 BBCode 源码"""
        data = self.read_notes(app_id)
        notes = data.get("notes", [])
        if 0 <= note_index < len(notes):
            note = notes[note_index]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(note.get("content", ""))

    def export_batch(self, app_ids: list, output_path: str, note_filter=None):
        """批量导出多个游戏的笔记为一个结构化文件
        note_filter: 可选的过滤函数，接受 note dict，返回 True 表示导出
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"{self.BATCH_EXPORT_HEADER}\n")
            f.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 包含游戏数: {len(app_ids)}\n\n")

            for app_id in app_ids:
                data = self.read_notes(app_id)
                notes = data.get("notes", [])
                if note_filter:
                    notes = [n for n in notes if note_filter(n)]
                if not notes:
                    continue
                f.write(f"{self.BATCH_APP_HEADER}{app_id}===\n")
                f.write(f"# 笔记数量: {len(notes)}\n\n")
                for i, note in enumerate(notes):
                    if i > 0:
                        f.write(f"\n{self.BATCH_NOTE_SEP}\n\n")
                    f.write(f"## {note.get('title', '(无标题)')}\n\n")
                    f.write(note.get("content", "") + "\n")
                f.write("\n")

    def import_single_note(self, app_id: str, title: str, file_path: str) -> dict:
        """从文件导入单条笔记（始终追加）"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        entry = self._build_entry(app_id, title, content)
        data = self.read_notes(app_id)
        data["notes"].append(entry)
        self.write_notes(app_id, data)
        # 重新读取以返回最新数据
        return self.read_notes(app_id)

    def import_batch(self, file_path: str) -> dict:
        """从批量导出文件导入笔记（始终追加，按 AppID 自动分发）
        Returns: {app_id: count, ...}
        """
        parsed = self.parse_batch_file(file_path)
        return self.apply_batch_import(parsed)

    @staticmethod
    def parse_batch_file(file_path: str) -> dict:
        """解析批量导出文件但不写入。
        Returns: {app_id: [entry_dict, ...], ...}
        每个 entry_dict 包含 title, content (原始文本，尚未 build_entry)
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        result = {}
        app_sections = re.split(r'===APP_ID:(\S+?)===', content)
        i = 1
        while i < len(app_sections) - 1:
            app_id = app_sections[i].strip()
            section = app_sections[i + 1]
            i += 2

            note_blocks = section.split(SteamNotesManager.BATCH_NOTE_SEP)
            entries = []
            for block in note_blocks:
                lines = block.strip().split('\n')
                title = None
                content_lines = []
                for line in lines:
                    if line.startswith('# '):
                        continue
                    if line.startswith('## ') and title is None:
                        title = line[3:].strip()
                        continue
                    content_lines.append(line)
                body = '\n'.join(content_lines).strip()
                if title and body:
                    entries.append({"title": title, "content": body})
                elif title:
                    entries.append({"title": title, "content": ""})

            if entries:
                result[app_id] = entries

        return result

    def apply_batch_import(self, parsed: dict, ai_policy: str = "append",
                           per_app_policy: dict = None) -> dict:
        """将解析后的数据写入笔记文件。
        parsed: {app_id: [{title, content}, ...]}
        ai_policy: 全局 AI 冲突策略
            "append"  — AI 笔记追加在已有笔记之后
            "replace" — 删除已有 AI 笔记，再写入新 AI 笔记
            "skip_ai" — 跳过导入文件中的 AI 笔记（仅导入非 AI 笔记）
        per_app_policy: {app_id: "replace"/"append"/"skip"} 逐一覆盖全局策略
        Returns: {app_id: imported_count, ...}
        """
        if per_app_policy is None:
            per_app_policy = {}
        results = {}

        for app_id, entries in parsed.items():
            policy = per_app_policy.get(app_id, ai_policy)
            data = self.read_notes(app_id)
            existing = data.get("notes", [])

            to_import = []
            for e in entries:
                note = self._build_entry(app_id, e["title"], e["content"])
                is_ai = is_ai_note(note)
                if is_ai and policy == "skip_ai":
                    continue
                to_import.append((note, is_ai))

            if policy == "replace":
                # 移除已有 AI 笔记
                existing = [n for n in existing if not is_ai_note(n)]

            for note, _ in to_import:
                existing.append(note)

            data["notes"] = existing
            self.write_notes(app_id, data)
            imported = len(to_import)
            if imported > 0:
                results[app_id] = imported

        return results

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """将笔记标题转为安全的文件名"""
        # 替换不可用于文件名的字符
        sanitized = re.sub(r'[\\/:*?"<>|]', '_', name)
        sanitized = sanitized.strip('. ')
        if not sanitized:
            sanitized = "untitled"
        return sanitized[:200]  # 限制长度

    def export_individual_files(self, app_ids: list, output_dir: str,
                               note_filter=None) -> tuple:
        """逐条导出：每条笔记导出为独立 txt 文件（文件名=笔记标题，内容=BBCode 源码）

        note_filter: 可选的过滤函数，接受 note dict，返回 True 表示导出
        为避免文件名冲突，同名笔记自动追加序号后缀。
        Returns: (total_files: int, total_notes: int)
        """
        os.makedirs(output_dir, exist_ok=True)
        used_names = {}  # {safe_name: count} 用于去重
        total_files = 0
        total_notes = 0
        for app_id in app_ids:
            data = self.read_notes(app_id)
            notes = data.get("notes", [])
            if note_filter:
                notes = [n for n in notes if note_filter(n)]
            for note in notes:
                total_notes += 1
                title = note.get("title", "untitled")
                content = note.get("content", title)
                safe_name = self.sanitize_filename(title)
                # 去重：如果同名则追加序号
                if safe_name in used_names:
                    used_names[safe_name] += 1
                    final_name = f"{safe_name}_{used_names[safe_name]}"
                else:
                    used_names[safe_name] = 0
                    final_name = safe_name
                filepath = os.path.join(output_dir, f"{final_name}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                total_files += 1
        return total_files, total_notes

    def scan_ai_notes(self) -> dict:
        """扫描所有笔记，识别 AI 处理过的游戏

        Returns: {app_id: {'models': [str], 'note_indices': [int], 'note_count': int,
                            'confidences': [str]}, ...}
        """
        result = {}
        if not os.path.exists(self.notes_dir):
            return result
        for f in os.listdir(self.notes_dir):
            fp = os.path.join(self.notes_dir, f)
            if not os.path.isfile(fp) or not f.startswith("notes_"):
                continue
            app_id = f.replace("notes_", "")
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                notes = data.get("notes", [])
                models = []
                indices = []
                confidences = []
                for i, note in enumerate(notes):
                    if is_ai_note(note):
                        model = extract_ai_model_from_note(note)
                        if model and model not in models:
                            models.append(model)
                        conf = extract_ai_confidence_from_note(note)
                        if conf and conf not in confidences:
                            confidences.append(conf)
                        indices.append(i)
                if indices:
                    result[app_id] = {
                        'models': models,
                        'note_indices': indices,
                        'note_count': len(indices),
                        'confidences': confidences,
                    }
            except Exception:
                continue
        return result

    def find_duplicate_notes(self) -> list:
        """扫描所有笔记，找到标题+内容完全相同的重复项。

        Returns: [{app_id, title, content, indices: [int], count: int}, ...]
        每个条目代表一组重复笔记（同一游戏内），indices 为该组所有副本的索引。
        """
        duplicates = []
        if not os.path.exists(self.notes_dir):
            return duplicates
        for f in os.listdir(self.notes_dir):
            fp = os.path.join(self.notes_dir, f)
            if not os.path.isfile(fp) or not f.startswith("notes_"):
                continue
            app_id = f.replace("notes_", "")
            try:
                with open(fp, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                notes = data.get("notes", [])
                # 按 (title, content) 分组
                seen = {}  # {(title, content): [index, ...]}
                for i, note in enumerate(notes):
                    key = (note.get("title", ""), note.get("content", ""))
                    if key not in seen:
                        seen[key] = []
                    seen[key].append(i)
                for (title, content), indices in seen.items():
                    if len(indices) > 1:
                        duplicates.append({
                            'app_id': app_id,
                            'title': title,
                            'content': content,
                            'indices': indices,
                            'count': len(indices),
                        })
            except Exception:
                continue
        return duplicates

    def delete_duplicate_notes(self, app_id: str, indices_to_remove: list) -> int:
        """删除指定游戏中的重复笔记（按索引列表，从大到小删除避免索引偏移）

        Returns: 实际删除的数量
        """
        data = self.read_notes(app_id)
        notes = data.get("notes", [])
        removed = 0
        for idx in sorted(indices_to_remove, reverse=True):
            if 0 <= idx < len(notes):
                notes.pop(idx)
                removed += 1
        if removed > 0:
            data["notes"] = notes
            if notes:
                self.write_notes(app_id, data)
            else:
                # 没有笔记了，删除文件
                path = self._get_note_file(app_id)
                if os.path.exists(path):
                    os.remove(path)
                self._dirty_apps.discard(app_id)
                if self.cloud_uploader and self.cloud_uploader.initialized:
                    self.cloud_uploader.file_delete(f"notes_{app_id}")
        return removed


# ═══════════════════════════════════════════════════════════════════════════════
#  AI 批量生成器 (Anthropic API)
# ═══════════════════════════════════════════════════════════════════════════════

# 默认系统提示词 — 来自导言区的【AI 撰写游戏说明笔记的指引】
AI_SYSTEM_PROMPT = """你是一个 Steam 游戏介绍撰写助手。请根据用户提供的游戏信息，撰写一段客观的"游戏说明"笔记。

目标读者：不一定了解独立游戏或单机游戏的普通玩家。
目的：让读者快速判断这个游戏是否符合自己的兴趣。

撰写规则（必须全部遵守）：
1. 客观描述：不能照抄商店页面的商业化宣传语，要客观地告诉读者这个游戏是什么、玩起来是什么感觉。
2. "现在打开会怎样"：必须具体描述"如果我现在立刻打开这个游戏，前几分钟会看到什么、做什么"。要写到读者脑中能浮现画面的程度——比如"打开后先是一段过场动画，然后进入角色创建，选完职业后直接被扔进一片雪原，没有任何提示，你需要自己摸索怎么活下去"。❌ 绝对禁止用"上手难度适中""需要一定学习成本""有一定门槛"这类模糊概括代替具体描述。你必须回答的是"我会看到什么界面、做什么操作、遇到什么状况"，而非"难不难"。
3. 认知资源与时间需求：必须说明需要全神贯注还是可以边看视频边玩、是否需要大段连续时间、每局/每次游玩大概多久。
4. 网络口碑：必须提及这个游戏在网络上是否受欢迎、大致评价如何。
5. 缺点与不适人群：必须有一定篇幅介绍缺点，以及明确说明不适合什么样的人玩。
6. 不用术语、说人话：禁止使用读者可能不懂的术语而不加解释。
7. 无需强调性价比：这些游戏已在用户库中，属于免费可玩，绝对禁止提及任何与价格相关的内容。禁止使用的词汇包括但不限于：价格、售价、原价、打折、折扣、性价比、值不值、定价、促销、半价、特惠、入手、购买建议。即使参考资料中大量提到这些内容，你也必须完全忽略——读者已经拥有这个游戏，任何价格讨论都是无意义的。

⚠️ 关键格式要求（最高优先级）：
- 输出必须是【纯文本单行】，即整段说明写在同一行内，禁止换行。
- 禁止使用任何 BBCode 标签（[p] [h1] [b] 等全部禁止）。
- 禁止使用分段式的小标题（如"初次打开的体验："、"认知资源："等），
  而应将所有信息自然融入一段连贯的叙述中，像朋友聊天一样娓娓道来。
- 可以使用 emoji 辅助排版: 📌✅⚠️🗺️⚔️📝🎯，
  但要克制，不要每句话都加 emoji。
- 注意控制长度，建议 200-500 字左右。
- 这段纯文本将同时作为笔记的标题和内容显示在 Steam 客户端中，
  所以第一句话应该具有概括性（如"XXX 是一个……的游戏"），让人一眼能抓住重点。

📋 完成后自查清单（输出前在心里逐条核对，有遗漏必须补上）：
□ 是否具体描述了"现在打开前几分钟会看到什么、做什么"？（不是"上手难度如何"，而是具体场景）
□ 是否说明了认知资源消耗模式（专注型/休闲型）和单次游玩时长？
□ 是否提到了网络口碑/社区评价？
□ 是否有缺点和不适合的人群？
□ 是否全文都是自然连贯的叙述，没有分段标题？
□ 是否纯文本单行，没有换行？
□ 第一句话是否有概括性？
□ 【关键】全文是否完全没有提及价格、性价比、售价、打折等与钱有关的内容？

请直接输出纯文本内容，不要输出任何解释、前缀、标签或格式符号。"""


# ── 联网搜索时追加的系统提示 ──
AI_WEB_SEARCH_ADDENDUM = """

🔍 你已获得联网搜索能力。在撰写之前，请主动搜索以下信息来增强你的描述质量：
1. 这个游戏的实际游玩体验（搜索游戏名 + review / gameplay / 评测）
2. 社区口碑和常见争议（搜索游戏名 + reddit / 讨论 / 争议）
3. 大致通关时长或典型游玩时长（搜索游戏名 + how long to beat / 游玩时长）

搜索策略：
- 优先用英文游戏名搜索，通常结果更丰富
- 如果对这个游戏已经非常了解，可以少搜或不搜；如果不太确定，多搜几次
- 搜索结果仅用于辅助你的写作，不要照抄搜索到的文字
- 特别注意搜索该游戏的缺点和负面评价，因为提示词要求必须包含这些内容"""


class SteamAIGenerator:
    """使用 AI API 生成游戏说明笔记 — 支持 Anthropic (Claude) 和 OpenAI 兼容 API"""

    # ── 已知 API 提供商配置 ──
    PROVIDERS = {
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'api_url': 'https://api.anthropic.com/v1/messages',
            'models': [
                'claude-opus-4-6',
                'claude-opus-4-5-20251101-thinking',
                'claude-sonnet-4-5-20250929',
                'claude-haiku-4-5-20251001',
            ],
            'default_model': 'claude-sonnet-4-5-20250929',
            'key_prefix': 'sk-ant-',
        },
        'openai': {
            'name': 'OpenAI',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'models': [
                'gpt-4o', 'gpt-4o-mini', 'gpt-4.1', 'gpt-4.1-mini',
                'gpt-4.1-nano', 'o3-mini',
            ],
            'default_model': 'gpt-4o-mini',
            'key_prefix': 'sk-',
        },
        'deepseek': {
            'name': 'DeepSeek',
            'api_url': 'https://api.deepseek.com/v1/chat/completions',
            'models': ['deepseek-chat', 'deepseek-reasoner'],
            'default_model': 'deepseek-chat',
            'key_prefix': 'sk-',
        },
        'openai_compat': {
            'name': '自定义 (OpenAI 兼容)',
            'api_url': '',
            'models': [],
            'default_model': '',
            'key_prefix': '',
        },
    }

    def __init__(self, api_key: str, model: str = None,
                 provider: str = 'anthropic', api_url: str = None):
        self.api_key = api_key
        self.provider = provider
        self._last_debug_info = ""
        self.model = model or self.PROVIDERS.get(provider, {}).get(
            'default_model', 'claude-sonnet-4-5-20250929')
        # 允许自定义 API URL（用于 OpenAI 兼容的第三方服务）
        if api_url:
            self.api_url = api_url
        else:
            self.api_url = self.PROVIDERS.get(provider, {}).get(
                'api_url', self.PROVIDERS['anthropic']['api_url'])

    @classmethod
    def detect_provider(cls, api_key: str) -> str:
        """根据 API Key 前缀自动检测提供商
        注意: 仅对明确的前缀（如 sk-ant-）自动切换，
        通用 sk- 前缀不自动切换（可能是中转服务的 Key）。
        """
        key = api_key.strip()
        if key.startswith('sk-ant-'):
            return 'anthropic'
        # 通用 sk- 开头的 Key 不再自动切换，因为中转服务也可能使用 sk- 前缀
        # 用户需要手动选择提供商
        return None  # 返回 None 表示无法自动检测

    def generate_note(self, game_name: str, app_id: str,
                      extra_context: str = "",
                      system_prompt: str = "",
                      use_web_search: bool = False) -> tuple:
        """为单个游戏生成笔记内容

        Returns: (text: str, model: str, confidence: str)
        """
        user_msg = f"请为以下 Steam 游戏撰写游戏说明笔记：\n\n"
        user_msg += f"游戏名称：{game_name}\n"
        user_msg += f"Steam AppID：{app_id}\n"
        if extra_context:
            user_msg += ("\n"
                         "══════ 以下是参考资料（仅供参考，严禁照抄或逐条总结）══════\n"
                         f"{extra_context}\n"
                         "══════ 参考资料结束 ══════\n"
                         "\n"
                         "⚠️ 重要提醒：以上参考资料只是帮你了解这个游戏的素材。\n"
                         "你的任务是根据系统提示词的格式要求，用自己的话写一段连贯自然的游戏说明，\n"
                         "像朋友聊天一样娓娓道来。不要变成「评测摘要」或「信息罗列」。\n")
        user_msg += ("\n请直接输出纯文本内容（单行，无换行，无 BBCode 标签）。\n"
                     "再次强调格式要求：\n"
                     "- 纯文本单行，禁止换行，禁止 BBCode 标签\n"
                     "- 禁止分段式小标题，所有信息融入一段连贯叙述\n"
                     "- 必须包含：「现在打开会怎样」、认知资源与时间需求、网络口碑、缺点与不适人群\n"
                     "- 第一句话要有概括性（如「XXX 是一个……的游戏」）\n"
                     "- 可适度使用 emoji（📌✅⚠️🗺️⚔️📝🎯）但要克制\n"
                     "- 建议 200-500 字\n"
                     "- 🚫 绝对禁止提及价格、售价、性价比、打折、原价、购买建议等任何与钱相关的内容（游戏已在用户库中）\n"
                     "\n"
                     "在你的回复最末尾，另起一行，用以下格式标注你对这段介绍的确信程度：\n"
                     "CONFIDENCE:很高 或 CONFIDENCE:较高 或 CONFIDENCE:中等 "
                     "或 CONFIDENCE:较低 或 CONFIDENCE:很低\n"
                     "（确信程度取决于你对这个游戏的了解程度——"
                     "如果这个游戏你很熟悉、信息确定性高就写\"很高\"，"
                     "如果是比较冷门/不太了解的游戏就写\"较低\"或\"很低\"。）")

        prompt = system_prompt.strip() if system_prompt.strip() else AI_SYSTEM_PROMPT

        # 联网搜索时追加搜索策略指引
        if use_web_search:
            prompt += AI_WEB_SEARCH_ADDENDUM
            user_msg += ("\n\n🔍 联网搜索已启用——如果你对这个游戏不够了解，"
                         "请先用 web_search 搜索它的实际游玩体验、社区口碑、"
                         "通关时长和常见缺点，再开始撰写。")

        if self.provider == 'anthropic':
            return self._call_anthropic(prompt, user_msg,
                                        use_web_search=use_web_search)
        else:
            return self._call_openai_compat(prompt, user_msg,
                                            use_web_search=use_web_search)

    def _call_anthropic(self, system_prompt: str, user_msg: str,
                        use_web_search: bool = False) -> tuple:
        """调用 Anthropic (Claude) API"""
        is_thinking = 'thinking' in self.model.lower()

        # 检测是否通过第三方代理（自定义URL）
        _default_url = self.PROVIDERS['anthropic']['api_url']
        _is_proxy = (self.api_url != _default_url)

        payload_dict = {
            "model": self.model,
            "max_tokens": 16000 if is_thinking else 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_msg}]
        }

        # thinking 模型需要额外参数
        if is_thinking:
            payload_dict["thinking"] = {
                "type": "enabled",
                "budget_tokens": 10000
            }

        # Web Search 工具
        if use_web_search:
            payload_dict["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5,
                }
            ]

        payload = json.dumps(payload_dict).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        # 第三方代理（new-api/one-api 等）通常需要 Bearer 认证
        # 同时发送两种认证头以兼容官方 API 和各类代理
        if _is_proxy:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Web Search 需要 beta header
        if use_web_search:
            headers["anthropic-beta"] = "web-search-2025-03-05"

        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers=headers,
            method="POST",
        )

        # 构建调试信息（在异常时使用）
        self._last_debug_info = self._build_debug_info(
            url=self.api_url, headers=headers, payload=payload_dict,
            method="POST"
        )

        # 联网搜索时 AI 需要更多时间（多次搜索+综合）
        _timeout = 180 if use_web_search else 120
        with _urlopen(req, timeout=_timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            self._last_debug_info += (
                f"\n--- 响应 ---\n"
                f"HTTP 状态码: {resp.status}\n"
                f"响应头: {dict(resp.headers)}\n"
                f"响应体 (前500字): {resp_body[:500]}\n"
            )
            data = json.loads(resp_body)

        content_blocks = data.get("content", [])
        text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
        full_text = "\n".join(text_parts)

        # 兼容：第三方代理可能返回 OpenAI 格式（choices[0].message.content）
        if not full_text and data.get("choices"):
            choices = data["choices"]
            if choices:
                full_text = choices[0].get("message", {}).get("content", "")

        actual_model = data.get("model", self.model)

        return self._extract_confidence(full_text, actual_model)

    def _call_openai_compat(self, system_prompt: str, user_msg: str,
                            use_web_search: bool = False) -> tuple:
        """调用 OpenAI 兼容 API (OpenAI, DeepSeek, 及其他兼容服务)"""
        payload_dict = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ]
        }

        # Web Search 工具（是否可用取决于中转服务商）
        if use_web_search:
            payload_dict["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5,
                }
            ]
        payload = json.dumps(payload_dict).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Web Search 需要 beta header（部分中转会透传给上游 Anthropic）
        if use_web_search:
            headers["anthropic-beta"] = "web-search-2025-03-05"

        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers=headers,
            method="POST",
        )

        # 构建调试信息
        self._last_debug_info = self._build_debug_info(
            url=self.api_url, headers=headers, payload=payload_dict,
            method="POST"
        )

        _timeout = 180 if use_web_search else 120
        with _urlopen(req, timeout=_timeout) as resp:
            resp_body = resp.read().decode("utf-8")
            self._last_debug_info += (
                f"\n--- 响应 ---\n"
                f"HTTP 状态码: {resp.status}\n"
                f"响应头: {dict(resp.headers)}\n"
                f"响应体 (前500字): {resp_body[:500]}\n"
            )
            data = json.loads(resp_body)

        full_text = ""

        # 优先尝试 OpenAI 格式: data.choices[0].message.content
        choices = data.get("choices", [])
        if choices:
            full_text = choices[0].get("message", {}).get("content", "")

        # 兼容 Anthropic 原生格式（部分中转直接透传）
        if not full_text and data.get("content"):
            content_blocks = data.get("content", [])
            text_parts = [b["text"] for b in content_blocks
                          if b.get("type") == "text"]
            full_text = "\n".join(text_parts)

        actual_model = data.get("model", self.model)

        return self._extract_confidence(full_text, actual_model)

    def _build_debug_info(self, url: str, headers: dict, payload: dict,
                          method: str = "POST") -> str:
        """构建调试信息字符串（脱敏）"""
        safe_headers = {}
        for k, v in headers.items():
            if k.lower() in ("x-api-key", "authorization"):
                if len(v) > 16:
                    safe_headers[k] = v[:10] + "..." + v[-4:]
                else:
                    safe_headers[k] = v[:4] + "..."
            else:
                safe_headers[k] = v

        safe_payload = dict(payload)
        if "system" in safe_payload and len(str(safe_payload["system"])) > 200:
            safe_payload["system"] = str(safe_payload["system"])[:200] + "...(截断)"
        if "messages" in safe_payload:
            safe_msgs = []
            for m in safe_payload["messages"]:
                sm = dict(m)
                if len(str(sm.get("content", ""))) > 300:
                    sm["content"] = str(sm["content"])[:300] + "...(截断)"
                safe_msgs.append(sm)
            safe_payload["messages"] = safe_msgs

        lines = [
            "=== API 调试信息 ===",
            f"时间: {datetime.now().isoformat()}",
            f"提供商: {self.provider}",
            f"模型: {self.model}",
            f"API URL: {url}",
            f"HTTP 方法: {method}",
            f"请求头: {json.dumps(safe_headers, ensure_ascii=False, indent=2)}",
            f"请求体: {json.dumps(safe_payload, ensure_ascii=False, indent=2)}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _extract_confidence(full_text: str, actual_model: str) -> tuple:
        """从 AI 输出中提取确信程度标签"""
        confidence = "中等"
        conf_match = re.search(
            r'CONFIDENCE[:：]\s*(很高|较高|中等|较低|很低|相当高|相当低)',
            full_text
        )
        if conf_match:
            confidence = conf_match.group(1)
            full_text = re.sub(r'\n*CONFIDENCE[:：].*$', '', full_text,
                               flags=re.MULTILINE).strip()
        return full_text, actual_model, confidence

    @staticmethod
    def get_game_name_from_steam(app_id: str) -> str:
        """通过 Steam Store API 获取游戏名称"""
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=schinese"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "SteamNotesGen/2.8"
            })
            with _urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            app_data = data.get(str(app_id), {})
            if app_data.get("success"):
                return app_data["data"].get("name", f"AppID {app_id}")
        except Exception:
            pass
        return f"AppID {app_id}"

    @staticmethod
    def get_game_details_from_steam(app_id: str) -> dict:
        """通过 Steam Store API 获取游戏的详细信息（名称、开发商、类型、简介等）

        Returns: dict with keys: name, developers, publishers, genres,
                 categories, short_description, release_date, metacritic,
                 recommendations, etc. 若失败返回空 dict。
        """
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=schinese"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "SteamNotesGen/2.8"
            })
            with _urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            app_data = data.get(str(app_id), {})
            if app_data.get("success"):
                return app_data.get("data", {})
        except Exception:
            pass
        return {}

    @staticmethod
    def format_game_context(details: dict) -> str:
        """将 Steam Store API 返回的游戏详情格式化为 AI 可参考的文本摘要"""
        if not details:
            return ""
        parts = []
        name = details.get("name", "")
        if name:
            parts.append(f"游戏名称：{name}")
        # 类型
        app_type = details.get("type", "")
        if app_type:
            parts.append(f"类型：{app_type}")
        # 开发商 / 发行商
        devs = details.get("developers", [])
        if devs:
            parts.append(f"开发商：{', '.join(devs)}")
        pubs = details.get("publishers", [])
        if pubs:
            parts.append(f"发行商：{', '.join(pubs)}")
        # 类型标签
        genres = details.get("genres", [])
        if genres:
            genre_names = [g.get("description", "") for g in genres]
            parts.append(f"类型标签：{', '.join(genre_names)}")
        # 分类（单人/多人/在线等）
        categories = details.get("categories", [])
        if categories:
            cat_names = [c.get("description", "") for c in categories]
            parts.append(f"功能特性：{', '.join(cat_names)}")
        # 简介
        short_desc = details.get("short_description", "")
        if short_desc:
            # 去除 HTML 标签
            clean_desc = re.sub(r'<[^>]+>', '', short_desc).strip()
            parts.append(f"官方简介：{clean_desc}")
        # 详细描述（about_the_game 通常比 detailed_description 更丰富）
        about = details.get("about_the_game", "") or details.get(
            "detailed_description", "")
        if about:
            clean_about = re.sub(r'<[^>]+>', ' ', about).strip()
            clean_about = re.sub(r'\s+', ' ', clean_about)
            # 截取前800字符，避免过长
            if len(clean_about) > 800:
                clean_about = clean_about[:800] + "…"
            if clean_about and clean_about != (
                    re.sub(r'<[^>]+>', '', short_desc).strip() if short_desc
                    else ""):
                parts.append(f"详细描述：{clean_about}")
        # Metacritic
        mc = details.get("metacritic", {})
        if mc and mc.get("score"):
            parts.append(f"Metacritic 评分：{mc['score']}")
        # Steam 评价数
        recs = details.get("recommendations", {})
        if recs and recs.get("total"):
            parts.append(f"Steam 评价数：{recs['total']}")
        # 发行日期
        rd = details.get("release_date", {})
        if rd and rd.get("date"):
            parts.append(f"发行日期：{rd['date']}")
            if rd.get("coming_soon"):
                parts.append("状态：尚未发售（抢先体验或即将发售）")
        # 支持的平台
        platforms = details.get("platforms", {})
        if platforms:
            plats = [p for p, v in platforms.items() if v]
            if plats:
                parts.append(f"支持平台：{', '.join(plats)}")
        # 支持的语言
        langs = details.get("supported_languages", "")
        if langs:
            clean_langs = re.sub(r'<[^>]+>', '', langs).strip()
            if clean_langs:
                parts.append(f"支持语言：{clean_langs}")
        # 成就数量
        achieves = details.get("achievements", {})
        if achieves and achieves.get("total"):
            parts.append(f"Steam 成就数：{achieves['total']}")
        # DLC 数量
        dlc = details.get("dlc", [])
        if dlc:
            parts.append(f"DLC 数量：{len(dlc)}")
        # 内容描述（成人、暴力等标记）
        content_desc = details.get("content_descriptors", {})
        if content_desc and content_desc.get("notes"):
            parts.append(f"内容警告：{content_desc['notes']}")
        # 是否免费
        if details.get("is_free"):
            parts.append("价格：免费")
        # 是否抢先体验
        if "Early Access" in str(genres):
            parts.append("⚠️ 该游戏目前处于「抢先体验」阶段")

        return "\n".join(parts)

    @staticmethod
    def get_game_reviews_from_steam(app_id: str, num_per_lang: int = 10) -> dict:
        """通过 Steam appreviews API 获取玩家评测文本和评分摘要。

        - 使用 purchase_type=steam 过滤非 Steam 购买来源（如免费 Key）
        - 返回后再过滤 received_for_free=true 的评测
        - 分别获取中文和英文的「最有帮助」评测

        Returns: dict with keys:
            'query_summary': {review_score, review_score_desc, total_positive,
                              total_negative, total_reviews}
            'reviews': list of dicts with keys: text, voted_up, playtime,
                       language, helpful_count
            若失败返回空 dict。
        """
        result = {'query_summary': {}, 'reviews': []}

        for lang in ('schinese', 'english'):
            url = (
                f"https://store.steampowered.com/appreviews/{app_id}"
                f"?json=1&language={lang}&filter=toprated"
                f"&purchase_type=steam&num_per_page={num_per_lang}"
            )
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "SteamNotesGen/4.5"
                })
                with _urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                if data.get("success") != 1:
                    continue

                # 首次获取时保存 query_summary（中文请求的 summary 就够了）
                qs = data.get("query_summary", {})
                if not result['query_summary'] and qs:
                    result['query_summary'] = {
                        'review_score': qs.get('review_score', 0),
                        'review_score_desc': qs.get('review_score_desc', ''),
                        'total_positive': qs.get('total_positive', 0),
                        'total_negative': qs.get('total_negative', 0),
                        'total_reviews': qs.get('total_reviews', 0),
                    }

                for r in data.get("reviews", []):
                    # 过滤：免费获取的评测
                    if r.get("received_for_free", False):
                        continue
                    review_text = r.get("review", "").strip()
                    if not review_text:
                        continue
                    author = r.get("author", {})
                    result['reviews'].append({
                        'text': review_text,
                        'voted_up': r.get("voted_up", True),
                        'playtime': round(
                            author.get("playtime_forever", 0) / 60, 1),
                        'language': lang,
                        'helpful_count': r.get("votes_up", 0),
                    })
            except Exception:
                continue

        return result

    @staticmethod
    def format_review_context(reviews_data: dict,
                              max_reviews: int = 8,
                              max_chars_per_review: int = 300) -> str:
        """将 Steam 评测数据格式化为 AI 可参考的文本摘要。

        包含好评率、评价等级、以及好评和差评的代表性文本摘录。
        """
        if not reviews_data:
            return ""
        parts = []

        # ── 评分摘要 ──
        qs = reviews_data.get('query_summary', {})
        if qs:
            desc = qs.get('review_score_desc', '')
            pos = qs.get('total_positive', 0)
            neg = qs.get('total_negative', 0)
            total = qs.get('total_reviews', 0)
            if total > 0:
                pct = round(pos / total * 100, 1)
                parts.append(
                    f"Steam 评价等级：{desc}（好评率 {pct}%，"
                    f"共 {total} 条评价，{pos} 好评 / {neg} 差评）")
            elif desc:
                parts.append(f"Steam 评价等级：{desc}")

        # ── 评测文本摘录 ──
        reviews = reviews_data.get('reviews', [])
        if not reviews:
            return "\n".join(parts)

        # ── 玩家游玩时长统计（帮助 AI 判断时间投入）──
        playtimes = sorted([r['playtime'] for r in reviews
                            if r['playtime'] > 0])
        if playtimes:
            median_pt = playtimes[len(playtimes) // 2]
            min_pt = playtimes[0]
            max_pt = playtimes[-1]
            parts.append(
                f"评测者游玩时长：中位数 {median_pt}h，"
                f"范围 {min_pt}h ~ {max_pt}h（共 {len(playtimes)} 人）")

        # 按好评/差评分组，各自按有帮助数排序
        positive = sorted(
            [r for r in reviews if r['voted_up']],
            key=lambda r: r['helpful_count'], reverse=True)
        negative = sorted(
            [r for r in reviews if not r['voted_up']],
            key=lambda r: r['helpful_count'], reverse=True)

        # 取最有帮助的几条（好评多取，差评也要有）
        n_pos = min(max(max_reviews * 2 // 3, 1), len(positive))
        n_neg = min(max(max_reviews - n_pos, 1), len(negative))
        if n_neg < max_reviews - n_pos and len(positive) > n_pos:
            n_pos = min(max_reviews - n_neg, len(positive))

        selected = ([('+', r) for r in positive[:n_pos]]
                    + [('-', r) for r in negative[:n_neg]])

        if selected:
            parts.append(
                "\n--- 以下是真实玩家评测摘录（供参考，请勿照抄）---")
            for tag, r in selected:
                text = r['text']
                if len(text) > max_chars_per_review:
                    text = text[:max_chars_per_review] + "…"
                text = ' '.join(text.split())  # 去换行压缩空白
                emoji = '👍' if tag == '+' else '👎'
                pt = (f"{r['playtime']}h"
                      if r['playtime'] > 0 else "未知时长")
                parts.append(f"{emoji} [{pt}] {text}")

        return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
#  富文本编辑器组件 (Steam BBCode WYSIWYG)
# ═══════════════════════════════════════════════════════════════════════════════

class SteamRichTextEditor(tk.Frame):
    """支持 Steam BBCode 的富文本编辑器

    在可视模式下以 tkinter Text widget 的标签渲染 BBCode 效果；
    可切换到源码模式直接编辑 BBCode 源码。
    """

    # 所有支持的 Steam BBCode 标签
    SUPPORTED_TAGS = ['p', 'h1', 'h2', 'h3', 'b', 'i', 'u', 'strike',
                      'list', 'olist', 'hr', 'code', 'url']

    def __init__(self, parent, height=15, **kwargs):
        super().__init__(parent, **kwargs)
        self._source_mode = False
        self._build_ui(height)

    def _build_ui(self, height):
        """构建工具栏和编辑区"""
        # ── 工具栏 ──
        toolbar = tk.Frame(self, bg="#e8e8e8", pady=2)
        toolbar.pack(fill=tk.X)

        # 格式按钮
        btn_defs = [
            ("B", "b", {"font": ("", 10, "bold")}),
            ("I", "i", {"font": ("", 10, "italic")}),
            ("U", "u", {"font": ("", 10, "underline")}),
            ("S", "strike", {"font": ("", 10, "overstrike")}),
            ("|", None, None),  # 分隔
            ("H1", "h1", {}),
            ("H2", "h2", {}),
            ("H3", "h3", {}),
            ("¶", "p", {}),
            ("|", None, None),
            ("• 列表", "list", {}),
            ("1. 列表", "olist", {}),
            ("── 分隔线", "hr", {}),
            ("{code}", "code", {}),
        ]

        for label, tag, _ in btn_defs:
            if tag is None:
                ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
                    side=tk.LEFT, fill=tk.Y, padx=4, pady=2)
                continue
            btn = tk.Button(toolbar, text=label, font=("", 9),
                            relief=tk.FLAT, bg="#e8e8e8", padx=4, pady=1,
                            command=lambda t=tag: self._apply_tag(t))
            btn.pack(side=tk.LEFT, padx=1)

        # 源码模式切换
        self._mode_btn = tk.Button(toolbar, text="📝 源码", font=("", 9),
                                    relief=tk.FLAT, bg="#e8e8e8", padx=6, pady=1,
                                    command=self._toggle_source_mode)
        self._mode_btn.pack(side=tk.RIGHT, padx=5)

        self._mode_label = tk.Label(toolbar, text="可视模式", font=("", 8),
                                     bg="#e8e8e8", fg="#666")
        self._mode_label.pack(side=tk.RIGHT)

        # ── 编辑区 ──
        editor_frame = tk.Frame(self)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self._text = tk.Text(editor_frame, font=("", 11), wrap=tk.WORD,
                             height=height, undo=True, padx=8, pady=5)
        scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL,
                                  command=self._text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._text.config(yscrollcommand=scrollbar.set)
        self._text.pack(fill=tk.BOTH, expand=True)

        # 绑定键盘事件用于"预设模式"
        self._text.bind("<Key>", self._on_key_press, add=True)

        # ── 配置富文本标签样式 ──
        # 解析 Text widget 实际使用的字体族名，确保 italic 等样式有效
        try:
            _base_font = tkfont.Font(font=self._text.cget("font"))
            _family = _base_font.actual()["family"]
        except Exception:
            _family = ""

        self._text.tag_configure("h1", font=(_family, 22, "bold"),
                                  spacing1=10, spacing3=5)
        self._text.tag_configure("h2", font=(_family, 17, "bold"),
                                  spacing1=8, spacing3=4)
        self._text.tag_configure("h3", font=(_family, 14, "bold"),
                                  spacing1=6, spacing3=3)
        self._text.tag_configure("bold", font=(_family, 11, "bold"))
        self._text.tag_configure("italic", font=(_family, 11, "italic"),
                                  foreground="#555555")
        self._text.tag_configure("underline", font=(_family, 11), underline=True)
        self._text.tag_configure("strike", font=(_family, 11), overstrike=True)
        self._text.tag_configure("code", font=("Courier", 10),
                                  background="#f0f0f0", relief=tk.SUNKEN,
                                  borderwidth=1, lmargin1=10, lmargin2=10,
                                  rmargin=10, spacing1=3, spacing3=3)
        self._text.tag_configure("bullet", lmargin1=20, lmargin2=35,
                                  font=("", 11))
        self._text.tag_configure("olist", lmargin1=20, lmargin2=35,
                                  font=("", 11))
        self._text.tag_configure("hr", font=("", 4), justify=tk.CENTER,
                                  foreground="#999", spacing1=5, spacing3=5)
        self._text.tag_configure("paragraph", font=("", 11),
                                  spacing1=2, spacing3=2)
        # URL 样式
        self._text.tag_configure("url", foreground="#1a73e8", underline=True,
                                  font=("", 11))
        self._text.tag_bind("url", "<Enter>",
                            lambda e: self._text.config(cursor="hand2"))
        self._text.tag_bind("url", "<Leave>",
                            lambda e: self._text.config(cursor=""))
        self._text.tag_bind("url", "<Button-1>", self._on_url_click)

        # ── 关键: 设置 tag 优先级 ──
        # 内联样式必须高于块级样式，否则 paragraph 的 font 会覆盖 bold 等
        # tag_raise(a, b) 表示 a 的优先级高于 b
        for inline_tag in ("bold", "italic", "underline", "strike", "url"):
            self._text.tag_raise(inline_tag, "paragraph")
            self._text.tag_raise(inline_tag, "bullet")
            self._text.tag_raise(inline_tag, "olist")

        # 用于"预设模式"——无选区时点格式按钮，后续输入自动带该格式
        self._pending_tags = set()
        # 用于存储 [url=...] 标签的 URL 目标映射: tag_name → url
        self._url_map = {}
        self._url_counter = 0

    # ────────── URL 点击 & 预设模式 ──────────

    _URL_RE = re.compile(r'https?://[^\s\[\]<>"\']+')

    def _on_url_click(self, event):
        """点击 URL 标签时在浏览器中打开"""
        idx = self._text.index(f"@{event.x},{event.y}")
        # 检查是否在带有特定 URL 映射的标签上（[url=...] 格式）
        tags_at_pos = self._text.tag_names(idx)
        for tag in tags_at_pos:
            if tag in self._url_map:
                webbrowser.open(self._url_map[tag])
                return
        # 回退：获取该位置 url tag 的完整范围，用显示文本作为 URL
        tag_range = self._text.tag_prevrange("url", f"{idx}+1c")
        if tag_range:
            url = self._text.get(tag_range[0], tag_range[1]).strip()
            if url:
                webbrowser.open(url)

    def _insert_url_link(self, display_text: str, target_url: str):
        """插入一个 URL 链接。如果 display_text != target_url，使用唯一标签存储映射"""
        if display_text.strip() == target_url.strip() or not target_url.strip():
            # 显示文本就是 URL，直接用通用 url tag
            self._text.insert(tk.END, display_text, "url")
        else:
            # 显示文本与 URL 不同，创建唯一标签
            self._url_counter += 1
            unique_tag = f"url_{self._url_counter}"
            self._url_map[unique_tag] = target_url
            self._text.tag_configure(unique_tag, foreground="#1a73e8",
                                      underline=True, font=("", 11))
            self._text.tag_bind(unique_tag, "<Enter>",
                                lambda e: self._text.config(cursor="hand2"))
            self._text.tag_bind(unique_tag, "<Leave>",
                                lambda e: self._text.config(cursor=""))
            self._text.tag_bind(unique_tag, "<Button-1>", self._on_url_click)
            self._text.insert(tk.END, display_text, unique_tag)

    def _on_key_press(self, event):
        """处理预设模式: 输入字符时自动附加 pending tags"""
        if self._source_mode or not self._pending_tags:
            return
        # 只处理普通可打印字符
        ch = event.char
        if not ch or len(ch) != 1 or ord(ch) < 32:
            return
        # 手动插入带 tag 的字符，阻止默认行为
        tags = tuple(self._pending_tags)
        self._text.insert(tk.INSERT, ch, tags)
        return "break"

    def _highlight_urls(self):
        """在 Text widget 中查找所有 URL 并添加 url tag"""
        self._text.tag_remove("url", "1.0", tk.END)
        content = self._text.get("1.0", tk.END)
        for m in self._URL_RE.finditer(content):
            # 计算 Text widget 中的位置
            start_offset = m.start()
            end_offset = m.end()
            start_idx = f"1.0+{start_offset}c"
            end_idx = f"1.0+{end_offset}c"
            self._text.tag_add("url", start_idx, end_idx)

    # ────────── 源码模式切换 ──────────

    def _toggle_source_mode(self):
        if self._source_mode:
            # 源码 → 可视: 获取源码然后渲染
            source = self._text.get("1.0", tk.END).rstrip()
            self._source_mode = False
            self._mode_btn.config(text="📝 源码")
            self._mode_label.config(text="可视模式")
            self._render_bbcode(source)
        else:
            # 可视 → 源码: 序列化为 BBCode 然后纯文本显示
            bbcode = self._serialize_to_bbcode()
            self._source_mode = True
            self._mode_btn.config(text="👁️ 可视")
            self._mode_label.config(text="源码模式")
            self._text.config(state=tk.NORMAL)
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", bbcode)

    # ────────── BBCode 解析 → 渲染 ──────────

    def _render_bbcode(self, bbcode: str):
        """将 BBCode 解析并渲染到 Text widget"""
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        # 重置 URL 映射
        self._url_map.clear()
        self._url_counter = 0

        if not bbcode.strip():
            return

        # 解析 token 流
        tokens = self._parse_bbcode(bbcode)
        for token in tokens:
            self._insert_token(token)

        # 渲染完成后高亮 URL
        self._highlight_urls()

    def _parse_bbcode(self, bbcode: str) -> list:
        """将 BBCode 解析为 token 列表
        每个 token: {'type': ..., 'content': ..., 'items': [...], 'url': ...}
        """
        tokens = []
        pos = 0
        text = bbcode

        while pos < len(text):
            # 查找下一个标签（包括 [url] 和 [url=...] 和 [/*]）
            match = re.search(
                r'\[(\/?)(h[123]|p|b|i|u|strike|list|olist|hr|code|url|\*)(?:=[^\]]*)?\]',
                text[pos:])
            if not match:
                # 剩余纯文本
                remaining = text[pos:]
                if remaining.strip():
                    tokens.append({'type': 'text', 'content': remaining})
                break

            # 标签前的纯文本
            before = text[pos:pos + match.start()]
            if before.strip():
                tokens.append({'type': 'text', 'content': before})

            tag_name = match.group(2)
            is_close = match.group(1) == '/'
            tag_pos = pos + match.start()
            tag_end = pos + match.end()

            if tag_name == 'hr' and not is_close:
                tokens.append({'type': 'hr', 'content': ''})
                pos = tag_end
                continue

            if tag_name == '*':
                # [*] 和 [/*] 只在列表内部有意义，在顶层跳过
                pos = tag_end
                continue

            if is_close:
                # 孤立闭合标签 → 跳过
                pos = tag_end
                continue

            # 寻找对应的闭合标签
            if tag_name in ('list', 'olist'):
                close_pattern = f'[/{tag_name}]'
                close_idx = text.find(close_pattern, tag_end)
                if close_idx == -1:
                    close_idx = len(text)
                inner = text[tag_end:close_idx]
                # 解析 [*] 项
                raw_items = [item.strip() for item in re.split(r'\[\*\]', inner) if item.strip()]
                # 去除列表项中可能的 [/*] 闭合标签和 [p]...[/p] 包裹
                items = []
                for it in raw_items:
                    # 先去除尾部的 [/*]
                    it = re.sub(r'\[/\*\]\s*$', '', it).strip()
                    # 再去除 [p]...[/p] 包裹
                    it = re.sub(r'^\[p\](.*)\[/p\]$', r'\1', it, flags=re.DOTALL).strip()
                    if it:
                        items.append(it)
                tokens.append({'type': tag_name, 'content': '', 'items': items})
                pos = close_idx + len(close_pattern) if close_idx < len(text) else len(text)
            elif tag_name == 'url':
                # 处理 [url=...]...[/url] 和 [url]...[/url]
                # 重新匹配完整开标签以提取可能的 url= 属性（含引号）
                url_attr = None
                full_open_match = re.match(
                    r'\[url(?:=([^\]]*))?\]', text[tag_pos:])
                if full_open_match:
                    tag_end = tag_pos + full_open_match.end()
                    raw_attr = full_open_match.group(1)
                    # 去除属性值两端的引号 "..." 或 '...'
                    if raw_attr:
                        url_attr = raw_attr.strip().strip('"').strip("'")
                close_pattern = '[/url]'
                close_idx = text.find(close_pattern, tag_end)
                if close_idx == -1:
                    close_idx = len(text)
                inner = text[tag_end:close_idx]
                # url_attr 存在时：显示文本=inner，链接=url_attr
                # url_attr 不存在时：显示文本=inner，链接=inner
                link_url = url_attr if url_attr else inner.strip()
                tokens.append({'type': 'url_link', 'content': inner, 'url': link_url})
                pos = close_idx + len(close_pattern) if close_idx < len(text) else len(text)
            else:
                close_pattern = f'[/{tag_name}]'
                close_idx = text.find(close_pattern, tag_end)
                if close_idx == -1:
                    close_idx = len(text)
                inner = text[tag_end:close_idx]
                tokens.append({'type': tag_name, 'content': inner})
                pos = close_idx + len(close_pattern) if close_idx < len(text) else len(text)

        return tokens

    def _insert_token(self, token):
        """将一个 token 插入到 Text widget"""
        t = token['type']
        content = token.get('content', '')

        if t == 'text':
            self._text.insert(tk.END, content, "paragraph")
        elif t in ('h1', 'h2', 'h3'):
            if self._text.get("end-2c", "end-1c") != "\n":
                self._text.insert(tk.END, "\n")
            self._insert_inline(content, t)
            self._text.insert(tk.END, "\n", t)
        elif t == 'p':
            # 段落内容可能含内联标签 [b] [i] [u] [strike]
            self._insert_inline(content, "paragraph")
            self._text.insert(tk.END, "\n", "paragraph")
        elif t == 'b':
            self._insert_inline(content, "bold")
        elif t == 'i':
            self._insert_inline(content, "italic")
        elif t == 'u':
            self._insert_inline(content, "underline")
        elif t == 'strike':
            self._insert_inline(content, "strike")
        elif t == 'code':
            if self._text.get("end-2c", "end-1c") != "\n":
                self._text.insert(tk.END, "\n")
            self._text.insert(tk.END, content + "\n", "code")
        elif t == 'hr':
            if self._text.get("end-2c", "end-1c") != "\n":
                self._text.insert(tk.END, "\n")
            self._text.insert(tk.END, "─" * 50 + "\n", "hr")
        elif t in ('list', 'olist'):
            if self._text.get("end-2c", "end-1c") != "\n":
                self._text.insert(tk.END, "\n")
            items = token.get('items', [])
            tag = "bullet" if t == 'list' else "olist"
            for idx, item in enumerate(items):
                prefix = "• " if t == 'list' else f"{idx + 1}. "
                self._text.insert(tk.END, prefix, tag)
                # 列表项内容可能含内联标签 [b][i][url] 等，需要解析
                self._insert_inline(item, tag)
                self._text.insert(tk.END, "\n", tag)
        elif t == 'url_link':
            # [url=...]显示文本[/url] 或 [url]链接[/url]
            display = content if content.strip() else token.get('url', '')
            self._insert_url_link(display, token.get('url', display))

    def _insert_inline(self, text: str, base_tag: str):
        """解析段落/列表项内的内联标签 [b] [i] [u] [strike] [url] 并渲染（递归支持嵌套）"""
        pos = 0
        while pos < len(text):
            # 匹配内联标签：[b]...[/b] 以及 [url=...]...[/url] 或 [url]...[/url]
            match = re.search(
                r'\[(b|i|u|strike)\](.*?)\[/\1\]|\[url(?:=([^\]]*))?\](.*?)\[/url\]',
                text[pos:], re.DOTALL)
            if not match:
                self._text.insert(tk.END, text[pos:], base_tag)
                break
            # 标签前文本
            before = text[pos:pos + match.start()]
            if before:
                self._text.insert(tk.END, before, base_tag)
            if match.group(1):
                # [b]/[i]/[u]/[strike] 匹配
                inline_tag = match.group(1)
                inline_content = match.group(2)
                tag_map = {'b': 'bold', 'i': 'italic', 'u': 'underline', 'strike': 'strike'}
                visual_tag = tag_map.get(inline_tag, base_tag)
                # 递归解析内部可能的嵌套内联标签
                self._insert_inline(inline_content, visual_tag)
            else:
                # [url] 匹配
                raw_attr = match.group(3)  # [url=VALUE] 的 VALUE，可能为 None
                url_content = match.group(4)
                # 去除引号
                url_attr = raw_attr.strip().strip('"').strip("'") if raw_attr else None
                display = url_content if url_content.strip() else (url_attr or '')
                target = url_attr if url_attr else url_content.strip()
                self._insert_url_link(display, target)
            pos = pos + match.end()

    # ────────── 可视模式 → BBCode 序列化 ──────────

    def _serialize_to_bbcode(self) -> str:
        """将 Text widget 的内容及标签序列化为 BBCode"""
        # 遍历 widget 内容，按标签还原 BBCode
        result = []
        index = "1.0"
        end = self._text.index(tk.END + "-1c")

        while self._text.compare(index, "<", end):
            tags = self._text.tag_names(index)
            # 找到该标签连续范围
            next_idx = self._find_tag_boundary(index, tags)

            chunk = self._text.get(index, next_idx)

            if 'hr' in tags and '─' in chunk:
                result.append('[hr]')
            elif 'h1' in tags:
                line = chunk.rstrip('\n')
                if line:
                    result.append(f'[h1]{line}[/h1]')
            elif 'h2' in tags:
                line = chunk.rstrip('\n')
                if line:
                    result.append(f'[h2]{line}[/h2]')
            elif 'h3' in tags:
                line = chunk.rstrip('\n')
                if line:
                    result.append(f'[h3]{line}[/h3]')
            elif 'code' in tags:
                line = chunk.rstrip('\n')
                if line:
                    result.append(f'[code]{line}[/code]')
            elif 'bullet' in tags:
                # 收集列表项
                lines = chunk.rstrip('\n').split('\n')
                items = []
                for l in lines:
                    l = l.strip()
                    if l.startswith('• '):
                        items.append(l[2:])
                    elif l:
                        items.append(l)
                if items:
                    result.append('[list]' + ''.join(f'[*]{it}' for it in items) + '[/list]')
            elif 'olist' in tags:
                lines = chunk.rstrip('\n').split('\n')
                items = []
                for l in lines:
                    l = l.strip()
                    m = re.match(r'^\d+\.\s*(.+)', l)
                    if m:
                        items.append(m.group(1))
                    elif l:
                        items.append(l)
                if items:
                    result.append('[olist]' + ''.join(f'[*]{it}' for it in items) + '[/olist]')
            elif 'bold' in tags:
                result.append(f'[b]{chunk}[/b]')
            elif 'italic' in tags:
                result.append(f'[i]{chunk}[/i]')
            elif 'underline' in tags:
                result.append(f'[u]{chunk}[/u]')
            elif 'strike' in tags:
                result.append(f'[strike]{chunk}[/strike]')
            elif 'url' in tags:
                # 通用 url 标签：显示文本就是 URL
                result.append(f'[url]{chunk}[/url]')
            elif any(t.startswith('url_') and t in self._url_map for t in tags):
                # 唯一 url 标签：有 url= 属性
                url_tag = next(t for t in tags if t.startswith('url_') and t in self._url_map)
                target = self._url_map[url_tag]
                result.append(f'[url={target}]{chunk}[/url]')
            elif 'paragraph' in tags:
                # 段落文本: 按换行分段落
                paras = chunk.split('\n')
                for p in paras:
                    p = p.strip()
                    if p:
                        result.append(f'[p]{p}[/p]')
            else:
                # 无特殊标签的纯文本
                text_stripped = chunk.strip()
                if text_stripped:
                    result.append(f'[p]{text_stripped}[/p]')

            index = next_idx

        return ''.join(result)

    def _find_tag_boundary(self, start_index, tags):
        """找到当前标签组合结束的位置"""
        tags_set = set(tags)
        index = start_index
        end = self._text.index(tk.END + "-1c")

        while self._text.compare(index, "<", end):
            next_char = self._text.index(f"{index}+1c")
            next_tags = set(self._text.tag_names(next_char))
            if next_tags != tags_set:
                return next_char
            index = next_char

        return end

    # ────────── 工具栏: 应用标签 ──────────

    def _apply_tag(self, tag_name: str):
        """工具栏按钮点击处理"""
        if self._source_mode:
            # 源码模式: 直接插入标签文本
            self._insert_bbcode_tag_source(tag_name)
            return

        # 可视模式
        if tag_name == 'hr':
            self._insert_hr()
            return

        if tag_name in ('list', 'olist'):
            self._insert_list(tag_name)
            return

        if tag_name in ('h1', 'h2', 'h3'):
            self._apply_block_tag(tag_name)
            return

        if tag_name == 'p':
            self._apply_block_tag('paragraph')
            return

        if tag_name == 'code':
            self._apply_code_block()
            return

        # 内联标签: b, i, u, strike
        tag_map = {'b': 'bold', 'i': 'italic', 'u': 'underline', 'strike': 'strike'}
        visual_tag = tag_map.get(tag_name, tag_name)
        try:
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
            # 检查选区是否已有该标签 → 切换
            current_tags = self._text.tag_names(sel_start)
            if visual_tag in current_tags:
                self._text.tag_remove(visual_tag, sel_start, sel_end)
            else:
                self._text.tag_add(visual_tag, sel_start, sel_end)
        except tk.TclError:
            # 无选区: 进入"预设模式"——后续输入自动带该格式
            if visual_tag in self._pending_tags:
                self._pending_tags.discard(visual_tag)
            else:
                self._pending_tags.add(visual_tag)
            # 在工具栏按钮上给出视觉反馈（通过状态栏提示）
            if self._pending_tags:
                active = ", ".join(sorted(self._pending_tags))
                self._mode_label.config(text=f"预设: {active}")
            else:
                self._mode_label.config(text="可视模式")

    def _insert_bbcode_tag_source(self, tag_name: str):
        """源码模式下在光标处插入 BBCode 标签对"""
        if tag_name == 'hr':
            self._text.insert(tk.INSERT, "[hr]")
            return
        try:
            sel_text = self._text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self._text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            if tag_name in ('list', 'olist'):
                items = sel_text.split('\n')
                inner = ''.join(f'[*]{item}' for item in items if item.strip())
                self._text.insert(tk.INSERT, f"[{tag_name}]{inner}[/{tag_name}]")
            else:
                self._text.insert(tk.INSERT, f"[{tag_name}]{sel_text}[/{tag_name}]")
        except tk.TclError:
            if tag_name in ('list', 'olist'):
                self._text.insert(tk.INSERT, f"[{tag_name}][*]项目一[*]项目二[/{tag_name}]")
            else:
                self._text.insert(tk.INSERT, f"[{tag_name}][/{tag_name}]")

    def _insert_hr(self):
        """可视模式下插入分隔线"""
        pos = self._text.index(tk.INSERT)
        if self._text.get(f"{pos}-1c", pos) != "\n":
            self._text.insert(tk.INSERT, "\n")
        self._text.insert(tk.INSERT, "─" * 50 + "\n", "hr")

    def _insert_list(self, list_type: str):
        """可视模式下插入列表"""
        tag = "bullet" if list_type == 'list' else "olist"
        try:
            sel_text = self._text.get(tk.SEL_FIRST, tk.SEL_LAST)
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
            self._text.delete(sel_start, sel_end)
            lines = [l.strip() for l in sel_text.split('\n') if l.strip()]
            pos = sel_start
        except tk.TclError:
            lines = ["项目一", "项目二"]
            pos = self._text.index(tk.INSERT)
            if self._text.get(f"{pos}-1c", pos) != "\n":
                self._text.insert(pos, "\n")
                pos = self._text.index(tk.INSERT)

        for idx, item in enumerate(lines):
            prefix = "• " if list_type == 'list' else f"{idx + 1}. "
            self._text.insert(pos, prefix + item + "\n", tag)
            pos = self._text.index(f"{pos}+{len(prefix) + len(item) + 1}c")

    def _apply_block_tag(self, tag_name: str):
        """为当前行或选区应用块级标签"""
        try:
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
        except tk.TclError:
            # 没有选区: 选取当前行
            sel_start = self._text.index("insert linestart")
            sel_end = self._text.index("insert lineend")

        # 移除已有的块级标签
        for bt in ('h1', 'h2', 'h3', 'paragraph', 'code'):
            self._text.tag_remove(bt, sel_start, sel_end)
        # 应用新标签
        self._text.tag_add(tag_name, sel_start, sel_end)

    def _apply_code_block(self):
        """插入或应用代码块"""
        try:
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
            current_tags = self._text.tag_names(sel_start)
            if 'code' in current_tags:
                self._text.tag_remove('code', sel_start, sel_end)
            else:
                for bt in ('h1', 'h2', 'h3', 'paragraph'):
                    self._text.tag_remove(bt, sel_start, sel_end)
                self._text.tag_add('code', sel_start, sel_end)
        except tk.TclError:
            pos = self._text.index(tk.INSERT)
            if self._text.get(f"{pos}-1c", pos) != "\n":
                self._text.insert(pos, "\n")
            self._text.insert(tk.INSERT, "代码内容\n", "code")

    # ────────── 公共接口 ──────────

    def set_content(self, bbcode: str):
        """设置内容（BBCode 字符串）"""
        if self._source_mode:
            self._text.config(state=tk.NORMAL)
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", bbcode)
        else:
            self._render_bbcode(bbcode)

    def get_content(self) -> str:
        """获取内容（BBCode 字符串）"""
        if self._source_mode:
            return self._text.get("1.0", tk.END).rstrip()
        else:
            return self._serialize_to_bbcode()

    def clear(self):
        """清空编辑器"""
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)

    def set_state(self, state):
        """设置 text widget 状态 (tk.NORMAL / tk.DISABLED)"""
        self._text.config(state=state)


# ═══════════════════════════════════════════════════════════════════════════════
#  GUI 应用
# ═══════════════════════════════════════════════════════════════════════════════

class SteamNotesApp:
    """Steam 笔记管理器 GUI"""

    # API Key 配置文件路径（跨平台）
    _CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".steam_notes_gen")
    _CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")

    def __init__(self):
        self.current_account = None
        self.accounts = []
        self.manager = None  # SteamNotesManager
        self.cloud_uploader = None  # SteamCloudUploader
        self.root = None
        self._games_data = []
        self._game_name_cache = {}  # {app_id: name} — 缓存在线解析的游戏名
        self._game_name_cache_loaded = False
        self._config = self._load_config()

    @classmethod
    def _load_config(cls) -> dict:
        """从配置文件加载已保存的设置"""
        try:
            if os.path.exists(cls._CONFIG_FILE):
                with open(cls._CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def _save_config(cls, config: dict):
        """保存设置到配置文件"""
        try:
            os.makedirs(cls._CONFIG_DIR, exist_ok=True)
            with open(cls._CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _get_saved_key(self, key_name: str) -> str:
        """获取已保存的 API Key"""
        return self._config.get(key_name, "")

    def _set_saved_key(self, key_name: str, value: str):
        """保存 API Key 到配置文件"""
        if value:
            self._config[key_name] = value
        elif key_name in self._config:
            del self._config[key_name]
        self._save_config(self._config)

    def _clear_saved_key(self, key_name: str):
        """清除已保存的 API Key"""
        if key_name in self._config:
            del self._config[key_name]
            self._save_config(self._config)

    def _get_ai_tokens(self) -> list:
        """获取已保存的 AI 令牌列表（含向后兼容）
        每个令牌: {name, key, provider, model, api_url}
        """
        tokens = self._config.get("ai_tokens", [])
        if tokens:
            return tokens
        # 向后兼容：从旧的单 key 配置迁移
        old_key = (self._config.get("ai_api_key") or
                   self._config.get("anthropic_api_key") or "")
        if old_key:
            prov = self._config.get("ai_provider", "anthropic")
            pinfo = SteamAIGenerator.PROVIDERS.get(prov, {})
            return [{
                "name": pinfo.get("name", prov),
                "key": old_key,
                "provider": prov,
                "model": self._config.get("ai_model", pinfo.get("default_model", "")),
                "api_url": self._config.get("ai_api_url", ""),
            }]
        return []

    def _save_ai_tokens(self, tokens: list, active_index: int = 0):
        """保存 AI 令牌列表到配置文件"""
        self._config["ai_tokens"] = tokens
        self._config["ai_active_token_index"] = active_index
        # 同步旧字段（保持向后兼容）
        if tokens and 0 <= active_index < len(tokens):
            t = tokens[active_index]
            self._config["ai_api_key"] = t.get("key", "")
            self._config["anthropic_api_key"] = t.get("key", "")
            self._config["ai_provider"] = t.get("provider", "anthropic")
            self._config["ai_model"] = t.get("model", "")
            self._config["ai_api_url"] = t.get("api_url", "")
        self._save_config(self._config)

    def _get_active_token_index(self) -> int:
        return self._config.get("ai_active_token_index", 0)

    def set_current_account(self, account):
        """设置当前账号"""
        self.current_account = account
        # 从配置中加载该账号的上传哈希
        fc = account.get('friend_code', '')
        hashes = self._config.get(f"uploaded_hashes_{fc}", {})
        self.manager = SteamNotesManager(
            account['notes_dir'], self.cloud_uploader,
            uploaded_hashes=hashes)
        # 切换账号时清空游戏名称缓存
        self._game_name_cache = {}
        self._game_name_cache_loaded = False

    def _save_uploaded_hashes(self):
        """持久化当前账号的上传哈希到配置文件"""
        if not self.current_account or not self.manager:
            return
        fc = self.current_account.get('friend_code', '')
        self._config[f"uploaded_hashes_{fc}"] = self.manager.get_uploaded_hashes()
        self._save_config(self._config)

    # ────────────────────── 启动流程 ──────────────────────

    def run(self):
        """主入口"""
        self.accounts = SteamAccountScanner.scan_accounts()

        if not self.accounts:
            self._show_no_account_ui()
        elif len(self.accounts) == 1:
            self.set_current_account(self.accounts[0])
            self._show_main_window()
        else:
            self._show_account_selector()

    def _show_no_account_ui(self):
        """未找到账号时的界面"""
        root = tk.Tk()
        root.title("Steam 笔记管理器")
        root.resizable(False, False)

        tk.Label(root, text="❌ 未找到 Steam 账号",
                 font=("", 14, "bold"), fg="red").pack(pady=20)
        tk.Label(root, text=(
            "请确保:\n"
            "1. Steam 已安装\n"
            "2. 至少登录过一个 Steam 账号\n"
            "3. 若 Steam 安装在非默认路径，请手动指定"
        ), font=("", 10), justify=tk.LEFT).pack(padx=30, pady=10)

        def manual_select():
            path = filedialog.askdirectory(title="选择 Steam 安装目录（含 userdata 的那个）")
            if path and os.path.exists(path):
                userdata = os.path.join(path, "userdata")
                if not os.path.exists(userdata):
                    messagebox.showerror("错误", "该目录下没有 userdata 文件夹。")
                    return
                for entry in os.listdir(userdata):
                    ep = os.path.join(userdata, entry)
                    if os.path.isdir(ep) and entry.isdigit():
                        notes_dir = os.path.join(ep, NOTES_APPID, "remote")
                        persona = SteamAccountScanner._get_persona_name(ep, entry)
                        nc = 0
                        if os.path.exists(notes_dir):
                            nc = len([f for f in os.listdir(notes_dir)
                                      if f.startswith("notes_")])
                        self.accounts.append({
                            'friend_code': entry,
                            'userdata_path': ep,
                            'notes_dir': notes_dir,
                            'persona_name': persona,
                            'steam_path': path,
                            'notes_count': nc,
                        })
                if self.accounts:
                    root.destroy()
                    if len(self.accounts) == 1:
                        self.set_current_account(self.accounts[0])
                        self._show_main_window()
                    else:
                        self._show_account_selector()
                else:
                    messagebox.showerror("错误", "该目录下未找到有效的 Steam 账号。")

        ttk.Button(root, text="📂 手动选择 Steam 目录", command=manual_select).pack(pady=20)
        self._center_window(root)
        root.mainloop()

    def _show_account_selector(self):
        """多账号选择界面"""
        sel = tk.Tk()
        sel.title("选择 Steam 账号")
        sel.resizable(False, False)

        tk.Label(sel, text="🎮 检测到多个 Steam 账号",
                 font=("", 12, "bold")).pack(pady=(20, 10))
        tk.Label(sel, text="请选择要管理笔记的账号：", font=("", 10)).pack()

        list_frame = tk.Frame(sel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        listbox = tk.Listbox(list_frame, width=60, height=min(10, len(self.accounts)),
                             font=("", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for acc in self.accounts:
            listbox.insert(tk.END,
                           f"{acc['persona_name']}  |  ID: {acc['friend_code']}  "
                           f"|  📝 {acc['notes_count']} 个游戏有笔记")

        listbox.selection_set(0)

        def on_select():
            idx = listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请选择一个账号。")
                return
            self.set_current_account(self.accounts[idx[0]])
            sel.destroy()
            self._show_main_window()

        ttk.Button(sel, text="✅ 确认选择", command=on_select).pack(pady=15)
        self._center_window(sel)
        sel.mainloop()

    # ────────────────────── 主界面 ──────────────────────

    def _show_main_window(self):
        """主功能窗口"""
        self.root = tk.Tk()
        self.root.title("Steam 笔记管理器")
        root = self.root

        # ── 顶部: 账号信息栏 ──
        acc_frame = tk.Frame(root, bg="#4a90d9", pady=6)
        acc_frame.pack(fill=tk.X)

        acc_info = (f"👤 {self.current_account['persona_name']}  |  "
                    f"ID: {self.current_account['friend_code']}  |  "
                    f"📂 .../{NOTES_APPID}/remote/")
        tk.Label(acc_frame, text=acc_info, font=("", 11, "bold"),
                 bg="#4a90d9", fg="white").pack(side=tk.LEFT, padx=15)

        if len(self.accounts) > 1:
            def switch():
                root.destroy()
                self._show_account_selector()
            tk.Button(acc_frame, text="🔄 切换账号", command=switch,
                      font=("", 9)).pack(side=tk.RIGHT, padx=15)

        # ── 主体: 左笔记列表 + 右控制区 ──
        main = tk.Frame(root)
        main.pack(fill=tk.BOTH, expand=True)

        # ═══════ 左侧: 笔记列表（主视图） ═══════
        left = tk.Frame(main, bg="#f0f0f0", padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        tk.Label(left, text="📝 游戏笔记列表", font=("", 11, "bold"),
                 bg="#f0f0f0").pack(anchor=tk.W)

        # ── 搜索栏 ──
        search_frame = tk.Frame(left, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(4, 0))

        self._main_search_var = tk.StringVar()
        self._main_search_mode = tk.StringVar(value="name")

        tk.Radiobutton(search_frame, text="名称/ID", variable=self._main_search_mode,
                        value="name", font=("", 8), bg="#f0f0f0",
                        command=lambda: self._on_main_search_changed()
                        ).pack(side=tk.LEFT)
        tk.Radiobutton(search_frame, text="笔记内容", variable=self._main_search_mode,
                        value="content", font=("", 8), bg="#f0f0f0",
                        command=lambda: self._on_main_search_changed()
                        ).pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self._main_search_var, width=18)
        search_entry.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)
        self._main_search_var.trace_add("write", lambda *_: self._on_main_search_changed())

        # 紧凑工具栏
        toolbar = tk.Frame(left, bg="#f0f0f0")
        toolbar.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(toolbar, text="✅全选", width=6,
                   command=self._select_all_games).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="📋ID", width=5,
                   command=self._copy_selected_appid).pack(side=tk.LEFT, padx=(0, 2))
        self._upload_sel_btn = ttk.Button(toolbar, text="☁️选中", width=7,
                                           command=self._cloud_upload_selected)
        self._upload_sel_btn.pack(side=tk.LEFT, padx=(0, 2))
        self._upload_all_btn = ttk.Button(toolbar, text="☁️全部", width=9,
                                           command=self._cloud_upload_all)
        self._upload_all_btn.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="📤导出", width=6,
                   command=self._ui_export_dialog).pack(side=tk.LEFT, padx=(0, 2))

        # 筛选行
        filter_frame = tk.Frame(left, bg="#f0f0f0")
        filter_frame.pack(fill=tk.X, pady=(4, 0))
        self._ai_filter_var = tk.StringVar(value="全部")
        tk.Label(filter_frame, text="筛选:", font=("", 9), bg="#f0f0f0").pack(side=tk.LEFT)
        self._ai_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self._ai_filter_var, width=16,
            values=["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理"], state='readonly')
        self._ai_filter_combo.pack(side=tk.LEFT, padx=(3, 0))
        self._ai_filter_combo.bind("<<ComboboxSelected>>",
                                    lambda e: self._on_filter_changed())

        # 确信度二级筛选（仅 AI 筛选时可见）
        self._conf_filter_var = tk.StringVar(value="全部确信度")
        self._conf_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self._conf_filter_var, width=10,
            values=["全部确信度"], state='readonly')
        self._conf_filter_combo.bind("<<ComboboxSelected>>",
                                      lambda e: self._refresh_games_list())
        # 默认隐藏
        self._conf_filter_visible = False

        # 提示
        tk.Label(left, text="🤖=AI(🟢很高 🔵较高 🟡中等 🟠较低 🔴很低) 🟡=改动",
                 font=("", 8), fg="#555", bg="#f0f0f0",
                 justify=tk.LEFT).pack(anchor=tk.W, pady=(3, 0))

        list_container = tk.Frame(left, bg="#f0f0f0")
        list_container.pack(fill=tk.BOTH, expand=True, pady=(5, 5))

        # 使用 Treeview 实现高性能列表（多选模式）
        style = ttk.Style()
        style.configure("GameList.Treeview", rowheight=24, font=("", 9))
        self._games_tree = ttk.Treeview(
            list_container, columns=("notes",), show="tree",
            style="GameList.Treeview", selectmode="extended", height=20)
        self._games_tree.column("#0", width=320, minwidth=200)
        self._games_tree.column("notes", width=45, minwidth=35, anchor=tk.CENTER)
        self._games_tree.tag_configure("dirty", foreground="#b8860b", background="#fffff0")
        self._games_tree.tag_configure("ai", foreground="#1a73e8")
        self._games_tree.tag_configure("normal", foreground="#333")
        self._games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                     command=self._games_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._games_tree.config(yscrollcommand=tree_scroll.set)

        # 双击查看
        self._games_tree.bind("<Double-1>", lambda e: self._on_tree_double_click())
        # 右键菜单
        self._games_tree.bind("<Button-2>" if platform.system() == "Darwin" else "<Button-3>",
                              self._on_tree_right_click)

        # 选中状态
        self._selected_game_idx = None

        btn_bottom = tk.Frame(left, bg="#f0f0f0")
        btn_bottom.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_bottom, text="🔄 刷新", width=8,
                   command=self._force_refresh_games_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bottom, text="📋 查看", width=8,
                   command=self._ui_view_selected).pack(side=tk.LEFT, padx=2)

        # ═══════ 右侧: 控制面板 ═══════
        right = tk.Frame(main, padx=4, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 6), pady=8)

        # ── Cloud 状态（单行） ──
        self._cloud_status_frame = tk.Frame(right)
        self._cloud_status_frame.pack(fill=tk.X)

        self._cloud_status_text = tk.Text(self._cloud_status_frame, font=("", 10), height=1,
                                          width=30,
                                          bg=root.cget("bg"), relief=tk.FLAT, wrap=tk.WORD)
        self._cloud_status_text.tag_config("red", foreground="red", font=("", 10, "bold"))
        self._cloud_status_text.tag_config("green", foreground="green", font=("", 10, "bold"))
        self._cloud_status_text.tag_config("gray", foreground="#888")
        self._cloud_status_text.pack(fill=tk.X)

        self._cloud_connect_btn = ttk.Button(right, text="☁️ 连接 Steam Cloud",
                                              command=self._toggle_cloud_connection)
        self._cloud_connect_btn.pack(anchor=tk.W, pady=(2, 6))

        self._update_cloud_status_display()

        # ── 功能按钮 ──
        style = ttk.Style()
        style.configure("TButton", font=("", 10), padding=6)

        btn_row1 = tk.Frame(right)
        btn_row1.pack(fill=tk.X, pady=(0, 3))
        ttk.Button(btn_row1, text="📝 新建", width=7,
                   command=self._ui_create_note).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row1, text="📋 查看", width=7,
                   command=self._ui_view_notes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row1, text="🗑️ 删除", width=7,
                   command=self._ui_delete_notes).pack(side=tk.LEFT, padx=2)

        btn_row2 = tk.Frame(right)
        btn_row2.pack(fill=tk.X, pady=3)
        ttk.Button(btn_row2, text="📥 导入", width=7,
                   command=self._ui_import).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row2, text="📂 目录", width=7,
                   command=self._ui_open_dir).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row2, text="🔑 AI 配置", width=7,
                   command=self._ui_api_key_settings).pack(side=tk.LEFT, padx=2)

        btn_row3 = tk.Frame(right)
        btn_row3.pack(fill=tk.X, pady=(3, 3))
        ttk.Button(btn_row3, text="🤖 AI 批量生成", width=11,
                   command=self._ui_ai_batch_generate).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row3, text="🔍 去重", width=6,
                   command=self._ui_dedup_notes).pack(side=tk.LEFT, padx=2)

        # ── 路径信息 + 关于 ──
        bottom_row = tk.Frame(right)
        bottom_row.pack(fill=tk.X, pady=(4, 0))
        path_label = tk.Label(bottom_row, text=f"📂 {self.current_account['notes_dir']}",
                              font=("", 8), fg="#888", cursor="hand2", anchor=tk.W,
                              wraplength=180)
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        path_label.bind("<Button-1>", lambda e: self._ui_open_dir())
        ttk.Button(bottom_row, text="ℹ️ 关于", width=5,
                   command=self._ui_show_about).pack(side=tk.RIGHT)

        # 初始加载
        self._refresh_games_list()

        # 后台解析未知游戏名称
        threading.Thread(target=self._bg_resolve_missing_names, daemon=True).start()

        # 启动 Steam 进程监控定时器
        self._steam_monitor_id = None
        self._start_steam_monitor()

        self._center_window(root)
        root.mainloop()

    # ────────────────────── Steam 进程监控 ──────────────────────

    def _start_steam_monitor(self):
        """启动后台定时器，每 5 秒检测 Steam 是否在运行"""
        self._check_steam_alive()

    def _check_steam_alive(self):
        """定时检测 Steam 进程，若 Cloud 已连接但 Steam 不在则自动断开"""
        if self.cloud_uploader and self.cloud_uploader.initialized:
            if not SteamCloudUploader.is_steam_running():
                # Steam 已关闭，自动断开 Cloud
                self.cloud_uploader.shutdown()
                self.cloud_uploader = None
                self.manager.cloud_uploader = None
                self._update_cloud_status_display()
        # 5 秒后再次检测
        try:
            self._steam_monitor_id = self.root.after(5000, self._check_steam_alive)
        except Exception:
            pass  # root 已销毁

    # ────────────────────── 右侧列表操作 ──────────────────────

    def _ensure_game_name_cache(self, force=False):
        """确保游戏名称缓存已加载 — 持久化 + 全量列表 + 本地扫描 + 后台补全"""
        if self._game_name_cache_loaded and not force:
            return
        # 1. 从配置文件加载已持久化的名称缓存
        persisted = self._config.get("game_name_cache", {})
        self._game_name_cache = dict(persisted)
        # 2. 尝试从 ISteamApps/GetAppList/v2/ 获取全量名称列表（无需 API Key）
        #    此列表约 15 万条，覆盖几乎所有 Steam 应用
        #    使用单独的缓存键来避免每次启动都重新请求
        bulk_cache_ts = self._config.get("game_name_bulk_cache_ts", 0)
        now = time.time()
        # 每 24 小时更新一次全量列表
        if now - bulk_cache_ts > 86400 or not persisted:
            try:
                bulk_names = SteamAccountScanner.fetch_all_steam_app_names()
                if bulk_names:
                    self._game_name_cache.update(bulk_names)
                    self._config["game_name_bulk_cache_ts"] = now
                    print(f"[游戏名称] 全量列表已更新: {len(bulk_names)} 条")
            except Exception as e:
                print(f"[游戏名称] 全量列表获取失败: {e}")
        # 3. 本地扫描（已安装游戏，可能有更准确的本地化名称）
        try:
            library_games = SteamAccountScanner.scan_library(
                self.current_account['steam_path'])
            for g in library_games:
                self._game_name_cache[g['app_id']] = g['name']
        except Exception:
            pass
        # 4. 持久化合并后的缓存
        self._persist_name_cache()
        self._game_name_cache_loaded = True

    def _persist_name_cache(self):
        """将游戏名称缓存持久化到配置文件"""
        self._config["game_name_cache"] = dict(self._game_name_cache)
        self._save_config(self._config)

    def _bg_resolve_missing_names(self):
        """后台线程：解析仍显示为 AppID 的游戏名称
        优先使用全量列表缓存，仅对缓存中也找不到的才逐个调 Store API"""
        games = self.manager.list_all_games()
        missing = [g['app_id'] for g in games
                   if g['app_id'] not in self._game_name_cache]
        if not missing:
            return
        # 先尝试批量获取（如果缓存中不够）
        resolved_any = False
        bulk_names = SteamAccountScanner.fetch_all_steam_app_names()
        if bulk_names:
            for aid in missing:
                if aid in bulk_names:
                    self._game_name_cache[aid] = bulk_names[aid]
                    resolved_any = True
            # 更新 missing 列表
            missing = [aid for aid in missing
                       if aid not in self._game_name_cache]
        # 对仍缺失的逐个调 Store API
        for aid in missing:
            try:
                name = SteamAIGenerator.get_game_name_from_steam(aid)
                if name and not name.startswith("AppID "):
                    self._game_name_cache[aid] = name
                    resolved_any = True
                time.sleep(0.3)  # 避免请求过快
            except Exception:
                pass
        if resolved_any:
            self._persist_name_cache()
            # 在主线程刷新列表
            try:
                self.root.after(0, lambda: self._refresh_games_list())
            except Exception:
                pass

    def _get_game_name(self, app_id: str) -> str:
        """获取游戏名称，优先缓存，否则返回 AppID"""
        return self._game_name_cache.get(app_id, f"AppID {app_id}")

    def _refresh_games_list(self, force_cache=False):
        """刷新右侧游戏列表（Treeview 实现，支持 AI 筛选 + 确信度筛选 + dirty 状态）"""
        tree = self._games_tree
        tree.delete(*tree.get_children())

        games = self.manager.list_all_games()

        # 确保游戏名称缓存已加载
        self._ensure_game_name_cache(force=force_cache)

        # 扫描 AI 笔记
        ai_notes_map = self.manager.scan_ai_notes()
        all_models = set()
        all_confidences = set()
        for info in ai_notes_map.values():
            for m in info.get('models', []):
                all_models.add(m)
            for c in info.get('confidences', []):
                all_confidences.add(c)

        # 更新 AI 筛选器
        filter_values = ["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理"]
        for m in sorted(all_models):
            filter_values.append(f"🤖 {m}")
        if hasattr(self, '_ai_filter_combo'):
            self._ai_filter_combo['values'] = filter_values

        filter_mode = self._ai_filter_var.get() if hasattr(self, '_ai_filter_var') else "全部"

        # 确定是否显示确信度筛选
        is_ai_filter = (filter_mode == "🤖 AI 处理过"
                        or (filter_mode.startswith("🤖 ")
                            and filter_mode != "🤖 AI 处理过"))
        if is_ai_filter:
            if not self._conf_filter_visible:
                self._conf_filter_combo.pack(side=tk.LEFT, padx=(3, 0))
                self._conf_filter_visible = True
            # 始终显示所有确信度等级，方便筛选
            conf_order = ["很高", "较高", "中等", "较低", "很低"]
            self._conf_filter_combo['values'] = ["全部确信度"] + conf_order
        else:
            if self._conf_filter_visible:
                self._conf_filter_combo.pack_forget()
                self._conf_filter_visible = False
            self._conf_filter_var.set("全部确信度")

        conf_filter = self._conf_filter_var.get() if hasattr(self, '_conf_filter_var') else "全部确信度"

        # 过滤
        filtered_games = []
        for g in games:
            aid = g['app_id']
            has_ai = aid in ai_notes_map
            is_dirty = self.manager.is_dirty(aid)

            if filter_mode == "☁️ 有改动" and not is_dirty:
                continue
            if filter_mode == "🤖 AI 处理过" and not has_ai:
                continue
            if filter_mode == "📝 未 AI 处理" and has_ai:
                continue
            if (filter_mode.startswith("🤖 ")
                    and filter_mode != "🤖 AI 处理过"):
                target_model = filter_mode[2:]
                models = ai_notes_map.get(aid, {}).get('models', [])
                if target_model not in models:
                    continue
            # 确信度二级筛选
            if is_ai_filter and conf_filter != "全部确信度":
                confs = ai_notes_map.get(aid, {}).get('confidences', [])
                if conf_filter not in confs:
                    continue
            g['has_ai'] = has_ai
            g['ai_models'] = ai_notes_map.get(aid, {}).get('models', [])
            g['game_name'] = self._get_game_name(aid)
            g['is_dirty'] = is_dirty

            # 搜索过滤
            search_q = ""
            search_mode = "name"
            if hasattr(self, '_main_search_var'):
                search_q = self._main_search_var.get().strip().lower()
            if hasattr(self, '_main_search_mode'):
                search_mode = self._main_search_mode.get()
            if search_q:
                if search_mode == "name":
                    # 按游戏名 / AppID 搜索
                    if (search_q not in g['game_name'].lower()
                            and search_q not in aid.lower()):
                        continue
                else:
                    # 按笔记内容搜索
                    try:
                        note_data = self.manager.read_notes(aid)
                        all_text = " ".join(
                            n.get("content", "") + " " + n.get("title", "")
                            for n in note_data.get("notes", []))
                        if search_q not in all_text.lower():
                            continue
                    except Exception:
                        continue

            filtered_games.append(g)

        self._games_data = filtered_games

        # 插入到 Treeview
        for g in filtered_games:
            aid = g['app_id']
            is_dirty = g.get('is_dirty', False)
            has_ai = g.get('has_ai', False)
            display_name = g['game_name']
            if len(display_name) > 38:
                display_name = display_name[:35] + "..."
            ai_tag = ""
            if has_ai:
                confs = ai_notes_map.get(aid, {}).get('confidences', [])
                conf_emoji = CONFIDENCE_EMOJI.get(confs[0], "") if confs else ""
                ai_tag = f" 🤖{conf_emoji}"
            dirty_tag = " ⬆" if is_dirty else ""
            text = f"{display_name}{ai_tag}{dirty_tag}"
            notes_col = f"📝{g['note_count']}"

            if is_dirty:
                tag = "dirty"
            elif has_ai:
                tag = "ai"
            else:
                tag = "normal"
            tree.insert("", tk.END, iid=aid, text=text, values=(notes_col,), tags=(tag,))

        # 更新上传按钮状态
        dirty_n = self.manager.dirty_count()
        if hasattr(self, '_upload_all_btn'):
            if dirty_n > 0:
                self._upload_all_btn.config(text=f"☁️全部({dirty_n})")
            else:
                self._upload_all_btn.config(text="☁️全部")

    def _force_refresh_games_list(self):
        """刷新按钮：强制重建游戏名称缓存 + 后台补全"""
        self._refresh_games_list(force_cache=True)
        threading.Thread(target=self._bg_resolve_missing_names, daemon=True).start()

    def _on_main_search_changed(self):
        """主界面搜索框内容或模式变化时刷新列表（带防抖）"""
        if hasattr(self, '_search_debounce_id') and self._search_debounce_id:
            self.root.after_cancel(self._search_debounce_id)
        delay = 300 if (hasattr(self, '_main_search_mode')
                        and self._main_search_mode.get() == "content") else 100
        self._search_debounce_id = self.root.after(delay, self._refresh_games_list)

    def _on_filter_changed(self):
        """主筛选器变更时，重置确信度筛选并刷新"""
        self._conf_filter_var.set("全部确信度")
        self._refresh_games_list()

    def _on_tree_double_click(self):
        """Treeview 双击 → 查看笔记（取第一个选中项）"""
        sel = self._games_tree.selection()
        if sel:
            self._open_notes_viewer(sel[0])

    def _on_tree_right_click(self, event):
        """右键弹出菜单"""
        iid = self._games_tree.identify_row(event.y)
        if not iid:
            return
        # 如果右键的项不在当前选中集中，则设为单选
        current_sel = self._games_tree.selection()
        if iid not in current_sel:
            self._games_tree.selection_set(iid)
        menu = tk.Menu(self.root, tearoff=0)
        sel = self._games_tree.selection()
        if len(sel) == 1:
            menu.add_command(label="📋 查看笔记", command=lambda: self._open_notes_viewer(sel[0]))
            menu.add_command(label="📋 复制 AppID", command=lambda: self._copy_appid_silent(sel[0]))
            menu.add_separator()
            menu.add_command(label="📤 导出笔记", command=self._ui_export_dialog)
            if self.manager.is_dirty(sel[0]):
                menu.add_separator()
                menu.add_command(label="☁️ 上传到 Steam Cloud",
                                 command=lambda: self._cloud_upload_single(sel[0]))
                menu.add_command(label="✅ 标记为已同步（消除改动标记）",
                                 command=lambda: self._mark_synced_selected())
        else:
            menu.add_command(label=f"📤 导出 ({len(sel)} 个游戏)",
                             command=self._ui_export_dialog)
            dirty_sel = [a for a in sel if self.manager.is_dirty(a)]
            if dirty_sel:
                menu.add_command(label=f"☁️ 上传选中 ({len(dirty_sel)} 个)",
                                 command=self._cloud_upload_selected)
                menu.add_command(label=f"✅ 标记选中为已同步 ({len(dirty_sel)} 个)",
                                 command=self._mark_synced_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _get_selected_app_id(self):
        """获取 Treeview 选中的第一个 AppID"""
        sel = self._games_tree.selection()
        return sel[0] if sel else None

    def _get_selected_app_ids(self):
        """获取 Treeview 选中的所有 AppID"""
        return list(self._games_tree.selection())

    def _copy_selected_appid(self):
        """复制选中游戏的 AppID（多选时用逗号分隔）"""
        aids = self._get_selected_app_ids()
        if aids:
            self._copy_appid_silent(",".join(aids))
        else:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")

    def _cloud_upload_selected(self):
        """上传选中游戏的笔记（支持多选）"""
        aids = self._get_selected_app_ids()
        if not aids:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")
            return
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        ok = fail = 0
        for aid in aids:
            if self.manager.is_dirty(aid):
                if self.manager.cloud_upload(aid):
                    ok += 1
                else:
                    fail += 1
        self._refresh_games_list()
        self._save_uploaded_hashes()
        if ok + fail == 0:
            messagebox.showinfo("提示", "选中的游戏没有需要上传的改动。", parent=self.root)
        elif fail == 0:
            messagebox.showinfo("✅ 成功", f"已上传 {ok} 个游戏。", parent=self.root)
        else:
            messagebox.showwarning("⚠️", f"成功 {ok}，失败 {fail}。", parent=self.root)

    def _mark_synced_selected(self):
        """将选中游戏的 dirty 状态手动标记为已同步（不实际上传）"""
        aids = self._get_selected_app_ids()
        if not aids:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")
            return
        dirty_aids = [a for a in aids if self.manager.is_dirty(a)]
        if not dirty_aids:
            messagebox.showinfo("提示", "选中的游戏没有需要同步的改动。", parent=self.root)
            return
        if not messagebox.askyesno("确认标记为已同步",
                f"即将把 {len(dirty_aids)} 个游戏标记为已同步。\n\n"
                "这将消除改动标记，让程序认为本地版本即云版本。\n"
                "适用于：本地文件是从云端下载的，但程序误判为有改动的情况。\n\n"
                "确认继续？", parent=self.root):
            return
        count = 0
        for aid in dirty_aids:
            if self.manager.mark_as_synced(aid):
                count += 1
        self._save_uploaded_hashes()
        self._refresh_games_list()
        messagebox.showinfo("✅ 完成", f"已将 {count} 个游戏标记为已同步。", parent=self.root)

    def _select_all_games(self):
        """全选/取消全选当前筛选下的所有游戏"""
        tree = self._games_tree
        all_items = tree.get_children()
        current_sel = tree.selection()
        if len(current_sel) == len(all_items) and len(all_items) > 0:
            # 已全选 → 取消全选
            tree.selection_remove(*all_items)
        else:
            # 全选
            tree.selection_set(all_items)

    def _ui_export_dialog(self):
        """导出对话框：选择两种导出模式，支持按 AI 筛选状态过滤"""
        aids = self._get_selected_app_ids()
        if not aids:
            messagebox.showinfo("提示",
                "请先在列表中选择要导出的游戏。\n"
                "💡 可点击「✅全选」一键选中全部，或 Ctrl+点击多选。",
                parent=self.root)
            return

        # 检测当前 AI 筛选状态
        current_filter = self._ai_filter_var.get() if hasattr(self, '_ai_filter_var') else "全部"
        is_ai_filtered = (current_filter == "🤖 AI 处理过"
                          or (current_filter.startswith("🤖 ")
                              and current_filter != "🤖 AI 处理过"))

        # 统计笔记数（全部 + AI）
        total_notes = 0
        total_ai_notes = 0
        for aid in aids:
            data = self.manager.read_notes(aid)
            notes = data.get("notes", [])
            total_notes += len(notes)
            total_ai_notes += sum(1 for n in notes if is_ai_note(n))

        if total_notes == 0:
            messagebox.showinfo("提示", "选中的游戏没有笔记可导出。", parent=self.root)
            return

        win = tk.Toplevel(self.root)
        win.title("📤 导出笔记")
        win.resizable(False, False)
        win.grab_set()
        win.transient(self.root)

        tk.Label(win, text="📤 导出笔记", font=("", 13, "bold")).pack(pady=(15, 5))

        # 统计信息标签（后面会动态更新）
        stats_label = tk.Label(win, font=("", 10), fg="#666")
        stats_label.pack(pady=(0, 10))

        # AI 笔记筛选选项（仅在 AI 筛选激活时显示）
        ai_only_var = tk.BooleanVar(value=is_ai_filtered)

        def _update_stats(*_):
            if ai_only_var.get():
                stats_label.config(
                    text=f"已选中 {len(aids)} 个游戏，"
                         f"导出 {total_ai_notes} 条 AI 笔记"
                         f"（共 {total_notes} 条）")
            else:
                stats_label.config(
                    text=f"已选中 {len(aids)} 个游戏，共 {total_notes} 条笔记")
        _update_stats()

        if total_ai_notes > 0:
            filter_frame = tk.Frame(win)
            filter_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
            cb = tk.Checkbutton(filter_frame,
                                text="🤖 仅导出 AI 笔记（每个游戏只导出 AI 生成的笔记）",
                                variable=ai_only_var, font=("", 10),
                                command=_update_stats)
            cb.pack(anchor=tk.W)
            if is_ai_filtered:
                tk.Label(filter_frame,
                         text=f"💡 当前筛选为「{current_filter}」，已自动勾选",
                         font=("", 9), fg="#4a90d9").pack(anchor=tk.W, padx=22)

        mode_frame = tk.LabelFrame(win, text="选择导出模式", font=("", 10),
                                    padx=15, pady=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=5)

        mode_var = tk.IntVar(value=2)

        # 模式一：逐条导出
        tk.Radiobutton(mode_frame,
                       text="📄 逐条导出为多个文件",
                       variable=mode_var, value=1, font=("", 10)).pack(anchor=tk.W)
        tk.Label(mode_frame,
                 text="每条笔记保存为独立 .txt 文件（文件名=笔记标题，内容=BBCode）",
                 font=("", 9), fg="#888").pack(anchor=tk.W, padx=25, pady=(0, 5))

        ttk.Separator(mode_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # 模式二：合并导出
        tk.Radiobutton(mode_frame,
                       text="📦 合并导出为单个文件（可跨账号导入）",
                       variable=mode_var, value=2, font=("", 10)).pack(anchor=tk.W)
        tk.Label(mode_frame,
                 text="所有笔记写入一个结构化 .txt 文件，可在其他账号上直接导入还原",
                 font=("", 9), fg="#888").pack(anchor=tk.W, padx=25, pady=(0, 5))

        def do_export():
            # 构建过滤函数
            nf = is_ai_note if ai_only_var.get() else None
            export_count = total_ai_notes if ai_only_var.get() else total_notes

            if mode_var.get() == 1:
                # 逐条导出 → 选择目录
                output_dir = filedialog.askdirectory(
                    title="选择保存目录（每条笔记一个文件）",
                    parent=win)
                if not output_dir:
                    return
                try:
                    n_files, n_notes = self.manager.export_individual_files(
                        aids, output_dir, note_filter=nf)
                    messagebox.showinfo("✅ 成功",
                        f"已导出 {n_files} 个文件到:\n{output_dir}",
                        parent=win)
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("❌ 错误", f"导出失败:\n{e}", parent=win)
            else:
                # 合并导出 → 选择文件
                path = filedialog.asksaveasfilename(
                    title="保存合并导出文件", defaultextension=".txt",
                    initialfile=f"steam_notes_batch_{datetime.now().strftime('%Y%m%d')}.txt",
                    filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                    parent=win)
                if not path:
                    return
                try:
                    self.manager.export_batch(aids, path, note_filter=nf)
                    messagebox.showinfo("✅ 成功",
                        f"已导出 {len(aids)} 个游戏的 {export_count} 条笔记到:\n{path}",
                        parent=win)
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("❌ 错误", f"导出失败:\n{e}", parent=win)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=(10, 15))
        ttk.Button(btn_frame, text="📤 确认导出",
                   command=do_export).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消",
                   command=win.destroy).pack(side=tk.LEFT, padx=5)

        self._center_window(win)

    def _batch_export_selected(self):
        """批量导出选中的游戏笔记（直接从列表选择）— 旧入口，转到新对话框"""
        self._ui_export_dialog()

    def _copy_appid_silent(self, app_id: str):
        """复制 AppID 到剪贴板（无弹窗）"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(app_id)
            self.root.update()
        except:
            pass

    def _cloud_upload_single(self, app_id: str):
        """上传单个游戏的笔记到 Steam Cloud"""
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        if self.manager.cloud_upload(app_id):
            self._save_uploaded_hashes()
            self._refresh_games_list()
        else:
            messagebox.showerror("❌", f"上传 AppID {app_id} 失败。", parent=self.root)

    def _cloud_upload_all(self):
        """上传所有有改动的笔记到 Steam Cloud"""
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        n = self.manager.dirty_count()
        if n == 0:
            messagebox.showinfo("提示", "没有需要上传的改动。", parent=self.root)
            return
        ok, fail = self.manager.cloud_upload_all_dirty()
        self._save_uploaded_hashes()
        self._refresh_games_list()
        if fail == 0:
            messagebox.showinfo("✅ 成功",
                                f"已上传 {ok} 个游戏的笔记到 Steam Cloud。\n\n"
                                "💡 这些改动仍需等待 Steam 客户端自动同步到云端，\n"
                                "通常在几秒到几分钟内完成。",
                                parent=self.root)
        else:
            messagebox.showwarning("⚠️ 部分失败",
                                    f"成功 {ok} 个，失败 {fail} 个。",
                                    parent=self.root)

    def _on_game_double_click(self, event):
        app_id = self._get_selected_app_id()
        if app_id:
            self._open_notes_viewer(app_id)

    def _ui_dedup_notes(self):
        """笔记去重功能：扫描所有笔记中的重复项，供用户选择删除"""
        duplicates = self.manager.find_duplicate_notes()

        win = tk.Toplevel(self.root)
        win.title("🔍 笔记去重")
        win.resizable(True, True)
        win.grab_set()
        win.transient(self.root)

        tk.Label(win, text="🔍 笔记去重", font=("", 13, "bold")).pack(pady=(15, 5))

        if not duplicates:
            tk.Label(win, text="✅ 没有发现重复的笔记！",
                     font=("", 11), fg="#2a7f2a").pack(padx=40, pady=20)
            ttk.Button(win, text="关闭", command=win.destroy).pack(pady=(0, 15))
            self._center_window(win)
            return

        total_dup_notes = sum(d['count'] - 1 for d in duplicates)
        total_groups = len(duplicates)
        tk.Label(win,
                 text=f"发现 {total_groups} 组重复笔记，"
                      f"共 {total_dup_notes} 条可删除的副本",
                 font=("", 10), fg="#c0392b").pack(pady=(0, 10))

        # 重复列表
        list_frame = tk.Frame(win)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ("game", "title_preview", "copies")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                             height=15, selectmode="extended")
        tree.heading("game", text="游戏")
        tree.heading("title_preview", text="笔记标题 (前50字)")
        tree.heading("copies", text="副本数")
        tree.column("game", width=200, minwidth=100)
        tree.column("title_preview", width=350, minwidth=150)
        tree.column("copies", width=70, minwidth=50, anchor=tk.CENTER)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=tree_scroll.set)

        # 存储数据映射
        dup_map = {}  # {iid: dup_entry}
        for i, d in enumerate(duplicates):
            game_name = self._get_game_name(d['app_id'])
            title_preview = d['title'][:50] + ("..." if len(d['title']) > 50 else "")
            iid = f"dup_{i}"
            tree.insert("", tk.END, iid=iid,
                        values=(game_name, title_preview, d['count']))
            dup_map[iid] = d

        # 预览区
        preview_frame = tk.LabelFrame(win, text="选中笔记预览", font=("", 10),
                                       padx=10, pady=5)
        preview_frame.pack(fill=tk.X, padx=15, pady=5)
        preview_text = tk.Text(preview_frame, height=4, font=("", 9), wrap=tk.WORD,
                                state=tk.DISABLED)
        preview_text.pack(fill=tk.X)

        def _on_select(event):
            sel = tree.selection()
            if not sel:
                return
            d = dup_map.get(sel[0])
            if not d:
                return
            preview_text.config(state=tk.NORMAL)
            preview_text.delete("1.0", tk.END)
            game_name = self._get_game_name(d['app_id'])
            preview_text.insert(tk.END, f"🎮 {game_name} (AppID: {d['app_id']})\n")
            preview_text.insert(tk.END, f"📝 标题: {d['title'][:100]}\n")
            preview_text.insert(tk.END, f"🔢 总副本数: {d['count']} (可删除 {d['count'] - 1} 条)\n")
            preview_text.insert(tk.END, f"📄 索引位置: {d['indices']}")
            preview_text.config(state=tk.DISABLED)
        tree.bind("<<TreeviewSelect>>", _on_select)

        # 按钮区
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=(10, 15))

        def _delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("提示", "请先选择要去重的条目。", parent=win)
                return
            total_to_remove = 0
            for iid in sel:
                d = dup_map.get(iid)
                if d:
                    total_to_remove += d['count'] - 1
            if not messagebox.askyesno("确认删除",
                    f"将为选中的 {len(sel)} 组重复笔记各保留 1 条，\n"
                    f"删除 {total_to_remove} 条副本。\n\n确定继续？",
                    parent=win):
                return
            removed_total = 0
            for iid in sel:
                d = dup_map.get(iid)
                if d:
                    # 保留第一条（索引最小），删除其余
                    indices_to_remove = d['indices'][1:]
                    removed = self.manager.delete_duplicate_notes(
                        d['app_id'], indices_to_remove)
                    removed_total += removed
            messagebox.showinfo("✅ 完成",
                f"已删除 {removed_total} 条重复笔记。", parent=win)
            self._refresh_games_list()
            win.destroy()

        def _delete_all():
            total_to_remove = sum(d['count'] - 1 for d in duplicates)
            if not messagebox.askyesno("确认删除全部重复",
                    f"将为所有 {total_groups} 组重复笔记各保留 1 条，\n"
                    f"共删除 {total_to_remove} 条副本。\n\n确定继续？",
                    parent=win):
                return
            removed_total = 0
            for d in duplicates:
                indices_to_remove = d['indices'][1:]
                removed = self.manager.delete_duplicate_notes(
                    d['app_id'], indices_to_remove)
                removed_total += removed
            messagebox.showinfo("✅ 完成",
                f"已删除 {removed_total} 条重复笔记。", parent=win)
            self._refresh_games_list()
            win.destroy()

        ttk.Button(btn_frame, text="🗑️ 删除选中组的副本",
                   command=_delete_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="🗑️ 全部去重",
                   command=_delete_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="取消",
                   command=win.destroy).pack(side=tk.LEFT, padx=(15, 4))

        self._center_window(win)

    def _ui_view_selected(self):
        app_id = self._get_selected_app_id()
        if app_id:
            self._open_notes_viewer(app_id)
        else:
            messagebox.showinfo("提示", "请先在右侧列表中选择一个游戏。")

    def _copy_appid(self, app_id: str):
        """复制AppID到剪贴板（无弹窗）"""
        self._copy_appid_silent(app_id)

    # ────────────────────── 新建笔记 ──────────────────────

    def _ui_create_note(self):
        """新建笔记窗口 — 使用富文本编辑器"""
        win = tk.Toplevel(self.root)
        win.title("📝 新建 Steam 笔记")
        win.resizable(True, True)
        win.grab_set()

        tk.Label(win, text="📝 新建笔记", font=("", 13, "bold")).pack(pady=(15, 10))

        form = tk.Frame(win, padx=20)
        form.pack(fill=tk.X)

        # AppID
        tk.Label(form, text="游戏 AppID:", font=("", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        app_id_var = tk.StringVar()
        sel_id = self._get_selected_app_id()
        if sel_id:
            app_id_var.set(sel_id)
        tk.Entry(form, textvariable=app_id_var, width=20, font=("", 10)).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        tk.Label(form, text="(如 1245620)", font=("", 9), fg="#888").grid(
            row=0, column=2, sticky=tk.W, padx=5)

        # 标题
        tk.Label(form, text="笔记标题:", font=("", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar()
        tk.Entry(form, textvariable=title_var, width=40, font=("", 10)).grid(
            row=1, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))

        # 富文本编辑器
        tk.Label(win, text="笔记内容:", font=("", 10), padx=20).pack(anchor=tk.W)
        editor = SteamRichTextEditor(win, height=12)
        editor.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

        def do_create():
            aid = app_id_var.get().strip()
            title = title_var.get().strip()
            content = editor.get_content()

            if not aid:
                messagebox.showwarning("提示", "请输入游戏 AppID。", parent=win)
                return
            if not title:
                messagebox.showwarning("提示", "请输入笔记标题。", parent=win)
                return
            if not content.strip():
                messagebox.showwarning("提示", "请输入笔记内容。", parent=win)
                return

            try:
                self.manager.create_note(aid, title, content)
                messagebox.showinfo("✅ 成功",
                                    f"已为 AppID {aid} 创建笔记:\n「{title}」",
                                    parent=win)
                self._refresh_games_list()
                win.destroy()
            except Exception as e:
                messagebox.showerror("❌ 错误", f"写入失败:\n{e}", parent=win)

        ttk.Button(win, text="✅ 创建笔记", command=do_create).pack(pady=(5, 15))
        self._center_window(win)

    # ────────────────────── 查看/编辑笔记 ──────────────────────

    def _ui_view_notes(self):
        app_id = simpledialog.askstring("查看笔记", "请输入游戏 AppID:",
                                        parent=self.root)
        if app_id and app_id.strip():
            self._open_notes_viewer(app_id.strip())

    def _open_notes_viewer(self, app_id: str, select_index: int = 0):
        """笔记浏览/编辑窗口 — 使用富文本编辑器"""
        data = self.manager.read_notes(app_id)
        notes = data.get("notes", [])

        win = tk.Toplevel(self.root)
        win.title(f"📋 AppID {app_id} 的笔记 ({len(notes)} 条)")
        win.resizable(True, True)
        win.grab_set()

        if not notes:
            tk.Label(win, text=f"📭 AppID {app_id} 暂无笔记",
                     font=("", 12), fg="#888").pack(padx=40, pady=30)
            ttk.Button(win, text="📝 新建一条",
                       command=lambda: [win.destroy(), self._ui_create_note()]).pack(pady=10)
            self._center_window(win)
            return

        # 笔记列表 + 详情
        paned = tk.PanedWindow(win, orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左: 列表
        left_f = tk.Frame(paned)
        paned.add(left_f, width=250)

        tk.Label(left_f, text="笔记列表", font=("", 10, "bold")).pack(anchor=tk.W)
        note_listbox = tk.Listbox(left_f, width=30, height=15, font=("", 10))
        note_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        for i, n in enumerate(notes):
            ts = n.get("time_modified", 0)
            t_str = datetime.fromtimestamp(ts).strftime("%m/%d %H:%M") if ts else ""
            ai_mark = "🤖 " if is_ai_note(n) else ""
            note_listbox.insert(tk.END, f"[{i}] {ai_mark}{n.get('title', '(无标题)')[:40]}  {t_str}")
            if is_ai_note(n):
                note_listbox.itemconfig(i, fg="#1a73e8")

        # 右: 详情（使用富文本编辑器）
        right_f = tk.Frame(paned)
        paned.add(right_f, width=550)

        tk.Label(right_f, text="标题:", font=("", 10)).pack(anchor=tk.W)
        title_entry = tk.Entry(right_f, font=("", 11), width=50)
        title_entry.pack(fill=tk.X, pady=(0, 5))

        tk.Label(right_f, text="内容:", font=("", 10)).pack(anchor=tk.W)
        editor = SteamRichTextEditor(right_f, height=15)
        editor.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        ts_label = tk.Label(right_f, text="", font=("", 9), fg="#888")
        ts_label.pack(anchor=tk.W)

        ai_info_label = tk.Label(right_f, text="", font=("", 9), fg="#1a73e8")
        ai_info_label.pack(anchor=tk.W)

        # 用于跟踪原始文本显示状态
        _raw_mode = {'active': False}

        btn_frame = tk.Frame(right_f)
        btn_frame.pack(fill=tk.X, pady=5)

        # 第一行按钮
        btn_row1 = tk.Frame(btn_frame)
        btn_row1.pack(fill=tk.X)

        def do_save():
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            # 如果在原始文本模式，先退出
            if _raw_mode['active']:
                do_toggle_raw()
            i = idx[0]
            new_title = title_entry.get().strip()
            new_content = editor.get_content()
            if self.manager.update_note(app_id, i, new_title, new_content):
                self._refresh_games_list()
                messagebox.showinfo("✅ 成功", "笔记已保存。\n在主界面点击 ☁️ 上传到 Steam Cloud。", parent=win)

        def do_delete():
            idx = note_listbox.curselection()
            if not idx:
                return
            i = idx[0]
            if messagebox.askyesno("确认", f"确定删除笔记 [{i}] ？", parent=win):
                result = self.manager.delete_note(app_id, i)
                if not result:
                    messagebox.showwarning("提示", "删除失败。", parent=win)
                    return
                win.destroy()
                self._refresh_games_list()
                self._open_notes_viewer(app_id)

        def do_export_single():
            """导出当前选中的单条笔记"""
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            i = idx[0]
            note = notes[i]
            title = note.get("title", "untitled")
            safe_name = SteamNotesManager.sanitize_filename(title)
            path = filedialog.asksaveasfilename(
                title="导出笔记", defaultextension=".txt",
                initialfile=f"{safe_name}.txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                parent=win
            )
            if path:
                try:
                    self.manager.export_single_note(app_id, i, path)
                    messagebox.showinfo("✅ 成功", f"已导出笔记「{title}」到:\n{path}",
                                        parent=win)
                except Exception as e:
                    messagebox.showerror("❌ 错误", f"导出失败:\n{e}", parent=win)

        def do_toggle_raw():
            """就地切换原始文本/富文本显示"""
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            i = idx[0]
            if _raw_mode['active']:
                # 原始 → 富文本：重新渲染
                _raw_mode['active'] = False
                raw_toggle_btn.config(text="📄 原始文本")
                editor.set_content(notes[i].get("content", ""))
            else:
                # 富文本 → 原始：显示原始 BBCode
                _raw_mode['active'] = True
                raw_toggle_btn.config(text="👁️ 富文本")
                raw_content = notes[i].get("content", "")
                editor._text.config(state=tk.NORMAL)
                editor._text.delete("1.0", tk.END)
                editor._text.insert("1.0", raw_content)

        ttk.Button(btn_row1, text="💾 保存修改", command=do_save).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="🗑️ 删除此条", command=do_delete).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="📤 导出此条", command=do_export_single).pack(
            side=tk.LEFT, padx=5)
        raw_toggle_btn = ttk.Button(btn_row1, text="📄 原始文本",
                                      command=do_toggle_raw)
        raw_toggle_btn.pack(side=tk.LEFT, padx=5)

        # 第二行按钮
        btn_row2 = tk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X, pady=(3, 0))

        def do_move(direction):
            idx = note_listbox.curselection()
            if not idx:
                return
            i = idx[0]
            new_i = i + direction
            if new_i < 0 or new_i >= len(notes):
                return
            result = self.manager.move_note(app_id, i, direction)
            if not result:
                # 移动失败，可能是试图移动受保护的同步触发笔记
                messagebox.showwarning("提示",
                    "无法移动该笔记。\n\n"
                    "第一条云同步触发笔记受到保护，不可移动，\n"
                    "也不允许将其他笔记移动到第一位。",
                    parent=win)
                return
            win.destroy()
            self._refresh_games_list()
            self._open_notes_viewer(app_id, select_index=new_i)

        ttk.Button(btn_row2, text="🔼 上移", command=lambda: do_move(-1)).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row2, text="🔽 下移", command=lambda: do_move(1)).pack(
            side=tk.LEFT, padx=5)

        # 切换笔记时重置原始文本模式
        def on_select(event=None):
            idx = note_listbox.curselection()
            if not idx:
                return
            _raw_mode['active'] = False
            raw_toggle_btn.config(text="📄 原始文本")
            i = idx[0]
            note = notes[i]
            title_entry.delete(0, tk.END)
            title_entry.insert(0, note.get("title", ""))
            editor.set_content(note.get("content", ""))
            ts = note.get("time_modified", 0)
            if ts:
                ts_label.config(text=f"⏰ {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}")
            # 显示 AI 模型信息
            if is_ai_note(note):
                model = extract_ai_model_from_note(note)
                ai_info_label.config(
                    text=f"🤖 AI 生成" + (f" (模型: {model})" if model else ""))
            else:
                ai_info_label.config(text="")

        note_listbox.bind("<<ListboxSelect>>", on_select)
        if notes:
            sel = min(select_index, len(notes) - 1)
            note_listbox.selection_set(sel)
            note_listbox.see(sel)
            note_listbox.event_generate("<<ListboxSelect>>")

        self._center_window(win)

    # ────────────────────── 删除笔记 ──────────────────────

    def _ui_delete_notes(self):
        app_id = self._get_selected_app_id()
        if not app_id:
            app_id = simpledialog.askstring("删除笔记", "请输入游戏 AppID:",
                                            parent=self.root)
        if not app_id:
            return

        notes = self.manager.read_notes(app_id).get("notes", [])
        if not notes:
            messagebox.showinfo("提示", f"AppID {app_id} 暂无笔记。")
            return

        if messagebox.askyesno("确认删除",
                               f"确定删除 AppID {app_id} 的全部 {len(notes)} 条笔记？\n"
                               f"此操作不可撤销。"):
            self.manager.delete_all_notes(app_id)
            messagebox.showinfo("✅ 成功", f"已删除 AppID {app_id} 的所有笔记。")
            self._refresh_games_list()

    # ────────────────────── API Key 设置 ──────────────────────

    def _ui_api_key_settings(self):
        """API Key 与 AI 配置管理窗口 — 支持多令牌管理"""
        win = tk.Toplevel(self.root)
        win.title("🔑 API Key 与 AI 配置")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="🔑 API Key 与 AI 配置", font=("", 13, "bold")).pack(pady=(15, 5))
        config_info_frame = tk.Frame(win)
        config_info_frame.pack(pady=(0, 5))
        tk.Label(config_info_frame, text="管理多个 AI 令牌，在 AI 生成页面可自由切换。",
                 font=("", 9), fg="#666").pack()
        config_path_row = tk.Frame(config_info_frame)
        config_path_row.pack()
        tk.Label(config_path_row, text="配置存储于: ",
                 font=("", 9), fg="#666").pack(side=tk.LEFT)
        config_link = tk.Label(config_path_row, text="~/.steam_notes_gen/",
                               font=("", 9, "underline"), fg="#4a90d9", cursor="hand2")
        config_link.pack(side=tk.LEFT)
        config_link.bind("<Button-1>", lambda e: self._open_config_dir())

        # ══════════ 已保存的令牌列表 ══════════
        tokens_frame = tk.LabelFrame(win, text="🔑 已保存的 AI 令牌", font=("", 10),
                                      padx=10, pady=5)
        tokens_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        tokens_data = list(self._get_ai_tokens())  # 可变副本
        active_idx = [self._get_active_token_index()]

        tokens_listbox = tk.Listbox(tokens_frame, font=("", 9), height=4,
                                     exportselection=False)
        tokens_listbox.pack(fill=tk.X, pady=(0, 5))

        def _refresh_token_list():
            tokens_listbox.delete(0, tk.END)
            for i, t in enumerate(tokens_data):
                prefix = "★ " if i == active_idx[0] else "   "
                key_preview = t.get("key", "")
                if len(key_preview) > 10:
                    key_preview = key_preview[:6] + "..." + key_preview[-4:]
                prov_name = SteamAIGenerator.PROVIDERS.get(
                    t.get("provider", ""), {}).get("name", t.get("provider", ""))
                tokens_listbox.insert(tk.END,
                    f"{prefix}{t.get('name', '未命名')}  |  {prov_name}  |  "
                    f"{t.get('model', '')}  |  Key: {key_preview}")
                if i == active_idx[0]:
                    tokens_listbox.itemconfig(i, fg="#1a73e8")

        _refresh_token_list()

        tokens_btn_row = tk.Frame(tokens_frame)
        tokens_btn_row.pack(fill=tk.X)

        def _delete_token():
            sel = tokens_listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请先选择要删除的令牌。", parent=win)
                return
            idx = sel[0]
            name = tokens_data[idx].get("name", "")
            if not messagebox.askyesno("确认", f"确定删除令牌「{name}」？", parent=win):
                return
            tokens_data.pop(idx)
            if active_idx[0] >= len(tokens_data):
                active_idx[0] = max(0, len(tokens_data) - 1)
            elif active_idx[0] > idx:
                active_idx[0] -= 1
            _refresh_token_list()

        def _set_default():
            sel = tokens_listbox.curselection()
            if not sel:
                return
            active_idx[0] = sel[0]
            _refresh_token_list()

        def _load_to_form():
            """将选中令牌加载到编辑表单"""
            sel = tokens_listbox.curselection()
            if not sel:
                return
            t = tokens_data[sel[0]]
            name_var.set(t.get("name", ""))
            pk = t.get("provider", "anthropic")
            pn = provider_names.get(pk, provider_names.get("anthropic", ""))
            provider_var.set(pn)
            ai_key_var.set(t.get("key", ""))
            model_var.set(t.get("model", ""))
            url_var.set(t.get("api_url", ""))
            _on_provider_changed()

        tk.Button(tokens_btn_row, text="🗑️ 删除", font=("", 9), relief=tk.FLAT,
                  command=_delete_token).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(tokens_btn_row, text="★ 设为默认", font=("", 9), relief=tk.FLAT,
                  command=_set_default).pack(side=tk.LEFT, padx=5)
        tk.Button(tokens_btn_row, text="📝 加载到表单", font=("", 9), relief=tk.FLAT,
                  command=_load_to_form).pack(side=tk.LEFT, padx=5)

        # ══════════ 令牌编辑表单 ══════════
        form_frame = tk.LabelFrame(win, text="➕ 添加 / 修改令牌", font=("", 10),
                                    padx=10, pady=5)
        form_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        form = tk.Frame(form_frame)
        form.pack(fill=tk.X)
        row = 0

        # ── 令牌名称 ──
        tk.Label(form, text="令牌名称:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        name_var = tk.StringVar()
        tk.Entry(form, textvariable=name_var, width=30,
                 font=("", 9)).grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0),
                                     columnspan=2)
        row += 1

        # ── AI 提供商 ──
        tk.Label(form, text="AI 提供商:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        provider_names = {k: v['name'] for k, v in SteamAIGenerator.PROVIDERS.items()}
        provider_var = tk.StringVar(value=provider_names.get("anthropic", ""))
        provider_combo = ttk.Combobox(form, textvariable=provider_var, width=30,
                                       values=list(provider_names.values()), state='readonly')
        provider_combo.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0), columnspan=2)
        row += 1

        def _provider_key_from_name(display_name):
            for k, v in provider_names.items():
                if v == display_name:
                    return k
            return 'anthropic'

        # ── AI API Key ──
        tk.Label(form, text="API Key:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        ai_key_var = tk.StringVar()
        ai_key_entry = tk.Entry(form, textvariable=ai_key_var, width=40,
                                 font=("", 9), show="•")
        ai_key_entry.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0))

        def toggle_show_ai():
            if ai_key_entry.cget("show") == "•":
                ai_key_entry.config(show="")
                show_ai_btn.config(text="🙈")
            else:
                ai_key_entry.config(show="•")
                show_ai_btn.config(text="👁️")
        show_ai_btn = tk.Button(form, text="👁️", font=("", 9), relief=tk.FLAT,
                                 command=toggle_show_ai)
        show_ai_btn.grid(row=row, column=2, padx=3)
        row += 1

        # ── 模型 ──
        tk.Label(form, text="模型:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        model_var = tk.StringVar()
        model_combo = ttk.Combobox(form, textvariable=model_var, width=35,
                                    values=[])
        model_combo.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0), columnspan=2)
        row += 1

        # ── 自定义 API URL ──
        tk.Label(form, text="API URL:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        url_var = tk.StringVar()
        tk.Entry(form, textvariable=url_var, width=40,
                 font=("", 9)).grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0),
                                     columnspan=2)
        row += 1

        url_hint = tk.Label(form, text="", font=("", 8), fg="#888")
        url_hint.grid(row=row, column=0, sticky=tk.W, columnspan=3)
        row += 1

        def _on_provider_changed(*_):
            pk = _provider_key_from_name(provider_combo.get())
            pi = SteamAIGenerator.PROVIDERS.get(pk, {})
            model_combo['values'] = pi.get('models', [])
            if not model_var.get() or model_var.get() not in pi.get('models', []):
                dm = pi.get('default_model', '')
                if dm:
                    model_var.set(dm)
            du = pi.get('api_url', '')
            url_hint.config(text=f"留空使用默认: {du}" if du else "⚠️ 请填写 API URL")
            # 自动填充名称
            if not name_var.get().strip():
                name_var.set(pi.get('name', pk))
        provider_combo.bind("<<ComboboxSelected>>", _on_provider_changed)
        _on_provider_changed()

        # 表单按钮
        form_btn_row = tk.Frame(form_frame)
        form_btn_row.pack(fill=tk.X, pady=(5, 0))

        def _save_as_new():
            key = ai_key_var.get().strip()
            if not key:
                messagebox.showwarning("提示", "请输入 API Key。", parent=win)
                return
            token = {
                "name": name_var.get().strip() or "未命名",
                "key": key,
                "provider": _provider_key_from_name(provider_var.get()),
                "model": model_var.get().strip(),
                "api_url": url_var.get().strip(),
            }
            tokens_data.append(token)
            if len(tokens_data) == 1:
                active_idx[0] = 0
            _refresh_token_list()
            messagebox.showinfo("✅", f"已添加令牌「{token['name']}」", parent=win)

        def _update_selected():
            sel = tokens_listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请先在上方列表中选择要更新的令牌。", parent=win)
                return
            key = ai_key_var.get().strip()
            if not key:
                messagebox.showwarning("提示", "请输入 API Key。", parent=win)
                return
            idx = sel[0]
            tokens_data[idx] = {
                "name": name_var.get().strip() or "未命名",
                "key": key,
                "provider": _provider_key_from_name(provider_var.get()),
                "model": model_var.get().strip(),
                "api_url": url_var.get().strip(),
            }
            _refresh_token_list()
            messagebox.showinfo("✅", "已更新所选令牌。", parent=win)

        ttk.Button(form_btn_row, text="➕ 添加为新令牌",
                   command=_save_as_new).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(form_btn_row, text="💾 更新选中令牌",
                   command=_update_selected).pack(side=tk.LEFT, padx=5)

        # ══════════ Steam Web API Key ══════════
        ttk.Separator(win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=8)

        steam_frame = tk.LabelFrame(win, text="🎮 Steam Web API Key", font=("", 10),
                                     padx=10, pady=5)
        steam_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        steam_row = tk.Frame(steam_frame)
        steam_row.pack(fill=tk.X)
        steam_var = tk.StringVar(value=self._get_saved_key("steam_web_api_key"))
        steam_entry = tk.Entry(steam_row, textvariable=steam_var, width=40,
                                font=("", 9), show="•")
        steam_entry.pack(side=tk.LEFT, pady=2)

        def toggle_show_steam():
            if steam_entry.cget("show") == "•":
                steam_entry.config(show="")
                show_s_btn.config(text="🙈")
            else:
                steam_entry.config(show="•")
                show_s_btn.config(text="👁️")
        show_s_btn = tk.Button(steam_row, text="👁️", font=("", 9), relief=tk.FLAT,
                                command=toggle_show_steam)
        show_s_btn.pack(side=tk.LEFT, padx=3)

        def clear_steam():
            steam_var.set("")
            self._clear_saved_key("steam_web_api_key")
        tk.Button(steam_row, text="🗑️ 清除", font=("", 9), relief=tk.FLAT,
                  command=clear_steam).pack(side=tk.LEFT, padx=3)

        steam_status = tk.Label(steam_frame, text="", font=("", 8))
        steam_status.pack(anchor=tk.W)
        if self._get_saved_key("steam_web_api_key"):
            steam_status.config(text="✅ 已保存", fg="green")

        tk.Label(steam_frame, text="用于在线扫描游戏库 — 从 steamcommunity.com/dev/apikey 获取",
                 font=("", 8), fg="#888").pack(anchor=tk.W, pady=(0, 3))

        # ── 保存全部按钮 ──
        def do_save_all():
            # 保存令牌列表
            self._save_ai_tokens(tokens_data, active_idx[0])
            # 保存 Steam Key
            sk = steam_var.get().strip()
            if sk:
                self._config["steam_web_api_key"] = sk
            elif "steam_web_api_key" in self._config:
                del self._config["steam_web_api_key"]
            self._save_config(self._config)
            steam_status.config(text="✅ 已保存" if sk else "", fg="green")
            messagebox.showinfo("✅ 成功", "所有配置已保存。", parent=win)

        btn_frame = tk.Frame(win, padx=20)
        btn_frame.pack(fill=tk.X, pady=(5, 15))
        ttk.Button(btn_frame, text="💾 保存全部", command=do_save_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=win.destroy).pack(side=tk.RIGHT, padx=5)

        self._center_window(win)

    # ────────────────────── AI 批量生成 ──────────────────────

    def _ui_ai_batch_generate(self):
        """AI 批量生成游戏说明笔记窗口 — 紧凑版，配置从主界面读取"""
        if not _HAS_URLLIB:
            messagebox.showerror("❌ 缺少依赖",
                                 "AI 功能需要 urllib 模块（Python 标准库），当前环境不可用。")
            return

        # 读取保存的令牌列表
        all_tokens = self._get_ai_tokens()
        saved_steam_key = (self._config.get("steam_web_api_key") or
                           os.environ.get("STEAM_WEB_API_KEY", ""))

        if not all_tokens:
            messagebox.showwarning("⚠️ 未配置 AI 令牌",
                "请先在主界面点击「🔑 AI 配置」添加至少一个 AI 令牌。")
            return

        # 当前选中的令牌
        active_token_idx = [min(self._get_active_token_index(), len(all_tokens) - 1)]
        current_token = [all_tokens[active_token_idx[0]]]

        win = tk.Toplevel(self.root)
        win.title("🤖 AI 批量生成游戏说明")
        win.resizable(True, True)
        win.grab_set()
        win.minsize(880, 580)

        # ── 令牌选择器 + Cloud 按钮 ──
        config_frame = tk.LabelFrame(win, text="当前 AI 令牌 & Steam Cloud",
                                      font=("", 9), padx=8, pady=3)
        config_frame.pack(fill=tk.X, padx=10, pady=(8, 3))

        token_row = tk.Frame(config_frame)
        token_row.pack(fill=tk.X)

        tk.Label(token_row, text="🔑 令牌:", font=("", 9)).pack(side=tk.LEFT)
        token_names = [f"{t.get('name', '未命名')} ({SteamAIGenerator.PROVIDERS.get(t.get('provider', ''), {}).get('name', t.get('provider', ''))} / {t.get('model', '')})"
                       for t in all_tokens]
        _token_select_var = tk.StringVar(value=token_names[active_token_idx[0]] if token_names else "")
        token_combo = ttk.Combobox(token_row, textvariable=_token_select_var,
                                    values=token_names, state='readonly', width=55)
        token_combo.pack(side=tk.LEFT, padx=(5, 10))

        token_detail_label = tk.Label(config_frame, text="", font=("", 8), fg="#555",
                                       justify=tk.LEFT)
        token_detail_label.pack(anchor=tk.W)

        def _update_token_detail():
            t = current_token[0]
            pname = SteamAIGenerator.PROVIDERS.get(t.get('provider', ''), {}).get('name', t.get('provider', ''))
            key_preview = t.get('key', '')
            if len(key_preview) > 10:
                key_preview = key_preview[:6] + '...' + key_preview[-4:]
            detail = f"提供商: {pname}  |  模型: {t.get('model', '')}  |  Key: {key_preview}"
            if t.get('api_url'):
                detail += f"  |  自定义 URL: {t['api_url']}"
            detail += f"  |  Steam API Key: {'✅' if saved_steam_key else '❌'}"
            token_detail_label.config(text=detail)

        def _on_token_changed(*_):
            sel_text = _token_select_var.get()
            for i, name in enumerate(token_names):
                if name == sel_text:
                    active_token_idx[0] = i
                    current_token[0] = all_tokens[i]
                    break
            _update_token_detail()

        token_combo.bind("<<ComboboxSelected>>", _on_token_changed)
        _update_token_detail()

        # ── Cloud 连接按钮（嵌入令牌行右侧） ──
        _cloud_connect_btn_ai = ttk.Button(token_row, text="☁️ 连接 Steam Cloud",
                                            command=lambda: None)  # placeholder
        _cloud_connect_btn_ai.pack(side=tk.RIGHT, padx=(5, 0))

        _cloud_status_label = tk.Label(token_row, text="", font=("", 9))
        _cloud_status_label.pack(side=tk.RIGHT)

        def _update_ai_cloud_status():
            if self.cloud_uploader and self.cloud_uploader.initialized:
                logged_in = self.cloud_uploader.logged_in_friend_code
                selected = self.current_account.get('friend_code', '')
                if logged_in and logged_in != selected:
                    _cloud_status_label.config(
                        text="⚠️ Cloud 已连接 (账号不匹配!)", fg="red")
                else:
                    _cloud_status_label.config(
                        text="☁️ Steam Cloud 已连接", fg="green")
                _cloud_connect_btn_ai.config(text="🔌 断开")
            else:
                _cloud_status_label.config(text="☁️ Steam Cloud 未连接", fg="#888")
                _cloud_connect_btn_ai.config(text="☁️ 连接 Steam Cloud")

        def _toggle_cloud_ai():
            if self.cloud_uploader and self.cloud_uploader.initialized:
                self.cloud_uploader.shutdown()
                self.cloud_uploader = None
                self.manager.cloud_uploader = None
                _update_ai_cloud_status()
                # 同步更新主界面状态
                try:
                    self._update_cloud_status_display()
                except Exception:
                    pass
                return
            _cloud_connect_btn_ai.config(state=tk.DISABLED)
            win.update_idletasks()
            uploader = SteamCloudUploader()
            steam_path = self.current_account.get('steam_path', '')
            ok, msg = uploader.auto_init(steam_path)
            if ok:
                # 先检查账号匹配
                logged_in = uploader.logged_in_friend_code
                selected = self.current_account.get('friend_code', '')
                if logged_in and logged_in != selected:
                    logged_name = None
                    for acc in self.accounts:
                        if acc['friend_code'] == logged_in:
                            logged_name = acc['persona_name']
                            break
                    logged_desc = (f"「{logged_name}」(ID: {logged_in})"
                                   if logged_name else f"ID: {logged_in}")
                    selected_name = self.current_account.get(
                        'persona_name', selected)
                    uploader.shutdown()
                    messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                        f"Steam 登录账号 {logged_desc} ≠ "
                        f"程序选择的「{selected_name}」\n\n"
                        f"请先在 Steam 客户端切换到正确账号后重新连接。",
                        parent=win)
                    _cloud_connect_btn_ai.config(state=tk.NORMAL)
                    return
                self.cloud_uploader = uploader
                self.manager.cloud_uploader = uploader
                _update_ai_cloud_status()
                try:
                    self._update_cloud_status_display()
                except Exception:
                    pass
            else:
                messagebox.showerror("❌ 连接失败",
                    f"无法连接 Steam Cloud:\n{msg}\n\n"
                    "请确保:\n"
                    "1. Steam 客户端正在运行\n"
                    "2. 库中至少有一个已安装的游戏\n"
                    "3. macOS 用户首次使用可能需要在系统设置中允许加载",
                    parent=win)
            _cloud_connect_btn_ai.config(state=tk.NORMAL)

        _cloud_connect_btn_ai.config(command=_toggle_cloud_ai)
        _update_ai_cloud_status()

        # 使用当前令牌的 provider/model 等信息
        def _get_current_provider(): return current_token[0].get("provider", "anthropic")
        def _get_current_model():
            m = current_token[0].get("model", "")
            if not m:
                pinfo = SteamAIGenerator.PROVIDERS.get(_get_current_provider(), {})
                m = pinfo.get("default_model", "claude-sonnet-4-5-20250929")
            return m
        def _get_current_key(): return current_token[0].get("key", "")
        def _get_current_url(): return current_token[0].get("api_url", "") or None

        # ═══════════════════════════════════════════════════════
        #  使用 PanedWindow 上下分割：上=提示词+游戏列表  下=进度区
        # ═══════════════════════════════════════════════════════
        main_paned = tk.PanedWindow(win, orient=tk.VERTICAL, sashwidth=5)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)

        # ── 上半部分：左=提示词 右=游戏列表 ──
        top_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL, sashwidth=5)
        main_paned.add(top_paned, minsize=280)

        # ═══════════════ 左列：系统提示词 ═══════════════
        left_panel = tk.Frame(top_paned)
        top_paned.add(left_panel, minsize=300, width=380)

        # ── 系统提示词 ──
        prompt_frame = tk.LabelFrame(left_panel, text="系统提示词（可编辑）",
                                      font=("", 10), padx=8, pady=3)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        prompt_collapsed = {'value': True}
        prompt_text = tk.Text(prompt_frame, font=("", 9), height=1, wrap=tk.WORD,
                               fg="#555")
        # 优先从配置加载保存的提示词，没有则用默认
        saved_prompt = self._config.get("ai_system_prompt", "").strip()
        prompt_text.insert("1.0", saved_prompt if saved_prompt else AI_SYSTEM_PROMPT)
        prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 3))

        def toggle_prompt():
            if prompt_collapsed['value']:
                prompt_text.config(height=12)
                toggle_btn.config(text="🔼 收起")
                prompt_collapsed['value'] = False
            else:
                prompt_text.config(height=1)
                toggle_btn.config(text="🔽 展开")
                prompt_collapsed['value'] = True

        prompt_btn_frame = tk.Frame(prompt_frame)
        prompt_btn_frame.pack(fill=tk.X)
        toggle_btn = tk.Button(prompt_btn_frame, text="🔽 展开", font=("", 9),
                                relief=tk.FLAT, command=toggle_prompt)
        toggle_btn.pack(side=tk.LEFT)

        def reset_prompt():
            prompt_text.delete("1.0", tk.END)
            prompt_text.insert("1.0", AI_SYSTEM_PROMPT)
        tk.Button(prompt_btn_frame, text="↩️ 恢复默认", font=("", 9),
                  relief=tk.FLAT, command=reset_prompt).pack(side=tk.LEFT, padx=10)

        def save_prompt():
            current_prompt = prompt_text.get("1.0", tk.END).strip()
            self._config["ai_system_prompt"] = current_prompt
            self._save_config(self._config)
            messagebox.showinfo("✅", "提示词已保存", parent=win)
        tk.Button(prompt_btn_frame, text="💾 保存提示词", font=("", 9),
                  relief=tk.FLAT, command=save_prompt).pack(side=tk.LEFT, padx=5)

        tk.Label(prompt_frame,
                 text="💡 标题=内容模式：AI 输出同时作为笔记标题和内容",
                 font=("", 8), fg="#4a90d9").pack(anchor=tk.W)

        # ═══════════════ 右列：游戏列表 ═══════════════
        right_panel = tk.Frame(top_paned)
        top_paned.add(right_panel, minsize=380)

        games_frame = tk.LabelFrame(right_panel, text="游戏列表", font=("", 10),
                                     padx=8, pady=3)
        games_frame.pack(fill=tk.BOTH, expand=True)

        # 模式切换 — 注意 command 用 IntVar.set 延迟触发，避免 Python 3.13 闭包问题
        mode_frame = tk.Frame(games_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 3))
        games_mode_var = tk.IntVar(value=1)

        # ── 模式1: 扫描库 ──
        scan_container = tk.Frame(games_frame)
        scan_container.pack(fill=tk.BOTH, expand=True)

        _library_games = []

        # Steam API 配置状态提示 + Steam ID 输入（合并为一行）
        steam_status_frame = tk.Frame(scan_container)
        steam_status_frame.pack(fill=tk.X, pady=(0, 2))

        steam_key_ok = "✅" if saved_steam_key else "❌"
        tk.Label(steam_status_frame,
                 text=f"Steam API Key: {steam_key_ok}",
                 font=("", 9), fg="#333").pack(side=tk.LEFT)

        tk.Label(steam_status_frame, text="  Steam ID:", font=("", 9)).pack(side=tk.LEFT)
        steam_id_var = tk.StringVar(
            value=self.current_account.get('friend_code', ''))
        tk.Entry(steam_status_frame, textvariable=steam_id_var, width=15,
                 font=("", 9)).pack(side=tk.LEFT, padx=(3, 0))
        tk.Label(steam_status_frame, text="（可填自己或家庭组其他成员 ID，扫描其游戏库）",
                 font=("", 8), fg="#888").pack(side=tk.LEFT, padx=3)

        # Steam 分类筛选
        collection_frame = tk.Frame(scan_container)
        collection_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(collection_frame, text="📂 按分类筛选:", font=("", 9)).pack(side=tk.LEFT)
        _collections = []
        _collection_var = tk.StringVar(value="（入库该账号的游戏）")
        collection_combo = ttk.Combobox(collection_frame, textvariable=_collection_var,
                                         width=25, state='readonly',
                                         values=["（入库该账号的游戏）"])
        collection_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 状态 + 搜索 — 必须在 _load_collections 之前创建
        info_search_frame = tk.Frame(scan_container)
        info_search_frame.pack(fill=tk.X, pady=(1, 1))

        scan_info_label = tk.Label(info_search_frame,
                                    text="正在加载...",
                                    font=("", 9), fg="#888")
        scan_info_label.pack(side=tk.LEFT)

        # 搜索框放右侧
        tk.Label(info_search_frame, text="🔎", font=("", 9)).pack(side=tk.LEFT, padx=(8, 0))
        search_var = tk.StringVar()
        search_entry = tk.Entry(info_search_frame, textvariable=search_var,
                                 width=18, font=("", 9))
        search_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)

        # 游戏列表（占满剩余空间）
        list_frame = tk.Frame(scan_container)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        games_listbox = tk.Listbox(list_frame, font=("Consolas", 9),
                                    selectmode=tk.EXTENDED,
                                    exportselection=False)
        games_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        games_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                         command=games_listbox.yview)
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        games_listbox.config(yscrollcommand=games_scrollbar.set)

        # 按钮行（合并为一行）
        scan_btn_row1 = tk.Frame(scan_container)
        scan_btn_row1.pack(fill=tk.X, pady=(2, 0))

        # AI 筛选器 — 在函数定义前创建 widget
        ai_filter_row = tk.Frame(scan_container)
        ai_filter_row.pack(fill=tk.X, pady=(1, 0))
        tk.Label(ai_filter_row, text="AI 筛选:", font=("", 9)).pack(side=tk.LEFT)
        _ai_gen_filter_var = tk.StringVar(value="全部")
        ai_gen_filter_combo = ttk.Combobox(
            ai_filter_row, textvariable=_ai_gen_filter_var, width=18,
            values=["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理"], state='readonly')
        ai_gen_filter_combo.pack(side=tk.LEFT, padx=(3, 0))

        # 确信度二级筛选（默认隐藏，选中 AI 相关筛选后自动出现）
        _conf_gen_filter_var = tk.StringVar(value="全部确信度")
        conf_gen_filter_combo = ttk.Combobox(
            ai_filter_row, textvariable=_conf_gen_filter_var, width=10,
            values=["全部确信度"], state='readonly')
        _conf_gen_filter_visible = [False]

        _filtered_indices = []
        _ai_notes_map_cache = {}

        # ═══════ 所有内部函数定义（在 widget 全部创建后） ═══════

        def _get_selected_collection_ids():
            """根据下拉框选中的分类名，返回该分类的 app_ids 集合，未选中返回 None"""
            sel = _collection_var.get()
            if sel == "（入库该账号的游戏）":
                return None
            for c in _collections:
                display_name = f"{c['name']} ({len(c['app_ids'])})"
                if display_name == sel:
                    return set(str(x) for x in c['app_ids'])
            return None

        def _populate_listbox(filter_text=""):
            nonlocal _filtered_indices, _ai_notes_map_cache
            games_listbox.delete(0, tk.END)
            _filtered_indices = []
            ft = filter_text.strip().lower()

            # 获取选中的分类
            col_app_ids = _get_selected_collection_ids()

            # 扫描 AI 笔记状态
            _ai_notes_map_cache = self.manager.scan_ai_notes()

            # AI 筛选模式 & 确信度筛选
            ai_mode = _ai_gen_filter_var.get()
            conf_filter = _conf_gen_filter_var.get()
            is_ai_mode = (ai_mode == "🤖 AI 处理过"
                          or (ai_mode.startswith("🤖 ")
                              and ai_mode != "🤖 AI 处理过"))

            # 收集所有确信度（用于更新下拉框）
            all_confidences = set()

            # 用于统计的变量
            intersection = None

            def _make_display(app_id, name):
                """为列表项生成显示文本和颜色"""
                has_ai = app_id in _ai_notes_map_cache
                is_dirty = self.manager.is_dirty(app_id)
                ai_info = _ai_notes_map_cache.get(app_id, {})
                confs = ai_info.get('confidences', [])
                for c in confs:
                    all_confidences.add(c)
                # 确信度 emoji（取第一个，通常只有一条 AI 笔记）
                conf_emoji = ""
                if has_ai and confs:
                    conf_emoji = CONFIDENCE_EMOJI.get(confs[0], "")
                ai_tag = f" 🤖{conf_emoji}" if has_ai else ""
                dirty_tag = " ⬆" if is_dirty else ""
                return f" {app_id:>10s}  |  {name}{ai_tag}{dirty_tag}", has_ai, is_dirty

            def _should_include(app_id):
                """判断是否通过 AI 筛选 + 确信度筛选 + dirty 筛选"""
                has_ai = app_id in _ai_notes_map_cache
                ai_info = _ai_notes_map_cache.get(app_id, {})
                if ai_mode == "☁️ 有改动" and not self.manager.is_dirty(app_id):
                    return False
                if ai_mode == "🤖 AI 处理过" and not has_ai:
                    return False
                if ai_mode == "📝 未 AI 处理" and has_ai:
                    return False
                if (ai_mode.startswith("🤖 ")
                        and ai_mode != "🤖 AI 处理过"):
                    target_model = ai_mode[2:]
                    if target_model not in ai_info.get('models', []):
                        return False
                # 确信度二级筛选
                if is_ai_mode and conf_filter != "全部确信度":
                    if conf_filter not in ai_info.get('confidences', []):
                        return False
                return True

            # 构建要显示的游戏列表
            if col_app_ids is not None:
                lib_app_ids = {g['app_id'] for g in _library_games}
                intersection = col_app_ids & lib_app_ids

                lib_name_map = {g['app_id']: g['name'] for g in _library_games}
                display_list = [{'app_id': a, 'name': lib_name_map[a]}
                                for a in sorted(intersection)]
                display_list.sort(key=lambda x: x['name'].lower())
                for idx, g in enumerate(display_list):
                    if ft and ft not in g['name'].lower() and ft not in g['app_id']:
                        continue
                    if not _should_include(g['app_id']):
                        continue
                    _filtered_indices.append(('col', g['app_id'], g['name']))
                    text, has_ai, is_dirty = _make_display(g['app_id'], g['name'])
                    games_listbox.insert(tk.END, text)
                    if is_dirty:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#b8860b")
                    elif has_ai:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#1a73e8")
            else:
                for idx, g in enumerate(_library_games):
                    if ft and ft not in g['name'].lower() and ft not in g['app_id']:
                        continue
                    if not _should_include(g['app_id']):
                        continue
                    _filtered_indices.append(idx)
                    text, has_ai, is_dirty = _make_display(g['app_id'], g['name'])
                    games_listbox.insert(tk.END, text)
                    if is_dirty:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#b8860b")
                    elif has_ai:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#1a73e8")

            # 统计信息
            if intersection is not None:
                total_in_collection = len(col_app_ids)
                owned_count = len(intersection)
                scan_info_label.config(
                    text=f"收藏夹共 {total_in_collection} 款，该用户拥有 {owned_count} 款"
                         + (f"，筛选 {len(_filtered_indices)} 款" if ft or ai_mode != "全部" else ""),
                    fg="#333"
                )
            else:
                extra = ""
                if ft or ai_mode != "全部":
                    extra = f"，筛选 {len(_filtered_indices)} 款"
                scan_info_label.config(
                    text=f"共 {len(_library_games)} 款{extra}",
                    fg="#333"
                )

            # 更新 AI 筛选器下拉选项（加入检测到的模型名）
            all_models = set()
            for info in _ai_notes_map_cache.values():
                for m in info.get('models', []):
                    all_models.add(m)
            filter_values = ["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理"]
            for m in sorted(all_models):
                filter_values.append(f"🤖 {m}")
            ai_gen_filter_combo['values'] = filter_values

            # 更新确信度筛选器
            _update_conf_filter_visibility(all_confidences)

        def _update_conf_filter_visibility(all_confidences):
            """根据 AI 筛选模式显示/隐藏确信度下拉框"""
            ai_mode = _ai_gen_filter_var.get()
            is_ai_mode = (ai_mode == "🤖 AI 处理过"
                          or (ai_mode.startswith("🤖 ")
                              and ai_mode != "🤖 AI 处理过"))
            if is_ai_mode:
                if not _conf_gen_filter_visible[0]:
                    conf_gen_filter_combo.pack(side=tk.LEFT, padx=(3, 0),
                                              after=ai_gen_filter_combo)
                    _conf_gen_filter_visible[0] = True
                conf_order = ["很高", "较高", "中等", "较低", "很低"]
                conf_gen_filter_combo['values'] = ["全部确信度"] + conf_order
            else:
                if _conf_gen_filter_visible[0]:
                    conf_gen_filter_combo.pack_forget()
                    _conf_gen_filter_visible[0] = False
                _conf_gen_filter_var.set("全部确信度")

        def _load_collections():
            nonlocal _collections
            raw = SteamAccountScanner.get_collections(
                self.current_account['userdata_path'])
            # 过滤掉空分类（0 个游戏的分类没意义）
            _collections = [c for c in raw if len(c['app_ids']) > 0]
            names = ["（入库该账号的游戏）"] + [
                f"{c['name']} ({len(c['app_ids'])})" for c in _collections]
            collection_combo['values'] = names
            if _collections:
                scan_info_label.config(
                    text=f"已加载 {len(_collections)} 个分类", fg="#333")

        # 分类变更时刷新列表
        def _on_collection_changed(*_):
            _populate_listbox(search_var.get())
        collection_combo.bind("<<ComboboxSelected>>", _on_collection_changed)

        def do_scan_library():
            scan_info_label.config(text="🔍 正在扫描本地已安装游戏...", fg="#333")
            win.update_idletasks()
            nonlocal _library_games
            _library_games = SteamAccountScanner.scan_library(
                self.current_account['steam_path'])
            if not _library_games:
                scan_info_label.config(
                    text="⚠️ 未扫描到本地游戏", fg="orange")
            _populate_listbox(search_var.get())

        _last_debug_info = {'text': ''}

        def _show_debug_info(info, parent=None):
            _last_debug_info['text'] = info
            dbg_win = tk.Toplevel(parent or win)
            dbg_win.title("🔍 调试信息")
            dbg_win.resizable(True, True)
            dbg_win.grab_set()
            dbg_win.focus_force()
            tk.Label(dbg_win, text="🔍 调试信息",
                     font=("", 12, "bold")).pack(pady=(10, 5))
            tk.Label(dbg_win, text="可选中文本复制，或点击下方按钮复制全部：",
                     font=("", 9), fg="#666").pack(pady=(0, 5))
            txt = tk.Text(dbg_win, font=("Consolas", 9), width=80, height=25,
                          wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            txt.insert("1.0", info)
            def _block_edit(event):
                if event.state & 0x4:
                    if event.keysym.lower() in ('a', 'c'):
                        return
                if event.keysym in ('Left', 'Right', 'Up', 'Down',
                                     'Home', 'End', 'Prior', 'Next',
                                     'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
                    return
                return "break"
            txt.bind("<Key>", _block_edit)
            def copy_debug():
                dbg_win.clipboard_clear()
                dbg_win.clipboard_append(info)
                messagebox.showinfo("✅", "已复制到剪贴板", parent=dbg_win)
            def close_debug():
                dbg_win.grab_release()
                dbg_win.destroy()
            btn_frame_d = tk.Frame(dbg_win)
            btn_frame_d.pack(pady=(0, 10))
            ttk.Button(btn_frame_d, text="📋 复制", command=copy_debug).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(btn_frame_d, text="关闭", command=close_debug).pack(
                side=tk.LEFT, padx=5)
            dbg_win.protocol("WM_DELETE_WINDOW", close_debug)

        def do_scan_online():
            skey = saved_steam_key
            sid = steam_id_var.get().strip()
            if not skey:
                messagebox.showwarning("提示",
                    "请在主界面「🔑 AI 配置」中设置 Steam Web API Key。\n"
                    "可从 https://steamcommunity.com/dev/apikey 免费获取。",
                    parent=win)
                return
            if not sid:
                messagebox.showwarning("提示", "请输入 Steam ID 或好友代码。",
                                        parent=win)
                return
            scan_info_label.config(text="🌐 正在通过 Steam API 获取...", fg="#333")
            win.update_idletasks()
            nonlocal _library_games
            debug_info = "[初始化] 开始在线扫描...\n"
            try:
                debug_info += f"[调用] scan_library_online(sid='{sid}', key='{skey[:6]}...')\n"
                scan_result = SteamAccountScanner.scan_library_online(sid, skey)
                debug_info += f"[返回] type = {type(scan_result)}\n"
                if isinstance(scan_result, tuple) and len(scan_result) == 2:
                    _library_games, scan_debug = scan_result
                    debug_info += scan_debug
                elif isinstance(scan_result, list):
                    _library_games = scan_result
                    debug_info += "[注意] 返回了 list 而非 tuple\n"
                else:
                    _library_games = []
                    debug_info += f"[异常] 返回值类型不符: {type(scan_result)}\n"
                _last_debug_info['text'] = debug_info
                if not _library_games:
                    scan_info_label.config(
                        text="⚠️ 未获取到游戏，检查 ID/Key 或资料可能未公开",
                        fg="orange")
                    _show_debug_info(debug_info, parent=win)
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                debug_info += f"\n[异常] {type(e).__name__}: {e}\n{tb_str}\n"
                _last_debug_info['text'] = debug_info
                err_display = str(e)
                if hasattr(e, 'code'):
                    err_display = f"HTTP {e.code}"
                    try:
                        err_display += f" — {e.read().decode('utf-8')[:200]}"
                    except Exception:
                        pass
                scan_info_label.config(text=f"❌ 失败: {err_display}", fg="red")
                _library_games = []
                _show_debug_info(debug_info, parent=win)
            _populate_listbox(search_var.get())

        def do_select_all():
            games_listbox.select_set(0, tk.END)
            _update_sel_count()

        def do_deselect_all():
            games_listbox.select_clear(0, tk.END)
            _update_sel_count()

        def on_search_changed(*_):
            _populate_listbox(search_var.get())
        search_var.trace_add("write", on_search_changed)

        def _on_ai_gen_filter(*_):
            """AI 筛选或确信度筛选变更时，刷新列表"""
            _populate_listbox(search_var.get())

        ai_gen_filter_combo.bind("<<ComboboxSelected>>", _on_ai_gen_filter)
        conf_gen_filter_combo.bind("<<ComboboxSelected>>", _on_ai_gen_filter)

        def _update_sel_count(event=None):
            n = len(games_listbox.curselection())
            sel_count_label.config(text=f"已选 {n} 款" if n else "")
        games_listbox.bind("<<ListboxSelect>>", _update_sel_count)

        def _on_double_click(event=None):
            """双击游戏条目，弹出笔记预览窗口"""
            sel = games_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx >= len(_filtered_indices):
                return
            entry = _filtered_indices[idx]
            if isinstance(entry, tuple) and entry[0] == 'col':
                app_id, game_name = entry[1], entry[2]
            else:
                g = _library_games[entry]
                app_id, game_name = g['app_id'], g['name']

            # 读取笔记
            data = self.manager.read_notes(app_id)
            notes_list = data.get("notes", [])
            if not notes_list:
                messagebox.showinfo("无笔记",
                    f"{game_name} (AppID {app_id}) 暂无笔记。",
                    parent=win)
                return

            # 弹出预览窗口
            preview = tk.Toplevel(win)
            preview.title(f"📝 笔记预览 — {game_name}")
            preview.transient(win)

            # 标题栏
            hdr = tk.Frame(preview, padx=10, pady=5)
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=f"🎮 {game_name}",
                     font=("", 12, "bold")).pack(side=tk.LEFT)
            tk.Label(hdr, text=f"AppID: {app_id}",
                     font=("", 9), fg="#666").pack(side=tk.RIGHT)

            # AI 状态摘要
            ai_info = _ai_notes_map_cache.get(app_id, {})
            if ai_info:
                models = ai_info.get('models', [])
                confs = ai_info.get('confidences', [])
                status_parts = []
                if models:
                    status_parts.append(f"模型: {', '.join(models)}")
                if confs:
                    conf_str = ', '.join(
                        f"{CONFIDENCE_EMOJI.get(c, '')} {c}" for c in confs)
                    status_parts.append(f"确信度: {conf_str}")
                if status_parts:
                    tk.Label(hdr, text="🤖 " + "  |  ".join(status_parts),
                             font=("", 9), fg="#1a73e8").pack(
                        side=tk.LEFT, padx=(15, 0))

            # 筛选出 AI 笔记和手动笔记
            ai_notes = [n for n in notes_list if is_ai_note(n)]
            manual_notes = [n for n in notes_list if not is_ai_note(n)]

            # 笔记内容区域
            txt_frame = tk.Frame(preview)
            txt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
            txt = tk.Text(txt_frame, font=("", 10), wrap=tk.WORD,
                          padx=10, pady=10)
            scrollbar = ttk.Scrollbar(txt_frame, orient=tk.VERTICAL,
                                       command=txt.yview)
            txt.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 优先显示 AI 笔记
            display_notes = ai_notes if ai_notes else manual_notes
            note_type_label = "AI 笔记" if ai_notes else "手动笔记（无 AI 笔记）"

            for i, note in enumerate(display_notes):
                content = note.get("content", note.get("title", ""))
                is_ai = is_ai_note(note)

                if i > 0:
                    txt.insert(tk.END, "\n" + "─" * 60 + "\n\n")

                tag_prefix = f"note_{i}"
                if is_ai:
                    conf = extract_ai_confidence_from_note(note)
                    emoji = CONFIDENCE_EMOJI.get(conf, "🤖")
                    txt.insert(tk.END, f"{emoji} AI 笔记",
                               f"{tag_prefix}_header")
                    if conf:
                        txt.insert(tk.END, f"（确信度: {conf}）",
                                   f"{tag_prefix}_header")
                    txt.insert(tk.END, "\n")
                    txt.tag_config(f"{tag_prefix}_header",
                                   foreground="#1a73e8",
                                   font=("", 10, "bold"))
                else:
                    txt.insert(tk.END, "📝 手动笔记\n",
                               f"{tag_prefix}_header")
                    txt.tag_config(f"{tag_prefix}_header",
                                   foreground="#333",
                                   font=("", 10, "bold"))

                # 显示内容（去掉 AI 前缀冗余信息，只保留正文）
                display_content = content
                if is_ai:
                    m = re.match(
                        r'🤖AI:\s*⚠️\s*以下内容由.+?确信程度[：:]\s*(?:很高|较高|中等|较低|很低)[。.]\s*',
                        display_content)
                    if m:
                        display_content = display_content[m.end():]
                txt.insert(tk.END, display_content.strip() + "\n")

            txt.config(state=tk.DISABLED)

            # 底部按钮
            btn_f = tk.Frame(preview, padx=10, pady=8)
            btn_f.pack(fill=tk.X)
            ttk.Button(btn_f, text="关闭",
                       command=preview.destroy).pack(side=tk.RIGHT)

            # 自适应窗口大小
            preview.update_idletasks()
            # 基于内容计算合适的高度，限制在合理范围内
            content_len = sum(len(n.get("content", "")) for n in display_notes)
            ideal_h = min(max(250, content_len // 2 + 150), 600)
            preview.geometry(f"700x{ideal_h}")
            # 居中
            preview.update_idletasks()
            pw, ph = preview.winfo_width(), preview.winfo_height()
            sx, sy = preview.winfo_screenwidth(), preview.winfo_screenheight()
            preview.geometry(f"+{(sx - pw) // 2}+{(sy - ph) // 2}")

        games_listbox.bind("<Double-1>", _on_double_click)

        # ═══════ 绑定按钮（所有函数已定义） ═══════

        ttk.Button(scan_btn_row1, text="🌐 在线扫描（完整库）",
                   command=do_scan_online).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row1, text="📂 本地扫描（仅已安装）",
                   command=do_scan_library).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row1, text="🔍 调试信息",
                   command=lambda: _show_debug_info(
                       _last_debug_info['text'] or "尚未执行在线扫描",
                       parent=win)).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row1, text="全选",
                   command=do_select_all).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row1, text="取消全选",
                   command=do_deselect_all).pack(side=tk.LEFT, padx=(0, 3))

        sel_count_label = tk.Label(scan_btn_row1, text="", font=("", 9), fg="#666")
        sel_count_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(collection_frame, text="🔄 刷新分类",
                   command=_load_collections).pack(side=tk.LEFT, padx=5)

        # ── 模式2: 手动输入 ──
        manual_container = tk.Frame(games_frame)

        tk.Label(manual_container,
                 text="每行一个: AppID 或 AppID:游戏名",
                 font=("", 9), fg="#555").pack(anchor=tk.W)
        games_text = tk.Text(manual_container, font=("Courier", 10), height=10,
                              wrap=tk.WORD)
        games_text.pack(fill=tk.BOTH, expand=True, pady=5)
        sel_id = self._get_selected_app_id()
        if sel_id:
            games_text.insert("1.0", f"{sel_id}\n")
        tk.Label(manual_container,
                 text="示例:  1245620:Elden Ring\n"
                      "       367520\n"
                      "       1086940:Baldur's Gate 3",
                 font=("Courier", 9), fg="#888", justify=tk.LEFT).pack(anchor=tk.W)

        def _switch_games_mode(mode):
            if mode == 1:
                manual_container.pack_forget()
                scan_container.pack(fill=tk.BOTH, expand=True)
            else:
                scan_container.pack_forget()
                manual_container.pack(fill=tk.BOTH, expand=True)

        # 模式切换按钮（在 _switch_games_mode 定义后创建）
        tk.Radiobutton(mode_frame, text="📚 从 Steam 库选择",
                       variable=games_mode_var, value=1, font=("", 9),
                       command=lambda: _switch_games_mode(1)).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="✏️ 手动输入 AppID",
                       variable=games_mode_var, value=2, font=("", 9),
                       command=lambda: _switch_games_mode(2)).pack(side=tk.LEFT, padx=(10, 0))

        # 首次自动加载分类（所有 widget 已创建）
        _load_collections()

        # 首次自动扫描库：优先在线扫描（如果配置了 Steam API Key 和 Steam ID），否则本地扫描
        if saved_steam_key and steam_id_var.get().strip():
            # 有 Steam API Key 且填写了 Steam ID，自动触发在线扫描
            win.after(100, do_scan_online)  # 延迟执行，确保窗口已完全显示
        else:
            # 否则触发本地扫描
            do_scan_library()

        # ═══════ 隐蔽调试：Ctrl+Shift+D 打开 AI 笔记识别调试面板 ═══════
        def _debug_ai_detection(event=None):
            """调试面板：显示所有笔记的 AI 识别结果"""
            dbg = "[AI 笔记识别调试]\n"
            dbg += f"notes_dir = {self.manager.notes_dir}\n\n"

            # 第一步：扫描所有笔记，找出 AI 笔记
            ai_map = self.manager.scan_ai_notes()
            dbg += f"=== 扫描结果：{len(ai_map)} 个游戏有 AI 笔记 ===\n\n"

            # 第二步：列出所有检测到的 AI 模型
            all_models = set()
            for info in ai_map.values():
                for m in info.get('models', []):
                    all_models.add(m)
            if all_models:
                dbg += f"检测到的 AI 模型: {', '.join(sorted(all_models))}\n\n"
            else:
                dbg += "未检测到任何 AI 模型名\n\n"

            # 第三步：列出 AI 笔记详情
            if ai_map:
                dbg += "── AI 笔记详情 ──\n"
                for app_id, info in sorted(ai_map.items()):
                    dbg += (f"  AppID {app_id}: "
                            f"{info['note_count']} 条 AI 笔记, "
                            f"模型={info['models']}\n")
                dbg += "\n"

            # 第四步：列出未被识别的笔记（供排查）
            dbg += "── 非 AI 笔记采样（前 10 个） ──\n"
            sample_count = 0
            for f in sorted(os.listdir(self.manager.notes_dir)):
                if sample_count >= 10:
                    break
                fp = os.path.join(self.manager.notes_dir, f)
                if not f.startswith("notes_") or not os.path.isfile(fp):
                    continue
                app_id = f.replace("notes_", "")
                if app_id in ai_map:
                    continue  # 跳过已检测为 AI 的
                try:
                    with open(fp, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    notes = data.get("notes", [])
                    if not notes:
                        continue
                    title = notes[0].get("title", "")
                    title_hex = ' '.join(f'U+{ord(c):04X}' for c in title[:15])
                    dbg += (f"  AppID {app_id}: title[:60]={title[:60]!r}\n"
                            f"    hex[:15]={title_hex}\n")
                    sample_count += 1
                except Exception:
                    continue
            _show_debug_info(dbg, parent=win)
        win.bind("<Control-Shift-D>", _debug_ai_detection)
        win.bind("<Control-Shift-d>", _debug_ai_detection)

        # ═══════════════ 下半部分：进度区 ═══════════════
        bottom_panel = tk.Frame(main_paned)
        main_paned.add(bottom_panel, minsize=140)

        progress_frame = tk.LabelFrame(bottom_panel, text="进度", font=("", 10),
                                        padx=8, pady=3)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        progress_top = tk.Frame(progress_frame)
        progress_top.pack(fill=tk.X)

        progress_var = tk.StringVar(value="等待开始...")
        tk.Label(progress_top, textvariable=progress_var, font=("", 9),
                 fg="#333").pack(side=tk.LEFT)

        progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=2)

        log_text = tk.Text(progress_frame, font=("Courier", 9), height=5,
                            state=tk.DISABLED, bg="#f8f8f8")
        log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        def log(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)

        # ── 底部按钮栏（含全局选项，两种模式下均可见）──
        btn_frame = tk.Frame(win, padx=10)
        btn_frame.pack(fill=tk.X, pady=(2, 6))

        # 第一行：全局选项
        options_row = tk.Frame(btn_frame)
        options_row.pack(fill=tk.X, pady=(0, 2))

        skip_existing_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_row, text="✅ 跳过已有 AI 笔记（取消则替换旧笔记）",
                        variable=skip_existing_var, font=("", 9)).pack(
            side=tk.LEFT, padx=(0, 15))

        web_search_var = tk.BooleanVar(value=False)
        ws_cb = tk.Checkbutton(
            options_row, text="🔍 联网搜索",
            variable=web_search_var, font=("", 9))
        ws_cb.pack(side=tk.LEFT)
        # 说明文字（不再锁定勾选框，仅提示）
        _cur_prov = _get_current_provider()
        _cur_url = current_token[0].get("api_url", "")
        if _cur_prov == 'anthropic' and not _cur_url:
            ws_tip = "（Anthropic 官方 API 额外收费 $10/1000次）"
        else:
            ws_tip = "（是否可用取决于 API 服务商）"
        tk.Label(options_row, text=ws_tip, font=("", 8),
                 fg="#888").pack(
            side=tk.LEFT, padx=(2, 0))

        # 第二行：按钮
        btn_row = tk.Frame(btn_frame)
        btn_row.pack(fill=tk.X)

        is_running = [False]
        is_paused = [False]
        is_stopped = [False]
        _worker_idle = [True]  # True when no worker thread is actively processing
        _remaining_queue = []  # 暂停时保存剩余队列

        def _save_queue(queue, token_idx, skip_existing, web_search):
            """保存未完成队列到配置"""
            self._config["ai_batch_queue"] = [[a, n] for a, n in queue]
            self._config["ai_batch_token_idx"] = token_idx
            self._config["ai_batch_skip_existing"] = skip_existing
            self._config["ai_batch_web_search"] = web_search
            self._save_config(self._config)

        def _clear_saved_queue():
            """清除已保存的队列"""
            for k in ("ai_batch_queue", "ai_batch_token_idx",
                      "ai_batch_skip_existing", "ai_batch_web_search"):
                self._config.pop(k, None)
            self._save_config(self._config)

        def _update_ctrl_buttons():
            """根据运行状态更新按钮可用性和文字"""
            if is_running[0] and not is_paused[0]:
                gen_btn.config(state=tk.DISABLED)
                pause_btn.config(state=tk.NORMAL, text="⏸️ 暂停")
                stop_btn.config(state=tk.NORMAL)
            elif is_running[0] and is_paused[0]:
                gen_btn.config(state=tk.DISABLED)
                pause_btn.config(state=tk.NORMAL, text="▶️ 继续")
                stop_btn.config(state=tk.NORMAL)
            else:
                gen_btn.config(state=tk.NORMAL)
                pause_btn.config(state=tk.DISABLED, text="⏸️ 暂停")
                stop_btn.config(state=tk.DISABLED)

        def do_pause():
            if not is_running[0]:
                return
            if is_paused[0]:
                # 继续 — 从保存的队列重新启动
                is_paused[0] = False
                resume_list = list(_remaining_queue)
                if not resume_list:
                    # 尝试从配置恢复
                    sq = self._config.get("ai_batch_queue", [])
                    resume_list = [(a, n) for a, n in sq]
                if resume_list:
                    is_running[0] = False  # reset so _start_generation can set it
                    _update_ctrl_buttons()
                    log("▶️ 继续生成...")
                    _start_generation(resume_list)
                else:
                    is_running[0] = False
                    _update_ctrl_buttons()
                    progress_var.set("队列为空")
            else:
                # 暂停
                is_paused[0] = True
                _update_ctrl_buttons()
                progress_var.set("⏸️ 正在暂停（等待当前游戏完成）...")
                log("⏸️ 正在暂停...")

        def do_stop():
            if not is_running[0]:
                return
            is_stopped[0] = True
            is_paused[0] = False
            _clear_saved_queue()
            progress_var.set("⏹️ 正在停止...")
            log("⏹️ 正在停止...（等待当前游戏完成）")

        def _start_generation(games_list):
            """启动生成线程（from do_generate or resume）"""
            is_running[0] = True
            is_paused[0] = False
            is_stopped[0] = False
            _worker_idle[0] = False
            _remaining_queue.clear()
            _remaining_queue.extend(games_list)
            _update_ctrl_buttons()
            progress_bar["maximum"] = len(games_list)
            progress_bar["value"] = 0
            total = len(games_list)

            api_key = _get_current_key()
            pkey = _get_current_provider()
            custom_url = _get_current_url()
            current_model = _get_current_model()

            def worker():
                generator = SteamAIGenerator(
                    api_key, current_model,
                    provider=pkey, api_url=custom_url)
                custom_prompt = prompt_text.get("1.0", tk.END).strip()
                success_count = 0
                fail_count = 0
                processed = 0

                while _remaining_queue:
                    # ── 检查停止 ──
                    if is_stopped[0]:
                        win.after(0, lambda s=success_count, f=fail_count: (
                            log(f"⏹️ 已停止。成功 {s} / 失败 {f}"),))
                        break

                    # ── 检查暂停：保存队列并退出线程 ──
                    if is_paused[0]:
                        _save_queue(
                            _remaining_queue, active_token_idx[0],
                            skip_existing_var.get(), web_search_var.get())
                        def _on_paused(s=success_count, f=fail_count, r=len(_remaining_queue)):
                            progress_var.set(f"⏸️ 已暂停 — 完成 {s}，失败 {f}，剩余 {r}")
                            log(f"⏸️ 已暂停，剩余 {r} 款待处理（已保存，可关闭窗口稍后继续）")
                            _populate_listbox(search_var.get())
                        win.after(0, _on_paused)
                        # 保持 is_running=True 以便"继续"按钮可用
                        _worker_idle[0] = True
                        return

                    aid, name = _remaining_queue[0]
                    idx = processed
                    win.after(0, lambda i=idx, a=aid, t=total: (
                        progress_var.set(f"正在处理 {i+1}/{t}: AppID {a}..."),
                        progress_bar.configure(value=i)
                    ))

                    if not name:
                        win.after(0, lambda a=aid: log(f"🔍 查询 AppID {a} 的游戏名..."))
                        try:
                            name = SteamAIGenerator.get_game_name_from_steam(aid)
                        except Exception:
                            name = f"AppID {aid}"

                    # 获取游戏详细信息作为 AI 参考资料
                    win.after(0, lambda a=aid, n=name: log(f"📋 获取 {n} 的详细信息..."))
                    game_context = ""
                    try:
                        details = SteamAIGenerator.get_game_details_from_steam(aid)
                        if details:
                            game_context = SteamAIGenerator.format_game_context(details)
                            if details.get("name") and name.startswith("AppID"):
                                name = details["name"]
                    except Exception:
                        pass

                    # 获取 Steam 玩家评测
                    win.after(0, lambda a=aid, n=name: log(
                        f"💬 获取 {n} 的玩家评测..."))
                    try:
                        reviews_data = (
                            SteamAIGenerator.get_game_reviews_from_steam(aid))
                        if reviews_data:
                            review_ctx = (
                                SteamAIGenerator.format_review_context(
                                    reviews_data))
                            if review_ctx:
                                game_context = (
                                    (game_context + "\n\n" + review_ctx)
                                    if game_context else review_ctx)
                    except Exception:
                        pass

                    # 是否启用联网搜索
                    _use_ws = web_search_var.get()

                    win.after(0, lambda a=aid, n=name, ws=_use_ws: log(
                        f"🤖 生成中: {n} (AppID {a})"
                        f"{' [🔍联网]' if ws else ''}..."))

                    try:
                        content, actual_model, confidence = generator.generate_note(
                            name, aid, extra_context=game_context,
                            system_prompt=custom_prompt,
                            use_web_search=_use_ws)
                        if content.strip():
                            flat_content = ' '.join(content.strip().splitlines())
                            flat_content = re.sub(
                                r'\[/?[a-z0-9*]+(?:=[^\]]*)?\]', '', flat_content)
                            flat_content = flat_content.strip()
                            ai_prefix = (f"🤖AI: ⚠️ 以下内容由 {actual_model} 生成，"
                                         f"该模型对以下内容的确信程度：{confidence}。")
                            flat_content = f"{ai_prefix} {flat_content}"

                            # 未跳过时自动替换旧 AI 笔记
                            if not skip_existing_var.get():
                                data = self.manager.read_notes(aid)
                                notes_list = data.get("notes", [])
                                had_old = False
                                for ni in reversed(range(len(notes_list))):
                                    if is_ai_note(notes_list[ni]):
                                        notes_list.pop(ni)
                                        had_old = True
                                if had_old:
                                    data["notes"] = notes_list
                                    self.manager.write_notes(aid, data)

                            self.manager.create_note(aid, flat_content, flat_content)
                            win.after(0, lambda a=aid, n=name, c=confidence: log(
                                f"✅ 完成: {n} (AppID {a}) [确信: {c}]"))
                            success_count += 1
                        else:
                            win.after(0, lambda a=aid: log(
                                f"⚠️ AppID {a}: API 返回空内容"))
                            fail_count += 1
                    except urllib.error.HTTPError as e:
                        error_body = ""
                        try:
                            error_body = e.read().decode("utf-8")
                        except Exception:
                            pass
                        # 构建完整调试信息
                        debug_info = getattr(generator, '_last_debug_info', '(无调试信息)')
                        debug_info += (
                            f"\n--- 错误响应 ---\n"
                            f"HTTP 状态码: {e.code}\n"
                            f"错误原因: {e.reason}\n"
                            f"响应头: {dict(e.headers) if e.headers else '(无)'}\n"
                            f"响应体: {error_body[:500]}\n"
                        )
                        win.after(0, lambda a=aid, err=e, body=error_body, dbg=debug_info:
                                  log(f"❌ AppID {a}: HTTP {err.code} — {body[:200]}\n"
                                      f"--- 调试信息 ---\n{dbg}"))
                        fail_count += 1
                        if e.code == 401:
                            # 认证失败 — 给出具体排查建议
                            hint = "💡 401 认证失败排查：\n"
                            if custom_url:
                                hint += ("  · 当前使用第三方代理/中转 URL\n"
                                         "  · 请确认 API Key 对该代理有效（未过期、额度充足）\n"
                                         "  · 检查代理是否支持当前模型: "
                                         f"{current_model}\n")
                            else:
                                hint += ("  · 请检查 API Key 是否有效（未过期、未撤销）\n"
                                         "  · 确认 Key 有访问该模型的权限\n")
                            win.after(0, lambda h=hint: log(h))
                            break  # 认证失败无需重试后续游戏
                        elif e.code == 429:
                            win.after(0, lambda: log("⏳ 触发限速，等待 60 秒..."))
                            time.sleep(60)
                            # 不弹出队列头，重试当前游戏
                            continue
                    except urllib.error.URLError as e:
                        debug_info = getattr(generator, '_last_debug_info', '(无调试信息)')
                        win.after(0, lambda a=aid, err=e, dbg=debug_info:
                                  log(f"❌ AppID {a}: 连接错误 — {err}\n"
                                      f"--- 调试信息 ---\n{dbg}"))
                        fail_count += 1
                    except Exception as e:
                        win.after(0, lambda a=aid, err=e: log(f"❌ AppID {a}: {err}"))
                        fail_count += 1

                    # 成功或失败都弹出队头
                    _remaining_queue.pop(0)
                    processed += 1

                    if _remaining_queue and not is_stopped[0]:
                        time.sleep(2)

                def finish():
                    _clear_saved_queue()
                    progress_bar["value"] = progress_bar["maximum"]
                    if is_stopped[0]:
                        progress_var.set(
                            f"⏹️ 已停止 — 成功 {success_count} / 失败 {fail_count}")
                    else:
                        progress_var.set(
                            f"完成！成功 {success_count} / 失败 {fail_count}")
                    log(f"\n{'='*40}")
                    log(f"✅ 成功: {success_count}  ❌ 失败: {fail_count}")
                    is_running[0] = False
                    is_stopped[0] = False
                    _worker_idle[0] = True
                    _update_ctrl_buttons()
                    _populate_listbox(search_var.get())
                    self._refresh_games_list()

                # 只有非暂停退出时才 finish
                if not is_paused[0]:
                    win.after(0, finish)

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()

        def do_generate():
            if is_running[0]:
                return

            api_key = _get_current_key()
            if not api_key:
                messagebox.showwarning("提示",
                    "当前令牌未配置 API Key，请在「🔑 AI 配置」中设置。", parent=win)
                return

            games_list = []
            if games_mode_var.get() == 1:
                selected = games_listbox.curselection()
                if not selected:
                    messagebox.showwarning("提示",
                        "请先扫描 Steam 库或选择分类，然后选择至少一个游戏。", parent=win)
                    return
                for sel_idx in selected:
                    if sel_idx < len(_filtered_indices):
                        entry = _filtered_indices[sel_idx]
                        if isinstance(entry, tuple) and entry[0] == 'col':
                            games_list.append((entry[1], entry[2]))
                        else:
                            real_idx = entry
                            g = _library_games[real_idx]
                            games_list.append((g['app_id'], g['name']))
            else:
                raw_lines = games_text.get("1.0", tk.END).strip().split('\n')
                for line in raw_lines:
                    line = line.strip()
                    if not line:
                        continue
                    if ':' in line:
                        parts = line.split(':', 1)
                        aid = parts[0].strip()
                        name = parts[1].strip()
                    else:
                        aid = line
                        name = ""
                    if aid:
                        games_list.append((aid, name))

            if not games_list:
                messagebox.showwarning("提示", "请至少选择一个游戏。", parent=win)
                return

            if skip_existing_var.get():
                filtered = []
                for aid, name in games_list:
                    existing = self.manager.read_notes(aid).get("notes", [])
                    has_ai_note = any(is_ai_note(n) for n in existing)
                    if has_ai_note:
                        log(f"⏭️ 跳过 AppID {aid} (已有 AI 笔记)")
                    else:
                        filtered.append((aid, name))
                games_list = filtered

            if not games_list:
                messagebox.showinfo("提示", "所有游戏都已有笔记。", parent=win)
                return

            _start_generation(games_list)

        gen_btn = ttk.Button(btn_row, text="🚀 开始生成", command=do_generate)
        gen_btn.pack(side=tk.LEFT, padx=3)
        pause_btn = ttk.Button(btn_row, text="⏸️ 暂停", command=do_pause,
                               state=tk.DISABLED)
        pause_btn.pack(side=tk.LEFT, padx=3)
        stop_btn = ttk.Button(btn_row, text="⏹️ 停止", command=do_stop,
                              state=tk.DISABLED)
        stop_btn.pack(side=tk.LEFT, padx=3)

        # ── 云同步按钮 ──
        def _ai_cloud_upload_selected():
            """上传 AI 批量生成界面中选中游戏的笔记"""
            if not self.cloud_uploader or not self.cloud_uploader.initialized:
                messagebox.showwarning("提示", "请先点击上方「☁️ 连接 Steam Cloud」按钮。", parent=win)
                return
            selected = games_listbox.curselection()
            if not selected:
                messagebox.showinfo("提示", "请先选择要上传的游戏。", parent=win)
                return
            ok = fail = 0
            for sel_idx in selected:
                if sel_idx < len(_filtered_indices):
                    entry = _filtered_indices[sel_idx]
                    if isinstance(entry, tuple) and entry[0] == 'col':
                        aid = entry[1]
                    else:
                        aid = _library_games[entry]['app_id']
                    if self.manager.is_dirty(aid):
                        if self.manager.cloud_upload(aid):
                            ok += 1
                        else:
                            fail += 1
            _populate_listbox(search_var.get())
            self._refresh_games_list()
            self._save_uploaded_hashes()
            if ok + fail == 0:
                messagebox.showinfo("提示", "选中的游戏没有需要上传的改动。", parent=win)
            elif fail == 0:
                messagebox.showinfo("✅ 成功", f"已上传 {ok} 个游戏。", parent=win)
            else:
                messagebox.showwarning("⚠️", f"成功 {ok}，失败 {fail}。", parent=win)

        def _ai_cloud_upload_all():
            """上传所有有改动的笔记"""
            if not self.cloud_uploader or not self.cloud_uploader.initialized:
                messagebox.showwarning("提示", "请先点击上方「☁️ 连接 Steam Cloud」按钮。", parent=win)
                return
            n = self.manager.dirty_count()
            if n == 0:
                messagebox.showinfo("提示", "没有需要上传的改动。", parent=win)
                return
            ok, fail = self.manager.cloud_upload_all_dirty()
            _populate_listbox(search_var.get())
            self._refresh_games_list()
            self._save_uploaded_hashes()
            if fail == 0:
                messagebox.showinfo("✅ 成功",
                                    f"已上传 {ok} 个游戏的笔记到 Steam Cloud。\n\n"
                                    "💡 这些改动仍需等待 Steam 客户端自动同步到云端。",
                                    parent=win)
            else:
                messagebox.showwarning("⚠️ 部分失败",
                                        f"成功 {ok} 个，失败 {fail} 个。", parent=win)

        ttk.Button(btn_row, text="☁️上传选中",
                   command=_ai_cloud_upload_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="☁️全部上传",
                   command=_ai_cloud_upload_all).pack(side=tk.LEFT, padx=5)

        def _smart_close():
            """关闭窗口前检查运行状态和未上传笔记"""
            # 如果正在生成且未暂停，先暂停
            if is_running[0] and not is_paused[0]:
                is_paused[0] = True
                _worker_idle[0] = False
                _update_ctrl_buttons()
                progress_var.set("⏸️ 正在暂停（等待当前游戏完成后关闭）...")
                log("⏸️ 正在暂停以便关闭...")
                def _wait_and_close():
                    if not _worker_idle[0]:
                        win.after(200, _wait_and_close)
                        return
                    _do_close_checks()
                win.after(200, _wait_and_close)
                return
            _do_close_checks()

        def _do_close_checks():
            """执行关闭前的脏数据检查"""
            dirty_n = self.manager.dirty_count()
            if dirty_n > 0:
                ans = messagebox.askyesnocancel(
                    "☁️ 未上传的笔记",
                    f"有 {dirty_n} 个游戏的笔记尚未上传到 Steam Cloud。\n\n"
                    "是否在关闭前一键上传？\n\n"
                    "「是」→ 上传后关闭\n"
                    "「否」→ 不上传，直接关闭（本地文件已保存）\n"
                    "「取消」→ 返回",
                    parent=win)
                if ans is None:
                    # 取消 → 不关闭
                    return
                if ans:
                    # 是 → 尝试上传
                    if not (self.cloud_uploader and self.cloud_uploader.initialized):
                        # 自动尝试连接
                        progress_var.set("☁️ 正在自动连接 Steam Cloud...")
                        win.update_idletasks()
                        uploader = SteamCloudUploader()
                        steam_path = self.current_account.get('steam_path', '')
                        ok, msg = uploader.auto_init(steam_path)
                        if ok:
                            # 检查账号匹配
                            logged_in = uploader.logged_in_friend_code
                            selected = self.current_account.get(
                                'friend_code', '')
                            if logged_in and logged_in != selected:
                                selected_name = self.current_account.get(
                                    'persona_name', selected)
                                uploader.shutdown()
                                messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                                    f"Steam 登录账号 (ID: {logged_in}) ≠ "
                                    f"程序选择的「{selected_name}」\n\n"
                                    f"请先在 Steam 客户端切换到正确账号后手动连接上传。",
                                    parent=win)
                                return  # 返回窗口
                            self.cloud_uploader = uploader
                            self.manager.cloud_uploader = uploader
                            _update_ai_cloud_status()
                            try:
                                self._update_cloud_status_display()
                            except Exception:
                                pass
                        else:
                            messagebox.showerror("❌ 连接失败",
                                f"无法自动连接 Steam Cloud:\n{msg}\n\n"
                                "请手动连接后再上传，或选择直接关闭。",
                                parent=win)
                            return  # 返回窗口
                    # 上传
                    ok_n, fail_n = self.manager.cloud_upload_all_dirty()
                    self._save_uploaded_hashes()
                    if fail_n > 0:
                        messagebox.showwarning("⚠️ 部分上传失败",
                            f"成功 {ok_n}，失败 {fail_n}。\n失败的笔记仍保留在本地。",
                            parent=win)
                    else:
                        log(f"☁️ 已上传 {ok_n} 个游戏的笔记")
            # 关闭
            try:
                self._refresh_games_list()
                self._update_cloud_status_display()
            except Exception:
                pass
            win.grab_release()
            win.destroy()

        ttk.Button(btn_row, text="关闭", command=_smart_close).pack(
            side=tk.RIGHT, padx=5)

        win.protocol("WM_DELETE_WINDOW", _smart_close)

        # 窗口打开时自动扫描已由上方条件逻辑处理

        # ── 检查是否有上次暂停保存的队列 ──
        saved_queue = self._config.get("ai_batch_queue", [])
        if saved_queue:
            n_saved = len(saved_queue)
            saved_tidx = self._config.get("ai_batch_token_idx", 0)
            saved_skip = self._config.get("ai_batch_skip_existing", True)
            saved_ws = self._config.get("ai_batch_web_search", False)
            ans = messagebox.askyesno(
                "▶️ 继续上次任务",
                f"检测到上次暂停的生成队列，还剩 {n_saved} 款游戏待处理。\n\n"
                "是否从断点继续？\n\n"
                "「是」→ 恢复令牌和选项，继续生成\n"
                "「否」→ 放弃队列，重新开始",
                parent=win)
            if ans:
                # 恢复令牌和选项
                if saved_tidx < len(all_tokens):
                    active_token_idx[0] = saved_tidx
                    current_token[0] = all_tokens[saved_tidx]
                    _token_select_var.set(
                        token_names[saved_tidx] if saved_tidx < len(token_names) else "")
                    _update_token_detail()
                skip_existing_var.set(saved_skip)
                web_search_var.set(saved_ws)
                # 恢复队列并启动
                resume_list = [(a, n) for a, n in saved_queue]
                log(f"▶️ 恢复上次暂停的队列：{n_saved} 款游戏")
                win.after(300, lambda: _start_generation(resume_list))
            else:
                _clear_saved_queue()

        self._center_window(win)

    # ────────────────────── 导入 ──────────────────────

    def _ui_import(self):
        """导入笔记窗口 — 支持单条导入和批量导入"""
        path = filedialog.askopenfilename(
            title="选择要导入的文件",
            filetypes=[("文本文件", "*.txt"), ("Markdown", "*.md"), ("所有文件", "*.*")]
        )
        if not path:
            return

        # 检测文件是否为批量导出格式
        is_batch_format = False
        try:
            with open(path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line == SteamNotesManager.BATCH_EXPORT_HEADER:
                    is_batch_format = True
        except:
            pass

        win = tk.Toplevel(self.root)
        win.title("📥 导入笔记")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="📥 导入笔记", font=("", 13, "bold")).pack(pady=(15, 5))

        fname = os.path.splitext(os.path.basename(path))[0]
        tk.Label(win, text=f"文件: {os.path.basename(path)}", font=("", 9),
                 fg="#555").pack(pady=(0, 10))

        # 导入模式
        mode_var = tk.IntVar(value=2 if is_batch_format else 1)

        mode_frame = tk.LabelFrame(win, text="导入模式", font=("", 10), padx=15, pady=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=10)

        # 模式一: 单条导入
        mode1_frame = tk.Frame(mode_frame)
        mode1_frame.pack(fill=tk.X, anchor=tk.W)
        tk.Radiobutton(mode1_frame, text="单条导入：整个文件作为一条笔记导入",
                       variable=mode_var, value=1, font=("", 10)).pack(anchor=tk.W)

        # 模式一的 AppID 和标题
        single_form = tk.Frame(mode_frame, padx=25)
        single_form.pack(fill=tk.X, pady=(0, 5))

        tk.Label(single_form, text="目标 AppID:", font=("", 9)).grid(
            row=0, column=0, sticky=tk.W, pady=2)
        single_app_id_var = tk.StringVar()
        sel_id = self._get_selected_app_id()
        if sel_id:
            single_app_id_var.set(sel_id)
        tk.Entry(single_form, textvariable=single_app_id_var, width=15,
                 font=("", 9)).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        tk.Label(single_form, text="笔记标题:", font=("", 9)).grid(
            row=1, column=0, sticky=tk.W, pady=2)
        single_title_var = tk.StringVar(value=fname)
        tk.Entry(single_form, textvariable=single_title_var, width=30,
                 font=("", 9)).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        ttk.Separator(mode_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

        # 模式二: 批量导入
        mode2_text = "批量导入：按导出格式解析，自动分配到各 AppID"
        if is_batch_format:
            mode2_text += "  ✅ 已检测到批量导出格式"
        tk.Radiobutton(mode_frame, text=mode2_text,
                       variable=mode_var, value=2, font=("", 10)).pack(anchor=tk.W)

        tk.Label(mode_frame, text="（无需指定 AppID，文件中已包含 AppID 信息）",
                 font=("", 9), fg="#888").pack(anchor=tk.W, padx=25)

        # 提示: 冲突检测模式
        conflict_mode_frame = tk.LabelFrame(win, text="冲突检测模式", font=("", 10),
                                              padx=10, pady=5)
        conflict_mode_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        conflict_mode_var = tk.IntVar(value=1)
        tk.Radiobutton(conflict_mode_frame,
                       text="🤖 AI 笔记冲突检测",
                       variable=conflict_mode_var, value=1, font=("", 10)).pack(anchor=tk.W)
        tk.Label(conflict_mode_frame,
                 text="检测导入的 AI 笔记与已有 AI 笔记的冲突（替换/追加/跳过）",
                 font=("", 9), fg="#888").pack(anchor=tk.W, padx=25, pady=(0, 3))
        tk.Radiobutton(conflict_mode_frame,
                       text="📝 字面重复检测",
                       variable=conflict_mode_var, value=2, font=("", 10)).pack(anchor=tk.W)
        tk.Label(conflict_mode_frame,
                 text="检测导入笔记的标题+内容是否与已有笔记完全重复，跳过重复项",
                 font=("", 9), fg="#888").pack(anchor=tk.W, padx=25, pady=(0, 3))

        def do_import():
            try:
                if mode_var.get() == 2:
                    # 批量导入 — 先解析，再按模式检测冲突
                    parsed = SteamNotesManager.parse_batch_file(path)
                    if not parsed:
                        messagebox.showwarning("提示",
                            "未在文件中识别到有效笔记。\n"
                            "如果这不是批量导出格式文件，请切换到单条导入。",
                            parent=win)
                        return

                    if conflict_mode_var.get() == 1:
                        # 模式 1: AI 笔记冲突检测（原有逻辑）
                        conflicts = {}
                        for aid, entries in parsed.items():
                            incoming_ai = [e for e in entries
                                           if is_ai_note({"title": e["title"],
                                                           "content": e["content"]})]
                            if not incoming_ai:
                                continue
                            existing_data = self.manager.read_notes(aid)
                            existing_ai = [n for n in existing_data.get("notes", [])
                                           if is_ai_note(n)]
                            if existing_ai:
                                conflicts[aid] = {
                                    "existing_ai": existing_ai,
                                    "incoming_ai": incoming_ai
                                }

                        if not conflicts:
                            results = self.manager.apply_batch_import(parsed)
                            self._show_import_result(win, results)
                            return

                        self._ui_import_conflict(win, parsed, conflicts)
                    else:
                        # 模式 2: 字面重复检测
                        skipped = {}  # {app_id: skipped_count}
                        filtered_parsed = {}
                        for aid, entries in parsed.items():
                            existing_data = self.manager.read_notes(aid)
                            existing_notes = existing_data.get("notes", [])
                            existing_set = set()
                            for n in existing_notes:
                                existing_set.add(
                                    (n.get("title", ""), n.get("content", "")))
                            kept = []
                            skip_count = 0
                            for e in entries:
                                if (e["title"], e["content"]) in existing_set:
                                    skip_count += 1
                                else:
                                    kept.append(e)
                            if kept:
                                filtered_parsed[aid] = kept
                            if skip_count > 0:
                                skipped[aid] = skip_count

                        total_skipped = sum(skipped.values())
                        if total_skipped > 0 and not filtered_parsed:
                            messagebox.showinfo("ℹ️ 全部重复",
                                f"导入文件中的所有 {total_skipped} 条笔记"
                                f"与已有笔记完全重复，\n已全部跳过。",
                                parent=win)
                            return
                        if total_skipped > 0:
                            # 有部分重复 — 告知用户
                            proceed = messagebox.askyesno("ℹ️ 检测到重复",
                                f"发现 {total_skipped} 条笔记与已有笔记完全重复，"
                                f"已自动跳过。\n\n"
                                f"剩余 {sum(len(v) for v in filtered_parsed.values())} "
                                f"条不重复笔记将被导入。\n\n继续导入？",
                                parent=win)
                            if not proceed:
                                return

                        if filtered_parsed:
                            results = self.manager.apply_batch_import(filtered_parsed)
                            self._show_import_result(win, results)
                        else:
                            results = self.manager.apply_batch_import(parsed)
                            self._show_import_result(win, results)
                else:
                    # 单条导入
                    aid = single_app_id_var.get().strip()
                    if not aid:
                        messagebox.showwarning("提示", "请输入目标游戏 AppID。",
                                               parent=win)
                        return
                    title = single_title_var.get().strip() or fname
                    # 单条导入也支持字面重复检测
                    if conflict_mode_var.get() == 2:
                        existing_data = self.manager.read_notes(aid)
                        existing_notes = existing_data.get("notes", [])
                        with open(path, "r", encoding="utf-8") as f_content:
                            file_content = f_content.read()
                        for n in existing_notes:
                            if n.get("title", "") == title and n.get("content", "") == file_content:
                                messagebox.showinfo("ℹ️ 重复",
                                    f"该笔记与 AppID {aid} 中已有笔记完全重复，已跳过导入。",
                                    parent=win)
                                return
                    self.manager.import_single_note(aid, title, path)
                    messagebox.showinfo("✅ 成功",
                                        f"已导入为 AppID {aid} 的笔记:\n「{title}」",
                                        parent=win)
                    self._refresh_games_list()
                    win.destroy()
            except Exception as e:
                messagebox.showerror("❌ 错误", f"导入失败:\n{e}", parent=win)

        ttk.Button(win, text="✅ 确认导入", command=do_import).pack(pady=(5, 15))
        self._center_window(win)

    def _show_import_result(self, parent_win, results: dict):
        """显示导入结果的可滚动窗口"""
        if not results:
            messagebox.showinfo("提示", "没有笔记被导入。", parent=parent_win)
            return
        total = sum(results.values())
        result_win = tk.Toplevel(parent_win)
        result_win.title("✅ 导入成功")
        result_win.resizable(False, True)
        result_win.grab_set()
        tk.Label(result_win,
                 text=f"✅ 已导入 {total} 条笔记到 {len(results)} 个游戏",
                 font=("", 12, "bold"), fg="#2a7f2a").pack(pady=(15, 5))
        txt_frame = tk.Frame(result_win)
        txt_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        scrollbar = tk.Scrollbar(txt_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text = tk.Text(txt_frame, width=50,
                              height=min(len(results) + 1, 20),
                              font=("", 10), wrap=tk.WORD,
                              yscrollcommand=scrollbar.set)
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=result_text.yview)
        for aid, cnt in results.items():
            game_name = self._get_game_name(aid)
            if game_name.startswith("AppID "):
                result_text.insert(tk.END, f"  AppID {aid}: {cnt} 条\n")
            else:
                result_text.insert(tk.END, f"  {game_name} ({aid}): {cnt} 条\n")
        result_text.config(state=tk.DISABLED)

        def _close_result():
            result_win.grab_release()
            result_win.destroy()
            self._refresh_games_list()
            parent_win.destroy()
        ttk.Button(result_win, text="✅ 确认",
                   command=_close_result).pack(pady=(5, 15))
        result_win.protocol("WM_DELETE_WINDOW", _close_result)
        self._center_window(result_win)

    def _ui_import_conflict(self, import_win, parsed: dict, conflicts: dict):
        """AI 笔记冲突处理主窗口
        parsed: 完整的解析数据 {app_id: [{title, content}, ...]}
        conflicts: {app_id: {existing_ai: [note_dict], incoming_ai: [entry_dict]}}
        """
        cwin = tk.Toplevel(import_win)
        cwin.title("⚠️ AI 笔记冲突处理")
        cwin.resizable(True, True)
        cwin.grab_set()
        cwin.transient(import_win)

        # ── 头部 ──
        tk.Label(cwin, text="⚠️ 检测到 AI 笔记冲突",
                 font=("", 14, "bold"), fg="#c0392b").pack(pady=(15, 5))

        n_conflict = len(conflicts)
        n_total = len(parsed)
        n_safe = n_total - n_conflict
        tk.Label(cwin,
                 text=f"共 {n_total} 个游戏待导入，其中 {n_conflict} 个存在 AI 笔记冲突"
                      f"（{n_safe} 个无冲突将正常导入）",
                 font=("", 10), fg="#666").pack(pady=(0, 10))

        # ── 冲突列表 ──
        list_frame = tk.LabelFrame(cwin, text=f"冲突游戏列表 ({n_conflict})",
                                   font=("", 10), padx=10, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        list_inner = tk.Frame(list_frame)
        list_inner.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_inner)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        conflict_text = tk.Text(list_inner, width=60,
                                height=min(n_conflict + 1, 12),
                                font=("", 10), wrap=tk.WORD,
                                yscrollcommand=scrollbar.set)
        conflict_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=conflict_text.yview)

        for aid, info in conflicts.items():
            game_name = self._get_game_name(aid)
            n_exist = len(info["existing_ai"])
            n_incoming = len(info["incoming_ai"])
            if game_name.startswith("AppID "):
                conflict_text.insert(tk.END,
                    f"  AppID {aid}: 已有 {n_exist} 条 AI ↔ 导入 {n_incoming} 条 AI\n")
            else:
                conflict_text.insert(tk.END,
                    f"  {game_name} ({aid}): "
                    f"已有 {n_exist} 条 AI ↔ 导入 {n_incoming} 条 AI\n")
        conflict_text.config(state=tk.DISABLED)

        # ── 操作说明 ──
        tk.Label(cwin,
                 text="请选择冲突的处理方式：",
                 font=("", 10, "bold")).pack(pady=(10, 5))

        desc_frame = tk.Frame(cwin, padx=20)
        desc_frame.pack(fill=tk.X)
        for icon, label, desc in [
            ("🔄", "全部替换", "删除已有 AI 笔记，写入导入文件中的 AI 笔记"),
            ("➕", "全部追加", "保留已有 AI 笔记，导入的 AI 笔记追加在后面"),
            ("⏭️", "跳过 AI",  "不导入文件中的 AI 笔记（仅导入非 AI 笔记）"),
            ("🔍", "逐一处理", "逐个游戏对比新旧 AI 笔记，分别选择替换/追加/跳过"),
        ]:
            tk.Label(desc_frame, text=f"  {icon} {label} — {desc}",
                     font=("", 9), fg="#555", anchor=tk.W).pack(anchor=tk.W)

        # ── 按钮 ──
        btn_frame = tk.Frame(cwin)
        btn_frame.pack(pady=(15, 15))

        def _do_apply(policy):
            results = self.manager.apply_batch_import(parsed, ai_policy=policy)
            cwin.grab_release()
            cwin.destroy()
            self._show_import_result(import_win, results)

        def _do_cancel():
            cwin.grab_release()
            cwin.destroy()

        def _do_one_by_one():
            cwin.grab_release()
            cwin.destroy()
            self._ui_import_one_by_one(import_win, parsed, conflicts)

        ttk.Button(btn_frame, text="🔄 全部替换",
                   command=lambda: _do_apply("replace")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="➕ 全部追加",
                   command=lambda: _do_apply("append")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="⏭️ 跳过 AI",
                   command=lambda: _do_apply("skip_ai")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="🔍 逐一处理",
                   command=_do_one_by_one).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="取消导入",
                   command=_do_cancel).pack(side=tk.LEFT, padx=(15, 4))

        cwin.protocol("WM_DELETE_WINDOW", _do_cancel)
        self._center_window(cwin)

    def _ui_import_one_by_one(self, import_win, parsed: dict, conflicts: dict):
        """逐一处理每个冲突游戏的 AI 笔记，左右对比"""
        conflict_list = list(conflicts.items())
        per_app_policy = {}  # {app_id: "replace"/"append"/"skip_ai"}
        current_idx = [0]

        owin = tk.Toplevel(import_win)
        owin.title("🔍 逐一处理 AI 笔记冲突")
        owin.resizable(True, True)
        owin.grab_set()
        owin.transient(import_win)
        owin.geometry("900x560")

        # ── 顶部进度 ──
        progress_label = tk.Label(owin, font=("", 11, "bold"))
        progress_label.pack(pady=(10, 0))

        game_label = tk.Label(owin, font=("", 12, "bold"), fg="#1a73e8")
        game_label.pack(pady=(2, 8))

        # ── 左右对比面板 ──
        compare_frame = tk.Frame(owin)
        compare_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        compare_frame.columnconfigure(0, weight=1)
        compare_frame.columnconfigure(1, weight=0)
        compare_frame.columnconfigure(2, weight=1)
        compare_frame.rowconfigure(1, weight=1)

        tk.Label(compare_frame, text="📋 已有 AI 笔记（本地）",
                 font=("", 10, "bold"), fg="#c0392b").grid(
                     row=0, column=0, sticky=tk.W, padx=5)
        tk.Label(compare_frame, text="📥 导入 AI 笔记（文件）",
                 font=("", 10, "bold"), fg="#27ae60").grid(
                     row=0, column=2, sticky=tk.W, padx=5)

        # 左侧
        left_frame = tk.Frame(compare_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(5, 2))
        left_scroll = tk.Scrollbar(left_frame)
        left_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        left_text = tk.Text(left_frame, font=("", 9), wrap=tk.WORD,
                            bg="#fff5f5", yscrollcommand=left_scroll.set)
        left_text.pack(fill=tk.BOTH, expand=True)
        left_scroll.config(command=left_text.yview)

        # 分隔
        tk.Frame(compare_frame, width=2, bg="#ccc").grid(
            row=1, column=1, sticky="ns", padx=2)

        # 右侧
        right_frame = tk.Frame(compare_frame)
        right_frame.grid(row=1, column=2, sticky="nsew", padx=(2, 5))
        right_scroll = tk.Scrollbar(right_frame)
        right_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        right_text = tk.Text(right_frame, font=("", 9), wrap=tk.WORD,
                             bg="#f5fff5", yscrollcommand=right_scroll.set)
        right_text.pack(fill=tk.BOTH, expand=True)
        right_scroll.config(command=right_text.yview)

        # ── 底部按钮 ──
        btn_frame = tk.Frame(owin)
        btn_frame.pack(pady=(8, 12))

        def _strip_bbcode(text):
            """简单去除 BBCode 标签以便阅读"""
            return re.sub(r'\[/?[a-z0-9*]+(?:=[^\]]*)?\]', '', text)

        def _show_current():
            idx = current_idx[0]
            aid, info = conflict_list[idx]
            game_name = self._get_game_name(aid)
            progress_label.config(text=f"冲突 {idx + 1} / {len(conflict_list)}")
            game_label.config(text=f"🎮 {game_name} (AppID: {aid})")

            # 左侧：已有 AI 笔记
            left_text.config(state=tk.NORMAL)
            left_text.delete("1.0", tk.END)
            for i, note in enumerate(info["existing_ai"]):
                if i > 0:
                    left_text.insert(tk.END, "\n" + "─" * 40 + "\n\n")
                title = note.get("title", "(无标题)")
                content = note.get("content", "")
                left_text.insert(tk.END, f"【{title}】\n\n")
                left_text.insert(tk.END, _strip_bbcode(content) + "\n")
            left_text.config(state=tk.DISABLED)

            # 右侧：导入 AI 笔记
            right_text.config(state=tk.NORMAL)
            right_text.delete("1.0", tk.END)
            for i, entry in enumerate(info["incoming_ai"]):
                if i > 0:
                    right_text.insert(tk.END, "\n" + "─" * 40 + "\n\n")
                title = entry.get("title", "(无标题)")
                content = entry.get("content", "")
                right_text.insert(tk.END, f"【{title}】\n\n")
                right_text.insert(tk.END, _strip_bbcode(content) + "\n")
            right_text.config(state=tk.DISABLED)

        def _choose(policy):
            aid = conflict_list[current_idx[0]][0]
            per_app_policy[aid] = policy
            current_idx[0] += 1
            if current_idx[0] >= len(conflict_list):
                _finish()
            else:
                _show_current()

        def _finish():
            owin.grab_release()
            owin.destroy()
            results = self.manager.apply_batch_import(
                parsed, ai_policy="append",
                per_app_policy=per_app_policy)
            self._show_import_result(import_win, results)

        def _cancel_remaining():
            # 将剩余冲突全部设为 skip_ai
            for j in range(current_idx[0], len(conflict_list)):
                aid = conflict_list[j][0]
                per_app_policy[aid] = "skip_ai"
            _finish()

        def _do_close():
            owin.grab_release()
            owin.destroy()

        ttk.Button(btn_frame, text="🔄 替换",
                   command=lambda: _choose("replace")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="➕ 追加",
                   command=lambda: _choose("append")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="⏭️ 跳过",
                   command=lambda: _choose("skip_ai")).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="⏩ 跳过剩余全部",
                   command=_cancel_remaining).pack(side=tk.LEFT, padx=(15, 4))
        ttk.Button(btn_frame, text="取消导入",
                   command=_do_close).pack(side=tk.LEFT, padx=(15, 4))

        owin.protocol("WM_DELETE_WINDOW", _do_close)
        _show_current()
        self._center_window(owin)

    def _ui_show_about(self):
        """弹出关于作者窗口"""
        about = tk.Toplevel(self.root)
        about.title("关于")
        about.resizable(False, False)

        tk.Label(about, text="Steam 笔记管理器 v5.3.2",
                 font=("", 12, "bold")).pack(padx=20, pady=(15, 8))

        info_frame = tk.Frame(about)
        info_frame.pack(padx=20, pady=(0, 5))

        tk.Label(info_frame, text="作者: ", font=("", 10),
                 anchor=tk.E).grid(row=0, column=0, sticky=tk.E)
        author_link = tk.Label(info_frame, text="dtq1997", font=("", 10, "underline"),
                               fg="#1a73e8", cursor="hand2")
        author_link.grid(row=0, column=1, sticky=tk.W)
        author_link.bind("<Button-1>",
                         lambda e: webbrowser.open("https://steamcommunity.com/id/dtq1997/"))

        tk.Label(info_frame, text="邮箱: ", font=("", 10),
                 anchor=tk.E).grid(row=1, column=0, sticky=tk.E)
        tk.Label(info_frame, text="919130201@qq.com", font=("", 10),
                 fg="#555").grid(row=1, column=1, sticky=tk.W)

        tk.Label(info_frame, text="", font=("", 10),
                 anchor=tk.E).grid(row=2, column=0, sticky=tk.E)
        tk.Label(info_frame, text="dtq1997@pku.edu.cn", font=("", 10),
                 fg="#555").grid(row=2, column=1, sticky=tk.W)

        motto_label = tk.Label(about, text="「总有一天人人都会控大喷菇的」",
                               font=("", 10), fg="#5599cc", cursor="hand2")
        motto_label.pack(pady=(5, 3))
        motto_label.bind("<Button-1>",
                         lambda e: webbrowser.open("https://aweidao1.com/t/986949"))

        ttk.Button(about, text="确定", command=about.destroy).pack(pady=(5, 15))
        self._center_window(about)

    def _ui_open_dir(self):
        d = self.current_account['notes_dir']
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        self._open_folder(d)

    def _open_config_dir(self):
        """打开配置文件所在目录"""
        d = self._CONFIG_DIR
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        self._open_folder(d)

    @staticmethod
    def _open_folder(d):
        """跨平台打开文件夹"""
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(d)
            elif system == "Darwin":
                os.system(f'open "{d}"')
            else:
                os.system(f'xdg-open "{d}" 2>/dev/null || open "{d}" 2>/dev/null')
        except:
            messagebox.showinfo("目录路径", f"路径:\n{d}")

    # ────────────────────── Steam Cloud 连接 ──────────────────────

    def _update_cloud_status_display(self):
        """更新主界面的云同步状态显示"""
        t = self._cloud_status_text
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        t.insert(tk.END, "✅ 已定位到笔记目录  ", "green")
        if self.cloud_uploader and self.cloud_uploader.initialized:
            # 检查账号是否匹配
            logged_in = self.cloud_uploader.logged_in_friend_code
            selected = self.current_account.get('friend_code', '')
            if logged_in and logged_in != selected:
                t.insert(tk.END, "⚠️ Cloud 已连接 (账号不匹配!)", "red")
            else:
                t.insert(tk.END, "☁️ Steam Cloud 已连接", "green")
            self._cloud_connect_btn.config(text="🔌 断开 Steam Cloud")
        else:
            t.insert(tk.END, "☁️ Cloud 未连接", "red")
            self._cloud_connect_btn.config(text="☁️ 连接 Steam Cloud")
        t.config(state=tk.DISABLED)

    def _toggle_cloud_connection(self):
        """连接或断开 Steam Cloud"""
        if self.cloud_uploader and self.cloud_uploader.initialized:
            # 断开
            self.cloud_uploader.shutdown()
            self.cloud_uploader = None
            self.manager.cloud_uploader = None
            self._update_cloud_status_display()
            return

        # 连接
        self._cloud_connect_btn.config(state=tk.DISABLED)
        self.root.update_idletasks()

        uploader = SteamCloudUploader()
        steam_path = self.current_account.get('steam_path', '')
        ok, msg = uploader.auto_init(steam_path)

        if ok:
            # 检查登录账号是否匹配当前选择的账号
            logged_in = uploader.logged_in_friend_code
            selected = self.current_account.get('friend_code', '')
            if logged_in and logged_in != selected:
                # 账号不匹配 — 拒绝连接
                logged_name = None
                for acc in self.accounts:
                    if acc['friend_code'] == logged_in:
                        logged_name = acc['persona_name']
                        break
                logged_desc = (f"「{logged_name}」(ID: {logged_in})"
                               if logged_name else f"ID: {logged_in}")
                selected_name = self.current_account.get('persona_name', selected)
                uploader.shutdown()
                messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                    f"Steam 客户端当前登录的账号是 {logged_desc}，\n"
                    f"但程序中选择的账号是「{selected_name}」(ID: {selected})。\n\n"
                    f"上传到 Steam Cloud 的笔记会同步到登录账号，\n"
                    f"而非程序中选择的账号！\n\n"
                    f"如果要为「{selected_name}」上传笔记，\n"
                    f"请先在 Steam 客户端切换到该账号后重新连接。",
                    parent=self.root)
                self._cloud_connect_btn.config(state=tk.NORMAL)
                self._update_cloud_status_display()
                return
            self.cloud_uploader = uploader
            self.manager.cloud_uploader = uploader
            self._update_cloud_status_display()
        else:
            messagebox.showerror("❌ 连接失败",
                f"无法连接 Steam Cloud:\n{msg}\n\n"
                "请确保:\n"
                "1. Steam 客户端正在运行\n"
                "2. 库中至少有一个已安装的游戏（需要其中的 libsteam_api）\n"
                "3. macOS 用户首次使用可能需要在系统设置中允许加载",
                parent=self.root)
            self._cloud_connect_btn.config(state=tk.NORMAL)
            self._update_cloud_status_display()
            return

        self._cloud_connect_btn.config(state=tk.NORMAL)

    # ────────────────────── 工具方法 ──────────────────────

    @staticmethod
    def _center_window(win):
        win.update_idletasks()
        cw, ch = win.winfo_reqwidth(), win.winfo_reqheight()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{cw}x{ch}+{int((sw - cw) / 2)}+{int((sh - ch) / 2)}")


# ═══════════════════════════════════════════════════════════════════════════════
#  入口
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = SteamNotesApp()
    app.run()
