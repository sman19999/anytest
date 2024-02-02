#####抖音登录入口#####
# douyindouyin_url = {
# https://www.douyin.com/user/self,
# https://www.douyin.com/,
# https://sso.douyin.com/,
# https://anchor.douyin.com/login?&login_after_redirect=/,
# https://creator.douyin.com/?next=https%3A%2F%2Fcreator-hl.douyin.com%2Fcontent%2F,
# }
import time,requests,re,json,os,sqlite3,base64,logging,webview,queue,threading,shutil,sys
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from about_version import custom_encode
from http.cookies import SimpleCookie
webstartmode=douyin_cookie_string=None
# 创建一个队列用于线程间通信
data_queue = queue.Queue()
stop_flag=False
# 创建一个锁对象
stop_flag_lock = threading.Lock()
def thread_send(conn):
    global data_queue,stop_flag,webstartmode
    running = True    
    while running:
        connany=None
        if conn.poll(1):
            connany = conn.recv()
        if connany:
            if webstartmode=="1":
                running = False
                sys.exit()
            with stop_flag_lock:
                stop_flag=True
        if not data_queue.empty():
            data = data_queue.get()
            if "finst2_pictrue" in data:
                data = data.replace('finst2_pictrue', 'base64,')
                conn.send(data)
                running = False  # 设置标志，结束循环
            else:
                conn.send(data)
        time.sleep(0.2)

def process_data_from_js(data):
    global data_queue
    # 处理从JavaScript接收的数据
    # print("Data received from JavaScript:", data)
    # 将数据放入队列
    data_queue.put(data)

def find_img_src(html_tree, class_name):
    parent_elements = html_tree.xpath(f'//*[@class="{class_name}"]')
    if parent_elements:
        img_elements = parent_elements[0].xpath('.//img')
        if img_elements:
            return img_elements[0].get('src')
    return None

def pyweb_douyin(window):
    global webstartmode,douyin_cookie_string,stop_flag
    html_source_str=html_tree=None
    check0=False
    with stop_flag_lock:
        stop_flag=False
    for i in range(40):
        jpeg_src=None
        print(stop_flag)
        if i==39 or stop_flag:
            time.sleep(0.8)
            window.destroy()
            break    
        time.sleep(1) 
        # print("正在获取网页源码")   
        html_source_str = str(window.evaluate_js('document.documentElement.outerHTML;'))
        html_tree = etree.HTML(html_source_str)
        title_val=window.evaluate_js("document.title;")
        if html_tree is not None:
            # print("获取到网页源码")
            if webstartmode=="0" and ("验证码" in title_val or "账号安全" in html_source_str or "短信验证" in html_source_str):
                logging.error("验证码提示")
                window.evaluate_js(f'pywebview.api.process_data_from_js("verificationCode")')
                time.sleep(0.5)
                window.destroy()
                break
            #####二维码获取
            elif not check0 and "semi-tabs-pane-motion-overlay" in html_source_str:
                img_src=find_img_src(html_tree, "semi-tabs-pane-motion-overlay")                
                if img_src is not None and "base64" in img_src:
                    window.evaluate_js(f'pywebview.api.process_data_from_js("{img_src}")')
                    check0 = True
            #####https://anchor.douyin.com/login头像获取
            elif "semi-avatar semi-avatar-circle semi-avatar-medium semi-avatar-img" in html_source_str:
                # 使用XPath表达式找到具有特定类名的元素
                class_elements = html_tree.xpath('//*[contains(@class, "semi-avatar-img") and contains(@class, "semi-avatar")]')
                if class_elements:
                    img_elements = class_elements[0].xpath('.//img')
                    if img_elements:
                        jpeg_src=img_elements[0].get('src')
            #####https://www.douyin.com/头像获取
            elif "hY8lWHgA hiGJ2DUn E33RhcjA" in html_source_str:
                jpeg_src=find_img_src(html_tree, "hY8lWHgA hiGJ2DUn E33RhcjA")                
                if jpeg_src is not None:
                    jpeg_src = "https:" + jpeg_src
            ###########头像获取后处理
            if jpeg_src:
                # 获取远程图片的二进制数据
                # print(jpeg_src)
                img_response = requests.get(jpeg_src)
                # 将二进制数据转换为 base64 编码
                base64_data = base64.b64encode(img_response.content).decode('utf-8')                
                with open('.\\xDLCache\\data_p.file', 'w') as file:
                    file.write(base64_data)  
                window.evaluate_js(f'pywebview.api.process_data_from_js("finst2_pictrue{base64_data}")')
                #####获取cookies方法一，比较全面
                douyin_cookie_string = ""
                cookies = window.get_cookies()
                # print(cookies)
                for c in cookies:
                    try:
                        dy_cookie=c.output()
                        # print(cookie_name)
                        dy_cookie= dy_cookie.replace("Set-Cookie:", "")         
                        # 使用 SimpleCookie 解析 Set-Cookie 头部信息                     
                        # 尝试解析 Cookie 头部信息
                        douyincookie = SimpleCookie()
                        douyincookie.load(dy_cookie)
                        # 遍历解析的 Cookie，提取属于 .douyin.com 的键值对
                        for key, morsel in douyincookie.items():
                            if key.strip() and morsel['domain'] == '.douyin.com':
                                douyin_cookie_string += f"{key}={morsel.value};"
                    except Exception as e:
                        # 捕获异常并记录日志，或者采取其他适当的处理措施
                        print(f"Error while parsing cookie: {e}")
                if douyin_cookie_string:
                    encodedata=custom_encode(douyin_cookie_string)  
                    # print(encodedata)         
                    with open('.\\xDLCache\\data_c.file', 'wb') as file:
                        file.write(encodedata)
                    # 使用JavaScript API将数据传递给Python函数
                    # window.evaluate_js(f'pywebview.api.process_data_from_js("{douyin_cookie_string}")')
                    time.sleep(0.8)
                    window.destroy()
                    break
