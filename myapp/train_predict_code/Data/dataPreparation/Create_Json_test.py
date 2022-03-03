# coding:utf-8
import json
import csv

json_file = open('test.json', 'w+', encoding='utf-8')
csv_file = open('test1.csv', 'r', encoding='utf-8')

# 读取文件第一行不读取换行符作为json文件里每个数据的键值
keys = csv_file.readline().strip('\n').split(',')

json_file.write('[\n')
flag = 0

while csv_file.readline():
    print(csv_file.readline())
    # 字符串列表转化为数字列表
    values = csv_file.readline().strip('\n').split(',')

    # 用zip()函数将两个列表形成映射关系，创建字典
    dic_temp = dict(zip(keys, values))

    # 将字典转化为字符串且带有缩进
    # flag用于判断json文件中 "," 和换行的添加位置
    json_str = json.dumps(dic_temp, indent=4, ensure_ascii=False)

    if flag == 1:
        json_file.write(',\n')

    json_file.write(json_str)

    flag = 1

json_file.write(']')
csv_file.close()
json_file.close()
