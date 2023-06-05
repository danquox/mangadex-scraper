from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import json

options = Options()

def get_series(url:str): 
    # series object
    series = {
        'title': None,
        'rating': None,
        'authors': None,
        'status': None,
        'genres': [],
        'description': None,
        'recent': {
            'volume': None,
            'chapter': None,
            'url': None
        }
    }
    # driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url);
    # page default loaded
    try:
        header_element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div')))
    except TimeoutException:
        return {"status": 400, "message": "Could not load page: Timeout", "exception": "Timeout"}
    try: 
        # title & authors
        title_element = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[4]')
        series["title"] = title_element.find_element(By.TAG_NAME, "p").text
        series["authors"] = title_element.find_elements(By.TAG_NAME, "div")[-1].text
        # rating
        rating_element = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[6]/div/span[1]')
        series["rating"] = rating_element.text
        # status
        status_element = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[7]/div/span')
        series["status"] = status_element.find_element(By.XPATH, "span").get_attribute("innerHTML")
        # genres
        genres_element = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[8]/div/div[1]/div/div[2]/div[3]/div[2]')
        genres_element_children = genres_element.find_elements(By.TAG_NAME, "a")
        for genre in genres_element_children: 
            series["genres"].append(genre.find_element(By.TAG_NAME, "span").get_attribute("innerHTML"))
        # description
        description_element = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[8]/div/div[1]/div/div[1]/div/p[1]')
        series["description"] = description_element.get_attribute("innerHTML")
        # !change languages
        md = {"metadata":{"modified":1685890033333},"readingHistory":{"_readingHistory":[[]]},"userPreferences":{"filteredLanguages":["en"],"originLanguages":[],"paginationCount":32,"listMultiplier":3,"showSafe":True,"showErotic":True,"showSuggestive":True,"showHentai":True,"theme":"system","mdahPort443":False,"dataSaver":False,"groupBlacklist":[],"userBlacklist":[],"locale":"en","interfaceLocale":"en"}}
        local_metadata = driver.execute_script(f'window.localStorage.setItem("md",JSON.stringify({json.dumps(md)}));')
        driver.refresh()
        # !wait reload finish
        try: 
            pageHeaderElement = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div')))
            print('found')
        except TimeoutException: 
            print("loading took to much time:exit")
            exit()
        # recent chapter
        chapters_container = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div[1]/div[2]/div[2]/div/div[9]/div[2]/div/div[2]')
        recent_chapters_container = chapters_container.find_element(By.TAG_NAME, 'div')
        ## volume 
        series["recent"]["volume"] = recent_chapters_container.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'div').get_attribute('innerHTML')
        ## chapter + url
        latest_chapter_element = recent_chapters_container.find_elements(By.XPATH, './*')[1].find_element(By.TAG_NAME, 'div')
        latest_chapter_link = latest_chapter_element.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'a')
        series["recent"]["chapter"] = latest_chapter_link.get_attribute('title')
        series["recent"]["url"] = latest_chapter_link.get_attribute('href')
        return {
            "status": 200,
            "message": series,
        }
    except Exception as e: 
        return {"status": 400, "message": "Something went wrong", "exception": str(e)}
