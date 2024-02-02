import time,psutil,os,configparser,json,GPUtil,re,json_dbase,random,string,logging,subprocess
from obswebsocket import obsws, requests
from zhibobanlv import killsdkid
from douyin_login_Stream import resolve_douyin_url

anyname=anynamecj=origename=url=None
base_w=base_h=pos_x=pos_y=wincpugpu=0
 

#####修改ini某个配置
def modify_ini_file(ini_file_path, section, option, value):

    """
    修改INI配置文件中指定section和option的值为给定的value
    """
    if os.path.exists(ini_file_path):
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(ini_file_path, encoding='utf-8-sig')

        # 修改配置
        config.set(section, option, str(value))

        # 保存修改后的配置到文件
        with open(ini_file_path, 'w', encoding='utf-8-sig') as configfile:
            config.write(configfile, space_around_delimiters=False)

#######获取ini某个配置
def read_ini_value(ini_file_path, section, option):
    """
    读取INI配置文件中指定section和option的值
    """
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_file_path, encoding='utf-8-sig')
    return config.get(section, option)

########OBS配置websocket连接
def get_obsini():    
    appdata_path = os.getenv('APPDATA')
    Server_Port =Server_Password = None
    # appdata_path = os.getenv('APPDATA')
    ini_file_path = os.path.join(appdata_path, 'obs-studio', 'global.ini')

    if os.path.exists(ini_file_path):
        obs_websocket_enabled = read_ini_value(ini_file_path, 'OBSWebSocket', 'ServerEnabled')
        Server_Port = read_ini_value(ini_file_path,'OBSWebSocket', 'ServerPort')
        Server_Password = read_ini_value(ini_file_path,'OBSWebSocket', 'ServerPassword')
        if obs_websocket_enabled=="false":            
            time.sleep(1)
            modify_ini_file(ini_file_path, 'OBSWebSocket', 'ServerEnabled', 'true')
        config_data = {
            "ServerPort": Server_Port,
            "ServerPassword":Server_Password
        }       
        try:
            with open("xdlconfig.json", "r") as config_file:
                existing_data = json.load(config_file)
        except FileNotFoundError:
            existing_data = {}
        # 合并现有数据和新数据
        existing_data.update(config_data)
        
        with open("xdlconfig.json", "w") as config_file:
            json.dump(existing_data, config_file, indent=4)
    return Server_Port,Server_Password
