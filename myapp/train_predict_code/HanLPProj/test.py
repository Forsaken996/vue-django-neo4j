import re
item_dict = {}
content = '召回2020年8月和11月期间制造的型号为CP-2017、CP-2019、CQ-2007V的自吸过滤式防颗粒呼吸器，东风汽车奥迪汽车'
F_GoodsName = './dicts/DmgTypeOfContent'
with open(F_GoodsName, 'r', encoding='utf-8') as f:
    # line = f.readline()
    a = []
    i = 1
    for line in f.readlines():
        if i < 3:
           a.append(line.strip().split(','))
        i += 1
f.close()
print(a)
    # while line and i <= 10:
    #     # if re.search(line.strip(), content):
    #     #     item_dict['消费品名称'].append(line.strip())
    #     print(line)
    #     i += 1
    #     line = part.readline()