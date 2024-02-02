from cryptography.fernet import Fernet
import requests,winreg,re,os,subprocess,shutil,logging,json_dbase
from datetime import datetime, timezone 
from pathlib import Path  # 导入Path模块
from lanzou import lanzou_download,zip2file,lanzouwebver,merge_files


key0=b'oyUZ__6GOJG71Mne7bwCykk0qRR1ZO1VZmsUvW3o7A8='
keyday0=b'paH_54RL2mrmHw_OIZ5rZxscYJ2u-Q_A9kg97PysvpI='
three_days_in_seconds = 3 * 24 * 60 * 60  # 3天 * 24小时 * 60分钟 * 60秒 *1000毫秒
appdata_path = os.getenv('APPDATA')
####加密或解码直接的数据必须为字节
##########会员加密文件
def encrypt_file(file_path,file_data, key):
    fernet = Fernet(key)
    ####file_data.encode('utf-8')转为字节
    encrypted_data = fernet.encrypt(file_data.encode('utf-8'))
    with open(file_path, "wb") as file:
        #####以字节保存
        file.write(encrypted_data)

##########会员解密文件
def decrypt_file(filename, key):
    fernet = Fernet(key)
    with open(filename, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    ##解码后从字节转为字符串
    txet_decrypted_data=decrypted_data.decode("utf-8")    
    # print(decrypted_data.decode("utf-8"))  # 打印解密后的数据
    # with open(filename, "wb") as file:
    #     file.write(decrypted_data)
    return txet_decrypted_data

#########简单加密
def custom_encode(data):
    #data是数据字符串，否则出错，如果是字典要转化为字符串
    key = 0xF9
    encoded_data = bytearray(data.encode('utf-8'))

    for i in range(len(encoded_data)):
        encoded_data[i] ^= key
    return bytes(encoded_data)

#########简单解密
def custom_decode(file_path):
    #要求encoded_data是字节组，所以用rb读取
    ##file_path为文件路径，直接读取文件内容
    with open(file_path, 'rb') as file:
        encoded_data = file.read()
    # 解码时再次进行异或运算
    key = 0xF9
    decoded_data = bytearray(encoded_data)

    for i in range(len(decoded_data)):
        decoded_data[i] ^= key

    return decoded_data.decode('utf-8')

#########电脑UUID获取
def uuid_winc():
    cmd = 'wmic csproduct get UUID'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    # print(result.stdout)
    # 检查命令是否成功执行
    # 使用正则表达式提取UUID
    uuid_match = re.search(r'[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}', result.stdout)
    
    # 提取到的UUID
    extracted_uuid = uuid_match.group(0) if uuid_match else None
    # 去掉连字符
    uuid_without_hyphen = extracted_uuid.replace("-", "")
    # print(uuid_without_hyphen)   

    # # 生成一个随机的起始索引
    # start_index = random.randint(0, len(uuid_without_hyphen) - 4)

    # # 获取任意连续的4个字符的值
    # random_substring = uuid_without_hyphen[start_index:start_index + 4]
    return uuid_without_hyphen

#########百度web报头获取
def get_website_datetime(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        server_time_str = response.headers.get('Date')
        if server_time_str:
            server_datetime = datetime.strptime(server_time_str, '%a, %d %b %Y %H:%M:%S %Z')
            server_timestamp = int(server_datetime.replace(tzinfo=timezone.utc).timestamp())
            return server_timestamp
    except requests.exceptions.RequestException:
        pass

    return None

#########QQ时间戳获取
def get_time_from_qq_urls():
    qq_urls = [
        "http://vv.video.qq.com/checktime?otype=json",
        "http://vv6.video.qq.com/checktime?otype=json",
    ]

    for url in qq_urls:
        try:
            response = requests.get(url)
            matches = re.findall(r'\d{10,}', response.text)
            if matches:
                return matches[0]
        except requests.exceptions.RequestException:
            pass

    return None

#########北京时间
def bjtime():
    time_now = get_time_from_qq_urls()
    if time_now is None:
        time_now = get_website_datetime("http://www.baidu.com")
    # 判断是否为13位时间戳，如果不是，转换为13位
    # if time_now and len(str(time_now)) != 13:
    #     time_now = int(time_now)*1000
    return time_now

#########获取注册表某个数据
def get_registry_value(key_path, value_name):
    try:
        # 打开注册表键
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

        # 尝试获取键值
        value, _ = winreg.QueryValueEx(key, value_name)

        # 关闭注册表键
        winreg.CloseKey(key)

        return value
    except Exception as e:
        # print(f"获取注册表值时发生错误: {e}")
        logging.exception(f"获取注册表值时发生错误")
        return None

#########写入注册表数据
def set_registry_value(key_path, value_name, value_data):
    try:
        # 尝试打开注册表键
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        # 如果键不存在，创建它
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)

    try:
        # 设置键值
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)

        # print(f"成功将值 {value_data} 写入注册表键 {key_path}\\{value_name}")
    except Exception as e:
        print(f"写入注册表值时发生错误: {e}")
        pass
    finally:
        # 关闭注册表键
        winreg.CloseKey(key)