######抖音web登录，pywebview启动
def get_douyin_login(webmode):
    global webstartmode,douyin_cookie_string
    appdata_path = os.getenv('APPDATA')
    pywebview_path = os.path.join(appdata_path, 'pywebview','EBWebView','Default')
    if os.path.exists(pywebview_path):
        shutil.rmtree(pywebview_path)
    webstartmode=webmode
    if webmode == "0":
        # 提供有效的网页 URL
        url = "https://anchor.douyin.com/login"
        # 创建窗口并加载网页，同时隐藏窗口
        window = webview.create_window('douyinlogin', url,width=1280,height=720,hidden=True)    
    else:
        # 提供有效的网页 URL
        url = "https://www.douyin.com"
        # 创建窗口并加载网页，同时隐藏窗口
        window = webview.create_window('douyinlogin', url,width=800,height=600)
    window.expose(process_data_from_js)
    # 在窗口中执行获取元素的操作
    webview.start(pyweb_douyin, window,private_mode=False)

    return douyin_cookie_string

#####抖音web登录方式,webdriver启动太慢
def get_douyinlogin(conn,webmode=0):
    douyin_cookie_string = ""
    print(f"抖音登录入口{webmode}")

    # 创建一个 Edge WebDriver 实例，加入 headless 选项
    try:
        user_home = os.path.expanduser("~")
        
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('--window-size=1920,1080')
        edge_options.add_argument(f"--user-data-dir={user_home}\\EdgeUserData\\")###此处填任意文件夹路径，防止浏览器显示data：
        # 屏蔽inforbar和edge/chrome正由自动测试软件控制，非常重要
        edge_options.add_experimental_option('useAutomationExtension', False)
        edge_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        edge_options.add_argument('disable-infobars')#不显示Chrome正在受自动软件控制 
        # edge_options.page_load_strategy = 'eager'
        if webmode==0:
            # 使用 edge 浏览器，并设置为无头模式    
            edge_options.add_argument("--headless")
            edge_options.add_argument("--disable-gpu")
            # 启动 Chrome 浏览器
            edge_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
            login_url = "https://www.douyin.com/user/self"
        else:
            login_url = "https://www.douyin.com/"
        ######### 使用 webdriver_manager 自动下载并配置 EdgeWebDriver
        Service_path=webdriver.EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(options=edge_options,service=Service_path)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })
        # 打开网页
        driver.get(login_url)  # 替换成你要获取标题的网页地址
        #### 创建 ActionChains 对象
        actions = ActionChains(driver)
        #### 移动鼠标到初始位置
        actions.move_by_offset(198, 97).perform()
        time.sleep(0.3)
        # # 进行其他操作，比如点击
        # actions.click().perform()
        # #移动鼠标到另一个位置
        actions.move_by_offset(311, 356).perform()
        for n in range(15):
            # 获取网页标题
            title = driver.title
            if "验证码" in title and webmode==0:
                logging.error("验证码提示")
                return None
            elif "web-login-container" in driver.page_source:
                if webmode==0:
                    try:
                        qrcode_element = driver.find_element(By.XPATH, '//*[@class="web-login-scan-code__content"]')
                        # 获取父元素内的 <img> 元素
                        img_element = qrcode_element.find_element(By.TAG_NAME, 'img')

                        # 获取 <img> 元素的 src 属性（即图片地址）
                        qrcode_image_src = img_element.get_attribute('src')
                        # print(f"QR Code URL: {qrcode_image_src}")
                        conn.send(qrcode_image_src)
                        break
                    except NoSuchElementException:
                        pass
                elif webmode==1:
                    break
            elif n==14 and not "web-login-container" in driver.page_source:
                return None

        # 等待用户扫码登录
        for i in range(60):
            time.sleep(1)
            if ("身份"in driver.page_source or "账号安全" in driver.page_source or "短信验证" in driver.page_source) and webmode==0:
                conn.send("二维码消失")
                logging.error("短信身份验证失败")
                return None
            ############################################################# 使用 WebDriver 查找具有 id="douyin-header" 的元素
            elif not "web-login-container" in driver.page_source and not "登录" in driver.find_element(By.ID, "douyin-header").text:      
                try:###定位唯一class标识
                    # douyin_header_element = driver.find_element(By.XPATH, '//*[@class="ScPBK7Wg eRChRJCd ja0bZiHO"]')
                    
                    douyin_header_element = driver.find_element(By.XPATH, '//*[@class="hY8lWHgA hiGJ2DUn E33RhcjA"]')
                    # 获取父元素内的 <img> 元素
                    img_element = douyin_header_element.find_element(By.TAG_NAME, 'img')

                    # 获取 <img> 元素的 src 属性（即图片地址）
                    img_src = img_element.get_attribute('src')

                    # 获取远程图片的二进制数据
                    img_response = requests.get(img_src)
                    # 将二进制数据转换为 base64 编码
                    base64_data = base64.b64encode(img_response.content).decode('utf-8')
                    with open('.\\xDLCache\\data_p.file', 'w') as file:
                        file.write(base64_data)
                    conn.send(f"base64,{base64_data}")
                    logging.info("登录成功")
                    time.sleep(6)
                    # 获取 Cookie
                    initial_cookies = driver.get_cookies()
                    for cookie in initial_cookies:
                        if '.douyin.com' == cookie['domain']:
                            douyin_cookie_string += f"{cookie['name']}={cookie['value']}; "
                    encodedata=custom_encode(douyin_cookie_string)  
                    # print(encodedata)         
                    with open('.\\xDLCache\\data_c.file', 'wb') as file:
                        file.write(encodedata)
                    # 保存douyin_cookie_string 到文件
                    # print("保存成功")
                    return douyin_cookie_string
                except NoSuchElementException:
                    pass  
            elif i==59:
                conn.send("二维码消失")
        return None
    finally: 
        # 关闭浏览器
        driver.quit()