class OBSWebSocket:
    def __init__(self):        
        try:        
            # 读取 xdlconfig.json 文件
            with open("xdlconfig.json", "r") as file:
                config_data = json.load(file)
            obs_port = config_data.get("ServerPort")
            obs_password = config_data.get("ServerPassword")
        except:
            obs_port,obs_password=get_obsini()

        try:
            self.client = obsws("localhost", obs_port, obs_password)
            self.client.connect()
            self.connected = True  # 连接成功
        except Exception as e:
            # 连接失败，设置连接状态为 False
            self.connected = False
            print(f"发生异常：{e}")

    def is_connected(self):
        # 检查连接状态
        return self.connected
    
    def disconnect(self):
        # 断开连接
        if self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                print("已断开连接")
            except Exception as e:
                print(f"断开连接时发生异常：{e}")
        else:
            print("未连接，无需断开")


    def start_stream(self, rtmp_server_url, stream_key):
        stream_service_type = "rtmp_custom"
        stream_service_settings = {
            "server": rtmp_server_url,
            "key": stream_key
        }

        try:
            self.client.call(requests.SetStreamServiceSettings(streamServiceType=stream_service_type, streamServiceSettings=stream_service_settings))  
  
            killsdkid()     
            self.client.call(requests.StartStream())
            time.sleep(0.5)
            killsdkid()
            # time.sleep(20)
        except Exception as e:
            print(f"Failed to start stream: {str(e)}")

    def GetProfileList_currentname(self):    #####获取当前配置文件名称
        respose=self.client.call(requests.GetProfileList())
        # return
        cuprofName=respose.datain.get('currentProfileName')
        return cuprofName
    def GetProfileParameter_function(self):       ########查询basic.ini中的参数，如(parameterCategory="Output",parameterName="Mode")
        respose=self.client.call(requests.GetProfileParameter(parameterCategory="Output",parameterName="Mode"))
        print(respose.datain)
        ####{'defaultParameterValue': 'Simple', 'parameterValue': 'Advanced'}


    def SetProfileParameter_function(self):          #######修改basic.ini中的参数，如切换为高级模式SetProfileParameter(parameterCategory="Output",parameterName="Mode",parameterValue="Advanced或Simple"))
        self.client.call(requests.SetProfileParameter(parameterCategory="Output",parameterName="Mode",parameterValue="Advanced"))


    def SetCurrentProfile_function(self,name):    #####切换配置文件
        self.client.call(requests.SetCurrentProfile(profileName=name))

    # def CreateProfile_function(self):    #####创建新配置文件
    #     self.client.call(requests.CreateProfile(profileName="test"))      


    def GetSceneCollectionList_currentname(self):    #####获取场景集合列表
        respose=self.client.call(requests.GetSceneCollectionList())
        cuprofName=respose.datain.get('currentSceneCollectionName')
        return cuprofName

    def SetCurrentSceneCollection_function(self,namecj):    #####切换场景集合
        self.client.call(requests.SetCurrentSceneCollection(sceneCollectionName=namecj))

    
    # def CreateSceneCollection_function(self):    #####创建场景集合
    #     self.client.call(requests.CreateSceneCollection(sceneCollectionName="222cj"))

    # def RemoveSceneCollection_function(self,name):    #####创建场景集合
    #     self.client.call(requests.RemoveSceneCollection(sceneCollectionName=name))

    def CreateScene_function(self):     ####创建场景
        response = self.client.call(requests.CreateScene(sceneName="target_scene_name"))     

    def SetCurrentProgramScene_function(self):     ####场景切换
        response = self.client.call(requests.SetCurrentProgramScene(sceneName="target_scene_name"))

    def GetVideoSettings_function(self):    #####获取画布分辨率等参数
        respose=self.client.call(requests.GetVideoSettings())
        opheight=respose.datain.get('baseHeight') 
        opwidth=respose.datain.get('baseWidth')
        return opwidth,opheight  

    def SetVideoSettings_function(self):    #####设置画布分辨率参数
        respose=self.client.call(requests.SetVideoSettings(baseHeight= 1920, baseWidth= 1080, fpsDenominator=50, outputHeight= 960, outputWidth= 760))

    # def CreateSource_function(self):    #####创建来源5.0+不支持
    #     respose=self.client.call(requests.CreateSource(inputName="tell",inputKind=""))
    #     print(respose.datain)
    # def GetSourcesList_function(self):    #####获取来源列表5.0+不支持
    #     respose=self.client.call(requests.GetSourcesList())
    #     print(respose.datain)

    def GetSourceFilterList_function(self):    #####获取某个来源的所有滤镜
        respose=self.client.call(requests.GetSourceFilterList(sourceName="直播调试"))
        print(respose.datain)
  
    def CreateSourceFilter_function(self):    #####创建/设置来源的滤镜
        colorfilterSet= {'brightness': 0.3127, 'contrast': -0.91, 'gamma': 0.99, 'hue_shift': 53.49, 'saturation': 1.2}
        respose=self.client.call(requests.CreateSourceFilter(sourceName="显示器采集",filterName="色彩校正",filterKind="color_filter_v2",filterSettings=colorfilterSet))
        lutfilterSet={'image_path': 'G:/Program Files/obs-studio/data/obs-plugins/obs-filters/LUTs/original.cube'}
        respose=self.client.call(requests.CreateSourceFilter(sourceName="显示器采集",filterName="应用 LUT",filterKind="clut_filter",filterSettings=lutfilterSet))
        recordfilterSet={'bitrate': 24000, 'different_audio': False, 'encoder': 'x264', 'preset': 'veryfast', 'profile': 'high', 'rate_control': 'CBR', 'rec_format': 'mp4', 'record_mode': 2}
        respose=self.client.call(requests.CreateSourceFilter(sourceName="显示器采集",filterName="Source Record",filterKind="source_record_filter",filterSettings=recordfilterSet))
        respose=self.client.call(requests.CreateSourceFilter(sourceName="桌面音频",filterName="噪声抑制",filterKind="noise_suppress_filter_v2"))    #####音频噪音抑制
    
    def SetSourceFilterEnabled_function(self):      ######来源滤镜中某个滤镜的开关
        self.client.call(requests.SetSourceFilterEnabled(sourceName="显示器采集",filterName="应用 LUT",filterEnabled=False))

    def GetInputKindList_function(self):    #####获取来源所支持的种类，以便于创建来源“Source”
        respose=self.client.call(requests.GetInputKindList())        
        print(respose.datain)
        #回复 {'inputKinds': ['image_source', 'color_source_v3', 'slideshow', 'browser_source', 'ffmpeg_source', 'text_gdiplus_v2', 'spectralizer', 'text_ft2_source_v2', 'monitor_capture', 'window_capture', 'game_capture', 'dshow_input', 'wasapi_input_capture', 'wasapi_output_capture', 'wasapi_process_output_capture']}
    def GetInputList_function(self):    #####获取当前场景的所有来源列表，包括声音,也可以指定某个类型
        # respose=self.client.call(requests.GetInputList())     #####获取所有来源列表,包括声音
        respose=self.client.call(requests.GetInputList(inputKind="text_gdiplus_v2"))     ########指定某个类型      
        print(respose.datain)
        return respose.datain
    def GetInputSettings_function(self):    #####获取来源的设置,参照此类设置，以便于创建来源“Source”
        respose=self.client.call(requests.GetInputSettings(inputName="直播调试"))
        print(respose.datain)

    # def CreateInput_function(self):    #####创建/设置来源“Source”
    #     # txtinputSet=
    #     # respose=self.client.call(requests.CreateInput(sceneName="场景",inputName="未命名txt",inputKind="text_gdiplus_v2"))
    #     self.client.call(requests.CreateInput(sceneName="场景",inputName="视频采集设备",inputKind="dshow_input"))

    def GetInputPropertiesListPropertyItems_function(self):    #####获取视频采集设备的列表
        respose=self.client.call(requests.GetInputPropertiesListPropertyItems(inputName="视频采集设备",propertyName="video_device_id"))
        for item in respose.datain['propertyItems']:
            itemName = item['itemName']
            itemValue = item['itemValue']
            print(f'itemName: {itemName}, itemValue: {itemValue}')
        print(respose.datain)
    def GetInputPropertiesListPropertyItems_function2(self):    #####获取视频采集设备的中分辨率的列表
        respose=self.client.call(requests.GetInputPropertiesListPropertyItems(inputName="视频采集设备",propertyName="resolution"))
        print(respose.datain)



    def GetOutputList_function(self):    #####切换配置文件
        respose=self.client.call(requests.GetOutputList())
        print(respose.datain)
    def GetOutputSettings_function(self):    #####切换配置文件
        respose=self.client.call(requests.GetStudioModeEnabled())
        print(respose.datain)
    def SetStudioModeEnabled_function(self):    #####工作模式打开
        respose=self.client.call(requests.SetStudioModeEnabled(studioModeEnabled=True))


    def OpenInputPropertiesDialog_function(self):    #####切换配置文件
        respose=self.client.call(requests.OpenInputPropertiesDialog(inputName="未命名txt"))
    def GetRecordDirectory_function(self):    #####获取OBS录像保存文件夹 
        try:       
            respose=self.client.call(requests.GetRecordDirectory())
            # print("recordDirectory")   
            recdir=respose.datain.get("recordDirectory")
            return recdir
        except Exception:
            appdata_path = os.getenv('APPDATA')
            return appdata_path
    ######OBS广告模板
    def Njdsmould_Profile(self):
        response = self.client.call(requests.GetProfileList())
        # print(response.datain)
        response1 = self.client.call(requests.GetSceneCollectionList())

        if not "Njdsmould" in response.datain.get('profiles') or not "Njdsmouldcj" in response1.datain.get('sceneCollections'):
            self.client.call(requests.CreateProfile(profileName="Njdsmould"))
            time.sleep(0.1)
            self.client.call(requests.CreateSceneCollection(sceneCollectionName="Njdsmouldcj"))
            time.sleep(0.1)
        self.client.call(requests.SetCurrentProfile(profileName="Njdsmould"))
        time.sleep(0.12)
        njdsset = {'antialiasing': False, 'bk_color': 4278190080, 'color': 4278255615, 'gradient': True, 'gradient_color': 4278212095, 'gradient_dir': 184.1, 'outline': True, 'outline_color': 4278255615, 'outline_size': 4, 'text': '牛角大叔'}
        njdsset2 = {'font': {'face': 'Arial', 'flags': 0, 'size': 72, 'style': 'Regular'}, 'text': '----------------直播调试----------------'}
        crossby = {'align': 'right', 'chatlog': False, 'gradient': True, 'gradient_color': 4278190335, 'gradient_dir': 126.2, 'outline': True, 'outline_color': 4278190335, 'outline_opacity': 99, 'outline_size': 16, 'text': '本方案由【牛角大叔】提供', 'valign': 'center', 'vertical': False}
        self.client.call(requests.SetCurrentSceneCollection(sceneCollectionName="Njdsmouldcj"))
        time.sleep(0.12)
        # zbts={'filterKind': 'crop_filter', 'filterName': '裁剪/填充', 'filterSettings': {'left': -1920, 'top': -1000}}, {'filterKind': 'scroll_filter', 'filterName': '滚动', 'filterSettings': {'speed_x': 228.0}}
        self.client.call(requests.CreateInput(sceneName="场景", inputName="直播调试", inputKind="text_gdiplus_v2", inputSettings=njdsset2))
        self.client.call(requests.CreateInput(sceneName="场景", inputName="牛角大叔", inputKind="text_gdiplus_v2", inputSettings=njdsset))      
        self.client.call(requests.CreateInput(sceneName="场景", inputName="crossby", inputKind="text_gdiplus_v2", inputSettings=crossby))
        filtes={'left': -500, 'top': -300}
        self.client.call(requests.CreateSourceFilter(sourceName="牛角大叔",filterName='裁剪/填充',filterKind='crop_filter',filterSettings=filtes))
        filter1 = {'left': -1920, 'top': -1000}
        filter2= {'speed_x': 228.0}
        self.client.call(requests.CreateSourceFilter(sourceName="直播调试", filterKind='crop_filter', filterName= '裁剪/填充',filterSettings=filter1))
        self.client.call(requests.CreateSourceFilter(sourceName="直播调试", filterKind='scroll_filter', filterName= '滚动',filterSettings=filter2))

