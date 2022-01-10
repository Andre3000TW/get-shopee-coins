# :moneybag:Get Shopee Coins:moneybag:
Get your shopee coins easily and automatically!:money_mouth_face::money_mouth_face::money_mouth_face:

# Usage
### Setup
1. Install selenium and pycryptodome. (Using [requirements.bat](./requirements.bat) or *pip*)
2. Put [chromedriver.exe](https://chromedriver.chromium.org/downloads) under the home path. (e.g., C:\Users\User)
3. Run `source/get-shopee-coins.pyw` and complete login process.

### Get coins! (With 2 options)
&nbsp;&nbsp;&nbsp;&nbsp;Option 1. Run `source/get-shopee-coins.pyw` to get coins. \
&nbsp;&nbsp;&nbsp;&nbsp;Option 2. Use Windows Task Scheduler to run `source/get-shopee-coins.pyw` periodically. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="./media/task-scheduler-1.png" width="500"> \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="./media/task-scheduler-2.png" width="500">
    
### Insert users
1. In home/GSC/users.txt, enter new line and new username.
2. Run `source/get-shopee-coins.pyw` and complete login process.

### Notes
1. ChromeDriver's version should be the same as Chrome's version.
2. You can check the title of login page to know which user you login to.
3. Do NOT refresh or go to previous page during login process. If you did, restart the program.
4. If you changed your password, delete home/GSC/credentials-username and complete login process.

# Disclaimer
**Your login credentials is stored in home/GSC/credentials-username and encrypted using AES.** \
**We use it to re-login after cookies expired. We do NOT steal any info about it or use it for any other purpose.**

# Test Environment
+ Windows 10
+ Python 3.9.0

# Package Requirements
+ selenium==4.1.0
+ requests==2.26.0
+ pycryptodome==3.12.0

# License
This project is under the [MIT License](./LICENSE).
