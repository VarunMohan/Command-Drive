from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# sudo pip install selenium
# https://sites.google.com/a/chromium.org/chromedriver/home

DOCUMENT_URL_FORMAT = 'https://docs.google.com/document/d/{0}/edit'
EMAIL_ID = 'gdrivecommandline'
FOLDER_URL_FORMAT = 'https://drive.google.com/drive/folders/{0}'
MAX_WAIT_TIME_SECONDS = 10
PASSWORD = 'temporary1'
ROOT_URL = 'https://drive.google.com/drive/my-drive'

def wait_until_load(driver):
    WebDriverWait(driver, MAX_WAIT_TIME_SECONDS).until(
        expected_conditions.presence_of_element_located((By.XPATH, "//div[@role='listbox' and @data-target='layout']"))
    )

def login(driver):
    driver.get('https://drive.google.com')
    email_box = driver.find_element_by_id('Email')
    email_box.send_keys(EMAIL_ID)
    email_box.submit()
    password_box = WebDriverWait(driver, MAX_WAIT_TIME_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, 'Passwd'))
    )
    password_box.send_keys(PASSWORD)
    password_box.submit()
    wait_until_load(driver)

def browse_to_document(driver, document_id):
    if document_id is None:
        url = ROOT_URL
    else:
        url = DOCUMENT_URL_FORMAT.format(document_id)
    driver.get(url)

def browse_to_folder(driver, folder_id):
    if folder_id is None:
        url = ROOT_URL
    else:
        url = FOLDER_URL_FORMAT.format(folder_id)
    driver.get(url)
    wait_until_load(driver)

def logout(driver):
    driver.get('https://accounts.google.com/Logout?service=wise')
    driver.close()

def main():
    try:
        driver = webdriver.Chrome()
        login(driver)
        folder_id = '0Bza7xsC4hvoAfjFCaXc3TUIyQUY3V01DTkZETTBJR180REtIRXBTSV80Q1RVb1FDNFpIZU0'
        browse_to_folder(driver, folder_id)
        logout(driver)
    except Exception as e:
        print 'Exception:', e
        driver.close()

if __name__ == '__main__':
    main()
