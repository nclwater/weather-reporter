FROM microsoft/windowsservercore:1803

RUN powershell (New-Object System.Net.WebClient).DownloadFile('https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe', 'Anaconda3.exe')

RUN powershell Unblock-File Anaconda3.exe

RUN Anaconda3.exe /InstallationType=JustMe /RegisterPython=1 /S /D=%UserProfile%\Anaconda3

RUN del Anaconda3.exe

WORKDIR /

RUN setx /M PATH "%PATH%;%UserProfile%\Anaconda3;%UserProfile%\Anaconda3\Scripts;%UserProfile%\Anaconda3\Library\bin"

COPY environment.yml environment.yml

RUN conda env update -n base -f environment.yml
