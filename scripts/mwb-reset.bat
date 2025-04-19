@echo off
title mwb-reset

net session >nul 2>&1
if not %errorLevel%==0 (
    echo [-] administrative permissions are required!
    pause >nul
    exit
)

echo [+] killing malwarebytes...
set "MBAM_PATH_X86=%PROGRAMFILES(X86)%\Malwarebytes\Anti-Malware\malwarebytes_assistant.exe"
set "MBAM_PATH_X64=%PROGRAMFILES%\Malwarebytes\Anti-Malware\malwarebytes_assistant.exe"
if exist "%MBAM_PATH_X86%" (
    "%MBAM_PATH_X86%" --stopservice
) else if exist "%MBAM_PATH_X64%" (
    "%MBAM_PATH_X64%" --stopservice
) else (
    echo [-] malwarebytes not found. exiting...
    timeout 3 >nul
    exit
)
taskkill /f /im MBAMService.exe

echo [+] changing guids...
for /f %%a in ('powershell -c "[guid]::NewGuid().ToString()"') do (
    reg add "HKLM\SOFTWARE\Microsoft\Cryptography" /v "MachineGuid" /t REG_SZ /d "%%a" /f >nul
)

echo [+] restarting malwarebytes...
if exist "%MBAM_PATH_X86%" (
    start "" "%MBAM_PATH_X86%" >nul 2>&1
) else if exist "%MBAM_PATH_X64%" (
    start "" "%MBAM_PATH_X64%" >nul 2>&1
)

echo [+] reinstalling malwarebytes...
curl https://data-cdn.mbamupdates.com/web/mb5-setup-consumer/MBSetup.exe --output %~dp0MBSetup.exe
start "" "%~dp0MBSetup.exe"

echo [+] done!
pause >nul
exit