# coding:utf-8
"""
名称: 国家市场监督管理总局缺陷产品管理中心投诉获取工具(SAMR DEFECTIVE PRODUCT ADMINISTRATIVE CENTER)
使用到的第三方库: requests ,re
"""

import requests
import re
import time
import csv
from pyquery import PyQuery as pq
import random


class Callback(object):
    def __init__(self):
        super().__init__()
        self.encode = "gbk"  # 文件编码
        self.pauseFile = "pause.conf"  # 中断文件
        self.searchApi = [
            "https://dpac.samr.gov.cn/xfpzh/xfpgnzh/",  # 消费品召回
            # "https://dpac.samr.gov.cn/qczh/gnzhqc/",  # 国内汽车召回
            # "https://dpac.samr.gov.cn/qczh/gwzh/",  # 国外汽车召回)
            "https://dpac.samr.gov.cn/xfpzh/xfpgwzh/"  # 国外消费品召回
        ]
        self.callback_info = []
        self.data = []
        # self.text = ["消费品召回", "国内汽车召回", "国外汽车召回"]
        self.text = ["国内消费品召回", "国外消费品召回"]

    def getmsg(self):
        # 获取数据
        text = self.text
        for i in range(0, 2):
            # 使用代理
            adrs = []
            requests.packages.urllib3.disable_warnings()
            for search_index in range(0, 59):
                time.sleep(0.1)
                if search_index == 0:
                    adr_index = self.searchApi[i] + "index.html"
                else:
                    adr_index = self.searchApi[i] + "index_" + str(search_index) + ".html"  # 构造表单地址
                # print(adr_index)
                proxy = {'http': '123.58.10.36:8080'}  # try catch换
                try:
                    response = requests.get(adr_index, verify=False, timeout=500)
                except:
                    response = requests.get(adr_index, verify=False, proxies=proxy, timeout=500)
                # print(response.text)
                # encode('iso-8859-1')是将gbk编码编码成unicode编码
                # decode('gbk')是从unicode编码解码成gbk字符串
                html = response.text.encode('iso-8859-1').decode('utf-8')  # 解析网页
                urls = re.findall('<a href="./([^\.].*).html"', html)  # 提取目标文本所在的网址
                # print(urls)
                for info in urls:
                    adr = self.searchApi[i] + info + ".html"
                    if adr not in adrs:
                        adrs.append(adr)
                        # print(adr)
                print(text[i], "---> 已获取到地址数:", len(adrs), "%1000")

            print(text[i], "!!!已完成!!!")
            time.sleep(0.1)
            # 访问每一个adr地址 提取信息 生成表单
            for callback_adr in adrs:
                time.sleep(0.1)
                # 根据文本提取日期信息
                date = callback_adr[-20:-12]
                # print(date)
                print(text[i], "---> 提取信息ing ---> 已经提取的信息数：", len(self.callback_info), "%", str(1000 * (i + 1)))
                try:
                    response = requests.get(callback_adr, verify=False, timeout=500)
                except:
                    print('保存数据中~')
                    # response = requests.get(callback_adr, verify=False, proxies=proxy, timeout=500)
                    self.storeData(i)
                    print('数据已保存')
                    break

                html = response.text.encode('iso-8859-1').decode('utf-8')  # 解析网页
                # print(html)
                title = pq(html)('h1').text()
                # title = re.findall('<div class="show_tit"><h1>(.*)</h1></div>', html)
                # title = title[0]
                print(title)
                area = re.findall('【(.*)】', title)
                if area:
                    area = area[0]
                else:
                    area = None
                company = re.findall('([^主动】]*)[主动]*召回', title)
                if company:
                    company = company[0]
                else:
                    company = None
                product = re.findall('召回[部分]*([^部分]*)', title)
                if product:
                    product = product[0]
                else:
                    area = None
                # print(area, company, product)
                # urls = re.findall('<p>[<span>]*(.*)</p>', html)  # 提取目标文本所在的网址
                p = pq(html)('p')  # 通过pyquery库来取得文本
                # print(p.text())
                infomations = p.text()
                print(date)
                self.callback_info.append({"召回时间": date, "召回地区": area, "召回公司": company,
                                           "召回产品": product, "召回内容": infomations, "标题内容": title, "页面地址": callback_adr})
            response.close()
            self.storeData(i)
            self.callback_info = []  # 清空数据集，若要将所有数据集中到一张表上，删除该句
        print(self.callback_info)

    def storeData(self, state):
        # 存储数据, 以csv格式存储，gbk编码
        if not self.callback_info:
            return
        name = './auto_data/' + self.text[state] + ".csv"
        with open(name, "a+", encoding='utf-8', newline="") as f:
            f_csv = csv.writer(f)
            f_csv.writerow(self.callback_info[0].keys())
            for i in self.callback_info:
                try:
                    f_csv.writerow(i.values())
                except UnicodeEncodeError:
                    pass  # 此处可能产生unicode编码问题


if __name__ == "__main__":
    a = Callback()
    a.getmsg()
