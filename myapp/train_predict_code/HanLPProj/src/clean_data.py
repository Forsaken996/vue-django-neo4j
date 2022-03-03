import re
import csv

_pattern = re.compile(r'日前，|根据.*的要求.*备案.{0,20}召回计划[。，]|(此外|消费者|用户).{0,10}可登录.*|登录.*了解.*|'\
    '版权.*|将[通过以].{0,8}挂.*了解.*(信息|详情)。|用户.{0,20}热线.*[咨询信息][。.]?|将[通过以].{0,30}通知.*(车主|事宜).*|登录网站.*|'\
    '(消费者|用户).{0,10}也?可.{0,35}[(热线)(电话)].*(详情|情况|信息).*|[，]反[应映]缺陷线索[，。]')
_symbol = re.compile(r'gov|[？?！!；;：:\n\r\t]')

def get_content(datapath, key='召回内容'):
    content = []
    with open(datapath, encoding='utf-8') as f:
        text = csv.DictReader(f)
        for raw in text:
            _ = raw[key]
            content.append(_)
    return content

def get_sentence(datapath):
    content = []
    with open(datapath, encoding='utf-8') as f:
        text = csv.DictReader(f)
        for raw in text:
            _ = sentence_clean(raw['召回内容'])
            tmp = sentence_sub(_)
            content.append(tmp)
    return content

def get_data(datapath):
    content = []
    with open(datapath, encoding='utf-8') as f:
        text = csv.DictReader(f)
        for raw in text:
            content.append(raw)
    return content

def sentence_sub(content):
    return _pattern.sub('', content)

def sentence_clean(content):
    return _symbol.sub('', content)

def clean_csv(origin_p, new_p, keywords='召回内容', need_dic=False, items=''):
    cus_dic=[]
    with open(new_p, 'w', encoding='utf-8') as fcsv:
        with open(origin_p, encoding='utf-8') as f:
            test = csv.DictReader(f)
            fields = test.fieldnames
            fout = csv.DictWriter(fcsv, fieldnames=fields, lineterminator='\n')
            fout.writeheader()
            for _ in test:
                _[keywords] = sentence_sub(sentence_clean(_[keywords]))
                for k in _:
                    if '产品类别' in k or '产品分类' in k:
                        _[k].replace('服装纺织品', '纺织品及服装鞋帽').replace('电子信息', '信息技术产品').replace('家具装饰装修材料', '家具及建筑装饰装修材料').replace('日化', '日杂用品')
                        if _[k] == '家用电器':
                            _[k] = '家用电器及电器附件'
                        elif _[k] == '家具装修':
                            _[k] = '家具及建筑装饰装修材料'
                        elif _[k] == '疫情相关产品':
                            _[k] = '其他'
                        elif _[k] == '服装鞋帽':
                            _[k] = '纺织品及服装鞋帽'
                        break
                fout.writerow(_)
                if need_dic:
                    cus_dic.append(_[items])
    return cus_dic
def DicttoFile(cus_dict, filepath):
    '''
    ### 将cus_dict自定义字典内容写入filepath目标文件中
    '''
    with open(filepath, 'a+', encoding='utf-8') as f:
        f.write('\n'.join(cus_dict))


def get_cars(datapath, dictpath):
    cars = []
    with open(dictpath, 'a+', encoding='utf-8') as f:
        with open(datapath, encoding='utf-8') as org:
            text = csv.DictReader(org) 
            i = 0
            for raw in text:
                # _ = raw['召回公司']
                n = re.search('车型[:：]?(.*)召回数量|产品名称[:：]?(.*) 产地', raw['召回内容'])
                if n.group(1):
                    n = n.group(1)
                else: n = n.group(2)
                # n = n.replace(',', '，')
                f.write('"' + n + '"' + ',交通工具及相关产品,\n')
                i += 1


if __name__ == '__main__':
    get_cars('../data/国外汽车召回1.csv', '../dicts/all_goods2')