import requests,logging,time,re,json,os,zipfile,glob
#######蓝奏下载方式
def lanzou_download(url):
    file_path=None
    # 替换成你的蓝奏云下载地址
    try:
        resp_url = re.sub(r'(?<=lanzou)[a-z]', 'i', url)

        # 设置自定义UserAgent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

        response1 = requests.get(resp_url, headers=headers)
        res_text1=response1.text
        matches_dat = re.findall(r'[0-9a-zA-Z_]{30,1000}', res_text1)[0]
        matches_name = re.findall(r'(?<=<title>).*?(?=<)', res_text1)
        matches_size = re.findall(r'文件大小：(.*?)\|', res_text1)
        cleaned_file_name = matches_name[0].replace(" - 蓝奏云", "")

        url2=f"https://wws.lanzoui.com/fn?{matches_dat}"
        response2 = requests.get(url2, headers=headers)
        res_text2=response2.text
        matches_dat = re.findall(r'[0-9a-zA-Z_]{30,1000}',res_text2 )
        matches_dat=matches_dat[0]
        #正则表达式获取数值
        def matches_vul(data):               
            match0 = r"{}(.*?),".format(re.escape(data))
            match1 = re.findall(match0,res_text2)[0]
            match2 = match1.split(":")[1].strip()
            websignkey_pattern = r"{}(.*?);".format(re.escape(match2))
            websignkey = re.findall(websignkey_pattern, res_text2)[0]
            match3 = re.findall(r"'(.*?)'", websignkey)[0]    
            return match3

        websignkey=matches_vul('websignkey')
        url3 = "https://www.lanzoui.com/ajaxm.php"

        # 请求头信息
        headers3 = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://wws.lanzous.com',
            'Referer': f'https://wws.lanzoui.com/fn?{matches_dat}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

        if not websignkey== " ":
            data = {
                'action': 'downprocess',
                'sign': f'{matches_dat}'  # 这里需要替换为实际的sgin值
            }       
        else:
            signs = matches_vul("signs")
            websignkey = matches_vul("websignkey")
            websign = matches_vul("websign")
            data = {
                'action': 'downprocess',
                'signs': f'{signs}',
                'sign': f'{matches_dat}',
                'ves': '1',
                'websign': f'{websign}',
                'websignkey': f'{websignkey}'
            }

        # 发送POST请求    
        response = requests.post(url3, headers=headers3, data=data) 
        get_link_data=json.loads(response.text)
        full_url = get_link_data["dom"] + "/file/" + get_link_data["url"]
        headers4 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'DNT': '1',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'Referer': f'{resp_url}'  # 请替换为实际的蓝奏地址
        }

    
        # 发送GET请求获取文件内容
        response = requests.get(full_url, headers=headers4)
        if response.status_code == 200:
            if not os.path.exists('filecache'):
                os.mkdir('filecache')

            # # 构建完整的文件路径
            file_path = os.path.join('filecache', cleaned_file_name)

            # 保存文件
            with open(file_path, 'wb') as file:
                file.write(response.content)

            # print(f'文件已保存到: {file_path}')
            return file_path
        else:
            print(f'下载失败，HTTP响应码: {response.status_code}')
            return None
    except Exception as e:
        logging.exception(f'下载出错: {str(e)}')
        return None

#######解压并获取解压文件路径
def zip2file(zip_file_path):      #这样函数的参数可以输入一个，也可以输入两个，很实用
    try:
        output_dir = os.path.dirname(os.path.abspath(zip_file_path))
        # 解压文件中的单个文件到指定的目标路径
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 获取压缩文件中的唯一文件名
            file_name = zip_ref.namelist()[0]

            # 构建解压后的文件路径
            extracted_file_path = os.path.join(output_dir, file_name)

            # 解压单个文件
            zip_ref.extract(file_name, output_dir)
        return extracted_file_path
    except Exception as e:
        logging.error(f'解压文件失败: {str(e)}')
        return None

#######从蓝奏获取软件启动版本
def lanzouwebver(url):
    try:
        resp_url = re.sub(r'(?<=lanzou)[a-z]', 'i', url)

        # 设置自定义UserAgent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        }

        response1 = requests.get(resp_url, headers=headers)
        res_text1=response1.text
        # matches_dat = re.findall(r'[0-9a-zA-Z_]{30,1000}', res_text1)[0]
        matches_name = re.findall(r'(?<=<title>).*?(?=<)', res_text1)[0]
        return matches_name
    except Exception:
        return None
    
####### 文件分割
def split_file(filename):
    """
    将文件按照指定大小进行分割，并保存为 Zip 格式的压缩文件。

    参数：
    filename: 要分割的文件名
    chunk_size: 每个分割文件的大小，单位为 MB，默认为 96MB
    """
    # 指定的分割文件大小（96M）
    chunk_size = 95 * 1024 * 1024
    
    # 打开原始文件
    with open(filename, 'rb') as f:
        part_num = 0
        while True:
            # 读取指定大小的数据
            chunk = f.read(chunk_size)
            if not chunk:
                break
            # 创建分割后的文件名
            part_filename = f"{filename}_{part_num}.zip"
            # 写入数据到分割文件
            with open(part_filename, 'wb') as part_file:
                part_file.write(chunk)
            part_num += 1

# split_file("xiaodlbuild.exe")

#####文件合并
def merge_files(file_path):
    """
    将分割后的文件合并成原始文件。

    参数：
    filename: 合并后的文件名
    """
    merged_abs_path=None
    # 提取文件名部分
    file_name = os.path.basename(file_path)

    # 使用正则表达式提取文件名中的主要部分
    match = re.match(r'(xiaodlbuild.+)\_\d+\.zip', file_name)
    if match:
        filename = match.group(1)

        # 获取当前工作目录
        current_directory = os.getcwd()
        os.chdir(".\\filecache")

        # 获取分割文件的数量
        num_parts = 0
        while os.path.exists(f"{filename}_{num_parts}.zip"):
            num_parts += 1
        # 创建合并后的文件
        with open(filename, 'wb') as merged_file:
            # 逐个读取分割文件并写入合并后的文件
            for i in range(num_parts):
                part_filename = f"{filename}_{i}.zip"
                with open(part_filename, 'rb') as part_file:
                    merged_file.write(part_file.read())
                # 删除已合并的分割文件
                os.remove(part_filename)  

        # 获取合并后文件的绝对路径
        merged_abs_path = os.path.abspath(filename)  
        os.chdir(current_directory)

    return merged_abs_path


# print(merge_files(r"E:\WinData\桌面\obspy20121024\obspy\filecache\xiaodlbuild.exe_1.zip"))