#########首次试用时间，写入文件和注册表
def firstinstall(nowtime):
    nowtimes=int(nowtime)
    encrypted_data=firsttiems=None
    lasstime=0
    appdata_path = os.getenv('APPDATA')
    t_key=key0
    fernet = Fernet(t_key)
    # 构建roomStore.json文件的完整路径
    roaming_path = os.path.join(appdata_path, 'Microsoft','Crypto', 'ins.txt')
    # 指定注册表键路径和值名称
    key_path = r"Software\\Microsoft\\Clients\\Media\\MediaCast\\InstallInfo"
    value_name = "instime"
    # value_data = "YourValueHere"
    try:
        if os.path.exists(roaming_path):
            # 获取文件的修改时间戳
            timestamp = os.path.getmtime(roaming_path)
            if nowtimes-timestamp<three_days_in_seconds:
                firsttiems=decrypt_file(roaming_path, t_key)
                ###获取前10位
            else:
                return 0
        if not firsttiems:
            encrypted_data=get_registry_value(key_path, value_name)
            if encrypted_data:
                decrypted_data = fernet.decrypt(encrypted_data.encode('utf-8'))
                firsttiems = decrypted_data.decode('utf-8', errors='replace') 
        if firsttiems and len(firsttiems)>3:
            firsttiems=re.search(r'\d{10}', firsttiems).group()
            if nowtimes-int(firsttiems)<three_days_in_seconds:
                lasstime = int(firsttiems) + three_days_in_seconds
                wirtetime=firsttiems
            else:
                return 0
        else: 
            lasstime = nowtimes + three_days_in_seconds
            wirtetime=nowtime
        # times.encode('utf-8')转换为字节
        if not os.path.exists(roaming_path) or not encrypted_data:
            encrypted_data = fernet.encrypt(wirtetime.encode('utf-8'))
            Path(os.path.dirname(roaming_path)).mkdir(parents=True, exist_ok=True)  
            with open(roaming_path, 'wb') as file:
                file.write(encrypted_data)
            #写入注册表
            set_registry_value(key_path, value_name, encrypted_data.decode('utf-8'))
 
        return lasstime 
    except Exception as e:
        logging.error("首次运行检查出错：")
        return 0

