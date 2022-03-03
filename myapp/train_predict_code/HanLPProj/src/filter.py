from simhash import simhash
import csv
import re

def filter_csv(origin_p, new_p, keywords='召回内容', lv = 4, sim = False, filt = False, o_enc='utf-8'):
    sims = simhash()
    if sim or filt:
        with open(new_p, 'w', encoding='utf-8') as fcsv:
            with open(origin_p, encoding=o_enc) as f:
                test = csv.DictReader(f)
                fields = test.fieldnames
                fout = csv.DictWriter(fcsv, fieldnames=fields, lineterminator='\n')
                fout.writeheader()
                for _ in test:
                    if filt and re.search(r'伤|危险[^驾]|(^感染)风险|安全|防范|害|健康', _[keywords]) and \
                        not re.search(r'滴滴|出行|打车|出租|司机|订单|快车', _[keywords]):
                        if not sim:
                            fout.writerow(_)
                        elif sim and sims.checkhash(_[keywords], lv):
                            fout.writerow(_)
                    elif sim and sims.checkhash(_[keywords], lv) and re.search(r'伤|危险[^驾]|(^感染)风险|安全|防范|害|健康', _[keywords]) and not re.search(r'滴滴|出行|打车|出租|司机|订单|快车', _[keywords]):
                        fout.writerow(_)


if __name__ == '__main__':
    # filter_csv('../data/spider/Weibo-Spider汽车 召回.csv', '../data/filter/Weibo-汽车召回.csv', sim = True)
    filter_csv('../data/黑猫文具7.1-9.16 120条数据.csv', '../data/filter/黑猫文具7.1-9.16数据-去重', '投诉内容', sim = True, filt = True, o_enc='gbk', lv = 12)