#####直播伴侣cookies登录方式
def local_wast_cookies(conn):
    douyin_cookie_string = ""
    wastpath=os.getenv("APPDATA")
    # 指定直播伴侣的Cookies文件路径
    cookies_file_path = os.path.join(wastpath, "webcast_mate", "Network", "Cookies")
    img_file_path = os.path.join(wastpath, "webcast_mate", "WBStore", "userStore.json")
    if os.path.exists(cookies_file_path) and os.path.exists(img_file_path):
        try:
            with open(img_file_path, 'r', encoding='utf-8') as file:
                img_json = json.load(file)
            # 获取远程图片的二进制数据
            # 获取url_list中的地址
            img_url = img_json["userStore"]["userInfo"]["avatar_thumb"]["url_list"][0]
            img_response = requests.get(img_url)
            # 将二进制数据转换为 base64 编码
            base64_data = base64.b64encode(img_response.content).decode('utf-8')
            with open('.\\xDLCache\\data_p.file', 'w') as file:
                file.write(base64_data)
            conn.send(f"base64,{base64_data}")
            # 连接Edge浏览器的Cookies数据库
            cookies_d = sqlite3.connect(cookies_file_path)
            # 创建一个游标对象
            cursor = cookies_d.cursor()
            # 指定目标域名
            target_domains = [".douyin.com"]

            # 查询特定域名下的Cookies
            for domain in target_domains:
                cursor.execute(f'SELECT name, value FROM cookies WHERE host_key LIKE ?;', (f'%{domain}',))
                initial_cookies = cursor.fetchall()
                for cookie in initial_cookies:
                        name, value = cookie
                        douyin_cookie_string += f"{name}={value}; "
            # 关闭数据库连接
            # print(douyin_cookie_string)
            cookies_d.close()
            if douyin_cookie_string:
                encodedata=custom_encode(douyin_cookie_string)        
                with open('.\\xDLCache\\data_c.file', 'wb') as file:
                    file.write(encodedata)
                return douyin_cookie_string
            else:
                return None
        except Exception as e:
            logging.exception(e)
            return None
    else:
        return None

