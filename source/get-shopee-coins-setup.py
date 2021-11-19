import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

try:
    # setup path
    home_path = str(Path.home())
    chrome_executable_path = home_path + r'\chromedriver.exe'
    chrome_profile_path = home_path + r'\AppData\Local\Google\Chrome\User Data\Default'

    # setup headless chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('log-level=3')
    options.add_argument(f'--user-data-dir={chrome_profile_path}')
    service = Service(chrome_executable_path)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 600)
    
    ### start! ###
    driver.get('https://shopee.tw/buyer/login')

    # wait until login successfully
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'navbar__username')))

    # modify selenium\webdriver\common\service.py to hide chromedriver console
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
    
    print('Setup completed successfully')
except TimeoutException:
    print('Timeout.')
except Exception as e:
    print(f'{e.__class__.__name__}: {e.args[0]}')
finally:
    driver.quit()
    os.system('pause')