########OBS画布配置
    def Switch_Profile(self,anynames):  
        global anyname,anynamecj,base_w,base_h,posx,posy,url,origename
        posx=posy=0
        base_w=1920
        base_h=1080
        ####获取当前OBS配置
        response_GetProfile = self.client.call(requests.GetProfileList())        
        current_profilename=response_GetProfile.datain.get('currentProfileName')
        response_GetSceneCollection = self.client.call(requests.GetSceneCollectionList())
        current_scenename=response_GetSceneCollection.datain.get('currentSceneCollectionName')

        try:
            ######主进程发送的按钮值分析
            if "NjdsDiy" in anynames:
                anyname,width_x,height_y = anynames.split(',')  
            elif "Adpt_selfAdaption" in anynames:
                anyname,url = anynames.split(',')
            else:
                anyname=anynames
            origename=anyname
            if "Njds" in anyname:
                if anyname == "Njdsdesktop":
                    pass
                elif anyname != "NjdsDiy":         
                    config_data = json_dbase.data
                    width_x=config_data["obsconfigs"]["setting"][anyname]["width"]  
                    height_y=config_data["obsconfigs"]["setting"][anyname]["height"]
                #####自定义分辨率
                else: 
                    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
                    anyname=anyname+random_string
                anynamecj=anyname+"cj"
            ############已存在的配置，直接切换
            if "Njds" in anyname and anyname in response_GetProfile.datain.get('profiles') and anynamecj in response_GetSceneCollection.datain.get('sceneCollections'):
                self.client.call(requests.SetCurrentProfile(profileName=anyname))
                time.sleep(0.1)
                self.client.call(requests.SetCurrentSceneCollection(sceneCollectionName=anynamecj))
                self.client.disconnect()  
                return None,None
            
            ######平台高清配置
            elif "Adpt_" in anyname:
                base_w,base_h=self.GetVideoSettings_function() 
                anyname=current_profilename
                anynamecj=current_scenename

            #######创建配置
            else:
                self.client.call(requests.CreateProfile(profileName=anyname))
                time.sleep(0.08)
                self.client.call(requests.CreateSceneCollection(sceneCollectionName=anynamecj))
                time.sleep(0.15)
                #####打开音频
                input_Setting={'device_id': 'default'}
                self.client.call(requests.CreateInput(sceneName="场景",inputName="麦克风/Aux",inputKind="wasapi_input_capture",inputSettings=input_Setting))
                self.client.call(requests.CreateInput(sceneName="场景",inputName='桌面音频',inputKind='wasapi_output_capture',inputSettings=input_Setting))
                #####PC端游创建
                if anyname == "Njdsdesktop":
                    self.client.call(requests.CreateInput(sceneName="场景",inputName="显示器采集",inputKind="monitor_capture"))
                    #####获取显示器列表
                    time.sleep(0.1)
                    respose=self.client.call(requests.GetInputPropertiesListPropertyItems(inputName="显示器采集",propertyName="monitor_id"))
                    for item in respose.datain['propertyItems']:
                        itemName = item['itemName']
                        if '主显示器' in itemName or '0,0' in itemName:
                            itemValue = item['itemValue']  
                            break
                    inputSets= {'monitor_id': itemValue}
                    ######选择和设置显示器
                    self.client.call(requests.SetInputSettings(inputName="显示器采集",inputSettings=inputSets))
                    base_w,base_h=self.GetVideoSettings_function()
                else:
                    #######创建input来源
                    self.client.call(requests.CreateInput(sceneName="场景",inputName="视频采集设备",inputKind="dshow_input"))
                    #####获取采集设备列表
                    time.sleep(0.1)
                    respose=self.client.call(requests.GetInputPropertiesListPropertyItems(inputName="视频采集设备",propertyName="video_device_id")) 
                    proportion=int(width_x)/int(height_y)
                    for item in respose.datain['propertyItems']:
                        itemName = item['itemName']
                        itemValue = item['itemValue']
                        if proportion<=1.1 and "usb" in itemValue and ("Webcam" in itemName or "Integrated" in itemName or "Camera" in itemName or "视频" in itemName):
                            break
                        elif proportion>1.1 and "usb" in itemValue and not "Webcam" in itemName and not "Integrated" in itemName and not "Camera" in itemName and not "视频设备" in itemName and not "Virtual" in itemName:
                        # print(f'itemName: {itemName}, itemValue: {itemValue}')
                            break

                    inputSets= {'last_video_device_id': itemValue, 'video_device_id': itemValue}
                    self.client.call(requests.SetInputSettings(inputName="视频采集设备",inputSettings=inputSets,overlay=True))
                    time.sleep(0.1)
                    resp10=self.client.call(requests.GetInputPropertiesListPropertyItems(inputName="视频采集设备",propertyName="resolution"))
                    resolution_val ='2560x1440' if '2560x1440' in str(resp10.datain) else \
                                    '1920x1080' if '1920x1080' in str(resp10.datain) else \
                                    "1280x720" if "1280x720" in str(resp10.datain) else \
                                    "1280x960" if "1280x960" in str(resp10.datain) else \
                                    "960x540" if "960x540" in str(resp10.datain) else \
                                    "640x360" if "640x360" in str(resp10.datain) else \
                                    "1080x1920" if "1080x1920" in str(resp10.datain) else \
                                    "720x1280" if "720x1280" in str(resp10.datain) else \
                                    "540x960" if "540x960" in str(resp10.datain) else \
                                    None
                    if proportion > 1.1:
                        frame_val = 166666
                        video_format_val = 201 if resolution_val == '2560x1440' else 0
                    else:                           
                        frame_val=333333
                        video_format_val=0         

                    if resolution_val:
                        # 设置采集卡的参数
                        inputSet2= {'color_range': 'partial', 'color_space': '709', 'frame_interval': frame_val, 'last_resolution': resolution_val, 'last_video_device_id': itemValue, 'res_type': 1, 'resolution': resolution_val, 'video_device_id': itemValue, 'video_format': video_format_val}
                        self.client.call(requests.SetInputSettings(inputName="视频采集设备",inputSettings=inputSet2,overlay=True))
                        width, height = map(int, resolution_val.split('x'))
                        if proportion>1.78:
                            y_value=int((1+0.04)*width/proportion)
                            posy=int((height-y_value)/2)
                            base_h=int(y_value*(1+65/1080))
                            base_w=width
                        elif proportion>1.1:
                            base_w=int(height*proportion)
                            posx=int((width-base_w)/2)
                            base_h=int(height*(1+60/1080))
                        else:
                            base_w=width_x
                            base_h=height_y
        
            #########将OBS的高级配置打开
            self.client.call(requests.SetProfileParameter(parameterCategory="Output",parameterName="Mode",parameterValue="Advanced"))
            ##### 切换模板广告
            self.Njdsmould_Profile()

            return anyname,anynamecj
        except Exception as e:
            # print("配置发生异常",e)
            logging.error("OBS切换发生异常",e)
            self.client.call(requests.SetCurrentProfile(profileName=current_profilename))
            time.sleep(0.1)
            self.client.call(requests.SetCurrentSceneCollection(sceneCollectionName=current_scenename))
            time.sleep(0.1)
            self.client.call(requests.RemoveProfile(profileName=anyname))
            self.client.disconnect()
            # self.client.call(requests.RemoveSceneCollection(sceneCollectionName=current_scenename))
            return None,None          

