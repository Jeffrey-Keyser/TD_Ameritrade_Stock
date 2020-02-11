    import requests
    import time
    import urllib
    from splinter import Browser
    from selenium import webdriver
    import config as cfg
    import xlsxwriter

def main():

    # store params from cfg file
    account_num = cfg.userInfo['account_num']
    password = cfg.userInfo['password']
    key = cfg.userInfo['client_id']

    setup_browser()
    connect_account()
    create_saved_order()


def export_to_excel():
    # EXCEL STUFF
    # Create file (workbook) and worksheet
    outWorkbook = xlsxwriter.Workbook("out.xlsx")
    outSheet = outWorkbook.add_worksheet()
    names = ["Jef", "Jeff"]
    outSheet.write("A1","Names")

    outWorkbook.close()


    # Extra Stuff
    #browser.visit("https://www.facebook.com")

    #username_box = browser.find_by_id("email")
    #username_box.fill("Jeffrey Keyser")

    # Click
    # submit = browser.find_by_id("").first.click()



def setup_browser():
    # Browser Stuff
    executable_path = {'executable_path':r'C:\Users\Storm\Documents\AutomateStock\chromedriver_win32\chromedriver'}

    # Set default behaviors for browser
    options = webdriver.ChromeOptions()

    # Ensure window is maximized
    options.add_argument("--start-maximized")

    # Ensure notifications are off
    options.add_argument("--disable-notifications")

    # Create new chrome browser object
    browser = Browser('chrome', **executable_path, headless = False, options = options)


    # Define the components of the URL
    method = 'GET'
    url = 'https://auth.tdameritrade.com/auth?'
    client_code = key + '@AMER.OAUTHAP'
    payload = {'response_type':'code', 'redirect_uri': 'http://localhost/test', 'client_id': client_code}

    # Build url
    built_url = requests.Request(method, url, params = payload).prepare()
    built_url = built_url.url

    # Go to our URL
    browser.visit(built_url)


    # Pass through username and password
    payload = {'username':account_num, 'password':password}

    browser.find_by_id("username").fill(payload['username'])
    browser.find_by_id("password").fill(payload['password'])
    browser.find_by_id("accept").first.click()

    time.sleep(3)


    # Accept terms and conditions
    browser.find_by_id("accept").first.click()

    time.sleep(3)


    # Capture url
    new_url = browser.url

    # Parse
    parse_url = urllib.parse.unquote(new_url.split('code=')[1])

    # Close the browser
    browser.quit()


    # Define endpoint
    url = r'https://api.tdameritrade.com/v1/oauth2/token'

    # Define headers
    headers = {'Content-Type':"application/x-www-form-urlencoded"}

    # Define payload
    payload = {'grant_type':'authorization_code',
            'access_type':'offline',
            'code':parse_url,
            'client_id':key,
            'redirect_uri':'http://localhost/test'}

    # Post the data to get the token
    authReply = requests.post(url, headers=headers, data = payload)


    # Convert json string to dict
    decoded_content = authReply.json()


    access_token = decoded_content['access_token']
    headers = {'Authorization': "Bearer {}".format(access_token)}
    headers

    # END BROWSER STUFF


def connect_account():
    # ACCOUNTS ENDPOINT

    endpoint = r"https://api.tdameritrade.com/v1/accounts"

    content = requests.get(url = endpoint, headers = headers)

    data = content.json()
    display(data)
    account_id = data[0]['securitiesAccount']['accountId']

    # END ACCOUNTS ENDPOINT


def create_saved_order():
    # Create Saved Order

    header = {'Authorization': "Bearer {}".format(access_token),
            "Content-Type":"application/json"}

    endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders".format(account_id)

    payload = {
    "orderType": "MARKET",
    "session": "NORMAL",
    "duration": "DAY",
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [
        {
        "instruction": "Buy",
        "quantity": 1,
        "instrument": {
            "symbol": "PINS",
            "assetType": "EQUITY"
        }
        }
    ]
    }

    # Data has been changed to JSON
    content = requests.post(url = endpoint, json = payload, headers = header)

    # Show status code, expecting 200
    content.status_code

    # END CREATE SAVED ORDER

def get_quote():
    # Get Quote
    payload2 = {'apikey':key}
    endpoint2 = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format('GOOG')

    content = requests.get(url = endpoint2, params = payload2)
    new_data = content.json()
    # END GET QUOTE

def get_daily_prices():
    # The daily prices endpoint

    # define endpoint
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format('AAA')

    # define payload
    payload = {'apikey':key,
            'periodType':'day',
            'frequencyType':'minute',
            'frequency':'1',
            'period':'2',
            'endDate':'1556158524000',
            'startDate':'1554535854000',
            'needExtendedHoursData':'true'}

    # make a request
    content = requests.get(url = endpoint, params = payload)

    # convert it a dictionary
    data = content.json()

    # END DAILY PRICES ENDPOINT



