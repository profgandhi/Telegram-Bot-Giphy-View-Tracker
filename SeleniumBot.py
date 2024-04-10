from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import asyncio
from abc import ABC,abstractmethod
from bs4 import BeautifulSoup 


class BOT(ABC):
    '''
    Abstract method for selenium bot
    '''
    @abstractmethod
    def target_html() -> str:
        pass


class GiphyBot(BOT):
    '''
    Clicks on ith registered Property and returns HTML
    '''
    def __init__(self,project_id):
        self.url = f'https://giphy.com/gifs/{project_id}'
    def target_html(self):
        print('Start')
        options = Options()
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(options=options)
        browser.get(self.url)
        time.sleep(3)
        html = browser.page_source
        #print(html)
        browser.quit()

        return html
    

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find("div", {"class": 'ViewCountContainer-sc-15ri43l hCQudc ss-view'})
    views = int(div.text.split(" ")[0].replace(",",''))
    return views