###########将数据写入obs的配置ini文件
def obs_profile(winconfig):
    global anyname,anynamecj,base_w,base_h,posx,posy,url,origename
    FPSCommon_val="60"
    appdata_path = os.getenv('APPDATA')
    Resresol_val_x=Resresol_val_y=0
    try:        
        basicini_path = os.path.join(appdata_path, 'obs-studio', 'basic','profiles',anyname,'basic.ini')                   
        streamEncoder_path = os.path.join(appdata_path, 'obs-studio', 'basic','profiles',anyname,'streamEncoder.json')
        scenesjson_path = os.path.join(appdata_path, 'obs-studio', 'basic', 'scenes', f"{anynamecj}.json")
        # print(base_w,base_h,posx,posy)

        if 'Adpt_' in origename:        
            if origename=='Adpt_highDefinition':
                Resresol_val_x=1280          
            elif origename=='Adpt_ultraclear':
                Resresol_val_y=720
            elif origename=='Adpt_blueLight':
                Resresol_val_y=1080
            #####自适应的数据处理
            elif origename=='Adpt_selfAdaption':
                res_val=str(resolve_douyin_url(url))
                if not res_val:
                    res_val=str(resolve_douyin_url(url))
                width_str, height_str = res_val.split('x')
                # print(width_str, height_str)
                x_value=int(width_str)
                y_value=int(height_str)
                if y_value==720 or y_value==1080:
                    Resresol_val_y=y_value
                elif x_value==1280:
                    Resresol_val_x=x_value
                elif y_value % 10 == 0:
                    Resresol_val_y=y_value
                elif x_value % 10 == 0:
                    Resresol_val_x=x_value
                else:
                    Resresol_val_y=y_value
        else:
            json_obsdata = json_dbase.data
            opEncoder_val=json_obsdata["obsconfigs"]["setting"][winconfig]["opEncoder_val"]
            Resresol_val_y=json_obsdata["obsconfigs"]["setting"][winconfig]["Resresol_val"]
            bitrate_val=json_obsdata["obsconfigs"]["setting"][winconfig]["bitrate_val"]
            preset_val=json_obsdata["obsconfigs"]["setting"][winconfig]["preset_val"]
            profile_val=json_obsdata["obsconfigs"]["setting"][winconfig]["profile_val"]
            streamEncoder_data={"bitrate":bitrate_val,"preset":preset_val,"profile":profile_val,"preset2":preset_val}
            # 将数据写入JSON文件            
            with open(streamEncoder_path, 'w') as json_file:
                json.dump(streamEncoder_data, json_file, indent=4)
        
        #####当宽度过大(手机)，就不能用1080作为高度缩放，不然宽度更大
        if int(base_w)/int(base_h)>1.78:
            Resresol_val_y=720
        #####竖屏时缩放与画布相同。
        elif int(base_w)/int(base_h)<1.1:
            Resresol_val_y=int(base_h)
            FPSCommon_val="30"

        if Resresol_val_x !=0:            
            Resresol_val_y=int(Resresol_val_x*int(base_h)/int(base_w))
        else:
            Resresol_val_x=int(Resresol_val_y*int(base_w)/int(base_h)) 

        if os.path.exists(basicini_path):
            config = configparser.ConfigParser()
            config.optionxform = str
            config.read(basicini_path, encoding='utf-8-sig')

            # ini文件修改配置        
            config.set('AdvOut', 'Rescale', "true")
            config.set('AdvOut', 'RescaleRes', f"{Resresol_val_x}x{Resresol_val_y}")
            if not "Adpt_" in origename:
                config.set('Video', 'BaseCX', f"{base_w}")
                config.set('Video', 'BaseCY', f"{base_h}")
                config.set('Video', 'OutputCX', f"{base_w}")
                config.set('Video', 'OutputCY', f"{base_h}")
                config.set('Video', 'FPSCommon', f"{FPSCommon_val}")
                config.set('AdvOut', 'Encoder', f"{opEncoder_val}")

            # 保存修改后的配置到文件
            with open(basicini_path, 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile, space_around_delimiters=False)
        ######在场景集合文件中修改采集卡或摄像头黑边移动位置
        if not "Adpt_" in anyname:
            with open(scenesjson_path, 'r',encoding='utf-8') as json_file:
                data = json.load(json_file)
            # 修改场景来源项中的pos中x和y的值
            data["sources"][0]["settings"]["items"][0]["pos"]["x"] = -posx
            data["sources"][0]["settings"]["items"][0]["pos"]["y"] = -posy
            # 保存回JSON文件
            with open(scenesjson_path, 'w') as json_file:
                json.dump(data, json_file, indent=2)
    except Exception as e:
        # print("OBS写入发生异常",e)
        logging.error("OBS写入发生异常",e)
        
        

