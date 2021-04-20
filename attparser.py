# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 21:32:18 2020

@author: InvictaeGuy
"""

#data processing libs:
import nltk
nltk.download('punkt')

import string
import numpy as np
import pandas as pd
from sklearn import linear_model
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
#from multiprocessing import pool
nltk.download('punkt')
nltk.download('stopwords')
import time
from rutermextract import TermExtractor

#parsing libs:
import urllib.request 
from urllib.request import Request, urlopen
from pytrends.request import TrendReq
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class Parser(object):
    
    def getIndexing(df, text):
        '''
        
        Parameters
        ----------
        df : DateFrame object
            Array with the text
    
        text : list
            Words of text without stop markers
    
        Returns (average)
        -------
        spam : int
            Amount of spam
            
        water : int
            Amount of water 
            
        dist : tuple
            Distribution of words in text
    
        '''
        #preparing df to count words:
        df = np.add.reduce(df['content'], axis=0)
        df = df.replace('//', '')
        dist = FreqDist(text)#distribution
        df = df.replace('/', '').replace('!', '').replace('.', '').replace(',', '')
        df = df.lower()
        words = df.split()
        words.sort()
        spam = sum([x[1] for x in dist.most_common(2000)])/len(words)
        water = 1 - (len(text)/len(words)) - 0.05
        print('Spam: ', spam)
        print('Water: ', water)

        return spam, water, dist
        
    def getAttendance(url):
        '''
        
        Parameters
        ----------
        url : string
            url of the site
    
        Returns
        -------
        frames_arr : list
            amount of attendance started with last
    
        '''
        #setting the browser:
        opts = Options()
        #opts.set_headless()
        #assert opts.headless       
        opts.add_argument('--start-maximized')
        #opts.add_argument('--profile-directory=Profile 1')
        browser = webdriver.Chrome(executable_path=r'C:\Users\VezoR\Documents\ML examples\AttendancePredictor\chromedriver.exe', 
                                   options=opts)
        
        browser.get('https://be1.ru/')
        form = browser.find_element_by_name('url')
        form.send_keys(url)
        button = browser.find_elements_by_css_selector('button')
        button[1].click()
        
        wait = WebDriverWait(browser, 10)
        time.sleep(30)
        
        circles_arr = []
        frames_arr = []
        minq = 0
        maxq = 0
        minpq = 0
        maxpq = 0
        
        #parsing all (dots) in scatter from be1.ru:
        circles = browser.find_elements_by_css_selector('circle')
        for w in range(52, 58):
            circle = wait.until(EC.visibility_of(circles[w]))
            circles_arr.append(float(circle.get_attribute('cy')))
        
        frames = browser.find_elements_by_css_selector('text')
        for r in [64, 61]:
            frame = wait.until(EC.visibility_of(frames[r]))
            framet = frame.text
            print(framet.findall(r'(\d),(\d)'))
            if framet.findall(r'(\d),(\d)'):
                print(framet, ',')
                framet = framet.replace(',', '').replace(' млрд', '00000000').replace(' млн', '00000').replace(' тыс.', '00')
            else:
                print(framet, 'nothing')
                framet = framet.replace(' млрд', '000000000').replace(' млн', '000000').replace(' тыс.', '000')
            framet = framet.replace(' ', '')
        
            if r == 61:
                minq = int(framet)
                maxpq = float(frame.get_attribute('y'))
            else:
                maxq = int(framet)
                minpq = float(frame.get_attribute('y'))
            print(minq, minpq, maxq, maxpq)

        for x in circles_arr:
            prop = int(((maxq - minq)/(maxpq - minpq))*(x-minpq) + minq)
            frames_arr.append(prop)
       
        #browser.quit()
        
        frames_arr = reversed(frames_arr)
        print('Attendance: ', list(frames_arr))
        return list(frames_arr)

    def getContent(url, keyword, language):
        '''
        
        Parameters
        ----------
        url : string
            url (domen) of site.
        
        keyword : string
            name of site
            
        language : string
            language of the content (exists ru/en)
    
        text : list
            Words of text without stop markers
            
        Returns
        -------
        content['count'].sum() : int
            amount of words in site
        
        df.index.max() : int
            amount of pages
        
        content : DataFrame object
            Array with the text
        '''
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        request = urllib.request.Request(url, None, headers) #The assembled request
        response = urllib.request.urlopen(request)
        
        #response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response, from_encoding=response.info().get_param('charset'))
    
        #parsing all pages from site:
        df = pd.DataFrame(data=None, columns=['page'])
        for i, link in enumerate(soup.find_all('a', href=True)):
            if link['href'].startswith('/') == True and \
               link['href'].startswith('//') == False and \
               link['href'] != '/' and \
               link['href'].find('banner') == -1 and \
               link['href'].find('/goto') == -1:
                df.loc[i] = link['href']
        
        #parsing all content from site:
        df = df.reset_index().drop(columns=['index'])
        df.loc[df.index.max()+1] = url
        print(df)
        content = pd.DataFrame(data=None, columns=['content', 'count'])
        
        for i in df.index:
            if df.loc[i, 'page'].startswith('h') == True:
                urlstr = url
            else:
                urlstr = url + df.loc[i, 'page']
            try:
                r = Request(urlstr, headers={"User-Agent": "Mozilla/5.0"})
                resp = urlopen(r)
            except urllib.error.HTTPError:
                continue  
            
            soup_ = BeautifulSoup(resp, 'html.parser')
            cont = pd.DataFrame(data=None, columns=['content', 'count'])
            #parsing selected page:
            for v, link in enumerate(soup_.find_all('p', text=True)):
                cont.loc[v, 'content'] = link.text
                text = link.text
                cont.loc[v, 'count'] = len(text.split())
            print ('COUNT:', i, urlstr)
            content = pd.concat([content, cont], axis=0)
            
        #frequency analysis of the text:
        txt = ' '.join(content['content']).lower()
        trash = string.punctuation + '\t\n\xa0«»—…®' 
        txt = ''.join([char for char in txt if char not in trash])
        tokens = word_tokenize(txt)
        text = nltk.Text(tokens)
        
        if language == 'en':
            stop_words = stopwords.words('english')
            stop_words.extend(['i', 'copyright', keyword])
        else:
            stop_words = stopwords.words('russian')
            stop_words.extend(['прав', 'см', keyword]) 
        
        text = [word for word in text if word not in stop_words]
    #        fig = go.Figure (data=[go.Bar(x=[x[0] for x in dist.most_common(50)], y=[x[1] for x in dist.most_common(50)])])
    #        fig.show()
    
        content = content.reset_index().drop(columns=['index'])
        #print(content)
        return content['count'].sum(), df.index.max(), content, text
    
    def getPopular(keyword):
        '''
        
        Parameters
        ----------
        keyword : string
            The word whose number of queries will be evaluated
    
        Returns
        -------
        coef : float
            Trend evaluation
        
        df : DataFrame 
            index|date|keyword
                date : string
                    Date of the querie
                keyword : int
                    Amount of queries
                    
        pr : ndarray
            Single predicted value of trend popularity
        
        '''
        #receiving and processing search queries:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([keyword], cat=0, timeframe='all', geo='', gprop='')
        df = pytrends.interest_over_time()
        df = df.drop(columns=['isPartial'])
        df = df.reset_index()
        
        #getting a EMA:
        n = 10
        ema = df.to_numpy()
        ema = np.cumsum (ema[:, 1], dtype=float)
        ema[n:] = ema[n:] - ema[:-n]
        ema = ema[n - 1:]/n
        
        #Trend evaluation based on EMA:
        maxm = ema.size
        ls = linear_model.Lasso(alpha=0.01)
        ls.fit(np.arange(0, 10).reshape(-1, 1), ema[maxm-10:maxm])
        pr = ls.predict(np.arange(14, 15).reshape(-1, 1))
        coef = pr/ema[maxm-1]
        #pred = ls.predict(np.arange(0, 10).reshape(-1, 1))
        #pred_ = np.sum(pred)/len(pred)
        #loc_ = df.loc[maxm-10:maxm, 'date']
        print(coef)
        if coef < 0.9:
            print('fall')
        elif coef > 1.1:
            print('growth')
        else:
            print('absence')
    #        fig = go.Figure (data=[go.Scatter(x=df['date'], y=df[keyword]),
    #                               go.Scatter(x=df['date'], y=ema),
    #                               go.Scatter(x=df.loc[maxm-10:maxm, 'date'], 
    #                                          y=ls.predict(np.arange(0, 10).reshape(-1, 1)))])                           
    #        fig.show()
        return coef, df, pr
