import requests
import subprocess
from colorama import Fore,init
import os
import getpass

def DowngradePip():
    subprocess.run("python -m pip install pip==20.2.4")
def InstallPip():
    script = requests.get('https://bootstrap.pypa.io/get-pip.py')
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\")
    with open('temp.py', 'w') as file:
        file.write(script.text)
    os.system('python temp.py')

    os.system("del temp.py")
def Upgrade():
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    try:
        import RobloxPyApi3
    except:
        init(convert=True)
        print(f"{Fore.RED}---- RobloxPyApi3 package not found ----{Fore.RESET}")
        Install()
    request = requests.get('https://pypi.org/pypi/RobloxPyApi3/json')
    global vers
    if not request.json()["info"]['version'] == RobloxPyApi3.__version__:
        vers = request.json()["info"]['version']
    else:
        vers = request.json()["info"]['version']
    if "pip.exe" in os.listdir():
        print(f'{Fore.GREEN}--- Found pip.exe! Updating RobloxPyApi3, (3/1) Downgrade pip ----{Fore.RESET}')
        DowngradePip()
        print(f'-{Fore.GREEN}-- Downgrade success! Updating RobloxPyApi3, (3/2) Uninstall ----{Fore.RESET}')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'{Fore.GREEN}--- Updating RobloxPyApi3, (3/3) install ----{Fore.RESET}')
        subprocess.run("pip install RobloxPyApi3")
        print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3 ----{Fore.RESET}")
    else:
        print(f'{Fore.RED}--- Pip not found. Updating RobloxPyApi3, (4/1) Installing pip ----{Fore.RESET}')
        InstallPip()
        print(f'{Fore.GREEN}--- installed pip! Updating RobloxPyApi3, (4/2) Downgrade pip ----{Fore.RESET}')
        DowngradePip()
        print(f'{Fore.GREEN}--- installed pip! Updating RobloxPyApi3, (4/3) Uninstall ----{Fore.RESET}')
        subprocess.run(f"pip uninstall RobloxPyApi3=={RobloxPyApi3.__version__}")
        print(f'{Fore.GREEN}--- Updating RobloxPyApi3, (4/4) install ----{Fore.RESET}')
        subprocess.run(f"pip install RobloxPyApi3=={request.json()['info']['version']}")
        print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3 ----{Fore.RESET}")
    #os.system("del temp.py")
