import os,time,random,string,subprocess,json,re,semantic_version,datetime,logging,threading,json_dbase
from zhibobanlv import check_process_pid,execute_zhibobanlv,nostrurl
from OBSplugins import obsplugin
from about_version import softBuild_download,check_Membership,bjtime,check_version,custom_encode,custom_decode
from obs_websocket import OBSWebSocket,requests,winConfiguration,obs_run_obsws,modify_ini_file,read_ini_value,obs_profile
from obs_setting import read_obs_exe_path_from_config
from douyin_login_Stream import get_douyin_login,get_streamURL,webcast_start,webcast_stop,local_wast_cookies,did_webcast,thread_send,resolve_douyin_url

def sub_process1(conn): 
    versions='1.1.6'
    findobs=winconfig=complete_push_urls=app_did=room_id=stream_id=None
    App_Start=douyin_onetime2=douyin_onetime4=is_vip=livesdk=False
    liverun=cookies_data=""
    appdata_path = os.getenv('APPDATA') 
    findlockfile=os.path.join(appdata_path, 'webcast_mate', 'lockfile') 
    initTime=0.2
    equipment=numb=0

    logging.basicConfig(filename='.\\worker1.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s: %(message)s')
    if not os.path.exists('.\\xDLCache') :
        os.makedirs('.\\xDLCache')

    while True:
        main_rec =''
        try:
            if conn.poll(initTime):           
                main_rec = conn.recv() 
            if not "dy_" in main_rec and not main_rec == "" and not "rtmp://" in main_rec:

                liverun=""
            elif "dy_" in main_rec:
                if main_rec !="dy_livestop":
                    equipment=numb=0
                    douyin_onetime4=douyin_onetime2=False
                    complete_push_urls=None
                liverun=main_rec
                livesdk=False
            # print(main_rec)
            ######exit必须第一条件，否则被其他条件匹配而无法关闭#####
            if main_rec == "exit": 
                break  

           ############启动验证###########
            elif not App_Start or main_rec =="manualUpdate":
                initTime=1
                App_Start=True
                nowtime=bjtime()
                if not nowtime:
                    conn.send("closeapp")
                else:  
                    if main_rec !="manualUpdate":   
                        ######检验会员                         
                        timevalue = check_Membership(nowtime)
                        if timevalue is not None:
                            is_vip=True
                            lessday=int(timevalue)-int(nowtime)
                            lessday=int(lessday/60/60/24)
                            converted_time = datetime.datetime.fromtimestamp(timevalue)
                            # 将时间格式化为字符串
                            formatted_time = converted_time.strftime('%Y-%m-%d %H:%M')
                            conn.send(f"True,{lessday},会员期: {formatted_time}")
                        else:
                            conn.send(f"False,0,会员已过期")

                    if main_rec =="manualUpdate" and os.path.exists('.\\xDLCache\\Cookies.file'):
                        os.remove('.\\xDLCache\\Cookies.file')                 
                    verlut=check_version(nowtime)                 
                    if verlut is not None:  
                        if verlut!="noRequired":                           
                            match = re.search(r'(\d+\.\d+\.\d+)', verlut)
                            if match:
                                ver_id = match.group(1)
                                if semantic_version.Version(versions) < semantic_version.Version(ver_id):
                                    # self.progressbar_signal.emit(f"{ver_id}版本更新", 0,"show") 
                                    conn.send(f"{ver_id}版本更新")  
                                    buildownload=softBuild_download()
                                    # print(buildownload)
                                    if buildownload and os.path.exists(buildownload):
                                        # 构建roomStore.json文件的完整路径   
                                        # print("下载完成")                                    
                                        # conn.send("taskCompleted")
                                        subprocess.run(buildownload, shell=True)
                                    else:
                                        conn.send("closeapp")
                                else:
                                    if main_rec =="manualUpdate":
                                        conn.send("noBuildUpdate")
                                    conn.send("cleanlogs")
                                    if os.path.exists('.\\worker1.log'):
                                        with open('.\\worker1.log', 'w'):
                                            pass
                                    encodedata=custom_encode("@欢迎使用小斗笠推流码软件，数据更新中，支持0粉，1000粉")
                                    with open('.\\xDLCache\\Cookies.file', 'wb') as file:                                        
                                        file.write(encodedata)
                            else:
                                conn.send("closeapp")
     
                        conn.send(f"startCompleted,{versions}")
                        findobs,obspath=read_obs_exe_path_from_config()
                        if findobs and obspath: 
                            conn.send(f'{findobs},{obspath}')  
                        winconfig=winConfiguration()
                    else:
                        conn.send("closeapp")
            
            #######会员充值同步
            elif main_rec=="is_vip_True":
                is_vip=True
            
            #########OBS一键启动+推流
            elif "rtmp://" in main_rec:
                startObs_ws=OBSWebSocket()                    
                if not startObs_ws.is_connected():
                    obs_run_obsws(findobs)
                    time.sleep(3)
                    for attempt in range(20):
                        try:
                            startObs_ws=OBSWebSocket()
                            if startObs_ws.is_connected():
                                print("OBS连接成功!")
                                break
                            time.sleep(1)
                        except Exception as e:
                            print(f"连接尝试 {attempt + 1} 失败: {e}")  
                            if attempt==20:
                                break                     
                ###启动直播流
                startObs_ws.start_stream(main_rec.split(',')[0],main_rec.split(',')[1])

            ######OBS插件下载#############
            elif "pushButton" in main_rec:
                obsplugin_rec=obsplugin(main_rec)
                conn.send(obsplugin_rec)
                if main_rec == "pushButton":
                    download_directoryobs = os.path.join('filecache','OBS-Studio-29.1.3-Full-Installer-x64.exe')
                    if os.path.exists(download_directoryobs):
                        subprocess.run("filecache\\OBS-Studio-29.1.3-Full-Installer-x64.exe", shell=True,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                elif main_rec == "pushButton_13":
                    download_directoryfx = os.path.join('filecache','streamfx-windows-installer.exe')
                    if os.path.exists(download_directoryfx):
                        subprocess.run("filecache\\streamfx-windows-installer.exe", shell=True)
            
            ######OBS画布设置
            elif "Njds" in main_rec or "Adpt_" in main_rec:
                tempbool=False   
                liverun=''      
                subobs_ws=OBSWebSocket()
                if not subobs_ws.is_connected():
                    obs_run_obsws(findobs)
                    time.sleep(3)
                    for attempt in range(20):
                        try:
                            subobs_ws=OBSWebSocket()
                            if subobs_ws.is_connected():
                                # print("OBS连接成功!")
                                tempbool=True
                                break
                            time.sleep(1)
                        except Exception as e:
                            # print(f"连接尝试 {attempt + 1} 失败: {e}")  
                            if attempt==20:
                                break 
                elif subobs_ws.is_connected():
                    tempbool=True

                if tempbool:    
                    # print("获取OBS数据")
                    profile_name,Scene_name=subobs_ws.Switch_Profile(main_rec) 
                    obs_profile(winconfig)
                    time.sleep(1)
                    subobs_ws.SetCurrentProfile_function(profile_name)
                    time.sleep(0.2)
                    subobs_ws.SetCurrentSceneCollection_function(Scene_name)
                    time.sleep(0.3)
                    if  not "Adpt_" in main_rec:
                        filterSet0={'sharpness': 0.16}
                        subobs_ws.client.call(requests.CreateSourceFilter(sourceName="视频采集设备",filterName="锐化",filterKind="sharpness_filter_v2",filterSettings=filterSet0))
                        filterSet1={'contrast': 0.21, 'gamma': -0.08, 'hue_shift': -0.03, 'saturation': 0.26}
                        subobs_ws.client.call(requests.CreateSourceFilter(sourceName="视频采集设备",filterName="色彩校正",filterKind="color_filter_v2",filterSettings=filterSet1))
                        time.sleep(1)
                    subobs_ws.disconnect()

            #####开播推流码获取                        
            elif "dy_" in liverun:
                ##########1000粉丝开播
                if "dy_1000" in liverun:
                    sdkserpid=check_process_pid('MediaSDK_Server.exe')
                    if os.path.exists(findlockfile) and sdkserpid is not None:   
                        complete_push_urls = execute_zhibobanlv()                                   
                        if is_vip and not complete_push_urls and not livesdk:
                            try:
                                nostrurl(sdkserpid)
                                time.sleep(1)
                                livesdk=True
                            except Exception:
                                pass 
                        if complete_push_urls:
                            conn.send(complete_push_urls)
                            liverun=""
                            livesdk=False   
                ##########0粉开播和账号登录
                elif liverun=="dy_auto_live" or liverun=="dy_phone" or liverun=="dy_livestop" or liverun=="dy_Accounts":
                    numb+=1
                    ####账号登录和cookies获取
                    if not os.path.exists('.\\xDLCache\\data_c.file') or liverun=="dy_Accounts":
                        # print("账号登录")
                        cookies_data=local_wast_cookies(conn)
                        if liverun=="dy_Accounts":
                            cookies_data=""
                            liverun="dy_phone"
                            if os.path.exists('.\\xDLCache\\data_c.file'):
                                os.remove('.\\xDLCache\\data_c.file')
                        if not cookies_data:
                            thread = threading.Thread(target=thread_send, args=(conn,)) 
                            thread.start()             
                            cookies_data=get_douyin_login("0")                              
                            # cookies_data=get_douyinlogin(conn,0)
                            # print(nuber)
                            if not cookies_data:
                                cookies_data=get_douyin_login("1")
                                # cookies_data=get_douyinlogin(conn,1)
                                if not cookies_data:
                                    liverun=""
                    elif not cookies_data:
                        cookies_data=custom_decode('.\\xDLCache\\data_c.file')
                    ###########关闭直播
                    if liverun=="":
                        pass
                    elif liverun=="dy_livestop" and os.path.exists('xdlconfig.json'):
                        with open('xdlconfig.json', 'r') as file:
                            existing_data = json.load(file)
                        room_id = existing_data.get("room_id")
                        stream_id = existing_data.get("stream_id")
                        if room_id and stream_id:                                              
                            webcast_stop(room_id,stream_id,cookies_data,equipment)
                            conn.send(f"直播间已关闭")
                            liverun=""      
                    ###########开始直播
                    elif is_vip and not douyin_onetime2: 
                        print("开始直播")
                        if liverun=="dy_auto_live":
                            equipment=1
                        statid,room_id,stream_id=get_streamURL(conn,cookies_data,numb,equipment)
                        #########状态ID为4，执行
                        if statid==4 and not douyin_onetime4:
                            douyin_onetime4=True
                            if liverun != "dy_auto_live":
                                conn.send("手机开播")
                            numb=3
                        #########状态ID为2和1时，将开播成功的数据写入本地
                        elif statid==2 or (liverun=="dy_auto_live" and statid==1): 
                            numb=3
                            douyin_onetime2=True 
                            if os.path.exists('xdlconfig.json'):
                                config_data = {
                                    "room_id": room_id,
                                    "stream_id": stream_id,
                                }
                                # 读取现有数据或创建一个空字典
                                try:
                                    with open('xdlconfig.json', 'r') as file:
                                        existing_data = json.load(file)
                                except FileNotFoundError:
                                    existing_data = {}
                                # 合并数据
                                existing_data.update(config_data)
                                # 将合并后的数据写回xdl.json文件
                                with open('xdlconfig.json', 'w') as file:
                                    json.dump(existing_data, file, indent=4)
                        #########账号开播不成功，表面cookie过期
                        elif not statid and numb==2 and os.path.exists('.\\xDLCache\\data_c.file'):
                            print('删除缓存')
                            os.remove('.\\xDLCache\\data_c.file') 
                    ###########直播状态延续
                    elif is_vip and douyin_onetime2 and numb<60: 
                        # print(room_id)
                        if liverun=="dy_auto_live":
                            equipment=1                                                
                        webcast_start(room_id,stream_id,cookies_data,equipment)
                        if numb==59:
                            liverun=""
                    ##########非会员直播
                    elif not is_vip and not complete_push_urls and os.path.exists('xdlconfig.json'):
                        if not douyin_onetime4:
                            douyin_onetime4 = True
                            try:
                                with open("xdlconfig.json", "r") as config_file:
                                    config_data = json.load(config_file)
                                    app_did = config_data.get("appDID", '')
                            except:
                                pass
                        if app_did:
                            complete_push_urls=did_webcast(app_did,cookies_data)
                            if complete_push_urls:
                                liverun=""
                                conn.send(complete_push_urls)

            else:
                time.sleep(0.5)
        except Exception as e:
            logging.error(f"Error in subprocess:{e}")
            # 捕获异常并打印错误信息，但不让子进程退出
            main_rec=liverun=""
            time.sleep(2)
            continue
