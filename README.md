
# Distributed Typosquatting Detector(Team 4 Project 4)

DTD is made up of three parts.

### Web Server 
Presents a webpage to users allowing them to submit new URLs to DTD and to see the results of previously submitted URLs.
Takes in a single argument a json file check out example file for format

### Typo Generator
Generates possible typo URLs from a source URL based on Section 3.1 of [this](https://www.usenix.org/legacy/event/sruti06/tech/full_papers/wang/wang.pdf) paper.

### Url Verifier
Takes the list of generated typo URLs and queries each one to determine if they are a valid website. Saves a screenshot of the returned website to server to users at a later date.
Takes in a single argument a json file check out example file for format

### local_test_server
A flask server that uses multithreading as apposed to a master/slave architecture. Helpful for testing functionality without setting up a mysql server

## Getting Started
The three main parts of the application(web server, typo generator, url verifier) are meant to be run concurrently a single database can support as many of these applications as required. They will run in parallel until stopped.


### Prerequisites
```
Python Version: 3.7.7-buster (https://www.python.org/downloads/)
Flask (pip install Flask)
mysql-connector-python 8.0.18 (pip install mysql-connector-python)
MySQl Community Edition 8.0.18
Requests(pip install requests)
Selenium(pip install selenium)
```

## Original Authors

* **[Austin Joseph](https://github.com/austinobejo)**
* **[Gao XiangShuai](https://github.com/GAO23)**
* **[Timothy Yuen](https://github.com/tyuen11)**
* **[Yehonathan Litman](https://github.com/yehonathanlitman)**
