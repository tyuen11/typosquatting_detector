#!/usr/bin/python3
# -*- coding: utf-8 -*-
import flask
import datetime
import json
import sys
import mysql.connector
from flask import Response
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

app = flask.Flask(__name__, static_url_path='',
                  static_folder=configFile["flask"]["static_folder"])
cnx = None

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/image/<string:url>")
def image(url):
    cursor = cnx.cursor(buffered=True)
    cursor.execute("SELECT generated_image FROM generatedUrls WHERE generated_url=%s LIMIT 1", (url,))
    image = None
    for x in cursor:
        if x[0] != None:
            image = x[0]
    cursor.close()
    if image != None:
        return app.response_class(base64.decodestring(str.encode(image)), mimetype="image/png")
    else:
        return Response("{'error':'image not found'}", status=404, mimetype='application/json')

@app.route("/view", methods=["POST"])
def viewResults():
    givenUrl = flask.request.form["url"]
    responseJson = {}
    responseJson["error"] = 0
    responseJson["inputUrl"] = givenUrl

    query = ("SELECT COUNT(*) FROM submittedUrls WHERE original_url=%s")
    queryData = (givenUrl,)
    cursor = cnx.cursor()
    cursor.execute(query, queryData)

    urlInDatabase = True
    for x in cursor:
        if x[0] <= 0:
            urlInDatabase = False
            break

    if not urlInDatabase:
        responseJson["error"] = 1
        query = ("INSERT INTO submittedUrls (original_url, date_added)  VALUES(%s, %s)")
        queryData = (givenUrl, datetime.datetime.utcnow())
        cursor.execute(query, queryData)
    else:
        query = ("SELECT generated_url, http_response_code, processing_finish, if(generated_image is not null, true, false)image_null FROM generatedUrls WHERE original_url = %s")
        queryData = (givenUrl,)
        cursor.execute(query, queryData)
        responseJson["generatedUrls"] = []
        responseJson["urlQueryResults"] = []
        for x in cursor:
            if x[2] == None:
                responseJson["error"] = 2
            if x[1] != None and x[1] >= 200 and x[1] <300:
                responseJson["generatedUrls"].append(x[0])
                responseJson["urlQueryResults"].append(
                    {
                        "generated_url" : x[0],
                        "http_response_code":x[1],
                        "generated_image" : "/image/" + str(x[0]) if x[3] == 1 else "#"
                    }
                )
    cursor.close()
    cnx.commit()
    return json.dumps(responseJson, sort_keys=True, default=str)



def log(message):
    if configFile["logging"] == "True":
        print(message)

cnx = mysql.connector.connect(**configFile["database"])

if cnx == None:
    print("Could not connect to database, exiting.")
    exit()

if __name__ == "__main__":
    app.run(port=configFile["flask"]["port"], threaded=True)
    log("Server started on port {}".format(configFile["flask"]["port"]))