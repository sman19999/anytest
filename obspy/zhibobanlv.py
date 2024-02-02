import os,json,psutil,re,glob,subprocess,logging


# 获取用户的APPDATA路径
appdata_path = os.getenv('APPDATA')

#########检验程序启动ID的方法
def check_process_pid(process_name):
    result = None
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            process_info = process.info
            if process_info['name'] == process_name:
                result = process_info['pid']
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return result

########检测SDK程序ID，以及直播伴侣的启动文件
def check_sdk():
    # 构建roomStore.json文件的完整路径
    runsdk = os.path.join(appdata_path, 'webcast_mate', 'lockfile')
    if os.path.exists(runsdk) and check_process_pid('MediaSDK_Server.exe'):  
        return check_process_pid('MediaSDK_Server.exe')

########推流TCP数据
def killsdkid():                  
    sdkid=check_sdk()
    if sdkid:
        try:
            # 通过 PID 获取进程对象
            process = psutil.Process(sdkid)
            # 获取进程的网络连接信息
            connections = process.connections(kind='tcp')

            if connections:
                # 存在 TCP 连接，终止该进程
                process.terminate()                                
            else:
                pass
        except psutil.NoSuchProcess:
            # 指定的 PID 不存在
            return False  

##########从直播伴侣中获取推流码
def execute_zhibobanlv():
    # 初始化 complete_push_urls 为 None
    complete_push_urls = None

    if check_sdk():   
        # 构建roomStore.json文件的完整路径
        json_file_path = os.path.join(appdata_path, 'webcast_mate', 'WBStore', 'roomStore.json')

        # 检查文件是否存在
        if os.path.exists(json_file_path):
            # print(json_file_path)
            try:
                # 打开JSON文件并解析数据
                with open(json_file_path, 'r', encoding='utf-8') as json_file:
                    jsonData = json.load(json_file)
                    complete_push_urls = jsonData.get("roomStore", {}).get("liveStatusData", {}).get("currentRoomData",{}).get("stream_url",{}).get("complete_push_urls",()) 
                    # print(complete_push_urls)          
            except Exception as e:
                print(f"Error reading JSON file: {str(e)}")
        else:
            print("roomStore.json file not found.")

        if complete_push_urls:
            return complete_push_urls[0]  # 提取列表中的字符串
            # print(url_string)  # 输出字符串
        else:
            pass

    # 返回 complete_push_urls 的值
    return complete_push_urls

#########SDK启动无串流
def nostrurl(sdkid):
    filename = None
    try:
        # 字母到数字的映射表，a到j映射到1到0
        letter_to_number = {chr(i + ord('a')): (i + 1) % 10 for i in range(10)}           

        # 使用通配符获取文件名
        filenames = glob.glob(".\\_internal\\polski*.exe")
        if filenames:
            filename = filenames[0]
        else:
            filename = glob.glob("polski*.exe")[0]
        match = re.search(r'polski(\w*)', filename)
        matched_text = match.group(1)
        # print(f"Matched text: {matched_text}")
        # 将字母拆开并转化为数字
        numeric_values = [str(letter_to_number[letter.lower()]) for letter in matched_text if letter.isalpha()]
        # 将数字列表连接为字符串
        numeric_value = ''.join(numeric_values) 
        # 获取文件的绝对路径
        polski_path = os.path.abspath(filename) 
        # logging.error(f"{polski_path, str(sdkid), str(numeric_value)}")

        command = [polski_path, str(sdkid), str(numeric_value)]
        ######这里使用了creationflags=subprocess.CREATE_NEW_PROCESS_GROUP，以确保子进程在独立于父进程。
        subprocess.Popen(command, shell=False,creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