#####自动开播和推流码获取
def get_streamURL(conn,cookie_data,numer,equipment):
    complete_push_urls=first_avatar_url=roomid=streamid=statid=None

    if equipment==0:
        url9="https://webcast.amemv.com/webcast/room/get_latest_room/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&device_platform=windows&webcast_sdk_version=1520&resolution=1920%2A1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=3096676051989080&iid=1117559680415880"
        data9={}
        Agent_value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    else:
        url9 = "https://webcast.amemv.com/webcast/room/create/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&webcast_sdk_version=1520&device_platform=android&resolution=1920*1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=2515294039547702&iid=1776452427890550"
        # 请求数据
        data9 = {
            "multi_resolution": "true",
            "title": "我刚刚开播,大家快来看吧",
            "thumb_width": "1080",
            "thumb_height": "1920",
            "orientation": "0",
            "base_category": "416",
            "category": "1124",
            "has_commerce_goods": "false",
            "disable_location_permission": "1",
            "push_stream_type": "3",
            "auto_cover": "1",
            "cover_uri": "",
            "third_party": "1",
            "gift_auth": "1",
            "record_screen": "1"
        }
        Agent_value="Mozilla/5.0 (Linux; Android 8.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.100 Mobile Safari/537.36"

    headers9 = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded; Charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-cn",
        "Cookie": cookie_data,
        "Host": "webcast.amemv.com",
        "Referer": url9,
        "User-Agent": Agent_value,
        "Origin": "file://",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
    }
    # print(headers9)
    # 发送POST请求
    try:
        response9 = requests.post(url=url9, headers=headers9, data=data9)
        # print(response9.text)
        if response9.status_code == 200:
            # 使用JSON解析将字符串转换为Python字典
            response9_data = response9.json()
            #####获取账号图片
            if numer<3:
                avatar_urls=response9_data.get("data", {}).get("owner", {}).get("avatar_thumb", {}).get("url_list",[])
                if avatar_urls:
                    first_avatar_url=avatar_urls[0]
                    image_data=requests.get(url=first_avatar_url).content
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    base64_data="base64,"+base64_data
                    conn.send(base64_data)

            
            # 获取"complete_push_urls"字段的值
            # complete_push_urls = response9_data.get("data", {}).get("stream_url", {}).get("complete_push_urls",[])
            statid = response9_data.get("data", {}).get("status")
            print(statid)
            complete_push_urls = response9_data.get("data", {}).get("stream_url", {}).get("rtmp_push_url")
            # print(complete_push_urls)
            
            if (statid==2 and equipment==0) or (statid==1 and equipment==1):
                if complete_push_urls:
                    conn.send(complete_push_urls)
                    roomid = response9_data.get("data", {}).get("living_room_attrs", {}).get("room_id")
                    streamid = response9_data.get("data", {}).get("stream_id")


        return statid,roomid,streamid
    except Exception as e:
        logging.error(f"Error in get_live_status: {e}")
        return None,None,None

