# %load go.py
"""
名称: 新浪投诉获取工具
使用到的第三方库: requests, pyquery
"""

import requests
import json
import time
from pyquery import PyQuery
import os
import csv
from datetime import datetime, timedelta


class SinaTousu(object):

    def __init__(self, time_: str, type_: int, keyword_: str):
        super().__init__()
        self.type = type_  # 数据获取方式，0.从网络获取，1.从本地获取
        self.time = time_  # 自定义时间，格式：2020-02-02
        self.encode = "utf-8"  # 文件编码
        self.pauseFile = "pause.conf"  # 中断文件
        self.searchApi = "https://tousu.sina.com.cn/api/index/s"  # 新浪投诉搜索api
        self.params = {
            "page_size": 10,
            "page": 1,  # 开始页
            "keywords": keyword_  # 搜索所用关键词
        }
        self.status = {
            3: "待分配",
            6: "已回复",
            7: "已完成",
            4: "处理中",

        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }
        self.data = []
        try:
            self.restorePause()
        except IOError:
            pass

    def getMsg(self):
        "获取数据"
        try:
            response = requests.get(self.searchApi, params=self.params, timeout=10)
        except:  # 网络错误
            return 0
        if response.status_code != 200:
            print(f"您的ip已被禁止, 本次中断页: {self.params['page']}")
            self.storePause()
            return -1
        try:
            data = json.loads(response.content.decode())
        except json.JSONDecodeError:  # json字符串解析错误
            return 0
        try:
            if len(data["result"]['data']['lists']) >= 1:
                return data["result"]['data']['lists']
            else:
                print("数据获取完毕")
                os.remove("pause.conf")
                return 0
        except TypeError:
            #             os.remove("pause.conf")
            self.storeData()
            print("数据获取完毕")
            return 0

    def restorePause(self):
        with open(self.pauseFile, 'r') as f:
            self.params['page'] = 1

    def storePause(self):
        with open(self.pauseFile, 'w') as f:
            f.write(str(self.params['page']))

    def getMsgFromFile(self, fileName):
        "从本地文件获取数据"
        data = []
        try:
            with open(fileName, 'r', encoding=self.encode) as f:
                f_csv = csv.reader(f)
                headers = next(f_csv)
                for i in f_csv:
                    time_ = '-'.join(i[-2].split("/")).strip()
                    if not self.time or self.time == time_:
                        self.data.append({
                            "标题": i[0],
                            "投诉对象": i[1],
                            "投诉要求": i[2],
                            "投诉内容": i[3],
                            "投诉时间": i[4],
                            "投诉链接": i[5],
                            "投诉进度": i[6]
                        }
                        )
        except IOError:  # 文件读取错误
            return

    def processData(self, data):
        "处理数据"
        for i in data:
            i = i['main']
            time_ = time.strftime("%Y-%m-%d", time.localtime(int(i['timestamp'])))
            status = self.status[i['status']] if i['status'] in self.status else "未知进度"
            if not self.time or time_ in self.time:
                self.data.append({
                    "标题": PyQuery(i['title']).text(),  # 用pyquery获取正常文本内容，否则会含有html标签
                    "投诉对象": PyQuery(i['cotitle']).text(),
                    "投诉要求": PyQuery(i['appeal']).text(),
                    "投诉内容": PyQuery(i['summary']).text(),
                    "投诉时间": time_,
                    "投诉链接": "https:" + i['url'],
                    "投诉进度": status
                })

    def storeData(self):
        "存储数据, 以csv格式存储，gbk编码"
        if not self.data:
            return
        # 将数据转化为标准形式即 序号 事件标题 日期 链接 投诉对象 投诉要求 投诉内容 投诉进度
        print(self.data)
        columns = ['序号', '事件标题', '日期', '链接', '数据来源', '投诉对象', '投诉要求', '投诉内容', '投诉进度']
        end = []
        count = 1
        for var in self.data:
            p = [count, var['标题'], var['投诉时间'], var['投诉链接'], '投诉', var['投诉对象'], var['投诉要求'], var['投诉内容'], var['投诉进度']]
            end.append(p)
            count = count+1
        print(end)

        # csv_name = './auto_data/黑猫_' + self.params['keywords'] + '_' + str(self.time[0]) + '-' + str(self.time[-1]) + '_数据数_' + str(len(self.data)) + '.csv'
        csv_name = './auto_data/黑猫投诉' + self.params['keywords'] + '.csv'
        # 创建该csv文件
        with open(csv_name, "w", encoding=self.encode, newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(columns)
            for i in end:
                try:
                    f_csv.writerow(i)
                except UnicodeEncodeError:
                    pass  # 此处可能产生unicode编码问题
            f.close()

    def run(self):

        if not self.type:
            while 1:
                data = self.getMsg()
                # -1为被禁止的返回值
                if data == -1:
                    self.storeData()
                    print("not nice")
                    self.params["page"] = 1
                    self.run()
                    return
                if data:
                    self.processData(data)
                    self.params["page"] += 1
                    # print(self.params['page'])  # 在控制台打印当前获取页
                    time.sleep(0.5)
                    if self.params["page"] == 500:
                        self.storeData()
                        return
                else:
                    self.storeData()
                    self.params["page"] = 1
                    # self.run()
                    return
                print("已获取" + str(len(self.data)) + '条数据')
        else:
            self.getMsgFromFile("test.csv")
            if self.data:
                self.storeData()


def onemonth():
    begin_date = (datetime.datetime.now() - datetime.timedelta(days=40)).strftime("%Y-%m-%d")
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


def datelist(start, end):
    date_list = []
    begin_date = datetime.strptime(start, r"%Y-%m-%d")
    end_date = datetime.strptime(end, r"%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime(r"%Y-%m-%d")
        date_list.append(date_str)
        # 日期加法days=1 months=1等等
        begin_date += timedelta(days=1)
    return date_list


def getsinadata(date_start, date_end, typetogetdata, keywords):
    b = datelist(date_start, date_end)
    a = SinaTousu(b, typetogetdata, keywords)  # 数据获取方式，0.从网络获取，1.从本地获取
    a.run()


if __name__ == "__main__":
    getsinadata("2021-07-01", "2021-09-17", 0, '手机')
