; 该脚本使用 HM VNISEdit 脚本编辑器向导产生
Unicode true
; 安装程序初始定义常量
!define PRODUCT_NAME "xiaodouli"
!define PRODUCT_VERSION "1.1.5"
!define PRODUCT_PUBLISHER "xiaodouli"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_INSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Install\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma
RequestExecutionLevel admin
; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
!define MUI_ABORTWARNING
!define MUI_ICON "obspy\icons\logo0.ico"
!define MUI_UNICON "obspy\icons\logo0.ico"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面
!insertmacro MUI_PAGE_LICENSE "obspy\xieyi.txt"
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\xiaodouli.exe"
!insertmacro MUI_PAGE_FINISH

; 安装卸载过程页面
!insertmacro MUI_UNPAGE_INSTFILES

; 安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装预释放文件
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI 现代界面定义结束 ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "xiaodlbuild.exe"
InstallDir "$LOCALAPPDATA\xdlwebcast"
ShowInstDetails show
ShowUnInstDetails show
BrandingText "小斗笠直播助手"

SilentInstall silent
;Section "appkill"
;    StrCpy $1 "${PRODUCT_NAME}.exe"
;    nsProcess::_FindProcess "$1"
;    Pop $R0
;    ${If} $R0 = 0
;        nsProcess::_KillProcess "$1"
;        Pop $R0
;        Sleep 500
;    ${EndIf}
;SectionEnd


Section "runamin"
  ;针对当前用户有效
  WriteRegStr HKCU "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${PRODUCT_NAME}.exe" "RUNASADMIN"
  ;针对所有用户有效
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${PRODUCT_NAME}.exe" "RUNASADMIN"
  ;WriteRegStr HKLM "SOFTWARE\xdlwebcast" "appinstalltime" "XXXXXX"
  ;WriteRegStr HKLM "Software\Microsoft\Clients\Medie\MedieCast\InstallInfo" "instime" "xxxxxxxx"
  ;WriteRegStr HKLM "Software\Microsoft\Clients\Medie\MedieCast\Capabilities" "KEY" "AAAAAAAABBBBBBBBBBBCCCCCCCCCCC"
SectionEnd

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File /r "obspy\dist\xiaodouli\*.*"
  CreateShortCut "小斗笠直播助手.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$DESKTOP\小斗笠直播助手.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$STARTMENU\小斗笠直播助手.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$QUICKLAUNCH\小斗笠直播助手.lnk" "$INSTDIR\xiaodouli.exe"
SectionEnd

Section -AdditionalIcons
  CreateDirectory "$SMPROGRAMS\xiaodouli"
  CreateShortCut "$SMPROGRAMS\xiaodouli\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_NAME}.exe"
SectionEnd

;静默安装后运行
Function .onInstSuccess
  ExecShell "open" "$INSTDIR\xiaodouli.exe"
FunctionEnd
/******************************
 *  以下是安装程序的卸载部分  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\uninst.exe"

  Delete "$SMPROGRAMS\xiaodouli\Uninstall.lnk"
  Delete "$QUICKLAUNCH\小斗笠直播助手.lnk"
  Delete "$STARTMENU\小斗笠直播助手.lnk"
  Delete "$DESKTOP\小斗笠直播助手.lnk"
  Delete "小斗笠直播助手.lnk"

  RMDir "$SMPROGRAMS\xiaodouli"
  RMDir ""

  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\*.*"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  ;DeleteRegKey HKLM "Software\Microsoft\Clients\Medie\MedieCast\InstallInfo"
  SetAutoClose true
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#


!macro KillProcess
    StrCpy $1 "${PRODUCT_NAME}.exe"
    nsProcess::_FindProcess "$1"
    Pop $R0
    ${If} $R0 = 0
        nsProcess::_KillProcess "$1"
        Pop $R0
        Sleep 500
    ${EndIf}
!macroend

Function .onInit
    !insertmacro KillProcess
    RMDir /r "$INSTDIR\_internal"
FunctionEnd

Function un.onInit
  !insertmacro KillProcess
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "您确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从您的计算机移除。"
FunctionEnd

