#!/usr/bin/env python
# coding: utf-8
#執行時間滿久的，希望大神們提供更好的爬法thx

import time
import numpy as np
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from highcharts import Highstock

class etf_scraper:
    
    def __init__(self, etf, startdate, enddate):
        
        self.etf = etf 
        self.startdate = startdate
        self.enddate = enddate
    
    def getsecID(self, sec = 1):    #爬蟲1，先拿secID，以連結到etf的資料網站
        
        url = 'https://www.morningstar.com/search.html?q={etf}'
        url = url.format(etf = self.etf)
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
        
        result = requests.get(url, headers = headers)
        soup = BeautifulSoup(result.content, 'html.parser')
        global etf_name
        etf_name = self.etf
        #為了讓下面的data function可以收到secID
        global secID
        #有些etf已經下市，若已經下市，morningstar會搜尋不到
        global exist        
        
        soup_dic = json.loads(soup.find_all("div", {"class":"search-list-content"})[0]['data-initialdata'])
        for i in soup_dic['m'][0]['r']:
            if i['OS001'] == self.etf.upper():
                secID = i['SecId']
                exist = True
                break
            else:
                exist = False
        delay = np.random.uniform(min(sec - 1, 0), sec + 1)
        time.sleep(delay)
        
        return None
        
    
    def data(self, data_type = 'nav'):  #爬蟲2，拿到secID後，進到該etf的資料網站爬資料
        
        if data_type == 'nav':
            dataid = '8217'
        elif data_type == 'price':
            dataid = '8225'
        elif data_type == 'volume':
            dataid = '8226'
        else:
            return 'Sorry, data_type should be nav, price or volume' 
        
        try:
            if etf_name == self.etf:
                pass
            else:
                self.getsecID(sec = 1)
        except:
            self.getsecID(sec = 1)
            
        if exist:
            pass
        else:
            return self.etf + ' ceased trading'
          
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5'}
        
        data_url = 'http://mschart.morningstar.com/chartweb/defaultChart?type=getcc&secids={secID};FE&dataid={dataid}&startdate={startdate}&enddate={enddate}&currency=&format=1&callback'
        data_url = data_url.format(secID = secID, dataid = dataid, startdate = self.startdate, enddate = self.enddate)
        data_soup = BeautifulSoup(requests.get(data_url, headers = headers).content, "html.parser")
        regex = r"\{\S+\}"
        matches = re.finditer(regex, str(data_soup), re.MULTILINE)
        global matchNum, match
        for matchNum, match in enumerate(matches):
            pass
        js_data = "{match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group())
        raw_data = json.loads(js_data)
        raw_data = raw_data['data']['r'][0]['t'][0]['d']
            
        data = dict()
        data[self.etf.upper()] = dict()
        for i in raw_data:
            data[self.etf.upper()][i['i']] = float(i['v'])
        
        return data
    
    def plot(self, plt_type = 'all'):
        
        self.getsecID(sec = 1)
        
        #以下一堆廢code，有時間再改XD
        
        nav_data = dict()
        price_data = dict()
        volume_data = dict()
        nav_data[self.etf] = dict()
        price_data[self.etf] = dict()
        volume_data[self.etf] = dict()
                 
        if plt_type == 'all':
            nav_data = self.data(data_type = 'nav')
            price_data = self.data(data_type = 'price')
            volume_data = self.data(data_type = 'volume')
        elif plt_type == 'nav':
            nav_data = self.data(data_type = 'nav')
        elif plt_type == 'price':
            price_data = self.data(data_type = 'price')
        else:
            return 'Sorry, plt_type should be nav, price or all'
            
        nav_date = [datetime.strptime(i, "%Y-%m-%d") for i in nav_data[self.etf.upper()]]
        nav_lst = [nav_data[self.etf.upper()][i] for i in nav_data[self.etf.upper()]]
        
        price_date = [datetime.strptime(i, "%Y-%m-%d") for i in price_data[self.etf.upper()]]
        price_lst = [price_data[self.etf.upper()][i] for i in price_data[self.etf.upper()]]
        
        volume_date = [datetime.strptime(i, "%Y-%m-%d") for i in volume_data[self.etf.upper()]]
        volume_lst = [volume_data[self.etf.upper()][i] for i in volume_data[self.etf.upper()]]

        #使用highchart中的highstock畫圖

        H = Highstock()

        nav_high_data = [[nav_date[i], nav_lst[i]] for i in range(len(nav_data[self.etf.upper()]))]
        price_high_data = [[price_date[i], price_lst[i]] for i in range(len(price_data[self.etf.upper()]))]
        volume_high_data = [[volume_date[i], volume_lst[i]] for i in range(len(volume_data[self.etf.upper()]))]
        
        if plt_type == 'all':
            H.add_data_set(price_high_data, 'line', 'price', id = 'dataseries', color = '#969696', tooltip = {'valueDecimals': 4})
            H.add_data_set(nav_high_data, 'line', 'nav', id = 'dataseries', tooltip = {'valueDecimals': 4})
            H.add_data_set(volume_high_data, 'column', 'Volume', yAxis = 1, color = '#969696')
        elif plt_type == 'nav':
            H.add_data_set(nav_high_data, 'line', 'nav', id = 'dataseries', tooltip = {'valueDecimals': 4})
        elif plt_type == 'price':
            H.add_data_set(price_high_data, 'line', 'price', id = 'dataseries', color = '#969696', tooltip = {'valueDecimals': 4})
        
        

        options = {
            'rangeSelector' : {'selected' : 4},
            'title' : {'text' : self.etf.upper()},
            'tooltip': {'style': {'width': '200px'},
                        'shared' : True,
                        'pointFormat': '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
                       },
             'yAxis': [{'labels': {'align': 'right', 'x': -3},
                        'title': {'text': 'USD'},
                        'height': '60%',
                        'lineWidth': 0.5}, 
                       {'labels': {'align': 'right','x': -3},
                        'title': {'text': 'Volume'},
                        'top': '65%',
                        'height': '35%',
                        'offset': 0,
                        'lineWidth': 2}],
             #'plotOptions': {'series': {'compare': 'percent'}},
                    }

        H.set_dict_options(options)
      
        return H  