def GetPythonVersion():
    os.chdir(f'C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\')
    if os.listdir()[0]:
        return os.listdir()[0]
    else:
        return
def UnInstall():
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'{Fore.GREEN}--- Found pip.exe! Uninstalling RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'{Fore.GREEN}--- Success! ----{Fore.RESET}')
    else:
        print(f"{Fore.RED}---- Pip not found, installing pip ----{Fore.RESET}\n")
        InstallPip()
        print(f'{Fore.GREEN}--- Pip installed successfully! UnInstalling RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'{Fore.GREEN}--- Success! ----{Fore.RESET}')
class UpdateEnums():
    def __init__(self,_UpTodate,_UpdateFound):
        UpTodate = _UpTodate
        UpdateFound = _UpdateFound
def Install():
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'{Fore.GREEN}--- Found pip.exe! installing RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run("pip install RobloxPyApi3")
    else:
        print(f"{Fore.RED}---- Pip not found, installing pip ----{Fore.RESET}\n")
        InstallPip()
        print(f'{Fore.GREEN}--- Pip installed successfully! installing RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run("pip install RobloxPyApi3")
        print(f'{Fore.GREEN}--- Success! ----{Fore.RESET}')

def Update():
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    try:
        import RobloxPyApi3
    except:
        print(f"{Fore.RED}---- RobloxPyApi3 package not found ----{Fore.RESET}")
        Install()


    request = requests.get('https://pypi.org/pypi/RobloxPyApi3/json')
    global vers
    if not request.json()["info"]['version'] == RobloxPyApi3.__version__:
        vers = request.json()["info"]['version']
    else:
        vers = request.json()["info"]['version']
    if "pip.exe" in os.listdir():
        print(f'{Fore.GREEN}--- Found pip.exe! Updating RobloxPyApi3, (3/1) Downgrade pip ----{Fore.RESET}')
        DowngradePip()
        print(f'-{Fore.GREEN}-- Downgrade success! Updating RobloxPyApi3, (3/2) Uninstall ----{Fore.RESET}')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'{Fore.GREEN}--- Updating RobloxPyApi3, (3/3) install ----{Fore.RESET}')
        subprocess.run("pip install RobloxPyApi3")
        print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3 ----{Fore.RESET}")
    else:
        print(f'{Fore.RED}--- Pip not found. Updating RobloxPyApi3, (4/1) Installing pip ----{Fore.RESET}')
        InstallPip()
        print(f'{Fore.GREEN}--- installed pip! Updating RobloxPyApi3, (4/2) Downgrade pip ----{Fore.RESET}')
        DowngradePip()
        print(f'{Fore.GREEN}--- installed pip! Updating RobloxPyApi3, (4/3) Uninstall ----{Fore.RESET}')
        subprocess.run(f"pip uninstall RobloxPyApi3=={RobloxPyApi3.__version__}")
        print(f'{Fore.GREEN}--- Updating RobloxPyApi3, (4/4) install ----{Fore.RESET}')
        subprocess.run(f"pip install RobloxPyApi3=={request.json()['info']['version']}")
        print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3 ----{Fore.RESET}")
def Update_RPA3U():
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\")
    with open("temp.py",'w') as file:
        file.write("""
import requests
import subprocess
import os
import getpass
from colorama import init,Fore
def InstallPip():
    init(convert=True)
    script = requests.get('https://bootstrap.pypa.io/get-pip.py')
    os.chdir(f"C:\\\\Users\\\\{getpass.getuser()}\\\\Appdata\\\\local\\\\programs\\\\python\\\\{GetPythonVersion()}\\\\")
    with open('tmp.py', 'w') as file:
        file.write(script.text)
    os.system('python tmp.py')
def DowngradePip():
    subprocess.run("python -m pip install pip==20.2.4")
def GetPythonVersion():
    init(convert=True)
    os.chdir(f'C:\\\\Users\\\\{getpass.getuser()}\\\\Appdata\\\\local\\\\programs\\\\python\\\\')
    if os.listdir()[0]:
        return os.listdir()[0]
    else:
        return
init(convert=True)
os.chdir(f"C:\\\\Users\\\\{getpass.getuser()}\\\\Appdata\\\\local\\\\programs\\\\python\\\\{GetPythonVersion()}\\\\Scripts\\\\")
request = requests.get('https://pypi.org/pypi/RobloxPyApi3Update/json')
vers = request.json()["info"]['version']
if "pip.exe" in os.listdir():
    init(convert=True)
    print(f'{Fore.GREEN}--- Found pip.exe! Updating RobloxPyApi3Update, (3/1) Downgrade pip ----{Fore.RESET}')
    DowngradePip()
    print(f'{Fore.GREEN}--- Downgrade successful! Updating RobloxPyApi3Update, (3/2) Uninstall ----{Fore.RESET}')
    subprocess.run("pip uninstall RobloxPyApi3Update")
    print(f'{Fore.GREEN}--- Updating RobloxPyApi3Update, (3/3) install ----{Fore.RESET}')
    subprocess.run(f"pip install RobloxPyApi3Update=={vers}")
    print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3Update ----{Fore.RESET}")
    #subprocess.run(f"del temp.py") 
else:
    print(f'{Fore.RED}--- Pip not found. Updating RobloxPyApi3Update, (4/1) Installing pip ----{Fore.RESET}')
    InstallPip()
    print(f'{Fore.GREEN}--- installed pip! Updating RobloxPyApi3Update, (4/2) Downgrade pip ----{Fore.RESET}')
    DowngradePip()
    print(f'{Fore.GREEN}---  Downgrade successful! Updating RobloxPyApi3Update, (4/3) Uninstall ----{Fore.RESET}')
    subprocess.run(f"pip uninstall RobloxPyApi3Update")
    print(f'{Fore.GREEN}--- Updating RobloxPyApi3Update, (4/4) install ----{Fore.RESET}')
    subprocess.run(f"pip install RobloxPyApi3Update=={vers}")
    print(f"{Fore.GREEN}---- Successfully updated RobloxPyApi3Update ----{Fore.RESET}")
     
    #subprocess.run(f"del temp.py") 
    """)
    subprocess.run("python temp.py")
    try:
        os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\")
        os.system(f"del temp.py")
    except:
        pass
def InstallVersion(version):
    init(convert=True)
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'{Fore.GREEN}--- Found pip.exe! installing RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run(f"pip install RobloxPyApi3=={version}")
    else:
        print(f"{Fore.RED}---- Pip not found, installing pip ----{Fore.RESET}\n")
        InstallPip()
        print(f'{Fore.GREEN}--- Pip installed successfully! installing RobloxPyApi3 ----{Fore.RESET}')
        subprocess.run(f"pip install RobloxPyApi3=={version}")
        print(f'{Fore.GREEN}--- Successfully Installed RobloxPyApi3! ----{Fore.RESET}')
#def SetupPythonForCmd():
    #print('this feature is unavailable. sorry')
    #return

     #try:
        #file = open(f'C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\data.txt')
        #if file:
            #print("Data found, delete data.txt to continue, or risk at ENVIRON spam .\n you need to delete every python variable after that.")
            #print(f'file located in C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\data.txt')

     #except:
        #os.environ['Path'] = os.environ[
                            #'Path'] + f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()};C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()}\\Scripts;"
        #os.environ['Python'] = f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()}\\python.exe"
        #with open('data.txt','w') as file:
            #file.write('SetupPythonForCmdSaved98822932')

def DeleteFileData():
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\")
    os.system('del data.txt')
def CheckForUpdates():
    try:
        import RobloxPyApi3
    except:
        init(convert=True)
        print(f"{Fore.RED}---- RobloxPyApi3 package not found ----{Fore.RESET}")
        Install()
    request = requests.get('https://pypi.org/pypi/RobloxPyApi3/json')
    if request.json()["info"]['version'] != RobloxPyApi3.__version__:
        UpdateFound = ['_UpdateFound',True]
        UpToDate = ['_UpToDate',False]
        return [UpdateFound,UpToDate]
    else:
        UpdateFound = ['_UpdateFound',False]
        UpToDate = ['_UpToDate',True]

        return [UpdateFound,UpToDate]