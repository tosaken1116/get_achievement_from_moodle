
import csv
import json
import os
import time

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def download_chromedriver():
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
    driver_path = f'./{chrome_ver}/chromedriver.exe'
    if os.path.exists(driver_path):
        print(f"chrom driver is installed: {driver_path}")
    else:
        print(f"install the chrome driver(ver: {chrome_ver})")
        chromedriver_autoinstaller.install(True)
    return driver_path

def scraping_achievement():
    url = "https://virginia.jimu.kyutech.ac.jp/"
    driver = open_url_link(url)
    driver.find_element(By.XPATH, '''//a[contains(@href,"JavaScript:openWin4MenuIcon('/portal/redirect.do?renkeiType=kyoumu', 'kyoumuWindow')")]''').click()
    driver.switch_to.window(driver.window_handles[2])
    time.sleep(1)
    driver.find_element(By.XPATH, '''//a[@onclick="dbLinkClick('/kyoumu/seisekiSearchStudentInit.do?mainMenuCode=008&parentMenuCode=007');"]''').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '''//a[contains(@href,"/kyoumu/seisekiRishuStudentInit.do?refStudentCode")]''').click()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    achievement_details = get_achievement_details(soup)
    output_csv(achievement_details,".")


def open_url_link(url: str):
    driver_path = download_chromedriver()
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(executable_path=f"{driver_path}".replace('.exe','').replace('./',''),options=option)
    driver.get(url)
    driver.find_element(By.XPATH, '//a[@href="JavaScript:openShibbolethWin()"]').click()
    driver.switch_to.window(driver.window_handles[1])
    user_info = get_user_info()
    driver.find_element(By.ID, 'username').send_keys(user_info["user_id"])
    driver.find_element(By.ID, 'password').send_keys(user_info["user_password"])
    driver.find_element(By.NAME, '_eventId_proceed').click()
    time.sleep(3)
    return driver
def replace_tag(_str:str):
    return _str.replace('\n', '').replace('???', '').replace('\t', '').replace(' ', '')

def get_achievement_details(soup):
    return_dicts = []
    achievement_table_elements = soup.find_all('tr',bgcolor="#FFFFCC")
    for achievement_table_element in achievement_table_elements:
        achievement_table_element_details = achievement_table_element.find_all('td')
        if replace_tag(achievement_table_element_details[9].text) != "":
            return_dicts.append(
                {
                    "?????????":replace_tag(achievement_table_element_details[3].text),
                    "????????????":replace_tag(achievement_table_element_details[6].text),
                    "????????????":replace_tag(achievement_table_element_details[7].text),
                    "?????????":replace_tag(achievement_table_element_details[8].text),
                    "??????":replace_tag(achievement_table_element_details[9].text),
                    "??????":replace_tag(achievement_table_element_details[10].text),
                }
            )
    return return_dicts
def output_csv(output_dicts:list,output_path:str):
    header = [
        "?????????",
        "????????????",
        "????????????",
        "?????????",
        "??????",
        "??????"
    ]
    with open(f"{output_path}/achievement.csv", "w", encoding="utf_8_sig") as f:
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        for dict in output_dicts:
            if dict is not None:
                writer.writerow(dict)
def get_user_info():
    try:
        with open("user_info.json","r") as f:
            user_info = json.load(f)
        return user_info
    except:
        user_id = input("ID:")
        user_password = input("Password:")
        with open("user_info.json","w") as f:
            json.dump(
                {
                    "user_id": user_id,
                    "user_password" : user_password
                },
                f,
                indent=2,
                ensure_ascii=False
            )
        return {
            "user_id": user_id,
            "user_password" : user_password
        }
if __name__ == "__main__":
    scraping_achievement()