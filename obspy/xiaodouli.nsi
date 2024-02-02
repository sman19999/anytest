; �ýű�ʹ�� HM VNISEdit �ű��༭���򵼲���
Unicode true
; ��װ�����ʼ���峣��
!define PRODUCT_NAME "xiaodouli"
!define PRODUCT_VERSION "1.1.5"
!define PRODUCT_PUBLISHER "xiaodouli"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_INSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Install\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma
RequestExecutionLevel admin
; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
!define MUI_ABORTWARNING
!define MUI_ICON "obspy\icons\logo0.ico"
!define MUI_UNICON "obspy\icons\logo0.ico"

; ��ӭҳ��
!insertmacro MUI_PAGE_WELCOME
; ���Э��ҳ��
!insertmacro MUI_PAGE_LICENSE "obspy\xieyi.txt"
; ��װ����ҳ��
!insertmacro MUI_PAGE_INSTFILES
; ��װ���ҳ��
!define MUI_FINISHPAGE_RUN "$INSTDIR\xiaodouli.exe"
!insertmacro MUI_PAGE_FINISH

; ��װж�ع���ҳ��
!insertmacro MUI_UNPAGE_INSTFILES

; ��װ�����������������
!insertmacro MUI_LANGUAGE "SimpChinese"

; ��װԤ�ͷ��ļ�
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI �ִ����涨����� ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "xiaodlbuild.exe"
InstallDir "$LOCALAPPDATA\xdlwebcast"
ShowInstDetails show
ShowUnInstDetails show
BrandingText "С����ֱ������"

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
  ;��Ե�ǰ�û���Ч
  WriteRegStr HKCU "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${PRODUCT_NAME}.exe" "RUNASADMIN"
  ;��������û���Ч
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" "$INSTDIR\${PRODUCT_NAME}.exe" "RUNASADMIN"
  ;WriteRegStr HKLM "SOFTWARE\xdlwebcast" "appinstalltime" "XXXXXX"
  ;WriteRegStr HKLM "Software\Microsoft\Clients\Medie\MedieCast\InstallInfo" "instime" "xxxxxxxx"
  ;WriteRegStr HKLM "Software\Microsoft\Clients\Medie\MedieCast\Capabilities" "KEY" "AAAAAAAABBBBBBBBBBBCCCCCCCCCCC"
SectionEnd

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File /r "obspy\dist\xiaodouli\*.*"
  CreateShortCut "С����ֱ������.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$DESKTOP\С����ֱ������.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$STARTMENU\С����ֱ������.lnk" "$INSTDIR\xiaodouli.exe"
  CreateShortCut "$QUICKLAUNCH\С����ֱ������.lnk" "$INSTDIR\xiaodouli.exe"
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

;��Ĭ��װ������
Function .onInstSuccess
  ExecShell "open" "$INSTDIR\xiaodouli.exe"
FunctionEnd
/******************************
 *  �����ǰ�װ�����ж�ز���  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\uninst.exe"

  Delete "$SMPROGRAMS\xiaodouli\Uninstall.lnk"
  Delete "$QUICKLAUNCH\С����ֱ������.lnk"
  Delete "$STARTMENU\С����ֱ������.lnk"
  Delete "$DESKTOP\С����ֱ������.lnk"
  Delete "С����ֱ������.lnk"

  RMDir "$SMPROGRAMS\xiaodouli"
  RMDir ""

  RMDir /r "$INSTDIR\_internal"
  RMDir /r "$INSTDIR\*.*"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  ;DeleteRegKey HKLM "Software\Microsoft\Clients\Medie\MedieCast\InstallInfo"
  SetAutoClose true
SectionEnd

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#


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
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "��ȷʵҪ��ȫ�Ƴ� $(^Name) ���������е������" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) �ѳɹ��ش����ļ�����Ƴ���"
FunctionEnd

