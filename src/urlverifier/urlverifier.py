#!/usr/bin/python3

import time
import datetime
import json
import sys
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import requests
import base64

config_file = ""

if len(sys.argv) < 2:
    config_file = "config.json"
    print("defaulting to config.json if config file not specified")
else:
    config_file = sys.argv[1]

with open(config_file) as configHandle:
    configFile = json.load(configHandle)
if configFile == None:
    print("Error loading config file aborting")
    exit()

cnx = None

#TODO input a single url in the form of a string. Utilize Selenium query the webpage. The results of the query are saved as an array that should be added to "generated_urls" dict in the format of generated_urls[url]=output array
# The format of hte output array should be [http response code, the binary data of the saved image so that it can saved by the application and served when the user calls for it.]
def checkURL(url, opts):
    print("Querying: "+ url)
    url = "http://www." + url
    driver = webdriver.Chrome(executable_path=configFile["chrome_driver"], options=opts)
    driver.set_page_load_timeout(5)
    driver.maximize_window()
    try:    
        driver.get(url)
    except TimeoutException:
        img = driver.get_screenshot_as_png()
        print("Page Timed Out")
        # print(base64.encodestring(img))
        return [403, base64.encodestring(img)]
   
    img = driver.get_screenshot_as_png()
    driver.close()
    try:
        req = requests.get(url)
        return [req.status_code, base64.encodestring(img)]
    except requests.ConnectionError:
        # print(base64.encodestring(img))
        return [503, base64.encodestring(img)] #503 = service unavailable

def loop():
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT generated_url FROM generatedUrls WHERE (processing_finish IS NULL OR TIMESTAMPDIFF(DAY, processing_finish, %s) > 1) AND (processing_start IS NULL OR TIMESTAMPDIFF(SECOND, processing_start, %s) > 2) ORDER BY date_generated ASC LIMIT %s", (datetime.datetime.utcnow(),datetime.datetime.utcnow(), configFile["max_allowed_tasks_per_update"]))
    subCursor = cnx.cursor(buffered=True)
    newResults = {}
    opts = Options()
    opts.add_argument("--headless")
    for x in cursor:
        newResults[x[0]] = []
        subCursor.execute("UPDATE generatedUrls SET processing_start = %s WHERE generated_url = %s", (datetime.datetime.utcnow(), x[0]))
        newResults[x[0]].extend(checkURL(x[0], opts))
        subCursor.execute("UPDATE generatedUrls SET processing_finish = %s WHERE generated_url = %s", (datetime.datetime.utcnow(), x[0]))
    subCursor.close()
    for generatedUrl, urlResults in newResults.items():
        length = len(urlResults[1])
        if length > configFile["max_image_size"]:
          cursor.execute("UPDATE generatedUrls SET http_response_code = %s WHERE generated_url = %s", (urlResults[0], generatedUrl))
        else:
#          print(urlResults[1])
          cursor.execute("UPDATE generatedUrls SET generated_image = %s, http_response_code = %s WHERE generated_url = %s", (urlResults[1].decode("utf-8"),urlResults[0], generatedUrl))
            
    cursor.close()
    cnx.commit()

def start():
    while True:
        loop()

def log(message):
    if configFile["logging"] == "True":
        print(message)

cnx = mysql.connector.connect(**configFile["database"])
start()
cnx.close()
