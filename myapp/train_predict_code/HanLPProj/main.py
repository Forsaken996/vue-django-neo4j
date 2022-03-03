import hanlp
import src.clean_data as cl
from src.item_match import Item_data as Item
import threading

def main(input_F, output_F,  _from, country='', needcl = True, cond = '', key='召回内容', encoding='utf-8', src=''):
    """
    params:
    -------
    >>> params
    input_F:
        输入文件路径名称
    output_F:  
        输出文件路径名称
    _from:
        数据来源---舆情 召回 投诉 网站
    country:
        来源国家，若为国内数据需手动填中国，否则不填
    needcl:
        是否需要数据清洗
    key:
        代表事件详细内容描述的列名，如'投诉内容'，'事件描述'等
    cond:
        代表危害情况的列名，如 导致的危害，仅对标准院的数据需要此参数
    src:
        代表危害源的列名，同样仅对标准院的数据需要此参数
    encoding:
        编码方式，默认为'utf-8'
    """
    if needcl:
        mid_input_F = input_F.rstrip('.csv') + '_new.csv'
        cl.clean_csv(input_F, mid_input_F, keywords=key)
    else:
        mid_input_F = input_F
    print(input_F,'数据清洗完毕，已生成预处理数据',mid_input_F)
    Struct = Item(output_F)
    # data = cl.get_content(mid_input_F, key)
    all_data = cl.get_data(mid_input_F)
    for data in all_data:
        # print(data)
        Struct.add_item(data, data[key], _from=_from, country=country, cond=cond, src=src)
        # print(Struct.item_dict)
        # a = input()
        # if a == -1:
            # break
    Struct.writetocsv(encoding=encoding)
    # print(test.csv_list)


if __name__=='__main__':
    # goods_csv = './data/消费品召回1.csv'
    input_path1 = './data/国内汽车召回1_new.csv'
    output_path1 = './data/result/国内汽车召回.tsv'
    input_path2 = './data/国外汽车召回1_new.csv'
    output_path2 = './data/result/国外汽车召回.tsv'
    input_path3 = './data/消费品召回1_new.csv'
    output_path3 = './data/result/消费品召回1.tsv'
    # main(input_path2, output_path2)
    # t1 = threading.Thread(target=main, args=(input_path1, output_path1, '召回', '中国', False, '召回内容', 'utf-8') )
    # t2 = threading.Thread(target=main, args=(input_path2, output_path2, '召回', '中国', False, '召回内容', 'utf-8'))
    # t3 = threading.Thread(target=main, args=(input_path3, output_path3, '召回', '中国', False, '召回内容', 'utf-8'))
    # t1.start()
    # t2.start()
    # t3.start()
    
    input_heim = './data/黑猫投诉童装.csv'
    output_heim = './data/result/黑猫投诉童装.tsv'
    # main(input_heim, output_heim, key='投诉内容', _from='投诉', needcl=True, encoding='utf-8', country='中国')

    # 以处理
    input_tj = './data/消费品质量安全事件统计2020年5月26日-2021年6月25日.csv'
    output_tj = './data/整合数据/消费品质量安全事件统计2020年5月-6月-有效数据.tsv'
    # main(input_tj, output_tj, key='伤害事件', encoding='utf-8', _from='舆情', needcl=False, country='中国', cond='伤害类别', src='危害源')

    input_guon = './data/标准院-国内召回情况-2021年6月  2021-6-29_new.csv'
    output_guon = './data/result/标准院-国内召回情况-2021年6月有效数据.tsv'
    # main(input_guon, output_guon, _from='召回', needcl=False, key='召回原因', encoding='utf-8', country='中国')

    input_guon = './data/标准院-国外召回情况-2021年6月  2021-6-29_new.csv'
    output_guon = './data/result/标准院-国外召回情况-2021年6月-有效数据.tsv'
    # main(input_guon, output_guon, _from='召回', needcl=True, key='召回原因', encoding='utf-8')

    # 
    input_yz2018 = './data/org/院长基金数据2018_召回通报.csv'
    output_yz2018 = './data/整合数据/院长基金数据2018_召回通报.tsv'
    main(input_yz2018, output_yz2018, _from='召回', needcl=True, key='通报原因', encoding='utf-8', cond='可能导致的伤害类型', src='召回产品存在的三级级危害因素')

    # 已处理
    input_yz2018_2 = './data/org/院长基金数据2018_舆情监测--新.csv'
    output_yz2018_2 = './data/整合数据/院长基金数据2018_舆情监测--新.tsv'
    # main(input_yz2018_2, output_yz2018_2, _from='舆情', needcl=True, key='备注（事件概述）', encoding='utf-8', country='中国', cond='导致的伤害', src='产品存在的三级危害因素')

    #
    input_yz2019 = './data/org/院长基金数据2019_舆情监测--新.csv'
    output_yz2019 = './data/整合数据/院长基金数据2019_舆情监测--新.tsv'
    main(input_yz2019, output_yz2019, _from='舆情', needcl=True, key='备注（事件概述）', encoding='utf-8', country='中国', cond='导致的伤害', src='产品存在的三级危害因素')

    input_yz2020 = './data/org/2020年1-12月-国内召回.csv'
    output_yz2020 = './data/result/2020年1-12月-国内召回.tsv'
    # main(input_yz2020, output_yz2020, _from='召回', needcl=True, key='召回原因', encoding='utf-8', country='中国')
