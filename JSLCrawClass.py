#   2024-01-28  用class实现获取集思录数据
#   2024-01-30  用coockie登录，代替selenium实现


from datetime import date
from chinese_calendar import is_workday
import numpy as np
import pandas as pd

import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import binascii
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from chinese_calendar import is_workday
import logging
from constants import JSL_DATA_FILE,DATA_LOG_FILE

pd.set_option('display.max_columns', None)

AES_KEY = '397151C04723421F'
USER_NAME = 'ilvnet' # 账户名
PASSWORD = 'bull4ever' # 密码

# 定义常量
headers = {
    'authority': 'www.jisilu.cn',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://www.jisilu.cn',
    'pragma': 'no-cache',
    'referer': 'https://www.jisilu.cn/account/login/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82',
    'x-requested-with': 'XMLHttpRequest',
}

def get_encryt_string(text):
    data = text
    key = AES_KEY
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    encrypted_text = cipher.encrypt(pad(data.encode(), AES.block_size))
    return binascii.hexlify(encrypted_text).decode()

# 获取cookie函数
def get_jsl_cookies(username, password):
    data = {
        'return_url': 'https://www.jisilu.cn/',
        'user_name': get_encryt_string(username),
        'password': get_encryt_string(password),
        'auto_login': '0',
        'aes': '1',
    }
    
    response = requests.post('https://www.jisilu.cn/webapi/account/login_process/', headers=headers, data=data)
    
    return response.cookies

 
def convert_ttm_to_years(ttm):
    if '天' in ttm:
        days = int(ttm.split('天')[0])
        years = days / 365
    elif '年' in ttm:
        years = float(ttm.split('年')[0])
    else:
        years = 0
    return years

#用API爬取
class JSLCrawAPI():

    def __init__(self):
        
        self.cookies = get_jsl_cookies(USER_NAME, PASSWORD) # 根据用户名密码获取集思录cookie

    def getCBData(self):                                                             #集思录获取可转债信息

        
        response = requests.get('https://www.jisilu.cn/webapi/cb/list/', cookies=self.cookies, headers=headers) # 获取集思录表格数据
        
        #如果不成功重新请求
        while response.status_code != 200:      
            time.sleep(5)                    
            response = requests.get('https://www.jisilu.cn/webapi/cb/list/', cookies=self.cookies, headers=headers) # 获取集思录表格数据
        
        #格式化为dataframe
        cbdf = pd.DataFrame(response.json().get('data')) 


        dfCB = pd.DataFrame(data=None,columns=['转债代码','转债名称','现价','涨跌幅','正股代码','正股名称','正股涨跌','转债年化波动率','正股PB','正股流通市值','溢价率','下修状态','纯债价值','评级','正股波动率',
                                            '强赎状态','基金持仓','剩余年限','剩余规模','换手率','税前YTM'])

        dfCB['转债代码'] = cbdf['bond_id']
        dfCB['现价'] = cbdf['price']
        dfCB['涨跌幅'] = cbdf['increase_rt']
        dfCB['正股涨跌'] = cbdf['sincrease_rt']
        dfCB['转债年化波动率'] = cbdf['volatility_rate']
        dfCB['溢价率'] = cbdf['premium_rt']
        dfCB['换手率'] = cbdf['turnover_rt']
        dfCB['税前YTM'] = cbdf['ytm_rt']
     
        return dfCB


#用selenium爬取全量数据
class JSLCrawAll():

    def __init__(self):
        
        self.account = 'ilvnet'
        self.password = 'mic1heal'
        self.url = f'https://www.jisilu.cn/web/data/cb/list'

    def getCBData(self):                                                                #集思录获取可转债信息

        opt = webdriver.FirefoxOptions()
        opt.add_argument("-headless")

        browser = webdriver.Firefox(options=opt)
        browser.get(self.url)#打开网址
        browser.maximize_window()#窗口最大化
        browser.implicitly_wait(5)
        time.sleep(5)#等待

        button = browser.find_element(By.XPATH,'//button[@type="button"][1]')       #进入登录页面
        browser.execute_script("arguments[0].click();", button)
        time.sleep(3)#等待

        button = browser.find_element(By.XPATH,'//input[@name="user_name"]')        #输入用户名
        browser.execute_script("arguments[0].click();", button)
        button.send_keys(self.account)#输入信息


        button = browser.find_element(By.XPATH,'//input[@name="password"]')         #输入密码
        browser.execute_script("arguments[0].click();", button)
        button.send_keys(self.password)#输入信息
        time.sleep(0.5)

        button = browser.find_element(By.XPATH,'//span[@class="agree_text"]')       #勾选同意
        browser.execute_script("arguments[0].click();", button)


        button = browser.find_element(By.XPATH,'//a[@class="btn btn-jisilu"]')     #点击登录
        browser.execute_script("arguments[0].click();", button)

        #browser.implicitly_wait(30)                                                  #等待页面加载
        sleep(15)

        html = browser.page_source

        soup = BeautifulSoup(html, 'html.parser')                                   #获取页面中所有表格
        tables = soup.find_all('table')
        table = tables[3]                                                           #table[3]为转债数据表格,基于集思录当前格式，未来可能变化

        data = []                                                                   #转债数据装载进入data List
        for row in table.find_all('tr'):
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            data.append(row_data)

        data = list(filter(None, data))                                             # 去除空值， 集思录原因

        dfCB = pd.DataFrame(data=None,columns=['转债代码','转债名称','现价','涨跌幅','正股代码','正股名称','正股涨跌','转债年化波动率','正股PB','正股流通市值','溢价率','下修状态','纯债价值','评级','正股波动率',
                                            '强赎状态','基金持仓','剩余年限','剩余规模','换手率','税前YTM'])

        

        i = 0

        for d in data:

            dfCB.loc[i, '转债代码'] = d[2]
            dfCB.loc[i, '转债名称'] = d[3]
            dfCB.loc[i, '现价'] = d[4]
            dfCB.loc[i, '涨跌幅'] = d[5]
            dfCB.loc[i, '正股代码'] = d[10]
            dfCB.loc[i, '正股名称'] = d[11]                     #2023-12-07 加入正股名称用于判断ST
            dfCB.loc[i, '正股涨跌'] = d[13]
            dfCB.loc[i, '转债年化波动率'] = d[18]
            dfCB.loc[i, '正股PB'] = d[22]
            dfCB.loc[i, '正股流通市值'] = d[26]
            dfCB.loc[i, '溢价率'] = d[35]
            dfCB.loc[i, '下修状态'] = d[38]
            dfCB.loc[i, '纯债价值'] = d[40]
            dfCB.loc[i, '评级'] = d[41]
            dfCB.loc[i, '正股波动率'] = d[43]
            dfCB.loc[i, '强赎状态'] = d[46]
            dfCB.loc[i, '基金持仓'] = d[50]
            dfCB.loc[i, '剩余年限'] = d[52]
            dfCB.loc[i, '剩余规模'] = d[53]
            dfCB.loc[i, '换手率'] = d[56]
            dfCB.loc[i, '税前YTM'] = d[58]
            dfCB.loc[i, '剩余市值'] = float(d[4])*float(d[53])/100
            
        
            i += 1

        dfCB.replace('-',np.nan,inplace = True)                 # 空替换为NaN
        dfCB.replace('停牌',np.nan,inplace = True)               # 空替换为NaN



        dfCB['剩余年限'] = dfCB['剩余年限'].apply(lambda x: convert_ttm_to_years(x) if isinstance(x, str) else x)           # 2023-11-27 集思录格式变化
        
        return dfCB