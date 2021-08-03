![Alt text](./images/woo_import.jpg?raw=true "Woo commerce import catalog")
## Table of Contents
1. [General Info](#general-info)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Run the import](#run-the-import)
### General Info
***
This script allow to import a woo commerce catalog into GoodBarber shop application. <br />
It is connected with both API.
## Prerequisites
***
A list of prerequisites:
* [Activate Woo commerce API](https://docs.woocommerce.com/document/woocommerce-rest-api/): In order to communicate with the woo commerce api, click on the documentation link that help to configure it. It will generate your api keys access that is required in the configuration files 
* [Activate GoodBarber API](https://commerce.goodbarber.dev/publicapi/v2/documentation/): The GoodBarber api have to be enable also. Follow the documentation in order to generate api keys
* [Python 3](https://www.python.org/downloads/): Version > 3.5
## Installation
***
A little intro about the installation. 
```
$ git clone https://github.com/goodbarber/shop_custom_dev_examples.git
$ cd shop_custom_dev_examples/woo_commerce_import
$ python3 -m venv [name_virtual_env]
$ source ./[name_virtual_env]/bin/activate
$ pip install -r requirements.txt
```
## Configuration
***
The configuration file is in configuration folder (/configuration/config.py)<br>
It contains the woo commerce credentials for the API, and the goodbarber credentials also.
You need to put your credentials in this file if you want to import your woo commerce catalog.
## Run the import
***
Once everything is install and configure, you can run your woo commerce catalog import:
```
$ python3 main.py
```
The command contain options. You can check it with the help option:
```
$ python3 main.py --help
```