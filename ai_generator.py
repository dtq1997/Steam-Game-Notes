"""AI 笔记生成器 — 支持 Anthropic (Claude) 和 OpenAI 兼容 API"""

import json
import re
import ssl
from datetime import datetime

try:
    import urllib.request
    import urllib.error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


def _get_ssl_context():
    """获取 SSL 上下文，macOS Python 安装后未运行证书脚本时自动 fallback"""
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        pass
    ctx = ssl._create_unverified_context()
    return ctx


def _urlopen(req, timeout=30):
    """封装 urlopen，自动处理 SSL 证书问题"""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise


# 默认系统提示词 — 来自导言区的【AI 撰写游戏说明笔记的指引】
AI_SYSTEM_PROMPT = """你是一个 Steam 游戏介绍撰写助手。请根据用户提供的游戏信息，撰写一段客观的"游戏说明"笔记。

目标读者：不一定了解独立游戏或单机游戏的普通玩家。
目的：让读者快速判断这个游戏是否符合自己的兴趣。

撰写规则（必须全部遵守）：
1. 客观描述：不能照抄商店页面的商业化宣传语，要客观地告诉读者这个游戏是什么、玩起来是什么感觉。
2. "现在打开会怎样"：必须具体描述"如果我现在立刻打开这个游戏，前几分钟会看到什么、做什么"。要写到读者脑中能浮现画面的程度——比如"打开后先是一段过场动画，然后进入角色创建，选完职业后直接被打进一片雪原，没有任何提示，你需要自己摸索怎么活下去"。❌ 绝对禁止用"上手难度适中""需要一定学习成本""有一定门槛"这类模糊概括代替具体描述。你必须回答的是"我会看到什么界面、做什么操作、遇到什么状况"，而非"难不难"。
3. 认知资源与时间需求：必须说明这个游戏需要怎样的注意力投入，让读者知道自己需要为它腾出怎样的精力和时间。是否需要大段连续时间、每局/每次游玩大概多久。
4. 网络口碑：必须提及这个游戏在网络上是否受欢迎、大致评价如何。
5. 缺点与不适人群：必须有一定篇幅介绍缺点，以及明确说明不适合什么样的人玩。
6. 不用术语、说人话：禁止使用读者可能不懂的术语而不加解释。例如不能直接说"ASCII 风格画面"或"1-bit 风格"，而应该用没玩过游戏的人都能理解的语言描述（如"画面几乎完全由彩色文字符号构成——你的角色是一个@，怪物是字母，墙壁是#号"）。术语不必刻意回避或删除，解释清楚即可。
7. 无需强调性价比：这些游戏已在用户库中，属于免费可玩，绝对禁止提及任何与价格相关的内容。禁止使用的词汇包括但不限于：价格、售价、原价、打折、折扣、性价比、值不值、定价、促销、半价、特惠、入手、购买建议。即使参考资料中大量提到这些内容，你也必须完全忽略——读者已经拥有这个游戏，任何价格讨论都是无意义的。
8. 适合的游玩情景：适合自己一个人单独玩？还是适合跟另一个朋友一起玩？适合跟一大群朋友玩？适合跟什么类型的人玩？适合什么场合——比如睡前放松、通勤途中、还是周末空出一整个下午？诸如此类。

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
□ 是否说明了注意力投入程度和单次游玩时长？
□ 是否提到了网络口碑/社区评价？
□ 是否有缺点和不适合的人群？
□ 是否所有术语都附带了通俗解释，没有让不懂游戏的读者感到困惑？
□ 是否有提到适合的游玩情景（跟谁玩、什么场合）？
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

🌐 多语言搜索策略（非常重要）：
- 必须用英文游戏名搜索至少一次（英文搜索结果通常最丰富）
- 如果游戏可能是日本开发/日文受众（如日式 RPG、视觉小说、同人游戏），
  也用日文名搜索（搜索「ゲーム名 レビュー」或「ゲーム名 感想」）
- 用中文游戏名也搜索一次
- 不要仅依赖中文搜索结果，很多独立/小众游戏几乎没有中文资料，
  但英文或日文社区可能有丰富的讨论
- 根据游戏的开发商/发行商国籍，判断哪种语言搜索更可能获得有效信息
- 如果对这个游戏已经非常了解，可以少搜或不搜；如果不太确定，多搜几次
- 搜索结果仅用于辅助你的写作，不要照抄搜索到的文字
- 特别注意搜索该游戏的缺点和负面评价，因为提示词要求必须包含这些内容

📊 信息量评估与回退策略（非常重要）：
- 搜索完成后，请严格评估搜索结果中"与这个游戏本身直接相关"的有效信息比例
- 注意：游戏名称可能与其他事物同名，搜索结果中可能有大量不相关内容，这些不算有效信息
- ⚠️ 回退规则：如果联网搜索发现网络上关于这个游戏的有效信息严重不足（如只搜到
  不相关结果、或只有寥寥几句），你必须回退到主要依靠上面提供的 Steam 评测内容来
  撰写游戏说明。请注意：即使全体搜索结果数量很多，但如果大部分都是不相关信息，
  也应当视为"网络有效信息不足"而回退到 Steam 评测。
  只有当联网搜索和 Steam 评测信息都严重不足时，才标注 INSUFFICIENT:true
- 如果联网搜索发现有效信息很丰富就写"相当多"，
  几乎没有相关信息就写"相当少"。
  可选值：相当多 / 较多 / 中等 / 较少 / 相当少）

⚠️ 最终语言要求（最高优先级）：
无论你搜索到的参考资料是英文、日文还是其他语言，你【必须】使用简体中文撰写最终的游戏说明笔记，严禁输出任何非中文的正文内容。
严禁使用 Markdown 格式（如 **粗体**、## 标题），严禁使用分段式小标题（如「Gameplay:」、「Reviews:」），
必须是纯文本单行中文叙述。"""


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

    # 参考资料最大长度（字符数）— 超过此长度会截断评测文本，
    # 避免大量参考资料"淹没"格式和内容指令
    MAX_EXTRA_CONTEXT_CHARS = 3000

    def generate_note(self, game_name: str, app_id: str,
                      extra_context: str = "",
                      system_prompt: str = "",
                      use_web_search: bool = False) -> tuple:
        """为单个游戏生成笔记内容

        Returns: (text: str, model: str, confidence: str,
                  info_volume: str, is_insufficient: bool, quality: str)

        消息结构设计原则（v6.0）：
        - LLM 对消息的【开头】和【末尾】最为敏感
        - 参考资料（评测、商店详情）放在中间
        - 联网搜索触发指令放在参考资料之前（让模型先搜索再看资料）
        - 内容要求清单和格式要求放在消息【最末尾】（最高优先级位置）
        - 元数据输出格式放在内容要求之前（次优先级）
        """
        # ── 第一段：任务声明 + 联网搜索触发（如有）──
        user_msg = f"请为以下 Steam 游戏撰写游戏说明笔记：\n\n"
        user_msg += f"游戏名称：{game_name}\n"
        user_msg += f"Steam AppID：{app_id}\n"

        # 联网搜索触发放在参考资料之前，让模型先搜索
        if use_web_search:
            user_msg += ("\n🔍 联网搜索已启用——请先用 web_search 搜索这个游戏的"
                         "实际游玩体验、社区口碑、通关时长和常见缺点，再开始撰写。\n")

        # ── 第二段：参考资料（中间位置，被指令包裹）──
        if extra_context:
            # 截断过长的参考资料
            if len(extra_context) > self.MAX_EXTRA_CONTEXT_CHARS:
                extra_context = (extra_context[:self.MAX_EXTRA_CONTEXT_CHARS]
                                 + "\n…（参考资料已截断）")
            user_msg += ("\n"
                         "╔═════ 以下是参考资料（仅供参考，严禁照抄或逐条总结）═════╗\n"
                         f"{extra_context}\n"
                         "╚═════ 参考资料结束 ═════╝\n"
                         "\n"
                         "⚠️ 重要提醒：以上参考资料只是帮你了解这个游戏的素材。\n"
                         "你的任务是用自己的话写一段连贯自然的游戏说明，"
                         "像朋友聊天一样娓娓道来。不要变成「评测摘要」或「信息罗列」。\n")

        # ── 第三段：元数据输出格式 ──
        user_msg += ("\n在你的回复最末尾，用以下格式逐行标注元数据（每行一个标签）：\n"
                     "\n")

        # 信息量评估指引
        if use_web_search:
            user_msg += (
                'INFO_VOLUME:（请严格根据你的联网搜索结果来判断「与这个游戏本身直接相关」的'
                '有效信息占全部搜索结果的比例——注意，游戏名可能搜出很多不相关的结果，'
                '只有确实在讨论这个游戏本身的玩法、评价、体验等内容才算有效信息。'
                '如果搜索结果中有效信息很丰富就写"相当多"，'
                '几乎没有相关信息就写"相当少"。'
                '可选值：相当多 / 较多 / 中等 / 较少 / 相当少）\n')
        else:
            user_msg += (
                'INFO_VOLUME:（请根据上面提供的参考资料（Steam 商店详情 + 玩家评测）'
                '以及你自身训练数据中对这个游戏的了解程度，综合判断你掌握的'
                '「与这个游戏本身直接相关」的有效信息量——注意，有些 Steam 评测可能'
                '是玩笑、与游戏内容无关或信息量极低，这类不算有效信息。'
                '如果有效信息很丰富就写"相当多"，'
                '几乎没有有效信息就写"相当少"。'
                '可选值：相当多 / 较多 / 中等 / 较少 / 相当少）\n')

        user_msg += (
            'INSUFFICIENT:（如果你掌握的有效信息实在太少，以至于你认为'
            '绝对不可能写出一段有意义的、对读者有帮助的游戏说明，就写 true。'
            '只要还能写出大致靠谱的介绍就写 false。这是一个很高的门槛——'
            '只有真的几乎一无所知时才写 true。'
            '⚠️ 特别注意：如果联网搜索信息不足但上面提供的 Steam 评测内容'
            '仍有足够参考价值，你应该基于评测内容撰写说明并写 false。'
            '只有联网搜索和 Steam 评测都严重不足时才写 true。）\n'
            'CONFIDENCE:很高 或 CONFIDENCE:较高 或 CONFIDENCE:中等 '
            '或 CONFIDENCE:较低 或 CONFIDENCE:很低\n'
            '（确信程度取决于你对这个游戏的了解程度——'
            '如果这个游戏你很熟悉、信息确定性高就写"很高"，'
            '如果是比较冷门/不太了解的游戏就写"较低"或"很低"。）\n'
            'QUALITY:相当好 或 QUALITY:较好 或 QUALITY:中等 '
            '或 QUALITY:较差 或 QUALITY:相当差\n'
            '（游戏总体质量是你综合所有信息后对这个游戏质量的客观判断——'
            '包括玩法设计、内容量、完成度、社区口碑等。'
            '如果是口碑极好的精品就写"相当好"，'
            '如果是质量堪忧的游戏就写"较差"或"相当差"。'
            '⚠️ 注意：这是对游戏本身质量的评估，不是对你写的说明的评估。）\n'
            '\n'
            '⚠️ 如果你判定 INSUFFICIENT:true，则不需要输出游戏说明正文，'
            '只需要输出上面四行元数据标签即可。\n'
        )

        # ── 第四段（最末尾 = 最高优先级）：内容要求清单 + 格式要求 ──
        # 这是用户消息的最后部分，LLM 对此最为敏感
        user_msg += (
            "\n"
            "════════════════════════════════════════\n"
            "📋 以下是你【必须遵守】的内容要求和格式要求（最高优先级）：\n"
            "════════════════════════════════════════\n"
            "\n"
            "【内容要求清单】— 缺一不可，输出前逐条自查：\n"
            "□ 第一句话是否有概括性（如「XXX 是一款……的游戏」）？\n"
            "□ 是否具体描述了「现在打开这个游戏，前几分钟会看到什么、做什么」？"
            "（❌ 禁止用「上手难度适中」「有一定门槛」等模糊概括代替！）\n"
            "□ 是否说明了注意力投入程度和单次游玩时长？\n"
            "□ 是否提到了网络口碑 / 社区评价？\n"
            "□ 是否有缺点和不适合的人群？\n"
            "□ 是否说了适合的游玩情景（跟谁玩、什么场合）？\n"
            "□ 是否所有术语都附带了通俗解释？\n"
            "□ 全文是否完全没有提及价格、性价比、打折等与钱相关的内容？\n"
            "\n"
            "【格式要求】— 违反任何一条都是不合格的输出：\n"
            "✦ 纯文本单行，禁止换行\n"
            "✦ 禁止 BBCode 标签（[p] [h1] [b] 等全部禁止）\n"
            "✦ 禁止 Markdown 格式（禁止 **粗体**、## 标题等）\n"
            "✦ 禁止分段式小标题（如「初次打开的体验：」「认知资源：」），"
            "所有信息融入一段连贯叙述\n"
            "✦ 可适度使用 emoji（📌✅⚠️🗺️⚔️📝🎯）但要克制\n"
            "✦ 建议 200-500 字\n"
            "✦ 必须使用简体中文\n"
            "\n"
            "请直接输出游戏说明正文（上述内容清单全部覆盖），"
            "然后在末尾附上四行元数据标签。不要输出任何解释或前缀。"
        )

        prompt = system_prompt.strip() if system_prompt.strip() else AI_SYSTEM_PROMPT

        # 联网搜索时追加搜索策略指引到系统提示词
        if use_web_search:
            prompt += AI_WEB_SEARCH_ADDENDUM

        if self.provider == 'anthropic':
            return self._call_anthropic(prompt, user_msg,
                                        use_web_search=use_web_search)
        else:
            return self._call_openai_compat(prompt, user_msg,
                                            use_web_search=use_web_search)

    def _call_anthropic(self, system_prompt: str, user_msg: str,
                        use_web_search: bool = False) -> tuple:
        """调用 Anthropic (Claude) API"""
        # 检测是否通过第三方代理（自定义URL）
        _default_url = self.PROVIDERS['anthropic']['api_url']
        _is_proxy = (self.api_url != _default_url)

        result = self._call_anthropic_inner(
            system_prompt, user_msg, use_web_search=use_web_search)

        # ── 代理联网搜索的兜底：两步法 ──
        # 第三方代理处理 web_search 时会重构请求，经常丢弃 system prompt，
        # 导致 Claude 用英文回复或不遵守格式（Markdown、分段等）。
        # 此时第一步的输出仍包含有价值的搜索信息。
        # 策略：检测到输出为非中文或格式不符时，以第一步输出作为"参考资料"，
        # 发起第二次调用（不带 web_search），让 Claude 按格式重写为中文。
        # 第二次调用不涉及 web_search，代理不会干预，system prompt 正常生效。
        if _is_proxy and use_web_search and result[0]:
            full_text = result[0]
            _cn_chars = len(re.findall(r'[\u4e00-\u9fff]', full_text))
            _total_chars = len(full_text.strip())
            _is_non_chinese = (_total_chars > 50
                               and _cn_chars < _total_chars * 0.15)
            _has_fmt_issues = bool(
                re.search(r'\*\*[^*]+\*\*', full_text)
            ) or full_text.count('\n') > 8
            # 新增：检测内容过短（低于 80 中文字符，说明可能没遵守内容要求）
            _is_too_short = (_cn_chars < 80 and not result[4])  # 排除 INSUFFICIENT
            # 新增：检测分段标题（提示词明确禁止）
            _has_section_headers = bool(re.search(
                r'(?:^|\n)\s*(?:[\w\u4e00-\u9fff]+[:：]\s*\n|'
                r'#{1,6}\s+|'
                r'\*\*[\u4e00-\u9fff]+(?:[:：]|：)\*\*)',
                full_text))
            # 新增：检测 BBCode 标签
            _has_bbcode = bool(re.search(
                r'\[/?(?:p|h[1-6]|b|i|u|url|img|list|olist|strike|spoiler)\b',
                full_text, re.IGNORECASE))

            _need_rewrite = (_is_non_chinese or _has_fmt_issues
                             or _is_too_short or _has_section_headers
                             or _has_bbcode)

            if _need_rewrite:
                # 诊断原因
                _reasons = []
                if _is_non_chinese:
                    _reasons.append(f"非中文（中文 {_cn_chars}/{_total_chars}）")
                if _has_fmt_issues:
                    _reasons.append(f"格式不符（Markdown/换行{full_text.count(chr(10))}处）")
                if _is_too_short:
                    _reasons.append(f"内容过短（仅 {_cn_chars} 中文字符）")
                if _has_section_headers:
                    _reasons.append("包含分段标题")
                if _has_bbcode:
                    _reasons.append("包含 BBCode 标签")
                _reason = " + ".join(_reasons)
                self._last_debug_info += (
                    f"\n⚠️ 联网搜索输出{_reason}，"
                    "启动第二步：用正常调用重写…\n"
                )
                # 构造第二步的 user message：
                # 将第一步的输出作为参考资料，要求按原始格式重写为中文
                rewrite_user_msg = (
                    f"请为以下 Steam 游戏撰写游戏说明笔记：\n\n"
                    f"以下是关于这个游戏的详细参考资料（来自联网搜索结果），"
                    f"请基于这些信息，严格按照系统提示词的要求撰写中文游戏说明：\n\n"
                    f"╔═════ 联网搜索参考资料 ═════╗\n"
                    f"{full_text}\n"
                    f"╚═════ 参考资料结束 ═════╝\n\n"
                )
                # 也包含原始 user_msg 中的 Steam 评测等信息
                # 从原始 user_msg 中提取游戏名和 AppID
                _name_match = re.search(r'游戏名称：(.+)', user_msg)
                _appid_match = re.search(r'Steam AppID：(\d+)', user_msg)
                if _name_match:
                    rewrite_user_msg += f"游戏名称：{_name_match.group(1)}\n"
                if _appid_match:
                    rewrite_user_msg += f"Steam AppID：{_appid_match.group(1)}\n"
                # 提取原始 user_msg 中的参考资料部分（Steam 评测等）
                _ref_match = re.search(
                    r'(╔═════ 以下是参考资料.*?╚═════ 参考资料结束 ═════╝)',
                    user_msg, re.DOTALL)
                if _ref_match:
                    rewrite_user_msg += f"\n{_ref_match.group(1)}\n"
                # 添加元数据输出要求（从原始 user_msg 中截取）
                _meta_match = re.search(
                    r'(在你的回复最末尾.*?)$', user_msg, re.DOTALL)
                if _meta_match:
                    rewrite_user_msg += f"\n{_meta_match.group(1)}"
                else:
                    # 如果没找到，手动添加简化版元数据要求
                    rewrite_user_msg += (
                        "\n请直接输出纯文本内容（单行，无换行，无 BBCode 标签）。\n"
                        "在回复最末尾标注：\n"
                        "INFO_VOLUME:（相当多/较多/中等/较少/相当少）\n"
                        "INSUFFICIENT:false\n"
                        "CONFIDENCE:（很高/较高/中等/较低/很低）\n"
                        "QUALITY:（相当好/较好/中等/较差/相当差）\n"
                    )

                # 第二步调用：不带 web_search，system prompt 正常传递
                _step1_debug = self._last_debug_info  # 保存第一步的调试信息
                result = self._call_anthropic_inner(
                    system_prompt, rewrite_user_msg, use_web_search=False)
                # 合并两步的调试信息
                self._last_debug_info = (
                    _step1_debug
                    + "\n\n=== 第二步（重写为中文）===\n"
                    + self._last_debug_info
                    + "\n✅ 第二步重写完成。\n"
                )

        return result

    def _call_anthropic_inner(self, system_prompt: str, user_msg: str,
                              use_web_search: bool = False) -> tuple:
        """调用 Anthropic (Claude) API 的内部实现"""
        is_thinking = 'thinking' in self.model.lower()

        # 检测是否通过第三方代理（自定义URL）
        _default_url = self.PROVIDERS['anthropic']['api_url']
        _is_proxy = (self.api_url != _default_url)

        # ── 代理防护：将系统提示词注入用户消息 ──
        # 第三方代理（new-api/one-api 等）在转发 Anthropic 请求时，
        # 经常丢弃或截断 "system" 字段，导致模型完全看不到提示词。
        # 解决方案：代理场景下，将系统提示词作为用户消息的开头注入，
        # 同时保留原始 "system" 字段（兼容正确处理 system 的代理）。
        _actual_user_msg = user_msg
        if _is_proxy:
            _actual_user_msg = (
                "【系统指令 — 请严格遵守以下全部要求】\n"
                f"{system_prompt}\n"
                "【系统指令结束】\n\n"
                f"{user_msg}"
            )

        payload_dict = {
            "model": self.model,
            "max_tokens": 16000 if is_thinking else 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": _actual_user_msg}]
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
            "User-Agent": "SteamNotesGen/5.9",
            "Accept": "application/json",
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

        # ── 关键：联网搜索时只取最后一个有实质内容的 text block ──
        # 启用 web search 后，API 返回的 content 数组包含多个 text block：
        #   text("Let me search...")  →  tool_use  →  tool_result  →
        #   text("Based on my search...")  →  tool_use  →  tool_result  →
        #   text("《游戏名》是一款……CONFIDENCE:……")   ← 这才是正文
        # 中间的 text block 是 AI 的思考/计划性文字，不是游戏说明。
        # 只有最后一个 text block 包含我们需要的正文和元数据标签。
        if use_web_search and len(text_parts) > 1:
            full_text = self._select_best_text_block(text_parts)
        else:
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
            "User-Agent": "SteamNotesGen/5.9",
            "Accept": "application/json",
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
            # 联网搜索时只取最后一个有实质内容的 text block（同 _call_anthropic）
            if use_web_search and len(text_parts) > 1:
                full_text = self._select_best_text_block(text_parts)
            else:
                full_text = "\n".join(text_parts)

        actual_model = data.get("model", self.model)

        return self._extract_confidence(full_text, actual_model)

    @staticmethod
    def _select_best_text_block(text_parts: list) -> str:
        """从多个 text block 中选择包含正文的那个。

        联网搜索时 API 返回多个 text block，其中大部分是 AI 的搜索计划
        和思考文字，只有一个（通常是最后一个）包含实际的游戏说明正文。

        选择策略（按优先级）：
        1. 从后往前找第一个同时包含元数据标签和足够中文内容的 block
        2. 从后往前找第一个包含元数据标签的 block
        3. 从后往前找第一个包含足够中文内容（≥30字）的 block
        4. 取最后一个非空 block
        """
        _meta_pattern = re.compile(
            r'(?:CONFIDENCE|QUALITY|INFO_VOLUME|INSUFFICIENT)[:：]')

        # 策略1：同时有元数据标签 + 足够中文（最理想）
        for i in range(len(text_parts) - 1, -1, -1):
            part = text_parts[i]
            if (_meta_pattern.search(part)
                    and len(re.findall(r'[\u4e00-\u9fff]', part)) >= 30):
                return part

        # 策略2：只有元数据标签
        for i in range(len(text_parts) - 1, -1, -1):
            if _meta_pattern.search(text_parts[i]):
                return text_parts[i]

        # 策略3：足够的中文内容
        for i in range(len(text_parts) - 1, -1, -1):
            if (text_parts[i].strip()
                    and len(re.findall(r'[\u4e00-\u9fff]', text_parts[i])) >= 30):
                return text_parts[i]

        # 策略4：最后一个非空 block
        for i in range(len(text_parts) - 1, -1, -1):
            if text_parts[i].strip():
                return text_parts[i]

        return text_parts[-1] if text_parts else ""

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
        """从 AI 输出中提取确信程度、信息量评估、信息不足标记和质量评估
        
        Returns: (text, model, confidence, info_volume, is_insufficient, quality)
        """
        confidence = "中等"
        info_volume = "中等"
        is_insufficient = False
        quality = "中等"

        # ── 先记录第一个元数据标签的位置（用于后续正文定位） ──
        # 必须在剥离元数据之前记录，否则锚点信息会丢失
        _first_meta_pos = None
        _meta_pos_match = re.search(
            r'(?:^|\n)\s*(?:INFO_VOLUME|INSUFFICIENT|CONFIDENCE|QUALITY)[:：]',
            full_text, re.MULTILINE
        )
        if _meta_pos_match:
            _first_meta_pos = _meta_pos_match.start()

        # 提取 INSUFFICIENT 标记
        insuf_match = re.search(
            r'INSUFFICIENT[:：]\s*(true|false|是|否)',
            full_text, re.IGNORECASE
        )
        if insuf_match:
            val = insuf_match.group(1).lower()
            is_insufficient = val in ('true', '是')
            full_text = re.sub(r'\n*INSUFFICIENT[:：].*$', '', full_text,
                               flags=re.MULTILINE).strip()

        # 提取 INFO_VOLUME 标记
        vol_match = re.search(
            r'INFO_VOLUME[:：]\s*(相当多|较多|中等|较少|相当少)',
            full_text
        )
        if vol_match:
            info_volume = vol_match.group(1)
            full_text = re.sub(r'\n*INFO_VOLUME[:：].*$', '', full_text,
                               flags=re.MULTILINE).strip()

        # 提取 QUALITY 标记
        qual_match = re.search(
            r'QUALITY[:：]\s*(相当好|较好|中等|较差|相当差)',
            full_text
        )
        if qual_match:
            quality = qual_match.group(1)
            full_text = re.sub(r'\n*QUALITY[:：].*$', '', full_text,
                               flags=re.MULTILINE).strip()

        # 提取 CONFIDENCE 标记
        conf_match = re.search(
            r'CONFIDENCE[:：]\s*(很高|较高|中等|较低|很低|相当高|相当低)',
            full_text
        )
        if conf_match:
            confidence = conf_match.group(1)
            full_text = re.sub(r'\n*CONFIDENCE[:：].*$', '', full_text,
                               flags=re.MULTILINE).strip()

        # ── 清理第三方代理（中转服务）可能泄露的原始工具调用标记 ──
        # 某些代理未正确拆分 content blocks，将 <function_calls>、<invoke>、
        # <thinking>、<search_results> 等 XML 标签作为纯文本混入 text 块中。
        # 必须在提取正文前彻底清除，否则会出现在最终笔记中。
        # 1. 移除完整的 XML 块（含内容），包括 <parameter> 块
        for tag in ('function_calls', 'invoke', 'thinking', 'search_results',
                     'search_quality_reflection', 'result', 'parameter',
                     'antml:thinking', 'antml:function_calls', 'antml:invoke',
                     'antml:parameter', 'tool_result', 'tool_use',
                     'tool_call', 'tool_calls'):
            full_text = re.sub(
                rf'<{re.escape(tag)}[^>]*>.*?</{re.escape(tag)}>',
                '', full_text, flags=re.DOTALL
            )
        # 2. 移除残余的自闭合或孤立 XML 标签（如 </invoke> </function_calls> 等）
        full_text = re.sub(
            r'</?(?:function_calls|invoke|thinking|parameter|search_results|'
            r'search_quality_reflection|result|antml:\w+|tool_result|tool_use|'
            r'tool_call|tool_calls)[^>]*>',
            '', full_text
        )
        
        # 3. 清除裸露的 JSON 格式工具调用（XML 标签被部分清除后可能残留）
        full_text = re.sub(
            r'\s*\{\s*"name"\s*:\s*"web_search"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}\s*',
            '', full_text
        )
        
        full_text = full_text.strip()

        # ═══════════════════════════════════════════════════════════════
        # 核心清理：定位中文正文起始位置，丢弃之前的非正文内容
        # ═══════════════════════════════════════════════════════════════
        # 联网搜索时，AI 的输出可能是：
        #   [英文思考/搜索计划] + [中文正文] + [元数据标签]
        # 或者中转服务把所有 text block 合并后变成一大段混合文本。
        #
        # 策略：找到第一个中文字符的位置，然后往前回溯到该句子的起始位置
        # （游戏名可能是英文如 "Hollow Knight 是一款..."），
        # 丢弃之前所有的英文思考/搜索计划文字。
        #
        # 这比逐条正则匹配英文前缀稳定得多，因为不需要穷举 AI 可能说的
        # 每一种英文思考句式。
        
        _first_cn = re.search(r'[\u4e00-\u9fff]', full_text)
        
        if _first_cn and _first_cn.start() > 0:
            # 第一个中文字符之前有非中文内容（可能是思考性前缀）
            _first_cn_pos = _first_cn.start()
            _text_before_cn = full_text[:_first_cn_pos]
            
            # 从第一个中文字符往前回溯，寻找"游戏说明句"的起始位置
            # 游戏名可能是英文（如 "Hollow Knight 是一款..."）
            # 也可能是带特殊字符的（如 ".T.E.S.T: Expected Behaviour 是一款..."）
            #
            # 找最后一个英文句子结尾（句号+空格），排除游戏名中的点号
            _best_boundary = 0
            
            for _sb in re.finditer(
                r'(?<![.A-Z])'     # 前面不是点号或大写字母（排除 .T.E.S.T 等）
                r'\.'              # 句号
                r'(?!\.)'          # 后面不是点号（排除省略号 ...）
                r'\s+',            # 后跟空白
                _text_before_cn
            ):
                _best_boundary = _sb.end()
            
            # 也检查换行作为边界
            for _nl in re.finditer(r'\n\s*', _text_before_cn):
                if _nl.end() > _best_boundary:
                    _best_boundary = _nl.end()
            
            if _best_boundary > 0:
                full_text = full_text[_best_boundary:].lstrip()

        full_text = full_text.strip()

        # 兜底：如果上面的锚点方法没生效（如正文本身就是英文），
        # 逐句清理残余的明显思考性前缀
        _changed = True
        while _changed:
            _changed = False
            for pattern in (
                # 英文思考/计划性句子（宽泛匹配：以常见 AI 思考开头词起始的英文句子）
                r"^(?:I'll |I will |Let me |I need to |I should |I'm going to |"
                r"I have |I now have |The game'?s? |The search |Based on |"
                r"After |Now that |This is |Here'?s? |Looking at |"
                r"The web search |I can see |From the |According to |"
                r"Now I |First,? |Next,? |Finally,? |Overall,? )"
                r"[^\n]*?(?:\.\s*|\n)",
                # 中文思考/计划性句子
                r"^(?:我[来先]|让我|我需要|我[会将要]|接下来我)"
                r"(?:搜索|查[找询]|检索|了解|收集|获取|看看|查一下|搜一下).*?[。.]\s*",
                # "根据搜索结果"类
                r"^根据(?:搜索结果|我的搜索|网络信息|以上信息)[，,].*?[。.]\s*",
                # "搜索结果显示"类
                r"^(?:搜索结果|网络上的信息|综合以上信息)(?:显示|表明|说明)?[，,：:].*?[。.]\s*",
            ):
                new_text = re.sub(pattern, '', full_text, count=1,
                                  flags=re.IGNORECASE).strip()
                if new_text != full_text:
                    full_text = new_text
                    _changed = True

        # ── 后处理：清理 Markdown 格式残留并强制单行 ──
        # 第三方代理 + 联网搜索时，模型可能输出 Markdown 而非纯文本
        # 1. Markdown 粗体 **text** → text
        full_text = re.sub(r'\*\*(.+?)\*\*', r'\1', full_text)
        # 2. 行尾孤立 * 号（Markdown 列表残留）
        full_text = re.sub(r'\s*\*\s*$', '', full_text, flags=re.MULTILINE)
        # 3. Markdown 标题标记 ## ...
        full_text = re.sub(r'(?:^|\n)\s*#{1,6}\s+', '', full_text)
        # 4. 合并多行为单行（提示词要求纯文本单行）
        full_text = re.sub(r'\s*\n\s*', '', full_text)
        # 5. 清理多余空格
        full_text = re.sub(r'  +', ' ', full_text).strip()

        return full_text, actual_model, confidence, info_volume, is_insufficient, quality

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
