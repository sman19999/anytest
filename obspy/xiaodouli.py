import sys,os,json,time,threading,logging,multiprocessing,json_dbase,random,base64
from childProcess1 import sub_process1
from PyQt5.QtWidgets import (
    QApplication,QScrollArea,QWidget, QMainWindow, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpacerItem, QSizePolicy, QMenu, QAction, QMessageBox,QProgressDialog)
from PyQt5.QtCore import pyqtSlot, QPoint, Qt,pyqtSignal
from PyQt5.QtGui import QPixmap,QIntValidator,QIcon
from main_ui import Ui_MainWindow
from obs_websocket import OBSWebSocket,requests,obs_run_obsws,is_obs_running,close_obs_processes
from about_version import check_key,uuid_winc
from functools import partial

# 创建一个事件对象，用于通知线程退出

button_object_name=find_obs=obs_path=sdkpid=vipdays=app_did=versions=None
qq_group='交流Q群:671868886'
threading_1=is_vip=False
lessday=0
initTime=0.5

# # 重定向标准输出和标准错误到日志文件
# class LoggerWriter:
#     def __init__(self, level):
#         self.level = level

#     def write(self, message):
#         # 记录消息到日志文件
#         if message.strip():  # 避免写入空行
#             self.level(message)


# 创建管道
parent_conn, child_conn = multiprocessing.Pipe()

##窗口移动

class DraggableWindowMixin:
    def __init__(self):
        super().__init__()
        
        # 初始化拖动标志和鼠标偏移量
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        # 当鼠标左键按下时记录偏移量和设置拖动标志
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.dragging = True

    def mouseMoveEvent(self, event):
        # 如果拖动标志为True，则根据鼠标移动更新窗口位置
        if self.dragging:
            new_position = self.mapToGlobal(event.pos() - self.offset)
            self.window().move(new_position)

    def mouseReleaseEvent(self, event):
        # 当鼠标左键释放时取消拖动
        if event.button() == Qt.LeftButton:
            self.dragging = False

