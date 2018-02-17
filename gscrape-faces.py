#!/usr/bin/env python3

#################################################################
#
# gscrape-faces
#
# Load a list of first names and perform a an advanced Google search
# for faces using the name as a search query. Results should be
# nearly random selections of faces
#
##################################################################


from selenium import webdriver
import os
import json
import requests
import sys
from time import sleep
from uuid import uuid4
from multiprocessing import Pool
import pdb
import tqdm
import logging

logging.basicConfig(filename='Logs/gscrape.log',level=logging.INFO)


# adding path to geckodriver to the OS environment variable
os.environ["PATH"] += os.pathsep + os.getcwd()

# Load names
with open('names','r') as infile:
    names = infile.read()
names = names.split('\n')
names = names[:-1]

def load_and_scroll(name):
    search_quantity = 1000
    print('Searching for: {}'.format(name))
    searchtext = name
    num_requested = search_quantity
    number_of_scrolls = int(num_requested / 400 + 1 )
    # number_of_scrolls * 400 images will be opened in the browser

    url = 'https://www.google.com/search?q={0}&as_st=y&hl=en&tbs=itp:face&tbm=isch&tbas=0&source=lnt&sa=X&ved=0ahUKEwiLxNO37_jYAhXBwFMKHZ5kDwoQpwUIHg&biw=1855&bih=982&dpr=1'.format(searchtext)
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(2)
    for i in range(number_of_scrolls):
        for n in range(10):
                # multiple scrolls needed to show all 400 images
                driver.execute_script("window.scrollBy(0, 1000000)")
                sleep(0.5)
        # to load next 400 images
        sleep(0.5)
        try:
            driver.find_element_by_xpath("//input[@value='Show more results']").click()
        except Exception as e:
            logging.info("Scrolling exception: []".format(name))
            break
    return driver

def find_images(name,driver):
    data = []
    img_count = 0
    imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    total_images = len(imges)
    for img in imges:
        img_count += 1
        img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
        img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
        ### Just write out to JSON for now ###
        data.append((img_url,img_type))
    driver.quit()
    return data

def download_image(rowdata):
    url,extension = rowdata
    download_path = "Source Data/Source Images/Google/"
    extensions = ["jpg", "jpeg", "png", "gif"]
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    try:
        if extension not in extensions:
            extension = "jpg"
        req = requests.get(url, headers=headers)
        filename = uuid4().hex+extension
        with open(os.path.join(download_path,filename), 'wb') as f:
            f.write(req.content)
    except Exception as e:
        logging.info("Download failed:")
        logging.info(e)
    finally:
        pass
    return None

if __name__ == "__main__":
# 
# I think I eventually just used curl and xargs to do this
#

##    to_download = []
##    print('Searching for names . . .')
##    for name in names:
##        driver = load_and_scroll(name)
##        data = find_images(name,driver)
##        to_download += data
##    print('Writing search results to file . . .')
##    # just in case downloading throws an error
##    with open('gscrape_urls','w') as outfile:
##        json.dump(to_download,outfile)
##    pdb.set_trace()
    with open('gscrape_urls','r') as infile:
        to_download = json.load(infile)
    print('Downloading . . .')
    pool = Pool(processes=4)
    for n in tqdm.tqdm(pool.imap_unordered(download_image,to_download),total=len(to_download)):
        pass
##    poolmap(download_image,data)
    
