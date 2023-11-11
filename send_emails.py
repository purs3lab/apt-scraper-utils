from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get('https://outlook.live.com/owa/')


input("After you've entered the 2FA code in the browser, press Enter to continue the script once you are on the outlook page...")


EMAIL_TXT_FILE = "/home/machiry/Downloads/email.txt"
EMAILS_TO_SEND_TXT = "/home/machiry/projects/apt-scraper-utils/final_debian_emails.csv"
#EMAILS_TO_SEND_TXT = "/home/machiry/projects/apt-scraper-utils/dummy_emails.csv"
email_content = None

fp = open(EMAIL_TXT_FILE, "r")
email_content = fp.read()
fp.close()

fp = open(EMAILS_TO_SEND_TXT, "r")
all_emails = fp.readlines()
fp.close()
for curr_line in all_emails:
    curr_line = curr_line.strip()
    if curr_line is not None:
        pkg_name = curr_line.split(",")[0]
        dev_name = curr_line.split(",")[1]
        dev_email = curr_line.split(",")[2]
        time.sleep(2)
        driver.switch_to.active_element.send_keys('n')
        time.sleep(1)

        driver.find_element(By.XPATH, "//div[@aria-label='To']").send_keys(dev_email)
        driver.find_element(By.XPATH, "//input[@aria-label='Add a subject']").send_keys('Using SAST Tools in ' + pkg_name)
        curr_email = email_content.replace("<PROJECTNAME>", pkg_name)
        curr_email = curr_email.replace("<NAME>", dev_name)
        driver.find_element(By.XPATH, "//div[@aria-label='Message body, press Alt+F10 to exit']").send_keys(curr_email)

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']"))).click()

        time.sleep(5)

driver.quit()