#####直播状态延续
def webcast_start(roomid,streamid,cookie_data,equipment):
    if equipment==0:
        url11="https://webcast.amemv.com/webcast/room/ping/anchor/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&device_platform=windows&webcast_sdk_version=1520&resolution=1920%2A1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=3096676051989080&iid=1117559680415880"
        Agent_value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    else:
        url11 = "https://webcast.amemv.com/webcast/room/ping/anchor/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&webcast_sdk_version=1520&device_platform=android&resolution=1920*1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=2515294039547702&iid=1776452427890550"
        # 请求数据
        Agent_value="Mozilla/5.0 (Linux; Android 8.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.100 Mobile Safari/537.36"

    headers11 = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded; Charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-cn",
        "Cookie": cookie_data,
        "Host": "webcast.amemv.com",
        "Referer": url11,
        "User-Agent": Agent_value,
        "Origin": "file://",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
    }
    # 发送POST请求
    data11 = f"stream_id={streamid}&room_id={roomid}&status=2"

    requests.post(url=url11, headers=headers11, data=data11)    

#####停止直播
def webcast_stop(roomid,streamid,cookie_data,equipment):
    if equipment==0:
        url11="https://webcast.amemv.com/webcast/room/ping/anchor/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&device_platform=windows&webcast_sdk_version=1520&resolution=1920%2A1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=3096676051989080&iid=1117559680415880"
        Agent_value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    else:
        url11 = "https://webcast.amemv.com/webcast/room/ping/anchor/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&webcast_sdk_version=1520&device_platform=android&resolution=1920*1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=2515294039547702&iid=1776452427890550"
        # 请求数据
        Agent_value="Mozilla/5.0 (Linux; Android 8.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.100 Mobile Safari/537.36"

    headers11 = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded; Charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-cn",
        "Cookie": cookie_data,
        "Host": "webcast.amemv.com",
        "Referer": url11,
        "User-Agent": Agent_value,
        "Origin": "file://",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
    }
    # 发送POST请求
    data11 = f"stream_id={streamid}&room_id={roomid}&status=4&reason_no=1"

    requests.post(url=url11, headers=headers11, data=data11)    

#非会员推流码获取
def did_webcast(did,cookie_json):
    rtmp_push_url=None
    try:
        url = f"https://webcast.amemv.com/webcast/room/continue/?device_id={did}&aid=1128&ac=wifi&app_name=webcast_mate&version_code=9.6.1&device_platform=android&webcast_sdk_version=1520&resolution=1920%2A1080&os_version=10.0.22621&language=zh&live_id=1"

        headers = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded; Charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-cn",
            "Cookie": cookie_json,
            "Host": "webcast.amemv.com",
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Origin": "file://",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
        }

        resp=requests.get(url, headers=headers)
        # print(cookie_json)

        if resp.status_code == 200:
            response_data = json.loads(resp.text)
            # txtw=response_data.get('rtmp_push_url', '')
            # print(response_data)
            # rtmp_push_url = response_data["data"]["stream_url"]["rtmp_push_url"]
            rtmp_push_url = response_data.get("data", {}).get("stream_url", {}).get("rtmp_push_url")  
            # print(txtw)
            # print("push_url:",rtmp_push_url)
            return rtmp_push_url
        else:
            return None
    except Exception as e:
        # 捕获其他异常
        # print(f"发生异常：{e}")
        return None
    
#########自动开播原代码
def creator_webcast(cookie_json):
    url = "https://webcast.amemv.com/webcast/room/create/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&webcast_sdk_version=1520&device_platform=android&resolution=1920*1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=2515294039547702&iid=1776452427890550"

    headers = {
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded; Charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-cn",
        "Cookie": cookie_json,
        "Host": "webcast.amemv.com",
        "Referer": "https://webcast.amemv.com/webcast/room/create/?ac=wifi&app_name=webcast_mate&version_code=5.6.0&webcast_sdk_version=1520&device_platform=android&resolution=1920*1080&os_version=10.0.22631&language=zh&aid=2079&live_id=1&channel=online&device_id=2515294039547702&iid=1776452427890550",
        "User-Agent": "Mozilla/5.0 (Linux; Android 8.2.1; M040 Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.100 Mobile Safari/537.36",
        "Origin": "file://",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
    }

    data = {
        "multi_resolution": "true",
        "title": "我刚刚开播,大家快来看吧",
        "thumb_width": "1080",
        "thumb_height": "1920",
        "orientation": "0",
        "base_category": "416",
        "category": "1124",
        "has_commerce_goods": "false",
        "disable_location_permission": "1",
        "push_stream_type": "3",
        "auto_cover": "1",
        "cover_uri": "",
        "third_party": "1",
        "gift_auth": "1",
        "record_screen": "1",
    }

    response = requests.post(url, headers=headers, data=data)

    # 打印响应内容
    print(response.text)

