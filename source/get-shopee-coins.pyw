import os
import json
import pickle
import logging
import requests
import traceback
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from subprocess import Popen, PIPE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class Cryptor():
    def __init__(self):
        self.key = self.loadOrCreateKey()
        self.iv = binascii.unhexlify(b'ffcf96321e198562928ca5bb01c49d01')
        self.encryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.decryptor = AES.new(self.key, AES.MODE_CBC, self.iv)
    # end __init__()

    def loadOrCreateKey(self):
        key = None
        if os.path.isfile(path.key):
            with open(path.key, 'rb') as key_file: key = key_file.read()
        else: 
            key = get_random_bytes(16)
            with open(path.key, 'wb') as key_file: key_file.write(key)
        # end if-else

        return key
    # end loadOrCreateKey()

    def encrypt(self, message):
        return self.encryptor.encrypt(pad(message.encode(), 16))
    # end encrypt()

    def decrypt(self, message):
        return unpad(self.decryptor.decrypt(message), 16).decode()
    # end decrypt()
# end class Cryptor

class Chrome():
    def __init__(self):
        self.options = None
        self.service = Service(path.chrome_driver)
        self.driver = None
        self.cryptor = Cryptor()
        self.getLatestChromedriver()
    # end __init__()

    def hasChromedriver(self):
        return os.path.isfile(path.chrome_driver)
    # end hasChromedriver()

    def getMajorBrowserVersion(self): # get current major Chrome browser version
        command = 'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v "version"'
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        process.terminate()

        return stdout.decode().split()[-1].split('.')[0]
    # end getMajorBrowserVersion()

    def getMajorDriverVersion(self): # get current major Chrome driver version
        command = f'{path.gsc}\chromedriver.exe -v'
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, _ = process.communicate()
        process.terminate()

        return stdout.decode().split()[1].split('.')[0]
    # end getMajorDriverVersion()

    def getLatestChromedriver(self): # when driver doesnt exist OR driver too old
        if not self.hasChromedriver() or self.getMajorBrowserVersion() != self.getMajorDriverVersion(): 
            # get latest driver version of Chrome
            latest_driver_version = requests.get(f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{self.getMajorBrowserVersion()}').text
            data = requests.get(f'https://chromedriver.storage.googleapis.com/{latest_driver_version}/chromedriver_win32.zip').content
            ZipFile(BytesIO(data)).extractall(path.gsc)
            logging.info(f'chromedriver.exe has been updated/downloaded')
        # end if
    # end getLatestChromedriver()

    def open(self, mode, url):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--' + mode)
        self.options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.get(url)
    # end open()

    def close(self):
        self.driver.quit()
    # end close()

    def clean(self): # clean current driver if any
        if self.driver and self.driver.service.is_connectable(): self.driver.quit()
    # end clean()

    def waitUntilElementIsLocated(self, locator, timeout):
        return WebDriverWait(self.driver, timeout).until(expected_conditions.presence_of_element_located(locator))
    # end waitUntilElementIsLocated()

    def loadCookies(self, user):
        for cookie in pickle.load(open(path.cookies + user, 'rb')): 
            self.driver.add_cookie(cookie)
        # end for

        self.driver.refresh()
    # end loadCookies()

    def saveCookies(self, user):
        pickle.dump(self.driver.get_cookies(), open(path.cookies + user, 'wb'))
    # end saveCookies()

    def loadCredentials(self, user):
        with open(path.credentials + user, 'rb') as credentials_file:
            credentials = self.cryptor.decrypt(credentials_file.read()).split('\n')
        # end with-as

        return credentials[0], credentials[1] # return username & password
    # end loadCredentials()

    def saveCredentials(self, user):
        username = self.driver.execute_script('return localStorage.getItem("un")\nlocalStorage.removeItem("un")')
        password = self.driver.execute_script('return localStorage.getItem("pw")\nlocalStorage.removeItem("pw")')
        
        with open(path.credentials + user, 'wb') as credentials_file:
            credentials_file.write(self.cryptor.encrypt(username + '\n' + password))
        # end with-as
    # end saveCredentials()

    def setupLoginPage(self, user):
        self.driver.execute_script(f'document.title = "Login Page for User[{user}]"')
        self.driver.execute_script('username = document.querySelector("#main > div > div._1229NB > div > div > form > div > div._3e4zDA > div._3nZHpB > div._3mizNj > input")\n\
                                    password = document.querySelector("#main > div > div._1229NB > div > div > form > div > div._3e4zDA > div._35M4-Y > div._3mizNj > input")\n\
                                    div = document.createElement("div")\n\
                                    div.id = "GSC"\n\
                                    parent = document.querySelector("#main > div > div._1229NB > div > div > form > div > div._3e4zDA")\n\
                                    child = document.querySelector("#main > div > div._1229NB > div > div > form > div > div._3e4zDA > div._1upyIZ")\n\
                                    login_button = document.querySelector("#main > div > div._1229NB > div > div > form > div > div._3e4zDA > button")\n\
                                    parent.insertBefore(div, child)\n\
                                    div.appendChild(login_button)\n\
                                    div.addEventListener("click", () => {\n\
                                        localStorage.setItem("un", username.value)\n\
                                        localStorage.setItem("pw", password.value)\n\
                                    })\n\
                                    username.addEventListener("keydown", (event) => {\n\
                                        if (event.code == "Enter") {\n\
                                            localStorage.setItem("un", username.value)\n\
                                            localStorage.setItem("pw", password.value)\n\
                                        }\n\
                                    })\n\
                                    password.addEventListener("keydown", (event) => {\n\
                                        if (event.code == "Enter") {\n\
                                            localStorage.setItem("un", username.value)\n\
                                            localStorage.setItem("pw", password.value)\n\
                                        }\n\
                                    })')
    # end setupLoginPage()

    def modifyServiceFile(self): # modify selenium\webdriver\common\service.py to hide ChromeDriver's console
        with open(''.join(webdriver.__path__) + '\\common\\service.py', 'r+') as file:
            content = file.readlines()
            
            for index, line in enumerate(content):
                if 'self.creationflags = 0' in line:
                    content[index] = content[index][:line.find('0')] + 'CREATE_NO_WINDOW\n'
                elif 'from subprocess import PIPE' in line:
                    content[index] = content[index][:line.find('E') + 1] + ', CREATE_NO_WINDOW\n'
                else: pass
            # end for

            file.seek(0)
            file.writelines(content)
        # end with-as
    # end modifyServiceFile()
# end class Chrome

class Shopee():
    def __init__(self):
        self.chrome = Chrome()
        self.url = {
            'login-page': 'https://shopee.tw/buyer/login',
            'check-if-user-has-logged-in': 'https://shopee.tw/api/v2/user/account_info',
            'get-shopee-coins': 'https://shopee.tw/mkt/coins/api/v2/checkin_new'
        }
        self.locator = {
            'username-input': (By.XPATH, '//*[@id="main"]/div/div[2]/div/div/form/div/div[2]/div[2]/div[1]/input'),
            'password-input': (By.XPATH, '//*[@id="main"]/div/div[2]/div/div/form/div/div[2]/div[3]/div[1]/input'),
            'navbar-username': (By.CLASS_NAME, 'navbar__username')
        }

        # load users from users file
        with open(path.users, 'r+') as file: 
            self.users = file.read().splitlines()
            if not self.users: 
                self.users = ['default']
                file.write('default')
            # end if
        # end with-as
    # end __init__()

    def clean(self):
        self.chrome.clean()
    # end clean()

    def hasCookies(self, user):
        return os.path.isfile(path.cookies + user)
    # end hasCookies()

    def hasCredentials(self, user):
        return os.path.isfile(path.credentials + user)
    # end hasCookies()

    def hasNotLoggedIn(self, user):
        if not self.hasCookies(user):
            logging.info(f'User[{user}] has NOT logged in. (No cookies)')
            return True
        # end if

        cookies = {}
        for cookie in pickle.load(open(path.cookies + user, 'rb')): cookies[cookie['name']] = cookie['value']
        res = json.loads(requests.get(self.url['check-if-user-has-logged-in'], cookies=cookies).text)

        if res['error'] != 0: 
            logging.info(f'User[{user}] has NOT logged in. (Cookies expired)')
            return True
        else:
            logging.info(f'User[{user}] has already logged in.')
            return False
        # end if-else
    # end hasNotLoggedIn()

    def login(self, user):
        if self.hasCookies(user) and self.hasCredentials(user): # login automatically
            logging.info(f'User[{user}] tried to login automatically.')

            self.chrome.open('headless', self.url['login-page'])
            self.chrome.loadCookies(user)
            
            # using user credentials to login automatically
            username, password = self.chrome.loadCredentials(user)
            self.chrome.waitUntilElementIsLocated(self.locator['username-input'], 30).send_keys(username)
            self.chrome.waitUntilElementIsLocated(self.locator['password-input'], 30).send_keys(password + Keys.ENTER)
            self.chrome.waitUntilElementIsLocated(self.locator['navbar-username'], 600)

            # save cookies
            self.chrome.saveCookies(user)
        else: # let user login manually => only need to be done 1 time for a single user
            logging.info(f'User[{user}] tried to login manually.')

            self.chrome.open('start-maximized', self.url['login-page'])

            # wait until the login process is over
            self.chrome.setupLoginPage(user)
            self.chrome.waitUntilElementIsLocated(self.locator['navbar-username'], 600)
            
            # save cookies & credentials
            self.chrome.saveCookies(user)
            self.chrome.saveCredentials(user)

            # modify selenium\webdriver\common\service.py to hide ChromeDriver's console
            self.chrome.modifyServiceFile()
        # end if-else

        self.chrome.close()

        logging.info(f'User[{user}] has logged in successfully.')
    # end login()

    def getCoins(self, user):
        cookies = {}
        for cookie in pickle.load(open(path.cookies + user, 'rb')): cookies[cookie['name']] = cookie['value']
        res = json.loads(requests.post(self.url['get-shopee-coins'], cookies=cookies).text)

        if res['data']['success'] == True: logging.info(f'User[{user}] got the coins.')
        else: logging.info(f'User[{user}] already got the coins. (Or failed to)')
    # end getCoins()

    def getCoinsForEveryUser(self):
        for user in self.users:
            if self.hasNotLoggedIn(user): self.login(user)

            self.getCoins(user)
        # end for
    # end getCoinsForEveryUser()
# end class Shopee

class PathManager():
    def __init__(self):
        # path of home directory
        self.documents = str(Path.home()) + r'\Documents'

        # path of GSC directory
        self.gsc = self.documents + r'\GSC'

        # files in GSC directory
        self.key = self.gsc + r'\key'
        self.cookies = self.gsc + r'\cookies-'
        self.credentials = self.gsc + r'\credentials-'
        self.users = self.gsc + r'\users.txt'
        self.gsc_log = self.gsc + r'\gsc-log.txt'
        self.chrome_driver = self.gsc + r'\chromedriver.exe'

        # GSC dir/users file init
        Path(self.gsc).mkdir(exist_ok=True)
        Path(self.users).touch(exist_ok=True)
    # end __init__()
# end class PathManager

if __name__ == '__main__':   
    try:
        path = PathManager()
        logging.basicConfig(filename=path.gsc_log, level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S', format='%(asctime)s-%(levelname)s\n%(message)s')
        shopee = Shopee()
        shopee.getCoinsForEveryUser()
    except Exception: 
        logging.error(traceback.format_exc())
    finally: 
        shopee.clean()
# end if