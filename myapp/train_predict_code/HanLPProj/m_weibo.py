import csv
import re
import threading
import time
from urllib.parse import urlencode
from urllib.parse import quote
import requests
import pandas as pd
from src.simhash import simhash
import os

UserAgent = 'Baiduspider+(+http://www.baidu.com/search/spider.htm)'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
cookie = 'SUB=_2A25MJ0xWDeRhGeBN7FUZ-SnIyDSIHXVv6FQerDV6PUJbkdCOLVjgkW1NRDwWkFEWW3WOyOIDw83XoHCH6tZNjDsz; WEIBOCN_FROM=1110106030; MLOGIN=1; _T_WM=28694145606;'
headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'User-Agent': user_agent
        }
base = 'https://m.weibo.cn/api/container/getIndex?containerid=100103'
detail = 'https://m.weibo.cn/statuses/extend?id='

user_URL = 'https://m.weibo.cn/detail/'

class Weibo(threading.Thread):
    '''
    ## 微博爬虫
    '''
    def __init__(self, keywords, outpath, org, lv):
        '''
        ### keywords：搜索关键字
        ### outpath: 目标文件路径
        关于多线程目前的两种实现
        1. 继承threading.Thread,
        2. class内添加函数实现多线程调用
        '''
        threading.Thread.__init__(self)
        self._keywords = keywords
        self.path = outpath
        self.types = {'实时': 61}
        self.cookies = []
        self.sim = simhash()
        self.org = org
        self.lv = lv
    
    def get_cookie(self):
        url = 'https://m.weibo.cn'
        cookie = ''
        session = requests.Session()
        session.get(url, headers=headers)
        # print(r.cookies)
        c = session.cookies.get_dict()
        for k in c:
            cookie += f'{k}={c[k]}; '
        # headers = 
        # print(cookie)
        return cookie

    def GetURL(self, type, page):
        params = {
            'containerid': 100103,
            'type': self.types[type],
            'q' : self._keywords,
            }
        return f'{base}{quote(urlencode(params))}&page_type=searchall&page={page}'

    def GetOnePage(self, page=None, type='实时', url=None):
        _url = self.GetURL(type, page) if not url else url
        try:
            response = requests.get(_url, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.ConnectionError as e:
            print('ConnectionError', e.args)
        except requests.exceptions.HTTPError as e:
            print('HttpError', e.args)
        except requests.exceptions.RequestException as e:
            print('RequestError', e.args)

    
    def SearchAndCsv(self, org = 0, lv = 10, encoding='utf-8', sep=','):
        with open(self.path + 'Weibo-Spider' + self._keywords + '.csv', 'w', encoding=encoding) as fcsv:
            fields = ['日期', '召回内容', '链接']
            fout = csv.DictWriter(fcsv, fieldnames=fields, lineterminator='\n')
            fout.writeheader()
            page = 1
            while (items := self.GetOnePage(type='实时', page=page)) != None:
                print(self._keywords, page)
                time.sleep(2)
                if items['ok']:
                    for item in items['data']['cards']:
                        if 'mblog' in item:
                            if item['mblog']['isLongText']:
                                text = re.sub(r'<.*?>|//@.+?:', '', self.GetOnePage(url=detail+item['mblog']['id'])['data']['longTextContent'])
                            else:
                                text = re.sub(r'<.*?>|//@.+?:', '', item['mblog']['text'])
                            # print(text)
                            if re.search('(消费品|商品|汽车|产品).*(受伤|死亡|伤害|危险|划伤|风险|隐患)|(造成|导致|引发|引起|致使)消费者.*(受伤|伤|危|亡|隐患|风险)', text) and not re.search('现货|优惠|打折|资讯|发货|恼火|发错|代言|形象|黑粉|赚钱|明星|法律|保护消费者', text) or org:
                                # print(text)
                                if org:
                                    fout.writerow({'日期': item['mblog']['created_at'],'召回内容': text, '链接': user_URL+item['mblog']['id']})
                                elif self.sim.checkhash(text, lv=lv):
                                    fout.writerow({'日期': item['mblog']['created_at'],'召回内容': text, '链接': user_URL+item['mblog']['id']})
                else: break
                page += 1
    
    def StoreData(self, item, encode='utf-8'):
        '''功能暂未启用'''
        with open(self.path, 'w',encoding=encode) as fcsv:
            fields = ['发微博时间', '召回内容']
            fout = csv.DictWriter(fcsv, fieldnames=fields, lineterminator='\n')
            fout.writeheader()
            for page in range(1, 100):
                print(page)
                time.sleep(2)
                items = self.GetOnePage(page)['data']['cards']
                for item in items:
                    if 'mblog' in item:
                        fout.writerow({'发微博时间': item['mblog']['created_at'],'召回内容': item['mblog']['text']})

    def run(self):
        '''对于继承threading.Thread的类，需要重写run方法'''
        self.SearchAndCsv(org = self.org, lv = self.lv)


def main():
    t1 = Weibo('消费品 商品 伤', './auto_data/', 1, 0)
    # t1.start()
    # t2.start()
    # t = Weibo('商品', '')
    headers['cookie'] = t1.get_cookie()
    # res = t.GetOnePage()
    # print(res)
    t1.start()


def Weibo_main():
    t1 = Weibo('消费品 商品 伤', './auto_data/', 1, 0)
    # t1.start()
    # t2.start()
    # t = Weibo('商品', '')
    headers['cookie'] = t1.get_cookie()
    # res = t.GetOnePage()
    # print(res)
    t1.start()


if __name__ == '__main__':
    main()