#####判断OBS是否在运行
def is_obs_running():
    # 获取所有正在运行的进程
    running_processes = psutil.process_iter(attrs=['name'])

    # 检查是否有名为 "obs64.exe" 的进程
    for process in running_processes:
        if process.info['name'] == 'obs64.exe':
            return True

    return False
########关闭OBS进程
def close_obs_processes():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if 'obs' in process.info['name'].lower():
                os.kill(process.info['pid'], 9)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

#####运行OBS
def obs_run_obsws(obs_exe_path):
    close_obs_processes()
    get_obsini()
    if obs_exe_path:
        current_directory = os.getcwd()
        obs_folder_path = os.path.dirname(obs_exe_path)
        ######使用了creationflags=subprocess.CREATE_NEW_PROCESS_GROUP，以确保子进程在独立于父进程，即便父进程退出也不影响OBS运行。
        subprocess.Popen([obs_exe_path], cwd=obs_folder_path,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        os.chdir(current_directory)
        time.sleep(1)
    else:
        print("未找到 OBS 路径.")
        return

#####获取电脑配置参数
def winConfiguration():
    total_gpu_memory = cpu_counts=0
    cpu_freqs=0.0
    try:
        gpu_list = GPUtil.getGPUs()
        if gpu_list:
            for i, gpu in enumerate(gpu_list):
                # print(f"\n显卡 {i + 1} 信息:")
                # print(f"显存总量: {gpu.memoryTotal} MB")                
                # 将显卡总容量累加到变量中
                total_gpu_memory += gpu.memoryTotal
        # 获取CPU信息
        cpu_counts=psutil.cpu_count(logical=False)
            # '逻辑核心数': psutil.cpu_count(logical=True),
        # 获取CPU频率
        freq = psutil.cpu_freq()
        cpu_freqs=freq.current
        if total_gpu_memory>6100:
            return "gpu_adv"
        elif cpu_counts>6 and cpu_freqs>3200.0:
            return "cpu_adv"
        elif total_gpu_memory>4000:
            return "gpu_basic"
        else:
            return "cpu_basic"
    except Exception as e:
        return "cpu_basic"
    


# #获取虚拟摄像头状态
# VCamStatus = ws.call(requests.GetVirtualCamStatus())
# output_active = VCamStatus.getoutputActive()
# print("虚拟摄像头状态:", output_active)
# # 打开虚拟摄像头
# StartVCam=ws.call(requests.StartVirtualCam())

# # 设置流媒体服务类型和设置信息
# stream_service_type = "rtmp_custom"
# stream_service_settings = {
#     "server": "your_rtmp_server_url",
#     "key": "your_stream_key"
# }
# # 发送SetStreamServiceSettings请求来设置流媒体服务设置
# SetStreamService = ws.call(requests.SetStreamServiceSettings(streamServiceType=stream_service_type, streamServiceSettings=stream_service_settings))

# # 开始录制
# Startany=ws.call(requests.StartRecord())

# # 开始直播
# Startany=ws.call(requests.StartStream())

# # 来源显示和隐藏切换（用名称触发，当前版本有BUG）
# # 查看可用的热名称
# hkynamelist = ws.call(requests.GetHotkeyList())
# for hotkey_name in hkynamelist.getHotkeys():
#     print(hotkey_name)
# # 发送TriggerHotkeyByName请求来触发显示场景元素的热键操作
# response = ws.call(requests.TriggerHotkeyByName(hotkeyName="libobs.show_scene_item.浏览器"))
# response = ws.call(requests.TriggerHotkeyByName(hotkeyName="libobs.hide_scene_item.浏览器"))
# ##来源显示和隐藏切换（快捷键触发,完美运行）
# key_id = "OBS_KEY_A"  # 注意OBS接收的热键必须是字符串如"OBS_KEY_A"，这样才与键盘A等同
# # 使用str()函数将key_id转换为字符串类型
# response = ws.call(requests.TriggerHotkeyByKeySequence(keyId=str(key_id)))
# # 组合键
# key_id = "OBS_KEY_B"  # 替换为要触发的按键的ID，参考 https://github.com/obsproject/obs-studio/blob/master/libobs/obs-hotkeys.h
# key_modifiers = {
#     "shift": False,     # 是否按下 Shift 键
#     "control": False,  # 是否按下 Ctrl 键
#     "alt": True,      # 是否按下 Alt 键
#     "command": False   # 是否按下 Command 键 (Mac)
# }
# # 发送触发热键的请求
# response = ws.call(requests.TriggerHotkeyByKeySequence(
#     keyId=key_id,
#     keyModifiers=key_modifiers
# ))

# # 关闭连接
# ws.disconnect()