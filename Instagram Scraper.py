"""
Created on Tue Nov 30 2021

@author: Xun Yang
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pandas as pd
import random
import time


#Import Raw Data set to Scrape
raw_data = pd.read_csv('raw_data.csv')


#DF Output
df = pd.DataFrame()
df['Name'] = ""
df['Follower'] = ""
df['postdate'] = ""
df['likes'] = ""
df['comment'] = ""
df['caption'] = ""
df['industry'] = ""

#Create Path
PATH = r"C:\Users\65821\Desktop\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get("https://www.instagram.com/")

#Login
time.sleep(5)
username=driver.find_element_by_css_selector("input[name='username']")
password=driver.find_element_by_css_selector("input[name='password']")
username.clear()
password.clear()
username.send_keys("username")
password.send_keys("password")
login = driver.find_element_by_css_selector("button[type='submit']").click()

#click the not now button
time.sleep(10)
notnow = driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()

for i in range(len(raw_data)):
    instagram_user =  str(raw_data['instagram'][i]).replace("@","")
    if instagram_user == "":
        continue
    #searchbox
    time.sleep(5)
    searchbox=driver.find_element_by_css_selector("input[placeholder='Search']")
    searchbox.clear()
    searchbox.send_keys(instagram_user)
    time.sleep(random.randint(5, 7))
    searchbox.send_keys(Keys.ENTER)
    time.sleep(random.randint(5, 7))
    searchbox.send_keys(Keys.ENTER)

    #Scroll down to scrape more Post
    #scrolldown=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    #match=False
    #while(match==False):
    #    last_count = scrolldown
    #    time.sleep(3)
    #    scrolldown = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    #    if last_count==scrolldown:
    #        match=True
    
    #Use Request to get website
    url = str(driver.current_url) + "?hl=en"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    scripts = soup.select('script')
    page_json = ""
    scripts = [script for script in scripts]
    for script in scripts:
        if 'window._sharedData =' in str(script.string):
            d = script
            break
    page_json = d.string.strip().replace('window._sharedData =', '').replace(';', '')
    data = json.loads(page_json)

    #Get Follower
    follower = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']

    time.sleep(random.randint(5, 10))
    posts = []
    links = driver.find_elements_by_tag_name('a')
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
          posts.append(post)

    #get Other information
    j = 0
    for post in posts:
        j += 1
        driver.get(post)
        shortcode = driver.current_url.split("/")[-2]
        time.sleep(random.randint(5, 10))
        if len(driver.find_elements_by_xpath("//script[@type='text/javascript']")) > 0:
            for b in driver.find_elements_by_xpath("//script[@type='text/javascript']"):
                if 'edge_media_preview_like' in b.get_attribute('innerHTML'):
                    text = b.get_attribute('innerHTML')
                    text2 = text.split('taken_at_timestamp')[1]
                    postdate = datetime.utcfromtimestamp(int(text2.split(":")[1].split(",")[0])).strftime('%Y-%m-%d %H:%M:%S')
                    likes = text.split('edge_media_preview_like":{"count":')[1].split(",")[0]
                    affliate = text.split('"is_affiliate":')[1].split(",")[0]
                    partnership = text.split('"is_affiliate":')[1].split(",")[0]
                    comment = text.split('edge_media_to_parent_comment":{"count":')[1].split(",")[0]
                    if '{"edges":[{"node":{"text":"' in text:
                        caption = text.split('{"edges":[{"node":{"text":"')[1].split('"')[0]
                    else:
                        caption = ""
        if j == 6:
            j = 0
            break
        df = df.append(pd.DataFrame({"Name":[instagram_user],
                                    "Follower":[follower],
                                    "postdate":[postdate],
                                    "likes":[likes],
                                    'comment': [comment],
                                    "caption": [caption],
                                    'industry': [raw_data['Topics'][i]],
                                    'affliate': [affliate],
                                    'partnership': [partnership],
                                    }), ignore_index = True)
        break
    print(df)
    #df.to_csv("raw_instagram_data.csv")
