# 连接Neo4j数据库并从excel文件导入数据并建立知识图谱
# 所用库：py2neo, pandas
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
import csv


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


def CreateHarmDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品属性与所属危害因素类别的关系字典表', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("危害类型", str(var[0]), '', '')
        node1 = createnode("一级危害因素", str(var[1]), '', '')
        node2 = createnode("二级危害因素", str(var[2]), '', '')
        node3 = createnode("三级危害因素", str(var[3]), '', '')
        createnode("一级危害因素", str(var[1]), '一级危害因素', node)
        createnode("二级危害因素", str(var[2]), '二级危害因素', node1)
        createnode("三级危害因素", str(var[3]), '三级危害因素', node2)


def CreateEnvDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品使用环境属性字典表', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("一级属性名称", str(var[1]), '', '')
        node1 = createnode("特征值", str(var[2]), '', '')
        createnode("特征值", str(var[2]), '特征值', node)


def CreateSortDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品与消费品类别', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("消费品类别", str(var[0]), '', '')
        node1 = createnode("消费品一级类别", str(var[1]), '', '')
        node2 = createnode("消费品名称", str(var[2]), '', '')
        createnode("消费品一级类别", str(var[1]), '消费品一级类别', node)
        createnode("消费品名称", str(var[2]), '消费品名称', node1)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='envdictionary')
    CreateEnvDictionary(graph)
