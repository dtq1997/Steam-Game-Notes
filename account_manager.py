"""Steam 账号发现与管理 — 自动扫描系统中所有 Steam 账号及笔记路径"""

import json
import os
import platform
import re

try:
    import urllib.request
    import urllib.error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False

from core import NOTES_APPID
from utils import urlopen as _urlopen


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
    def check_free_apps(app_ids: list, cache: dict = None) -> set:
        """通过 Steam Store API (appdetails) 检查哪些游戏是免费的

        对每个 app_id 调用 appdetails，检查 is_free 字段。
        已知结果会跳过（通过 cache 参数传入 {app_id_str: bool}）。
        返回免费游戏的 app_id 字符串集合。
        """
        if cache is None:
            cache = {}
        free_ids = set()
        to_check = [str(a) for a in app_ids if str(a) not in cache]
        # 已有缓存中的免费游戏直接加入
        for aid_str, is_free in cache.items():
            if is_free and str(aid_str) in {str(a) for a in app_ids}:
                free_ids.add(str(aid_str))
        if not to_check:
            return free_ids
        for aid in to_check:
            try:
                url = f"https://store.steampowered.com/api/appdetails?appids={aid}"
                req = urllib.request.Request(url, headers={
                    "User-Agent": "SteamNotesGen/5.5"
                })
                with _urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                app_data = data.get(str(aid), {})
                if app_data.get("success") and app_data.get("data", {}).get("is_free"):
                    free_ids.add(aid)
                    cache[aid] = True
                else:
                    cache[aid] = False
            except Exception:
                cache[aid] = False  # 失败时保守地认为不是免费
        return free_ids

    @staticmethod
    def fetch_all_steam_app_names(api_key: str = "", progress_callback=None,
                                   estimated_total: int = 0) -> dict:
        """获取 Steam 全量应用名称列表

        优先使用 IStoreService/GetAppList/v1/（需要 API Key，分页请求），
        失败时回退到已弃用的 ISteamApps/GetAppList/v2/（无需 Key）。

        Args:
            api_key: Steam Web API Key（可选，但强烈推荐提供）
            progress_callback: 可选回调函数
                (fetched_count, page, is_done, estimated_total) -> None
            estimated_total: 估计总数（用于进度条，0=未知）

        Returns:
            {app_id_str: name_str, ...} 字典，失败时返回空字典。
        """
        # ── 方案 A: IStoreService/GetAppList/v1/（推荐，需要 API Key）──
        if api_key:
            try:
                result = {}
                last_appid = 0
                max_results = 50000
                page = 0
                while True:
                    page += 1
                    url = (f"https://api.steampowered.com/IStoreService/GetAppList/v1/"
                           f"?key={api_key}&max_results={max_results}"
                           f"&last_appid={last_appid}&include_games=1"
                           f"&include_dlc=0&include_software=1&include_videos=0&include_hardware=0")
                    req = urllib.request.Request(url, headers={
                        "User-Agent": "SteamNotesGen/5.6"
                    })
                    with _urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    apps = data.get("response", {}).get("apps", [])
                    if not apps:
                        break
                    for app in apps:
                        aid = str(app.get("appid", ""))
                        name = app.get("name", "")
                        if aid and name:
                            result[aid] = name
                    has_more = data.get("response", {}).get("have_more_results", False)
                    # 动态更新估计总数：如果还有更多页，按当前均值估算
                    if has_more and estimated_total < len(result):
                        avg_per_page = len(result) / page
                        # 保守估计还剩 1~2 页
                        estimated_total = max(estimated_total,
                                              int(len(result) + avg_per_page * 1.5))
                    if not has_more:
                        estimated_total = len(result)
                    if progress_callback:
                        try:
                            progress_callback(len(result), page, not has_more,
                                              estimated_total)
                        except Exception:
                            pass
                    # 检查是否还有更多（have_more_results 字段）
                    if not has_more:
                        break
                    last_appid = apps[-1].get("appid", 0)
                    if page > 10:  # 安全上限，避免无限循环
                        break
                if result:
                    print(f"[游戏名称] IStoreService 获取成功: {len(result)} 条 ({page} 页)")
                    return result
            except Exception as e:
                print(f"[游戏名称] IStoreService 获取失败: {e}，尝试回退方案...")

        # ── 方案 B: ISteamApps/GetAppList/v2/（已弃用，可能 404）──
        url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        try:
            if progress_callback:
                try:
                    progress_callback(0, 0, False, estimated_total)
                except Exception:
                    pass
            req = urllib.request.Request(url, headers={
                "User-Agent": "SteamNotesGen/5.6"
            })
            with _urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            apps = data.get("applist", {}).get("apps", [])
            result = {}
            for app in apps:
                aid = str(app.get("appid", ""))
                name = app.get("name", "")
                if aid and name:
                    result[aid] = name
            if result:
                print(f"[游戏名称] ISteamApps (v2) 获取成功: {len(result)} 条")
            if progress_callback:
                try:
                    progress_callback(len(result), 1, True, len(result))
                except Exception:
                    pass
            return result
        except Exception as e:
            print(f"[游戏名称] 全量列表获取失败: {e}")
            return {}


