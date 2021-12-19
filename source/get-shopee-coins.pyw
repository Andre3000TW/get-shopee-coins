import os
import time
import pickle
import traceback
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
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
    # end __init__()

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

    def waitUntilElementIsClickable(self, locator, timeout):
        return WebDriverWait(self.driver, timeout).until(expected_conditions.element_to_be_clickable(locator))
    # end waitUntilElementIsClickable()

    def loadCookies(self, user):
        for cookie in pickle.load(open(path.cookies + user, 'rb')): self.driver.add_cookie(cookie)
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
        self.xpath = {
            'username_input': '//*[@id="main"]/div/div[2]/div/div/form/div/div[2]/div[2]/div[1]/input',
            'password_input': '//*[@id="main"]/div/div[2]/div/div/form/div/div[2]/div[3]/div[1]/input',
            'login_button': '//*[@id="main"]/div/div[2]/div/div/form/div/div[2]/button',
            'navbar_username': '//*[@id="main"]/div/div[2]/div[1]/div[1]/div/ul/li[3]/div/div/div/div[2]',
            'gsc_button': '//*[@id="main"]/div/div[3]/div/main/section[1]/div[1]/div/section/div/button'
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
        if not self.hasCookies(user): return True

        try:
            is_timeout = False
            self.chrome.open('headless', 'https://shopee.tw')
            self.chrome.loadCookies(user)
            self.chrome.waitUntilElementIsLocated((By.XPATH, self.xpath['navbar_username']), 3)
        except TimeoutException:
            is_timeout = True
        finally:
            self.chrome.close()
            return is_timeout
    # end hasNotLoggedIn()

    def login(self, user):
        if self.hasCookies(user) and self.hasCredentials(user):
            self.chrome.open('headless', 'https://shopee.tw/buyer/login')
            self.chrome.loadCookies(user)

            # using user credentials to login automatically
            username, password = self.chrome.loadCredentials(user)
            self.chrome.waitUntilElementIsLocated((By.XPATH, self.xpath['username_input']), 30).send_keys(username)
            self.chrome.waitUntilElementIsLocated((By.XPATH, self.xpath['password_input']), 30).send_keys(password)
            self.chrome.waitUntilElementIsClickable((By.XPATH, self.xpath['login_button']), 30).click()
            self.chrome.waitUntilElementIsLocated((By.XPATH, self.xpath['navbar_username']), 600)

            # save cookies
            self.chrome.saveCookies(user)
        else:
            self.chrome.open('start-maximized', 'https://shopee.tw/buyer/login')

            # wait until login successfully
            self.chrome.setupLoginPage(user)
            self.chrome.waitUntilElementIsLocated((By.XPATH, self.xpath['navbar_username']), 600)
            
            # save cookies & credentials
            self.chrome.saveCookies(user)
            self.chrome.saveCredentials(user)

            # modify selenium\webdriver\common\service.py to hide ChromeDriver's console
            self.chrome.modifyServiceFile()
        # end if-else

        self.chrome.close()
    # end login()

    def getCoins(self, user):
        self.chrome.open('headless', 'https://shopee.tw/shopee-coins')
        self.chrome.loadCookies(user)
        
        # get coins
        time.sleep(3) # to avoid page redirect
        self.chrome.waitUntilElementIsClickable((By.XPATH, self.xpath['gsc_button']), 30).click()

        self.chrome.close()
    # end getCoins()

    def getCoinsForEveryUser(self):
        for user in self.users:
            # login if user has NOT logged in yet
            if self.hasNotLoggedIn(user): self.login(user)

            # get coins
            self.getCoins(user)
        # end for
    # end getCoinsForEveryUser()
# end class Shopee

class PathManager():
    def __init__(self):
        # path of home directory
        self.home = str(Path.home())

        # file in home directory
        self.chrome_driver = self.home + r'\chromedriver.exe'

        # path of GSC directory
        self.gsc = self.home + r'\GSC'

        # files in GSC directory
        self.key = self.gsc + r'\key'
        self.cookies = self.gsc + r'\cookies-'
        self.credentials = self.gsc + r'\credentials-'
        self.users = self.gsc + r'\users.txt'
        self.error_log = self.gsc + r'\error-log.txt'

        # GSC dir/users file init
        Path(self.gsc).mkdir(exist_ok=True)
        Path(self.users).touch(exist_ok=True)
    # end __init__()
# end class PathManager

try:
    path = PathManager()
    shopee = Shopee()
    shopee.getCoinsForEveryUser()
except Exception as e:
    with open(path.error_log, 'a') as log:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log.write(f'{current_time}\n{traceback.format_exc()}')
    # end with-as
finally:
    shopee.clean()