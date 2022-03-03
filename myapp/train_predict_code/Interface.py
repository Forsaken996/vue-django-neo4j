from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd


# 接口函数1
def Dbresearch_countlist():
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    c = 'MATCH (n1:`事件`)-[rel]->(n:`伤害类型`) RETURN n,count(*)'
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        p = {}
        for row in data.values:
            p.update({row[0]['name']: row[1]})
        return p
    else:
        return 0


# 接口函数2
def Dbresearch_pro():
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
    c = 'match (y:`严重程度`)-[rel]-(m:`伤害类型`) return m,y;'
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        tp = []
        dt = {}
        for p in data:
            if p not in tp:
                tp.append(p)
        for p in tp:
            if p['m']['name'] not in dt:
                dt.update({p['m']['name']: int(p['y']['name'])})
            else:
                if int(p['y']['name']) > dt[p['m']['name']]:
                    dt.update({p['m']['name']: int(p['y']['name'])})
        return dt
    else:
        return 0


# 接口函数3
def Dbresearch_old(str):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    c = 'MATCH (n1:`消费品一级类别`{name:"' + str + '"})-[rel1]-(n:`事件`) with n1,rel1,n match (n:`事件`)-[rel2]-(n2:`消费者年龄`) return n2'
    # print(c)
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        # print(data)
        special = 0
        unspecial = 0
        for row in data:
            if row['n2']['name'] != '-1':
                special = special + 1
            else:
                unspecial += 1
        if special >= unspecial:
            return 1
        else:
            return 0
    else:
        return 0


# 接口函数4
def Dbresearch_badscore():
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    c = 'match (n:`事件`)-[rel]-(m:`伤害类型`) with n,rel,m match (n:`事件`)-[rel1]-(y:`严重程度`) return m,y;'
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        tp = []
        dt = {}
        for p in data:
            if p not in tp:
                tp.append(p)
        for p in tp:
            if p['m']['name'] not in dt:
                dt.update({p['m']['name']: int(p['y']['name'])})
            else:
                if int(p['y']['name']) > dt[p['m']['name']]:
                    dt.update({p['m']['name']: int(p['y']['name'])})
        return dt
    else:
        return 0


# 接口函数5
def Dbresearch_littlepart(product, littleparts):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    c = 'match (n:`事件`)-[rel]-(m:`小零件`) with n,rel,m match (n:`事件`)-[rel1]-(y:`涉及的消费品数量`) with n,rel,m,rel1,y match (n:`事件`)-[rel2]-(h:`伤害类型`) return m,y,h'
    data = graph.run(c).data()
    answer = {}
    hurts = {}
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        # print(data)
        # dicts = {}
        uselittleparts = []
        for p in data:
            if p['m']['name'] in littleparts:
                lpn = p['m']['name'].replace('\"', '')
                num = p['y']['name'].replace('\"', '')
                num = num.replace('.0', '')
                hurt = p['h']['name'].replace('\"', '')
                if lpn == '-1':
                    lpn = '其他'
                if hurt == '-1':
                    hurt = '其他'
                # print(lpn, num, hurt)
                if not hurts:
                    hurts.update({hurt: int(num), '总计': int(num)})
                    if lpn not in uselittleparts:
                        uselittleparts.append(lpn)
                elif hurt not in hurts:
                    temp = hurts['总计']
                    hurts.update({hurt: int(num), '总计': int(num) + int(temp)})
                    if lpn not in uselittleparts:
                        uselittleparts.append(lpn)
                else:
                    tp = hurts[hurt]
                    temp = hurts['总计']
                    hurts.update({hurt: int(num) + int(tp), '总计': int(num) + int(temp)})
        print('hurts', hurts)
    prohurts = Dbresearch_product(product)
    print('prohurts', prohurts)
    for p in prohurts:
        if p not in hurts:
            hurts.update({p: prohurts[p]})
        else:
            tp = hurts[p]
            hurts.update({p: prohurts[p] + tp})
    print('hurts2', hurts)
    # print(uselittleparts)
    answer = {}
    for p in hurts:
        if p != '总计':
            answer.update({p: float(hurts[p])/float(hurts['总计'])})
    if uselittleparts:
        answer.update({'小零件': uselittleparts})
    print('answer', answer)
    return answer


# 接口函数6
def Dbresearch_product(product):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    c = 'match (n:`事件`)-[rel]-(m:`消费品名称`) with n,rel,m match (n:`事件`)-[rel1]-(y:`涉及的消费品数量`) with n,rel,m,rel1,y match (n:`事件`)-[rel2]-(h:`伤害类型`) return m,y,h'
    data = graph.run(c).data()
    pro_names = []
    hurts = {}
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        # print(data)
        for p in data:
            # print(p)
            if product in p['m']['name']:
                lpn = p['m']['name'].replace('\"', '')
                num = p['y']['name'].replace('\"', '')
                num = p['y']['name'].replace('.0', '')
                hurt = p['h']['name'].replace('\"', '')
                if lpn == '-1':
                    lpn = '其他'
                if hurt == '-1':
                    hurt = '其他'
                print(lpn, num, hurt)
                if not hurts:
                    hurts.update({hurt: int(num), '总计': int(num)})
                elif hurt not in hurts:
                    temp = hurts['总计']
                    hurts.update({hurt: int(num), '总计': int(num) + int(temp)})
                else:
                    tp = hurts[hurt]
                    temp = hurts['总计']
                    hurts.update({hurt: int(num) + int(tp), '总计': int(num) + int(temp)})
        print(hurts)
        return hurts
    else:
        return {'总计': 0}


if __name__ == "__main__":
    # print(Dbresearch_countlist())
    # print(Dbresearch_old('儿童用品'))
    # print(Dbresearch_pro())
    # print(Dbresearch_badscore())
    print(Dbresearch_product('水晶泥'))
    print(Dbresearch_littlepart('水晶泥', ['电池', '齿轮']))