class MyWindow(QMainWindow, DraggableWindowMixin):
    show_message_signal = pyqtSignal(str, str)  
    update_ui_signal = pyqtSignal(str)  
    progressbar_signal = pyqtSignal(str,int,str)
    check_version_signal = pyqtSignal()
    
    processpoll = douyin_onetime1=progressbaron=False  
    button_texts = sender_button = buttons_text =current_button=old_button=old_button_1=obssender_button=None
    exit_event = threading.Event()  
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  
        # self.setWindowIcon(QIcon('./logo.png')) 
        self.ui.setupUi(self)  
        # 隐藏菜单栏
        # self.menuBar().setHidden(True)
        # 无边框窗口
        # self.setWindowFlags(Qt.FramelessWindowHint)  
        self.button_lock = threading.Lock()
        self.thread_lock=threading.Lock()
        # DraggableWindowMixin( self.ui.label)
        self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint |Qt.WindowSystemMenuHint|Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint)
        self.msg_box = None

        # 将信号连接到槽
        self.check_version_signal.connect(self.check_version_and_start_app)
        # self.update_ui_signal.connect(self.update_ui_slot)
        self.progressbar_signal.connect(self.show_progressbar_dialog)
        self.show_message_signal.connect(self.show_msg_box)


        self.ui.qqqun.setText(qq_group)
        self.ui.confirm.setText("确认")
        #文本可换行
        self.ui.kaibotishi.setWordWrap(True)
        self.ui.chajiantxt.setWordWrap(True) 
        # 禁用按钮
        # self.ui.video_jishu.setDisabled(True)
        self.switch_mainpage(self.ui.start_page)      
        self.ui.toolButton_pingtai.clicked.connect(lambda: self.switch_mainpage(self.ui.pt_pape))
        self.ui.toolButton_obsset.clicked.connect(lambda: self.switch_mainpage(self.ui.obs_page))
        self.ui.toolButton_tool.clicked.connect(lambda: self.switch_mainpage(self.ui.tool_page))
        self.ui.vip_dates.clicked.connect(lambda: self.switch_mainpage(self.ui.Price_page))
        self.ui.weixinkefu.clicked.connect(lambda: self.qcode_page(self.ui.wxkefe))
        self.ui.chongzhi.clicked.connect(lambda: self.qcode_page(self.ui.chongzhihuiyuan))
        self.ui.vipinputtxt.clicked.connect(lambda: self.qcode_page(self.ui.shouquankey))
        self.ui.chongzhihuiyuan.setVisible(False)    ##将该元素设置为不可见状态
        self.ui.wxkefe.setVisible(False)
        self.ui.shouquankey.setVisible(False)  
        self.ui.keybuttonyes.clicked.connect(self.rechargeMembership)      
        #双击事件
        # self.ui.video_jishu.mouseDoubleClickEvent = self.handle_double_click
        self.ui.toolButton_bili.clicked.connect(self.jinggaotxt)
        self.ui.toolButton_ks.clicked.connect(self.jinggaotxt)


        self.ui.dy_1000.clicked.connect(self.switch_livemode)
        self.ui.dy_phone.clicked.connect(self.switch_livemode)
        self.ui.dy_auto_live.clicked.connect(self.switch_livemode)
        self.ui.dy_Accounts.clicked.connect(self.switch_livemode)
        self.ui.dy_livestop.clicked.connect(self.switch_livemode)
        ###connect 方法期望的是可调用对象（函数或方法）作为参数，而不是函数调用的结果。
        ###使用 lambda 函数的优点是代码更加紧凑，而不需要定义额外的函数。
        self.ui.ser_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.ui.ser_line.text()))
        self.ui.key_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.ui.key_line.text()))
        self.ui.bigin_live.clicked.connect(self.start_live_clicked)

        self.ui.toolButton_logo.clicked.connect(self.show_logo_menu)
        
        self.ui.pushButton.clicked.connect(self.obs_funtions)
        self.ui.pushButton_2.clicked.connect(self.obs_funtions)
        self.ui.pushButton_3.clicked.connect(self.obs_funtions)
        self.ui.pushButton_4.clicked.connect(self.obs_funtions)
        self.ui.pushButton_5.clicked.connect(self.obs_funtions)
        self.ui.pushButton_6.clicked.connect(self.obs_funtions)
        self.ui.pushButton_7.clicked.connect(self.obs_funtions)
        self.ui.pushButton_8.clicked.connect(self.obs_funtions)
        self.ui.pushButton_9.clicked.connect(self.obs_funtions)
        self.ui.pushButton_10.clicked.connect(self.obs_funtions)
        self.ui.pushButton_11.clicked.connect(self.obs_funtions)
        self.ui.pushButton_12.clicked.connect(self.obs_funtions)
        self.ui.pushButton_13.clicked.connect(self.obs_funtions)


        self.ui.Njds11Inches.clicked.connect(self.obs_funtions)
        self.ui.Njds129Inches.clicked.connect(self.obs_funtions)
        self.ui.Njds1920x1080.clicked.connect(self.obs_funtions)
        self.ui.Njdsdesktop.clicked.connect(self.obs_funtions)
        self.ui.Njds1080x1920.clicked.connect(self.obs_funtions)
        self.ui.NjdsDiy.clicked.connect(self.obs_funtions)

        self.ui.Adpt_highDefinition.clicked.connect(self.obs_funtions)
        self.ui.Adpt_ultraclear.clicked.connect(self.obs_funtions)
        self.ui.Adpt_blueLight.clicked.connect(self.obs_funtions)
        self.ui.Adpt_selfAdaption.clicked.connect(self.obs_funtions)


        self.ui.confirm.clicked.connect(self.obs_confirm_button)

        # 创建下拉菜单
        self.logo_menu = QMenu(self)
        self.logo_menu.setStyleSheet("QMenu::item { padding: 2px 20px; }")
        # 创建下拉菜单项
        action1 = QAction('手机DID', self)
        action2 = QAction('充值会员', self)
        action3 = QAction('关于软件', self)
        action4=QAction('版本更新',self)
        # 将菜单项添加到下拉菜单
        self.logo_menu.addAction(action1)
        self.logo_menu.addAction(action2)
        self.logo_menu.addAction(action3)
        self.logo_menu.addAction(action4)
        action1.triggered.connect(self.phone_did)
        action2.triggered.connect(lambda: self.switch_mainpage(self.ui.Price_page))
        action3.triggered.connect(self.show_about_ver)
        action4.triggered.connect(partial(self.check_version_and_start_app, 'upgrade'))

    ########中心窗口位置设计
    def center_window(self, child_window):
        # 计算子窗口的位置，使其显示在父窗口中间
        parent_window_pos = self.pos()
        parent_window_width = self.width()
        parent_window_height = self.height()

        child_window_width = child_window.width()
        child_window_height = child_window.height()

        x = int(parent_window_pos.x() + (parent_window_width - child_window_width) / 2)
        y = int(parent_window_pos.y() + (parent_window_height - child_window_height) / 2)

        child_window.move(QPoint(x, y))  # 使用QPoint传递整数坐标

    ########关闭事件设计
    def closeEvent(self,event):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        parent_conn.send("exit")
            # 终止子进程
        self.exit_event.set()
            # 等待线程结束 
        time.sleep(0.3)
        process1.join()  # 等待子进程结束
        event.accept()  # 关闭窗口
        # sys.exit()    #备用，主要关闭停止当前线程的循环和运行，某些情况下需要self.close()+sys.exit()来完全退出整个程序
        # os._exit(0)   #备用，强制关闭整个程序

    ########显示进度条
    def show_progressbar_dialog(self,label,value,start_progressbar):          
        # 设置进度值
        if value>80:
            value=80
        if not self.progressbaron:
            # 创建一个进度条实例
            self.progress_dialog = QProgressDialog(label, None, 0, 100)
            
            # 设置为无边框窗口
            self.progress_dialog.setWindowFlags(Qt.FramelessWindowHint)   
            
            # 设置为置顶窗口
            self.progress_dialog.setWindowModality(Qt.ApplicationModal)        

            # 设置背景颜色为白色
            self.progress_dialog.setStyleSheet("background-color: rgb(247, 249, 255);")
            
             # 根据需要设置宽度和高度
            self.progress_dialog.resize(360, 23) 

            # 将对话框与主应用程序关联，以主进程为父窗口
            self.progressbaron = True
            
        # # 设置进度条的位置为主窗口的中间
        self.center_window(self.progress_dialog)
        # 设置进度值
        self.progress_dialog.setValue(value)          
        # 显示无边框的进度对话框
        if start_progressbar=="show":
            # self.progress_dialog.setWindowFlag(Qt.WindowStaysOnTopHint)
            self.progress_dialog.show()
        elif start_progressbar=="close":
            self.processpoll=False
            for value in range (value,100):
                self.progress_dialog.setValue(value) 
                time.sleep(0.013)
                # QCoreApplication.processEvents()  # 让应用程序处理事件，以确保进度对话框更新          
            self.progress_dialog.close()
            self.progressbaron=False
            if label=="exit":    #####升级退出
                return
            if self.obssender_button == "pushButton_13" or self.obssender_button == "pushButton":
                self.show_message_signal.emit("提示", f"'{self.buttons_text}'根据提示安装程序,并重启小斗笠")
            else:
                self.show_message_signal.emit("提示", f"'{self.buttons_text}'安装成功")

    # def handle_double_click(self, event):
    #     if event.button() == Qt.LeftButton:
    #         # self.show_qrcode()
    #         parent_conn.send(self.old_button_1)
                
    ##########Pipn与子进程1通信
    def Listening_sub1(self):
        global app_did,sdkpid,threading_1,find_obs,obs_path,is_vip,lessday,initTime,versions,button_object_name
        threading_1=True
        self.exit_event.clear()
        ncout=0
        try:
            while not self.exit_event.is_set():
                ncout+=1
                if self.processpoll:
                    self.progressbar_signal.emit("", ncout,"")
                sub_send_result="" 
                if parent_conn.poll(initTime):
                    sub_send_result = parent_conn.recv()
                    # print("接收：",sub_send_result) 
                if "rtmp://" in sub_send_result:
                    left_part =sub_send_result.split('stream')[0]
                    right_part = "stream" + sub_send_result.split('stream')[1]            
                    self.ui.ser_line.setText(left_part)
                    self.ui.key_line.setText(right_part)
                    if button_object_name=="dy_phone":
                        self.show_message_signal.emit("操作提示", f"将手机飞行模式打开或清后台")
                    threading_1=False
                    self.exit_event.set()
                elif sub_send_result=="手机开播":
                    self.show_message_signal.emit("开播提示", f"将手机开播")
                elif "base64" in sub_send_result: 
                    self.ui.video_jishu.setVisible(True)                   
                    base64_data = sub_send_result.split(',')[1]
                    # 使用 QPixmap 设置图片u
                    pixmap = QPixmap()
                    pixmap.loadFromData(base64.b64decode(base64_data))
                    # Get the size of the button
                    button_size = self.ui.video_jishu.size()
                    self.ui.video_jishu.setIcon(QIcon(pixmap))
                    self.ui.video_jishu.setIconSize(button_size)
                    self.ui.video_jishu.setFixedSize(button_size)
                elif sub_send_result=="二维码消失":
                    self.ui.video_jishu.setVisible(False)  # 设置按钮不可见
                elif sub_send_result=="cleanlogs":
                    if os.path.exists('.\\worker0.log'):
                        with open('.\\worker0.log', 'w'):
                            pass

                elif sub_send_result=="plugin":
                    self.progressbar_signal.emit("", ncout,"close")
                    threading_1=False
                    self.processpoll=False
                    self.exit_event.set()
                elif "sub_Info_data" in sub_send_result:
                    print(sub_send_result)

                elif "版本更新" in sub_send_result:
                    self.processpoll=True
                    self.progressbaron=False
                    self.progressbar_signal.emit(f"{sub_send_result}", 0,"show")
                    ncout=3

                elif sub_send_result=="noBuildUpdate":
                    self.show_message_signal.emit("提示", "已经最新版本")
                elif sub_send_result=="直播间已关闭":
                    self.show_message_signal.emit("提示", "直播间已关闭")
                elif "会员" in sub_send_result:
                    # print(sub_send_result)
                    valvip,lessday,vipdays = sub_send_result.split(',')
                    #####将valvip获取的字符串值与"True"比较，如果一样，则is_vip为真
                    is_vip = valvip == "True"
                    self.ui.vip_dates.setText(vipdays)
                    self.ui.huiyuantime.setText(vipdays) 
                elif "obs64.exe" in sub_send_result: 
                    find_obs,obs_path = sub_send_result.split(',')
                    threading_1=False
                    self.exit_event.set()                  
                    initTime=1
                elif "startCompleted" in sub_send_result:
                    self.progressbar_signal.emit("exit", ncout,"close")
                    _,versions = sub_send_result.split(',')
                    self.processpoll=False
                  
                elif sub_send_result=="closeapp":
                    self.show_message_signal.emit("错误", "数据更新失败") 
                    threading_1=False
                    self.exit_event.set()
                    self.close()
                    sys.exit() 

                
        except Exception as e:
            # 捕获所有类型的异常，并将异常信息存储在变量 e 中
            logging.error(f"子线程发生异常：{e}")

    ##########充值会员
    def rechargeMembership(self):
        global is_vip,vipdays
        keys_txt=self.ui.vipinput.text()
        if keys_txt:
            is_key=check_key(keys_txt)
            # print(is_key)
            if is_key is not None:
                is_vip=True
                parent_conn.send("is_vip_True")
                vipdays=is_key
                self.ui.vip_dates.setText(is_key)
                self.ui.huiyuantime.setText(is_key)
                self.show_message_signal.emit("提示", f"开通成功")
            else:
                self.show_message_signal.emit("提示", f"密钥出错")
        else:
            self.show_message_signal.emit("提示", f"请输入密钥")            


    def jinggaotxt(self):
        self.show_message_signal.emit("提示", f"不可用")

    #########插件说明和显示
    def obs_funtions(self):  
        with self.button_lock:  
            self.current_button = self.sender().objectName()
            self.button_texts = self.sender().text()
            self.ui.confirm.setText("确认")
        try:
            config_data = json_dbase.data
            if 'pushButton' in self.current_button:
                button_info = config_data["obsconfigs"]["plugins"][self.current_button]["description"]                
                if obs_path:
                    plugins_file_path = config_data["obsconfigs"]["plugins"][self.current_button]["plugins_path"]
                    if self.current_button != 'pushButton_13' and self.current_button != 'pushButton_11':
                        plugins_file_path = os.path.join(obs_path, plugins_file_path)
                    if 'pushButton' ==self.current_button:
                        plugins_file_path=find_obs
                    if os.path.exists(plugins_file_path):
                        confirm_Text = config_data["obsconfigs"]["plugins"][self.current_button]["plugins_state"]
                        self.ui.confirm.setText(confirm_Text)

            elif 'Njds' in self.current_button or 'Adpt_' in self.current_button:
                button_info = config_data["obsconfigs"]["setting"][self.current_button]["description"]
            self.ui.chajiantxt.setText(button_info)

            if self.current_button=="NjdsDiy":
                txt1,txt2=self.resolution_dialog()
                if txt1 is None or txt2 is None:
                    self.current_button=None
                else:
                    self.current_button = f"{self.current_button},{str(txt1)},{str(txt2)}"
            elif self.current_button=="Adpt_selfAdaption":
                txt3=self.selfAdaption_dialog()
                if txt3 is None:
                    self.current_button=None
                else:
                    self.current_button = f"{self.current_button},{str(txt3)}"

        except Exception as e:
            # 捕获其他异常
            print(f"发生异常1：{e}")
            logging.error(f"发生异常1：{e}")
            return

    ##########插件下载
    def obs_confirm_button(self): 
        global threading_1
        # print(self.current_button)
        if self.current_button is None:
            return
        elif not find_obs and self.current_button=="pushButton":
            pass
        elif find_obs:
            if self.ui.confirm.text()=="应用" or "Njds" in self.current_button or "Adpt_" in self.current_button:
                if not is_vip:
                    self.show_msg_box("提示","此项为会员功能")
                else:
                    parent_conn.send(self.current_button)
                return
            elif "pushButton"in self.current_button:
                if self.ui.confirm.text()=="已安装":
                    self.show_message_signal.emit("提示", f"插件已安装")
                    return
                elif is_obs_running():
                    answ=self.show_msg_box("OBS关闭提示","关闭OBS安装插件","0")
                    if answ:
                        close_obs_processes()
                    else:
                        return  
        else:
            self.show_msg_box("提示","请先安装OBS")
            return

        if not self.processpoll: 
            self.processpoll=True 
            self.obssender_button = self.current_button
            self.buttons_text = self.button_texts
            # 发送数据到子进程
            parent_conn.send(self.obssender_button)
            self.progressbar_signal.emit(f"“{self.buttons_text}”插件安装", 0,"show")
            if not threading_1:
                polling_thread = threading.Thread(target=self.Listening_sub1)
                polling_thread.daemon = True
                polling_thread.start() 
        else:
            self.show_message_signal.emit("提示", f"“{self.buttons_text}”正在安装")

    def souserec_list(self):
        # 创建 QDialog 对话框
        getobssouse_dialog = QDialog(self)
        getobssouse_dialog.setWindowTitle('请选择录制源')

        # 创建可滚动区域
        scroll_area = QScrollArea(getobssouse_dialog)
        scroll_area.setWidgetResizable(True)

        # 创建 QWidget 作为可滚动区域的内部部件
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # 创建垂直布局
        layout = QVBoxLayout(scroll_content)

        # 获取输入源列表
        insourselist = self.mainobs_ws.client.call(requests.GetInputList())
        # print(insourselist.datain)

        # 根据输入源列表创建按钮并连接槽函数
        if len(insourselist.datain['inputs'])>0:
            chackkindname=False
            for item in insourselist.datain['inputs']:
                if item['inputKind']=='game_capture' or item['inputKind']=='window_capture' or item['inputKind']=='dshow_input':
                    file_name = item['inputName']
                    chackkindname=True
                    button = QPushButton(file_name, scroll_content)
                    button.clicked.connect(lambda _, name=file_name, dialog=getobssouse_dialog: self.show_file_content(name, dialog))####点击按钮时，传递按钮的名称，对话框的对象（用于关闭对话框）
                    layout.addWidget(button)
            if not chackkindname:
                self.show_message_signal.emit("操作错误", f"找不到“视频源”")
                return
        else:
            self.show_message_signal.emit("操作错误", f"找不到“视频源”")
            return

        # 设置按钮布局为可滚动区域的内部部件
        getobssouse_dialog_layout = QVBoxLayout(getobssouse_dialog)
        getobssouse_dialog_layout.addWidget(scroll_area)

        # 计算总高度
        total_height = len(insourselist.datain['inputs']) * 40  # 40是按钮的预估高度，可以根据实际情况调整
        getobssouse_dialog.setFixedSize(200, min(total_height, 200))  # 设置对话框的大小，最大高度200

        getobssouse_dialog.exec_()

    def show_file_content(self,file_name,about_dialog):
        cuprfname=self.mainobs_ws.GetProfileList_function()
        # output_w,output_h=self.mainobs_ws.GetVideoSettings_function()
        cucollename=self.mainobs_ws.GetSceneCollectionList_function()
        about_dialog.accept()
        self.mainobs_ws.Njdsmould_Profile()        
        time.sleep(2)
        self.mainobs_ws.SetCurrentProfile_function(cuprfname)
        time.sleep(0.2)
        self.mainobs_ws.SetCurrentSceneCollection_function(cucollename)
        time.sleep(0.2)        
        recordfilterSet={'bitrate': 16000, 'different_audio': False, 'encoder': 'x264', 'preset': 'veryfast', 'profile': 'high', 'rate_control': 'CBR', 'rec_format': 'mp4', 'record_mode': 2}
        self.mainobs_ws.client.call(requests.CreateSourceFilter(sourceName=file_name,filterName="Source Record",filterKind="source_record_filter",filterSettings=recordfilterSet))
        self.mainobs_ws.disconnect()