# from about_version import softBuild_download,check_Membership,UUID_vul,check_key,bjtime,check_version,uuid_winc,custom_encode,custom_decode
# with open('.\\xDLCache\\data_c.file', 'rb') as f:
#     byte_data=f.read()
# cookies_data=custom_decode(byte_data)
# print(cookies_data)
# # print("jsow")
# # cookies_data=json.dumps(cookies_data)
# # print(cookies_data)


# creator_webcast(cookies_data)



#############抖音平台自适应request获取方法1,比较快
def resolve_douyin_url(live_url):
    matches = re.findall(r'\d{10,}', live_url)
    rid=matches[0]
    session = requests.Session()

    # Send initial request to obtain __ac_nonce
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Upgrade-Insecure-Requests": "1",
    }
    oresp = session.get(live_url, headers=headers)
    oresp.close()

    # Extract __ac_nonce from Set-Cookie header
    ac_nonce_match = re.search(r'(?i)__ac_nonce=(.*?);', oresp.headers.get("Set-Cookie", ""))
    if ac_nonce_match:
        ac_nonce = ac_nonce_match.group(1)
    else:
        return None

    # Set __ac_nonce cookie and send another request
    session.cookies.set("__ac_nonce", ac_nonce)
    resp = session.get(live_url, headers=headers)

    # Extract ttwid from Set-Cookie header
    ttwid_match = re.search(r'(?i)ttwid=.*?;', resp.headers.get("Set-Cookie", ""))
    if ttwid_match:
        ttwid = ttwid_match.group(0)
    else:
        return None

    # Build URL for final request
    url = f"https://live.douyin.com/webcast/room/web/enter/?aid=6383&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=web_live&cookie_enabled=true&screen_width=1728&screen_height=1117&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=116.0.0.0&web_rid={rid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Cookie": ttwid,
        "Accept": "*/*",
        "Host": "live.douyin.com",
        "Connection": "keep-alive",
    }

    # Send the final request
    ress = session.get(url, headers=headers)
    ress.close()

    # Parse the JSON response
    data = json.loads(ress.text)
    status = data.get("data", {}).get("data", [])[0].get("status", 0)

    if status != 2:
        return None

    stream_data = data.get("data", {}).get("data", [])[0].get("stream_url", {}).get("live_core_sdk_data", {}).get("pull_data", {}).get("options", {}).get("qualities", [])

    quality_order = ["蓝光", "超清", "高清"]

    for quality_name in quality_order:
        for quality in stream_data:
            name = quality.get("name")
            resolution = quality.get("resolution")

            if name == quality_name and not resolution=='':
                return resolution

    return None



#############抖音平台自适应Selenium.webdriver获取方法2
def douyin_resolving_url(url):
    # 创建Chrome浏览器选项
    option = webdriver.ChromeOptions()
    option.add_argument("--headless --disable-gpu")  # 无头模式

    # 创建浏览器实例并加载网页
    driver = webdriver.Chrome(options=option)
    driver.get("https://live.douyin.com/417255778059")

    # 等待网页加载完全,Selenium 中的一个等待条件（Expected Condition），它的作用是等待页面上的某个元素出现在 DOM 结构中。
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

    # 获取网页HTML内容
    html_content = driver.page_source

    # 使用正则表达式匹配所有M3U8链接
    m3u8_pattern = r'(https?://\S+\.flv)'
    m3u8_links = re.findall(m3u8_pattern, html_content)

    print("所有M3U8链接：")
    for link in m3u8_links:
        if "标清" in link or "高清" in link or "超清" in link:
            print(link)
            break    

    # 关闭浏览器实例
    driver.quit()