#########会员启动验证，有两个文件之一
def check_Membership(nowtimestr):
    global three_days_in_seconds
    now_time=int(nowtimestr) 
    key_value=None
    t1_key = key0 
    fernet = Fernet(t1_key)
    key_path = r"Software\\Microsoft\\Clients\\Media\\MediaCast\\Capabilities"
    value_name = "userky"
    # d0_key = keyday0  # 假设load_key()函数返回一个密钥，如果是字符串请进行相应处理
    file_path = os.path.join('xDLCache', 'Cookies.file')
    datav_path = os.path.join('xDLCache', 'data_v.file')
    roaming_path = os.path.join(appdata_path, 'Microsoft','Crypto', 'UserMD5',"ukey.md5")
    try:
        if os.path.exists(datav_path) or os.path.exists(roaming_path):
            if os.path.exists(datav_path):
                with open(datav_path, "rb") as file:
                    byte_datav = file.read()
                key_value = byte_datav.decode('utf-8', errors='replace')
            if not key_value:
                if not os.path.exists(roaming_path):
                    key_value=get_registry_value(key_path, value_name)
                else:
                    with open(roaming_path, "rb") as file:
                        byte_data = file.read()
                    key_value = byte_data.decode('utf-8', errors='replace')

            if key_value and len(key_value)>40:  
                # 指定要去除的位置
                positions_to_diy = [9, 19, 29, 39]
                # 通过列表解析取出指定位置的字符
                extracted_characters = [key_value[position] for position in positions_to_diy]
                # 将提取的字符列表转换为字符串
                extracted_characters_str = ''.join(extracted_characters)
                if extracted_characters_str in uuid_winc():
                    # if now_time/1000-os.path.getmtime('.\\xDLCache\\0003.file')>100000:
                    # 通过列表解析去除指定位置字符后的字符串
                    original_string = ''.join([char for i, char in enumerate(key_value) if i not in positions_to_diy])
                    decrypted_data = fernet.decrypt(original_string.encode('utf-8'))
                    vipfile_data=decrypted_data.decode("utf-8") 
                    matches=int(re.search(r'\d{10}', vipfile_data).group())
                    if matches-now_time>0:
                        if not os.path.exists(file_path) or now_time-os.path.getmtime('.\\xDLCache\\Cookies.file')>100000:
                            f_path = lanzou_download("https://sman19999.lanzoub.com/xiaodoulidislist1000")  
                            if not f_path:
                                f_path = lanzou_download("https://sman19999.lanzoub.com/xiaodoulidislistbak1000")
                                if not f_path:
                                    return None
                            disdata = custom_decode(zip2file(f_path))
                            # original_string_4=original_string+extracted_characters_str
                            if key_value in disdata:
                                os.remove(roaming_path)
                                os.remove(datav_path)
                                return None 
                            if not os.path.exists(roaming_path):
                                # print("3")
                                Path(os.path.dirname(roaming_path)).mkdir(parents=True, exist_ok=True) 
                                with open(roaming_path, "wb") as file:
                                    #以字节保存
                                    file.write(key_value.encode('utf-8'))
                            if not os.path.exists(datav_path) or not byte_datav:
                                with open('.\\xDLCache\\data_v.file', 'wb') as f:
                                    f.write(key_value.encode('utf-8'))   

                        return matches
                    else:
                        os.remove(datav_path) 
                        os.remove(roaming_path)                       
        else:
            fisrttime=firstinstall(nowtimestr)
            if now_time - fisrttime <0:                      ####试用期的时间

                # 使用datetime模块将时间戳转化为时间
                return fisrttime
        return None

    except Exception as e:
        logging.error(f"An error check:{e}")
        # 捕获其他异常
        return None

######开机检验版本
def check_version(nowtimestr):
    verlut=None
    recent_change_time=0
    try:
        if not os.path.exists('xDLCache'):
            os.makedirs('xDLCache')        
        file_path = os.path.join('xDLCache', 'Cookies.file') 
        #获取文件时间戳
        if os.path.exists(file_path):
            recent_change_time = os.path.getmtime(file_path) 
        # 获取当前日期的时间戳   
        current_timestamp = int(nowtimestr)
        # 将时间戳转换为日期对象
        current_date = datetime.fromtimestamp(current_timestamp)
        # 获取日期的天数
        day_of_month = current_date.day
        if not os.path.exists(file_path) or (current_timestamp - recent_change_time > 100000 and day_of_month % 2 == 0):
            verlut = lanzouwebver("https://sman19999.lanzoub.com/xiaodoulidownloadp0")
            if verlut is None:
                verlut = lanzouwebver("https://sman19999.lanzoub.com/xiaodoulidownloadp1")  
                if verlut is None:
                    return None
            # # 创建文件
            # with open(file_path, 'w') as file:
            #     file.write('gAAAAABlnBO6SpzMZaQ83EBcF3nfCy0xVhIP7l0IFzM5RteIaaKxOswhajSB9e4g_m3CFk8XS_i7lRGcA6a-HDD1cvD55rL66xqGbxWT4QcgAqOTWgSHKsLLeWeKJFIWlQiT8fDM=')
            return verlut
        else:
            return "noRequired"
    except Exception as e:
        logging.error("check_version error:{e}")
        # 捕获其他异常
        return None   