###########直播间地址输入
    def selfAdaption_dialog(self):
        resolution_value = ''  # 默认为空字符串
        resolution_dialog = QDialog(self)
        resolution_dialog.setWindowTitle('请输入设备分辨率')
        resolution_dialog.setGeometry(0, 0, 400, 200)
        self.center_window(resolution_dialog)

        layout = QVBoxLayout()

        resolution_label = QLabel('直播地址:')
        layout.addWidget(resolution_label)
        resolution_input = QLineEdit()
        layout.addWidget(resolution_input)

        confirm_button = QPushButton('确认')
        layout.addWidget(confirm_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        resolution_dialog.setLayout(layout)

        # 将确认按钮点击事件连接到对话框的 accept 方法
        confirm_button.clicked.connect(resolution_dialog.accept)

        result = resolution_dialog.exec_()

        if result == QDialog.Accepted and not resolution_input.text()=="":
            return resolution_input.text()
        else:
            return None

############画布自定义分辨率输入
    def resolution_dialog(self):
        # resolution_values = ('', '')  # 默认为空字符串
        resolution_dialog = QDialog(self)
        resolution_dialog.setWindowTitle('请输入设备分辨率(100-9999)')
        resolution_dialog.setGeometry(0, 0, 400, 200)
        self.center_window(resolution_dialog)

        layout = QVBoxLayout()

        width_label = QLabel('宽度:')
        layout.addWidget(width_label)
        width_input = QLineEdit()
        width_validator = QIntValidator(100, 9999)  # 设置范围
        width_input.setValidator(width_validator)
        layout.addWidget(width_input)

        height_label = QLabel('高度:')
        layout.addWidget(height_label)
        height_input = QLineEdit()
        height_validator = QIntValidator(100, 9999)  # 设置范围
        height_input.setValidator(height_validator)
        layout.addWidget(height_input)

        confirm_button = QPushButton('确认')
        layout.addWidget(confirm_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        resolution_dialog.setLayout(layout)

        # 将确认按钮点击事件连接到对话框的 accept 方法
        confirm_button.clicked.connect(resolution_dialog.accept)

        result = resolution_dialog.exec_()

        if result == QDialog.Accepted and not width_input.text()=='' and not height_input.text()=='' and int(width_input.text())>100 and int(height_input.text())>100:
            return width_input.text(), height_input.text()
        else:
            return None, None
     
###########手机DID填写
    def phone_did(self):
        app_did = ''
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle('请输入手机DID')
        about_dialog.setGeometry(0, 0, 400, 200)
        self.center_window(about_dialog)

        layout = QVBoxLayout()
        name_label = QLabel('手机抖音-->设置(拉到底部)-->狂点版本-->填写出现的DID值')
        layout.addWidget(name_label)

        try:
            with open("xdlconfig.json", "r") as config_file:
                config_data = json.load(config_file)
                app_did = config_data.get("appDID", '')
        except FileNotFoundError:
            app_did = ''
        did_input = QLineEdit()
        did_input.setText(app_did)
        layout.addWidget(did_input)

        confirm_button = QPushButton('确认')
        layout.addWidget(confirm_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        about_dialog.setLayout(layout)

        # 使用 lambda 传递参数
        confirm_button.clicked.connect(lambda: self.handle_did_input(did_input.text(), about_dialog))

        about_dialog.exec_()
        return did_input.text()

##########did写入和更新
    def handle_did_input(self, did, dialog):

        config_data = {
            "appDID": did        
        }

        # 读取现有数据（如果存在）
        try:
            with open("xdlconfig.json", "r") as config_file:
                existing_data = json.load(config_file)
        except FileNotFoundError:
            existing_data = {} 

        # 合并现有数据和新数据
        existing_data.update(config_data)

        # 将合并后的数据写回文件
        with open("xdlconfig.json", "w") as config_file:
            json.dump(existing_data, config_file, indent=4)

        dialog.accept()

##########软件的版本说明
    def show_about_ver(self):
        # 创建关于软件窗口
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle('关于小斗笠直播助手')
        about_dialog.setGeometry(0, 0, 500, 500)  # 设置窗口大小
        # 计算关于软件窗口的位置，使其显示在主窗口中间
        self.center_window(about_dialog)        
        # 创建布局
        layout = QVBoxLayout()

        # 创建并添加图标
        pixmap = QPixmap(":/img/imgs/douli.png")  # 替换成您的图标文件路径
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        layout.addWidget(icon_label)
        # 创建并添加标签显示软件版本
        version_label = QLabel(f'软件版本: V{versions}')
        layout.addWidget(version_label)

        # 创建并添加标签显示QQ群和微信号        
        qq_group_label = QLabel(qq_group)
        wechat_label = QLabel('其他说明: 本软件部分插件内容来源于网络，若有版权纠纷请及时告知，我们会在第一时间处理')
        layout.addWidget(qq_group_label)
        layout.addWidget(wechat_label)

        about_dialog.setLayout(layout)
        # 显示关于软件窗口
        about_dialog.exec_()

#########小菜单的显示位置
    def show_logo_menu(self):
        # 获取菜单工具按钮的全局坐标
        pos = self.ui.toolButton_logo.mapToGlobal(self.ui.toolButton_logo.rect().bottomLeft())    
        # 在指定位置显示下拉菜单
        self.logo_menu.exec_(pos)

##########软件界面的交替显示
    @pyqtSlot()
    def switch_mainpage(self, page):
        self.ui.pt_pape.hide()
        self.ui.obs_page.hide()
        self.ui.music_page.hide()
        self.ui.Price_page.hide()
        self.ui.start_page.hide()
        self.ui.tool_page.hide()
        page.show()

##########充值码是显示
    @pyqtSlot()
    def qcode_page(self, page):
        self.ui.wxkefe.hide()
        self.ui.chongzhihuiyuan.hide()
        self.ui.shouquankey.hide()
        page.show()
        if page==self.ui.chongzhihuiyuan:
            uuid4_mod=uuid_winc()
            # 生成一个随机的起始索引
            start_index = random.randint(0, len(uuid4_mod) - 4)

            # 获取任意连续的4个字符的值
            random_substring = uuid4_mod[start_index:start_index + 4]

            yanzheng=f"{random_substring}{lessday}"
            self.ui.chongzhibz.setText(yanzheng)

########开播方式选择
    def switch_livemode(self):
        global app_did,is_vip,threading_1,button_object_name
        live_list={
            "dy_1000":"选择“伴侣开播”--->电脑直播伴侣开播--->等待软件自动获取到推流码--->一键开播(会员功能)",
            "dy_phone":"选择“手机开播”--->手机抖音扫码--->手机抖音手游开播--->等待软件自动获取到推流码--->手机飞行模式或强退抖音--->一键开播(会员功能)",
            "dy_Accounts":"选择“账号切换”--->手机扫码登录--->显示账号图像及切换成功",
            "dy_livestop":"针对手机开播和自动开播，一键停止直播",
            "dy_auto_live":"支持0粉和1000粉,省去繁杂步骤，一键自动开播",
        }
        
        try:  
            with self.button_lock:
                button_object_name = self.sender().objectName()
                self.ui.ser_line.setText("")
                self.ui.key_line.setText("")
                self.ui.kaibotishi.setText(live_list.get(button_object_name, ""))
            if not is_vip and (button_object_name == "dy_auto_live" or button_object_name =="dy_livestop"):
                self.show_message_signal.emit("提示", f"会员功能")
                return
            if button_object_name == "dy_phone" and not is_vip:
                # try:
                #     with open("xdlconfig.json", "r") as config_file:
                #         config_data = json.load(config_file)
                #         app_did = config_data.get("appDID", '')
                # except Exception as e:
                #     pass
                # print(app_did)
                if not app_did:
                    app_did = self.phone_did()                      
                    if not app_did:                            
                        return
                time.sleep(0.5)
                self.show_message_signal.emit("开播模式提示", f"手机上选择“手游”开播")
            
            parent_conn.send(button_object_name)  
       
            if not threading_1:
                zhibobanlv_thread = threading.Thread(target=self.Listening_sub1)
                zhibobanlv_thread.start()
        except Exception as e:
            # 捕获所有类型的异常，并将异常信息存储在变量 e 中
            logging.exception(f"按钮发生异常：{e}")

########一键开播
    def start_live_clicked(self):
        global is_vip,find_obs
        if find_obs is not None:              
            if self.ui.ser_line.text() or self.ui.key_line.text():
                if is_vip:  
                    parent_conn.send(f'{self.ui.ser_line.text()},{self.ui.key_line.text()}')
                else:
                    self.show_message_signal.emit("错误", f"非会员!!!请手动复制串流到OBS")                
            else:
                self.show_message_signal.emit("错误", f"先获取推流码")
        else:
            self.show_message_signal.emit("错误", f"请先安装OBS")

#########消息框设计
    def show_msg_box(self,title,txt,Code_name=None):
        # 如果旧消息框存在，关闭它
        if self.msg_box and self.msg_box.isVisible():
            self.msg_box.accept()
        self.msg_box = QMessageBox(self)
        # 设置消息框的中心坐标为主窗口的中心坐标
        self.center_window(self.msg_box)
        self.msg_box.setIcon(QMessageBox.Warning)
        self.msg_box.setWindowTitle(title)
        self.msg_box.setText(txt)

        # 添加确定按钮
        ok_button = self.msg_box.addButton(QMessageBox.Ok)    
        # 添加关闭按钮
        if Code_name is not None:
            close_button = self.msg_box.addButton(QMessageBox.Close)          

        # 显示消息框
        result = self.msg_box.exec_()

        
        # 根据用户的选择返回不同的标志
        if result == QMessageBox.Ok:
            return True
        else:
            return False   

#########软件启动检验
    def check_version_and_start_app(self,nowcheck=None):
        global versions,vipdays,is_vip,lessday
        try:
            if nowcheck is not None:
                parent_conn.send("manualUpdate") 
            else:  
                self.progressbar_signal.emit(f"加载中...", 0,"show")  
                self.processpoll=True  
            if os.path.exists('.\\xDLCache\\data_p.file') and os.path.exists('.\\xDLCache\\data_c.file'):
                try:
                    with open('.\\xDLCache\\data_p.file', 'r') as file:
                        base64_data = file.read() 
                        # 使用 QPixmap 设置图片u
                    pixmap = QPixmap()
                    pixmap.loadFromData(base64.b64decode(base64_data))
                    # Get the size of the button
                    button_size = self.ui.video_jishu.size()
                    self.ui.video_jishu.setIcon(QIcon(pixmap))
                    self.ui.video_jishu.setIconSize(button_size)
                    self.ui.video_jishu.setFixedSize(button_size)
                except Exception as e:
                    logging.error(f"头像加载图片失败：{e}")
            Update_thread = threading.Thread(target=self.Listening_sub1)
            Update_thread.daemon=True
            Update_thread.start()
            
        except Exception as e:
            self.show_message_signal.emit("start错误", str(e))
            self.close()
            sys.exit()

    # def open_browser(self):
    #     # 在点击按钮时打开浏览器并跳转到指定网址
    #     url = QUrl("http://www.baidu.com")
    #     QDesktopServices.openUrl(url)

    # def display_gif(self):
    #     # 本地 GIF 文件路径
    #     gif_path = ".\\waiting0.gif"

    #     # 使用 QMovie 设置动图
    #     movie = QMovie(gif_path)

    #     # 设置动图给 QLabel
    #     self.ui.live0_movie.setMovie(movie)
    #     # 获取 GIF 的原始大小
    #     original_size = movie.scaledSize()

    #     # 缩放 GIF 以适应 QLabel 的大小，保持宽高比
    #     aspect_ratio = original_size.width() / original_size.height()
    #     target_width = self.ui.live0_movie.width()
    #     target_height = int(target_width / aspect_ratio)

    #     #     # 缩放 GIF 自适应 QLabel 的大小，但比例不匹配会拉伸
    #     #     movie.setScaledSize(self.ui.live0_movie.size())
    #     # 开始播放动图
    #     movie.setScaledSize(QSize(target_width, target_height))
    #     # 开始播放动图
    #     movie.start()

# 主函数
def main():
    # 配置 logging
    logging.basicConfig(filename='.\\worker0.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s: %(message)s')

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()    
    window.check_version_signal.emit()  # 发送信号启动版本检测,使用后发现，如果版本不匹配退出时，self.close()退出软件但还有后台在运行，需要加上sys.exit()才完全退出，最后还有一种就是os._exit(0)强制完全退出
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        # #########创建LoggerWriter实例并重定向输出流
        # sys.stdout = LoggerWriter(logging.info)
        # sys.stderr = LoggerWriter(logging.error)
        # ###### 创建一个线程来检测版本和启动应用

        multiprocessing.freeze_support()    #防止子进程无限创建
        ########创建子进程，将管道传递给子进程
        process1 = multiprocessing.Process(target=sub_process1, args=(child_conn,))
        process1.start()
        main()
    except Exception as e:
        logging.error(f"An error occurred in the main block: {e}")