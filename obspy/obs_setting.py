import os,json,winreg,glob
import win32com.client
#####电脑快捷方式的实际地址方法
def get_shortcut_target(path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    target = shortcut.TargetPath
    return target
#####电脑快捷方式的获取方法
def find_obs_studio_shortcut(obs_shortcut_pattern):
    # 获取桌面路径（公共桌面和用户桌面）
    desktop_path = os.path.join(os.environ['PUBLIC'], 'Desktop')
    # user_desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    user_desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    # 检查在公共桌面和用户桌面上是否存在符合模式的 OBS Studio 快捷方式文件
    for path in [desktop_path, user_desktop_path]:
        obs_shortcut_path = os.path.join(path, obs_shortcut_pattern)
        matching_shortcuts = glob.glob(obs_shortcut_path)
        if matching_shortcuts:
            return get_shortcut_target(matching_shortcuts[0])

    return None


##########################################通过注册表查找################################
########注册表获取方法
def get_software_info(target_name):
    # 定义检测位置
    sub_key = [        
        r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    ]
    for i in sub_key:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            i,
            0,
            winreg.KEY_ALL_ACCESS
        )
        for j in range(0, winreg.QueryInfoKey(key)[0] - 1):
            try:
                key_name = winreg.EnumKey(key, j)
                key_path = i + '\\' + key_name
                each_key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_ALL_ACCESS
                )
                display_name, _ = winreg.QueryValueEx(each_key, 'DisplayName')
                install_location, _ = winreg.QueryValueEx(each_key, 'DisplayIcon')
                # Convert to bytes-like objects
                display_name = display_name.encode('utf-8')
                install_location = install_location.encode('utf-8') if install_location else b''  # 处理安装目录为空的情况

                if target_name.encode('utf-8') in install_location:
                    # 将 bytes 转换为字符串
                    install_location_str = install_location.decode('utf-8')
                    # 规范化路径
                    normalized_path = os.path.normpath(install_location_str)
                    return normalized_path
            except WindowsError:
                pass

    return None  # 返回 None 表示未找到

########OBS地址获取
def read_obs_exe_path_from_config():
    obs_path_exe, obs_path = None, None 
    config_data = {}  
    try:
        if os.path.exists("xdlconfig.json"):
            with open("xdlconfig.json", "r") as config_file:
                config_data = json.load(config_file)
            obs_path_exe = config_data.get("obs_exe")
            obs_path = config_data.get("obs_path")
            if obs_path_exe and obs_path and os.path.exists(obs_path_exe):
                return obs_path_exe, obs_path
        else:
            with open("xdlconfig.json", 'w') as file:
                pass
    except:
        print(f"Error in read_obs_exe_path_from_config")

    try:
        # 示例用法
        obs_path_exe = find_obs_studio_shortcut('OBS Studio.lnk')
        if not obs_path_exe:
            obs_path_exe = find_obs_studio_shortcut('obs*.lnk')
            if not obs_path_exe:
                find_steam_path = find_obs_studio_shortcut('Steam*.lnk')
                if find_steam_path:
                    directory_steam = os.path.dirname(find_steam_path)
                    test_obs_path_exe=os.path.join(directory_steam,"steamapps","common","OBS Studio","bin","64bit","obs64.exe")
                    if os.path.exists(test_obs_path_exe):
                        obs_path_exe=test_obs_path_exe
                if not obs_path_exe:
                    obs_path_exe=get_software_info("obs64.exe")
                    if not obs_path_exe:
                        return None,None      
        if os.path.exists(obs_path_exe):
            obs_path= obs_path_exe.split("bin")[0]

            config_data = {
                "obs_exe": obs_path_exe, 
                "obs_path": obs_path     
            }
            # 读取现有数据（如果存在）
            try:
                with open("xdlconfig.json", "r") as config_file:
                    existing_data = json.load(config_file)
            except:
                existing_data = {} 
            # 合并现有数据和新数据
            existing_data.update(config_data)
            # 将合并后的数据写回文件
            with open("xdlconfig.json", "w") as config_file:
                json.dump(existing_data, config_file, indent=4)  #############indent=4为数据格式，如果省略，数据就紧凑省空间。

            return obs_path_exe, obs_path
        else:
            return None,None
    except Exception:
        return None,None


# 调用函数以创建xdlconfig.json文件或从中读取obs_exe的值
# print(read_obs_exe_path_from_config())
