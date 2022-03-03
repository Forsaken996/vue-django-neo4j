# 连接Neo4j数据库并从excel文件导入数据并建立知识图谱
# 所用库：py2neo, pandas
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
import csv

# harm字典表
harms = []
# 危害类型->一级危害因素
harm_rel1 = []
# 一级危害因素->二级危害因素
harm_rel2 = []
# 二级危害因素->三级危害因素
harm_rel3 = []
# 三级危害因素
harm3 = []


# 格式化数据
def managedata(data):
    # 传入frame数据
    data.columns = ['n1', 'rel', 'n2']
    # 初次转
    # 化数据
    json_records = data.to_json(orient="records")
    data = eval(json_records)
    data = pd.DataFrame(data)
    for row in data.values:
        row[0] = row[0]['name']
        row[2] = row[2]['name']
    # 最终把数据转化为json格式
    end = data.to_dict('records')
    # print(end)
    return end


# 创建节点的同时并创建关系
def createnode(label_name, property_value, rela_name, node_name1):
    node = Node(label_name, name=property_value)
    matcher = NodeMatcher(graph)
    nodelist = list(matcher.match(label_name, name=property_value))
    if len(nodelist) > 0:  # 表示节点存在，不需创建新的节点
        node = nodelist[0]  #
        # 可以直接添加关系
        if rela_name != '':
            rela = Relationship(node_name1, rela_name, node)
            graph.create(rela)
    else:
        # 创建节点
        graph.create(node)
        # 创建关系
        if rela_name != '':
            rela = Relationship(node_name1, rela_name, node)
            graph.create(rela)
    return node


def createproductdata(graph):
    global harm3
    global harms
    global harm_rel1
    global harm_rel2
    global harm_rel3
    graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    df = pd.read_excel('reldata.xlsx', sheet_name='安全事件数据表', keep_default_na=False)
    # print(df)
    data = df.values.tolist()
    # print(data)
    columns = df.columns.values
    print(columns)
    count = 0
    # 由于伤害可能有多种，因此单独分出
    hurt_index = columns.tolist().index('伤害类型')
    harm_index = columns.tolist().index('消费品危害类型')
    harm_index1 = columns.tolist().index('消费品一级危害类型')
    harm_index2 = columns.tolist().index('消费品二级危害类型')
    for var in data:
        count += 1
        print("进度:", count, "%", len(data))
        print(var[0])
        node_event = createnode("事件", "事件" + str(var[0]), '', '')
        for i in range(0, len(var)):
            if var[i]:
                if i == harm_index or i == hurt_index:
                    print(type(var[i]))
                    if '，' in var[i]:
                        var[i] = str(var[i]).split('，')
                        for n in var[i]:
                            print("已创建节点：", n, "子进度:", i, "%", len(var))
                            node = createnode(str(columns[i]), str(n), columns[i], node_event)
                    elif '、' in var[i]:
                        var[i] = str(var[i]).split('、')
                        for n in var[i]:
                            print("已创建节点：", n, "子进度:", i, "%", len(var))
                            node = createnode(str(columns[i]), str(n), columns[i], node_event)
                    else:
                        print("已创建节点：", var[i], "子进度:", i, "%", len(var))
                        node = createnode(str(columns[i]), str(var[i]), columns[i], node_event)
                elif columns[i] in harm3:
                    node = createnode(str(columns[i]), str(var[i]), columns[i], node_event)
                    node3 = createnode('三级危害因素', str(columns[i]), '三级危害因素', node_event)
                    for k in harm_rel3:
                        if k['n2'] == columns[i]:
                            print(i, var[i], columns[i])
                            node2 = createnode('二级危害因素', str(k['n1']), '二级危害因素', node3)
                            for t in harm_rel2:
                                if t['n2'] == k['n1']:
                                    node1 = createnode('一级危害因素', str(t['n1']), '一级危害因素', node2)
                                    for p in harm_rel1:
                                        if p['n2'] == t['n1']:
                                            node0 = createnode('危害类型', str(p['n1']), '危害类型', node1)
                                            break
                                    break
                            break
                    print("已创建节点：", var[i], "子进度:", i, "%", len(var))
                elif i == harm_index1 or i == harm_index2:
                    continue
                else:
                    print(type(var[i]))
                    ts = Timestamp('2018-12-01 00:00:00', freq='MS')
                    if type(var[i]) == type(ts):
                        var[i] = str(var[i]).split()[0]
                        print(type(ts), var[i])
                    print("已创建节点：", var[i], "子进度:", i, "%", len(var))
                    node = createnode(str(columns[i]), str(var[i]), columns[i], node_event)


def getallharm(graph):
    c = "MATCH (n1)- [rel] -> (n2) RETURN n1,type(rel),n2"
    answer = graph.run(c).data()
    if answer:
        global harm3
        global harm
        global harm_rel1
        global harm_rel2
        global harm_rel3
        answer = graph.run(c).to_data_frame()
        answer = managedata(answer)
        harm = answer
        for var in answer:
            if var['rel'] == '三级危害因素':
                harm3.append(var['n2'])
                harm_rel3.append(var)
                print(harm3)
            elif var['rel'] == '二级危害因素':
                harm_rel2.append(var)
            elif var['rel'] == '一级危害因素':
                harm_rel1.append(var)
        print(answer)
        print(harm_rel1)
        print(harm_rel2)
        print(harm_rel3)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='harmdictionary')
    getallharm(graph)
    # 连接neo4j数据库，输入地址、用户名、密码
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    createproductdata(graph)
