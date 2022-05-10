import argparse
from metamask_helpers import *
from flask import Flask, jsonify
import argparse
import json
import threading 

driver = None # seleniumm webdriver
metamask_recovery_phrase = "upon coffee volcano purity morning badge observe process crystal paddle festival ripple"
metamask_password = "testAccount"
page = None # source page for current website
apr = {} # the APR data is stored here 
app = Flask(__name__)
state = False

def init():
    """
    initializes the selenium driver and setsup metamask wallet
    """
    global driver,page
    driver = launchSeleniumWebdriver("/usr/bin/chromedriver")
    metamaskSetup(metamask_recovery_phrase, metamask_password)
    _ = driver.get("https://vfat.tools/aurora/auroraswap/")
    driver.find_element_by_xpath('//*[@id="connect_wallet_button"]').click()
    driver.find_element_by_xpath('//*[@id="WEB3_CONNECT_MODAL_ID"]/div/div/div[2]/div[1]/div/div[1]').click()
    connectToWebsite()
    driver.find_element_by_xpath('//*[@id="connect_wallet_button"]').click()
    add_network()
    time.sleep(15) # wait for page to load the logs
    page = driver.page_source
    return 

def get_data(contract):
    """
    checks if the page is loaded if so then exctract the desired chunck of data from the page
    Inputs:
        - contract: the contract address of the token we want APR for
    Returns:
        - (str): html as text
    """
    global driver,page
    if page is None:
        return {"error":"no page"}
    else:
        data = []
        while len(data)<2:
            start = page.find(contract)
            end = start+800
            data = page[start:end].split("<br>")
            time.sleep(1)
        return data[-2]

def extract_info(data:str):
    """
        this function expects a string containing Day, Week and Year along with some value against each.
        Inputs:
            - data(str): a string of data
        Returns:
            - (dict): a dictionary containing the APRs
    """
    print(data)
    c1 = data.find("Day")
    c2 = data.find("Week")
    c3 = data.find("Year")
    print(c1,c2,c3)
    p1 = data[c1:c2].split(" ")[1]
    p2 = data[c2:c3].split(" ")[1]
    p3 = data[c3:].split(" ")[1]
    return {"day":p1,"week":p2,"year":p3}

def updater(config):
    """
    This is a parent function that endlessly will refresh the targetted page after the desired interval and scrape the page.
    Inputs:
        -config(dict): this should contain the following:
            - contract_address
            - refresh_time
     
    """
    global driver,page,apr
    init()
    data = get_data(config["contract_address"])
    apr = extract_info(data)
    global state
    state = True
    while True:
        driver.refresh()
        time.sleep(15)
        data = get_data(config["contract_address"])
        apr = extract_info(data)
        print(apr)
        time.sleep(config["refresh_time"])

@app.route("/apr/year",methods=["GET"])
def get_year():
    """
        returns the yearly APR for the desired contract
    """
    global apr,state
    if state and "year" in apr:
        return jsonify({"year":apr["year"]}),200
    else:
        jsonify({"error":"data not available"}),200

@app.route("/apr/day",methods=["GET"])
def get_day():
    """
        returns the daily APR for the desired contract
    """
    global apr
    if state and "day" in apr:
        return jsonify({"day":apr["day"]}),200
    else:
        return jsonify({"error":"data not available"}),200

@app.route("/apr/week",methods=["GET"])
def get_week():
    """
        returns the weekly APR for the desired contract
    """
    global apr
    if state and "week" in apr:
        return jsonify({"week":apr["week"]}),200
    else:
        return jsonify({"error":"data not available"}),200

@app.route("/",methods=["GET"])
def index():
    """
    returns all apr as dictionary
    """
    if state:
        return jsonify(apr),200
    else:
        return jsonify({"error":"data not available"}),200

def parse_arguments():
    """to Read arguments from command line."""
    parser = argparse.ArgumentParser(
        description='Arguments get parsed via --commands')
    parser.add_argument("-config", metavar='config', type=str,
                        required=True, help='path to config file')
    args = parser.parse_args()

    return args

def main():
    args = parse_arguments()
    with open(args.config, "r") as f:
        config = json.load(f)
    
    threading.Thread(target=updater, args=(config,)).start()
    while not state:
        pass
    app.run(host="0.0.0.0", port=8080)

if __name__=="__main__":
    main()
