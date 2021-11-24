import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

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
time.sleep(3) # to avoid page redirect
wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div[3]/div/main/section[1]/div[1]/div/section/div/button'))).click()

# close ChromeDriver
driver.quit()