######软件固件自动下载和更新
def softBuild_download():
    try:
        # 构建完整的下载文件夹路径
        download_directory = os.path.join('filecache')
        # 检查下载文件夹是否存在，如果不存在则创建它
        if os.path.exists(download_directory):
            shutil.rmtree(download_directory)
        os.makedirs(download_directory)
        # 检查按钮名称是否存在于配置中
        urls=json_dbase.data["xiaodouli"]["xdldownload_url"]
        for url in urls:
            softbuilt=lanzou_download(url)
        return merge_files(softbuilt)
    except Exception as e:
        logging.error(f"软件自动更新失败,{e}")
        return None
    

####会员充值的KEY验证######
def check_key(key_value):   
    t1_key = key0
    fernet = Fernet(t1_key)
    key_path = r"Software\Microsoft\Clients\Media\MediaCast\Capabilities"
    value_name = "userky"
    roaming_path = os.path.join(appdata_path, 'Microsoft','Crypto', 'UserMD5',"ukey.md5")
    # with open(filename, "rb") as file:
    #     encrypted_data = file.read()
    try:
        if len(key_value)>40:             
            positions_to_diy = [9, 19, 29, 39]
            extracted_characters = [key_value[position] for position in positions_to_diy]
            extracted_characters_str = ''.join(extracted_characters)
            # print(extracted_characters_str)
            if extracted_characters_str in uuid_winc():
                # 通过列表解析去除指定位置字符后的字符串                
                original_string = ''.join([char for i, char in enumerate(key_value) if i not in positions_to_diy])   
                # print(original_string) 
                decrypted_data = fernet.decrypt(original_string)
                vipfile_data=decrypted_data.decode("utf-8")       
                # vipfile_data = decrypt_file(original_string, t1_key)
                # print(vipfile_data)
                ######以后可以去除这部分
                vip_time=int(re.search(r'\d{10}', vipfile_data).group())
                # print(vip_time)
                if vip_time-int(bjtime())>0:
                    # print("充值验证")
                    f_path = lanzou_download("https://sman19999.lanzoub.com/xiaodoulidislist1000")  
                    if not f_path:
                        f_path = lanzou_download("https://sman19999.lanzoub.com/xiaodoulidislistbak1000")
                        if not f_path:
                            return None
                    disdata=custom_decode(zip2file(f_path))               
                    # original_string_4=original_string+extracted_characters_str
                    if key_value in disdata:
                        return None
                    # print(disdata)

                    # 获取用户主目录
                    Path(os.path.dirname(roaming_path)).mkdir(parents=True, exist_ok=True) 
                    with open(roaming_path, "wb") as file:
                        #以字节保存
                        file.write(key_value.encode('utf-8'))
                    with open('.\\xDLCache\\data_v.file', 'wb') as f:
                        f.write(key_value.encode('utf-8'))   
                    # set_registry_value(key_path, value_name, key_value) 
                    # print("2")           
                    converted_time = datetime.fromtimestamp(vip_time)
                    # 将时间格式化为字符串
                    formatted_time = converted_time.strftime('%Y-%m-%d %H:%M')
                    vipdays = f"会员期:{formatted_time}"
                    return vipdays  
        return None      
    except Exception as e:
        logging.error(f"充值错误{e}")
        print(e)
        return None




