#   2023/7/6
#   从集思路搜集当日转债数据存入文件
#   2023/9/7    加入剩余市值
#   2023-12-07 加入正股名称用于判断ST

from selenium import webdriver
from selenium.webdriver.common.by import By

import time
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from chinese_calendar import is_workday
import numpy as np
import logging
from constants import JSL_DATA_FILE,DATA_LOG_FILE
#import sys

#sys.stdout = open('log.txt', 'w')

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=DATA_LOG_FILE, level=logging.INFO, format=LOG_FORMAT)

logging.warning('JSLCrow start-->'+str(date.today()))

#print('JSLCrow start-->'+str(date.today()))

account = 'ilvnet'
password = 'bull4ever'
url = f'https://www.jisilu.cn/web/data/cb/list'

dt = date.today()
file = JSL_DATA_FILE+str(dt)+'.xlsx'

def is_trade_day(ddate):
    if is_workday(ddate):
        if ddate.isoweekday() < 6:
            return True
    return False
 
def convert_ttm_to_years(ttm):
    if '天' in ttm:
        days = int(ttm.split('天')[0])
        years = days / 365
    elif '年' in ttm:
        years = float(ttm.split('年')[0])
    else:
        years = 0
    return years

def getJSLCBData():                                                             #集思录获取可转债信息

    opt = webdriver.FirefoxOptions()
    opt.add_argument("-headless")

    browser = webdriver.Firefox(options=opt)
    browser.get(url)#打开网址
    browser.maximize_window()#窗口最大化
    browser.implicitly_wait(5)
    time.sleep(5)#等待

    button = browser.find_element(By.XPATH,'//button[@type="button"][1]')       #进入登录页面
    browser.execute_script("arguments[0].click();", button)
    time.sleep(3)#等待

    button = browser.find_element(By.XPATH,'//input[@name="user_name"]')        #输入用户名
    browser.execute_script("arguments[0].click();", button)
    button.send_keys(account)#输入信息


    button = browser.find_element(By.XPATH,'//input[@name="password"]')         #输入密码
    browser.execute_script("arguments[0].click();", button)
    button.send_keys(password)#输入信息
    time.sleep(0.5)

    button = browser.find_element(By.XPATH,'//span[@class="agree_text"]')       #勾选同意
    browser.execute_script("arguments[0].click();", button)


    button = browser.find_element(By.XPATH,'//a[@class="btn btn-jisilu"]')     #点击登录
    browser.execute_script("arguments[0].click();", button)

    #browser.implicitly_wait(30)                                                  #等待页面加载
    sleep(15)

    html = browser.page_source

    browser.quit()                                              

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



if __name__ == '__main__':
    


    dfCB = getJSLCBData()

    dfCB.to_excel(file)
