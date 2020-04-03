#!/usr/bin/python3

import time
import datetime
import json
import sys
import mysql.connector
import re

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

#TODO input a single url in the form of a string. Output a list of valid urls. The output may or may not include the starting url. The output url list should be generated using the paper thats linked in the assignment document 
def generateURLs(start_url):
    print("Processed: " + str(start_url))
    adjacentKeys = {
        'q': ['w'],
        'w': ['q','e'],
        'e': ['w','r'],
        'r': ['e', 't'],
        't': ['r','y'],
        'y': ['u','t'],
        'u': ['y','i'],
        'i': ['u','o'],
        'o': ['i','p'],
        'p': ['o'],
        'a': ['s'],
        's': ['a','d'],
        'd': ['f','s'],
        'f': ['g','d'],
        'g': ['h','f'],
        'h': ['j','g'],
        'j': ['k','h'],
        'k': ['l','j'],
        'l': ['k'],
        'z': ['x'],
        'x': ['c','z'],
        'c': ['v','x'],
        'v': ['b','c'],
        'b': ['n','v'],
        'n': ['m','b'],
        'm': ['n']
    }
    output = []
    httpsRemover = re.compile(r"https?://")
    wwwRemover = re.compile(r"^www.")
    url = httpsRemover.sub('', start_url).strip().strip('/')
    url = wwwRemover.sub('', url)

    # Missing-dot typos:
    if "www." in start_url:
        output.append(start_url.replace('.', '', 1))

    # Character-omission typos:
    startIndex = start_url.find(url)  # Get position where the two string are the same
    i = startIndex
    while start_url[i] != '.':
        new_url = start_url[:startIndex] + start_url[startIndex:i] + start_url[i+1:]
        output.append(new_url)
        i +=1

    # Character-omission typos:
    i = startIndex
    while start_url[i+1] != '.':
        new_url = start_url[:startIndex] + start_url[startIndex:i] + start_url[i+1] + start_url[i] + start_url[i+2:]
        output.append(new_url)
        i +=1

    # Character-replacement typos:
    i = startIndex
    while start_url[i] != '.':
        value = adjacentKeys.get(start_url[i])
        for letter in value:
            new_url = start_url[:startIndex] + start_url[startIndex:i] + letter + start_url[i+1:]
            output.append(new_url)
        i +=1

    # Character-insertion typos:
    i = startIndex
    while start_url[i] != '.':
        value = adjacentKeys.get(start_url[i])
        new_url = start_url[:startIndex] + start_url[startIndex:i] + start_url[i] + start_url[i:]
        output.append(new_url)
        for letter in value:
            new_url = start_url[:startIndex] + start_url[startIndex:i] + letter + start_url[i:]
            output.append(new_url)
        i +=1

    return output

def loop():
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT original_url FROM submittedUrls WHERE (processing_finish IS NULL OR TIMESTAMPDIFF(DAY, processing_finish, %s) > 1) AND (processing_start IS NULL OR TIMESTAMPDIFF(SECOND, processing_start, %s) > 2) ORDER BY date_added ASC LIMIT %s", (datetime.datetime.utcnow(),datetime.datetime.utcnow(), configFile["max_allowed_tasks_per_update"]))
    subCursor = cnx.cursor(buffered=True)
    newUrls = {}
    for x in cursor:
        newUrls[x[0]] = []
        subCursor.execute("UPDATE submittedUrls SET processing_start = %s WHERE original_url = %s", (datetime.datetime.utcnow(), x[0]))
        newUrls[x[0]].extend(generateURLs(x[0]))
        subCursor.execute("UPDATE submittedUrls SET processing_finish = %s WHERE original_url = %s", (datetime.datetime.utcnow(), x[0]))
    
    for originalUrl, generatedUrlList in newUrls.items():
        for generatedUrl in generatedUrlList:
            cursor.execute("SELECT generated_url FROM generatedUrls WHERE generated_url = %s", (generatedUrl,))
            urlExists = False
            for x in cursor:
                urlExists = True
            if urlExists:                
                subCursor.execute("UPDATE generatedUrls SET date_generated = %s WHERE generated_url =  %s", (datetime.datetime.utcnow(), generatedUrl))
            else:
                cursor.execute("INSERT INTO generatedUrls (generated_url, original_url, date_generated) VALUES(%s, %s, %s)", (generatedUrl, originalUrl, datetime.datetime.utcnow()))
          
    subCursor.close()
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

