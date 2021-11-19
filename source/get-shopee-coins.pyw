from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

try:
    # setup path
    home_path = str(Path.home())
    chrome_executable_path = home_path + r'\chromedriver.exe'
    chrome_profile_path = home_path + r'\AppData\Local\Google\Chrome\User Data\Default'

    # setup headless chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument(f'--user-data-dir={chrome_profile_path}')
    service = Service(chrome_executable_path)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)
    
    ### start! ###
    driver.get('https://shopee.tw/shopee-coins')

    # get shopee coins
    wait.until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[3]/div/main/section[1]/div[1]/div/section/div/button'))).click()
except Exception as e:
    print(f'{e.__class__.__name__}: {e.args[0]}')
finally:
    driver.quit()