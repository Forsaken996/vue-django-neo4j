# 连接Neo4j数据库并从json文件导入数据并建立知识图谱
# 所用库：py2neo, pandas
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
import csv
import json


# 判断该节点及子节点是否为空
def node_is_empty(var):
    # print(var)
    if var == "" or var == [] or var == {}:
        return True
    if var and (type(var) is not dict):
        return False
    else:
        for so in var:
            p = node_is_empty(var[so])
            if p is False:
                return False
    return True


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


# 递归处理节点
def Create_Node(value, last_node):
    global nodes
    for key in value:
        if node_is_empty(value[key]):
            continue
        if type(value[key]) is list:
            for values in value[key]:
                node = createnode(values, values, key, last_node)
                nodes.append(node)
        elif type(value[key]) == dict:
            node = createnode(key, key, '属性', last_node)
            Create_Node(value[key], node)
            nodes.append(node)
        else:
            node = createnode(value[key], value[key], key, last_node)
            nodes.append(node)


# # 连接neo4j数据库，输入地址、用户名、密码
graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
graph.delete_all()  # 清除neo4j中原有的结点等所有信息

# 读取json文件内容,返回字典格式
with open('file1.json', 'r', encoding='utf8')as fp:
    json_data = json.load(fp)
    print('这是文件中的json数据：', json_data)
    print('这是读取到文件数据的数据类型：', type(json_data))

# Json格式： 在neo4j中采用 消费品->消费品名称->手机 消费品->机械危害->尺寸
# 处理Json格式数据 将其转换为一个个节点以及关系
count = 0
for var in json_data:
    if var:
        count = count + 1
        print(count, "%", len(json_data))
        nodes = []
        harmnode = Node("", name="")
        newnode = createnode("product", var['消费品']['消费品名称'], '', '')
        # newnode = createnode("product", var["消费品名称"], '', '')
        nodes.append(newnode)
        for key in var:
            # print(key, node_is_empty(var[key]))
            if key == '伤害':
                harmnode = createnode("伤害"+str(count), "伤害"+str(count), '', '')
                for keys in var[key]:
                    if node_is_empty(var[key][keys]):
                        continue
                    else:
                        node = createnode(var[key][keys], var[key][keys], keys, harmnode)
                        createnode("伤害"+str(count), "伤害"+str(count), "有关", node)
                continue
            # print("key:", key)
            # print("value:", var[key])
            # print(type(var[key]))
            # print("var[key]:", var[key])
            if node_is_empty(var[key]):
                continue
            if type(var[key]) is not dict:
                if type(var[key]) is list:
                    for values in var[key]:
                        node = createnode(values, values, key, newnode)
                        nodes.append(node)
                else:
                    node = createnode(var[key], var[key], key, newnode)
                    nodes.append(node)
            else:
                node = createnode(key, key, "属性", newnode)
                nodes.append(node)
                Create_Node(var[key], node)
        # print(nodes)
        for p in nodes:
            # print(harmnode)
            createnode("伤害"+str(count), "伤害"+str(count), "有关", p)
            # 首先创立节点
            # 循环处理value使其变为节点

            # while(type(var[key]) != dict):
            #     print("hh")


'''
{
"消费品": 
    {	
    "消费品名称":"手机",
    "机械危害":
        {
        "尺寸": [],
        "绳索及类似物": [],
        "不透气": [],
        "填充物": [],
        "小零件":"",
        "尖角":"",
        "锐利边缘":"",
        "光滑表面":"",
        "粗糙表面":"",
        "部件空隙及开口":""
        },
    "噪声危害":""
    },
"消费者": 
    {	
    "姓名":"",
    "性别": [],
    "年龄": [],
    "健康状况": [],
    "职业": []
    },
"使用环境特征": 
    {	
    "昼夜":"",   
    "环境":["室内","..."],
    "温度": [],
    "形状": [],
    "其他环境特征": []
    },
"时间":"",
"伤害":
    {
    "伤害类型":"",
    "伤害严重性":"",
    "伤害说明":""
    }
}
'''
