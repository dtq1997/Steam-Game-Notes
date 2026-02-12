"""Steam Cloud 上传器 — 通过 Steamworks API 直接上传文件到 Steam Cloud"""

import ctypes
import glob
import hashlib
import os
import platform
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


