@echo off
echo Checking for Python installation...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading and installing Python...
    curl -o python_installer.exe https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    echo Python installed successfully.
) ELSE (
    echo Python is already installed.
)
echo Checking Python installation path...
setlocal
for /f "delims=" %%F in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%F
endlocal & set PATH=%PATH%;%PYTHON_PATH%
echo Upgrading pip...
python -m ensurepip --default-pip
python -m pip install --upgrade pip
echo Installing required Python packages...
pip install pygame-ce pygame_gui requests
echo Installation complete!
pause
