import os
import json
from lanzou import lanzou_download
import zipfile
import shutil
# 导入json_data模块
import json_dbase



def delete_files_and_subfolders(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            os.rmdir(folder_path)

def obsplugin(sender_button): 
    downloaded_file_path=None

    try:
        # 构建完整的下载文件夹路径
        download_directory = os.path.join('filecache')

        # 检查下载文件夹是否存在，如果不存在则创建它
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
        else:
            # 删除download_directory目录下的所有文件和文件夹
            delete_files_and_subfolders(download_directory)
        config_data = json_dbase.data
        # 检查按钮名称是否存在于配置中
        if sender_button in config_data["obsconfigs"]["plugins"]:
            button_url = config_data["obsconfigs"]["plugins"][sender_button]
            urls = button_url["urls"]                      
            # local_app_data = os.environ.get('LOCALAPPDATA')
            # user_fonts=f"{local_app_data}\\Microsoft\\Windows\\Fonts\\"
            user_fonts="C:\\Windows\\Fonts\\"

            for url in urls:
                # 执行URL下载操作
                downloaded_file_path = lanzou_download(url)

                # 根据不同的按钮名称进行不同的处理
                if sender_button == "pushButton_13":
                    shutil.copy(downloaded_file_path, f"{download_directory}\\streamfx-windows-installer.exe")
                    os.remove(downloaded_file_path)                 
                    # subprocess.run(f"{download_directory}\\streamfx-windows-installer.exe")
                elif sender_button == "pushButton":
                    pass
                elif sender_button == "pushButton_11":                 
                    with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            # 获取压缩文件中的文件名
                            file_name = os.path.join(user_fonts, file_info.filename)
                            
                            # 检查文件是否已存在
                            if not os.path.exists(file_name):
                                # 文件不存在，解压到目标文件夹
                                zip_ref.extract(file_info, user_fonts)
                                print(f"解压完成，目标文件夹：{user_fonts}")
                            else:
                                print(f"文件已存在，跳过解压：{file_name}")
                    # 删除下载的压缩文件
                    os.remove(downloaded_file_path)
                else:
                    with open("xdlconfig.json", "r") as config_file:
                        config_data = json.load(config_file)
                        # 提取obs_exe的值
                        obs_paths = config_data.get("obs_path")

                    if sender_button == "pushButton_2" or sender_button == "pushButton_3":
                        obs_paths=f"{obs_paths}\\data\\obs-plugins\\frontend-tools\\scripts\\"


                    with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                        # 解压到目标文件夹
                        zip_ref.extractall(obs_paths)  
                        # print(obs_paths)                      
                    os.remove(downloaded_file_path)


            if sender_button == "pushButton":
                # 获取当前工作目录
                current_directory = os.getcwd()
                os.chdir(download_directory)
                # 定义输入文件名的前缀和输出文件名
                input_prefix = 'OBS-Studio-29.1.3-Full-Installer-x64'
                output_filename = 'OBS-Studio-29.1.3-Full-Installer-x64.exe'

                # 获取分割文件列表
                split_files = [f for f in os.listdir() if f.startswith(input_prefix)]
                # 按文件名排序，确保按顺序合并
                split_files.sort()
                # 创建一个新的输出文件，将分割文件内容合并到其中
                with open(output_filename, 'wb') as output:
                    for split_file in split_files:
                        with open(split_file, 'rb') as input_file:
                            output.write(input_file.read())                
                os.remove('OBS-Studio-29.1.3-Full-Installer-x64.exe_1.zip')
                os.remove('OBS-Studio-29.1.3-Full-Installer-x64.exe_2.zip')
                os.chdir(current_directory)
               
    except Exception as e:
        # 捕获所有类型的异常，并将异常信息存储在变量 e 中
        print(f"发生异常：{e}")
        return "plugin_0"
        # 进一步处理异常，例如记录日志、通知用户或采取其他操作


    return "plugin"
