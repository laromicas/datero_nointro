from pathlib import Path
import os
import time
import random

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By


WORK_FOLDER = os.getenv('WORK_FOLDER', os.getcwd())
SEED_NAME = os.getenv('SEED_NAME', os.path.basename(os.getcwd()))
TMP_DIR = os.path.join(WORK_FOLDER, os.getenv('TMP_FOLDER', 'tmp'))
TMP_FOLDER = os.path.join(TMP_DIR, SEED_NAME)

def execute_with_retry(method, max_attempts):
    e = None
    for i in range(0, max_attempts):
        try:
            return method()
        except Exception as e:
            print(e)
            time.sleep(1)
    if e is not None:
        raise e


def sleep_time():
    time.sleep(random.random() * 3 + 4)


def is_download_finished() -> bool:
    firefox_temp_file = sorted(Path(TMP_FOLDER).glob('*.part'))
    chrome_temp_file = sorted(Path(TMP_FOLDER).glob('*.crdownload'))
    downloaded_files = sorted(Path(TMP_FOLDER).glob('*.*'))
    return (len(firefox_temp_file) == 0) and \
       (len(chrome_temp_file) == 0) and \
       (len(downloaded_files) >= 1)


def downloads_disabled(driver) -> bool:
    words = ['temporary suspended', 'temporary disabled']
    return any(word in driver.page_source for word in words)

def download_daily():
    options = FirefoxOptions()
    # options.add_argument("--headless")
    options.set_capability("marionette", True)
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", TMP_FOLDER)
    options.set_preference("browser.download.folderList", 2)

    driver = webdriver.Firefox(options=options)

    driver.implicitly_wait(10)
    driver.get("https://www.google.com")

    driver.get("https://datomatic.no-intro.org")

    sleep_time()


    try:

        if downloads_disabled(driver):
            print("Downloads suspended")
            driver.close()
            exit(1)

        # driver.manage().timeouts().implicitlyWait(5, TimeUnit.SECONDS)
        download_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Download')]")
        download_button.click()

        sleep_time()
        daily_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Daily')]")
        daily_link.click()

        sleep_time()
        aftermarket = driver.find_element(By.CSS_SELECTOR, "input[name='include_additional']")
        if not aftermarket.is_selected():
            aftermarket.click()

        sleep_time()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        prepare_button = driver.find_element(By.CSS_SELECTOR, "form[name='daily'] input[type='submit']")



        sleep_time()
        prepare_button.click()

        sleep_time()
        download_button = driver.find_element(By.CSS_SELECTOR, "form[name='opt_form'] input[name='lazy_mode']")
        download_button.click()

        while not is_download_finished():
            print("Waiting for download to finish")
            time.sleep(10)

    except Exception as e:
        print(e)

    driver.close()

if __name__ == '__main__':
    download_daily()