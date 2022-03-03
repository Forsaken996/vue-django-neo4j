# UTF-8
from django.http import JsonResponse
from py2neo import Graph
from pandas import DataFrame as df
import pandas as pd
import json
import numpy as np


# answer = graph.run(c1).to_data_frame()
# answer.columns = ['n1', 'rel', 'n2']
# # 初次转化数据
# json_records = answer.to_json(orient="records")
# data = eval(json_records)
# print(type(data))
# data = pd.DataFrame(data)
# for row in data.values:
#     row[0] = row[0]['name']
#     row[2] = row[2]['name']
# # 最终把数据转化为json格式
# end = data.to_json(orient="records")
# print(end)


# 格式化数据
def managedata(data):
    # 传入frame数据
    data.columns = ['n1', 'rel', 'n2']
    # 初次转化数据
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


# 关系查询:实体1
def findRelationByEntity1(graph, entity1):
    # 预处理
    answer = graph.run("MATCH (n1:`" + entity1 + "`})- [rel] -> (n2) RETURN n1,type(rel),n2").data()
    if answer is None:
        return None
    else:
        answer = graph.run("MATCH (n1:`" + entity1 + "`})- [rel] -> (n2) RETURN n1,type(rel),n2").to_data_frame()
        answer = managedata(answer)
        return answer


# 关系查询:实体1+实体2
def finRelationByEntities(graph, entity1, entity2):
    # 预处理
    answer = graph.run("MATCH (n1:`" + entity1 + "`)- [rel] -> (n2:`" + entity2 + "`) RETURN n1,type(rel),n2").data()
    if answer:
        answer = graph.run("MATCH (n1:`" + entity1 + "`)- "
                                                     "[rel] -> (n2:`" + entity2 + "`) RETURN n1,type(rel),n2").to_data_frame()
        answer = managedata(answer)
        return answer
    else:
        return None


# 根据单条伤害输出结果 hurt为伤害名称
def querybyhurt(graph, hurt):
    c1 = "MATCH (n1)- [rel] -> (n2:`" + hurt + "`) RETURN n1,type(rel),n2"
    answer1 = graph.run(c1).data()
    if answer1 is None:
        return None
    else:
        # answer[0]为产品名
        c = "MATCH (n1:`product`)- [rel] -> (n2:`" + hurt + "`) RETURN n1,type(rel),n2"
        answer = graph.run(c).to_data_frame()
        answer = managedata(answer)
        # answer1为指向伤害的节点
        answer1 = graph.run(c1).to_data_frame()
        answer1 = managedata(answer1)
        for var in answer1:
            answer.append(var)
        nodes = []
        for var in answer1:
            nodes.append(var['n1'])
        for entity1 in nodes:
            for entity2 in nodes:
                if entity1 == entity2:
                    continue
                answers = finRelationByEntities(graph, entity1, entity2)
                if answers:
                    for var in answers:
                        answer.append(var)

    # answer2为伤害指向的节点
    c2 = "MATCH (n1:`" + hurt + "`)- [rel] -> (n2) RETURN n1,type(rel),n2"
    answer2 = graph.run(c2).data()
    if answer2:
        answer2 = graph.run(c2).to_data_frame()
        answer2 = managedata(answer2)
        for var in answer2:
            answer.append(var)
    return answer


# 根据产品名查询伤害记录
def querybyproduct(graph, product):
    products = []
    # 根据伤害查询的记录
    c1 = "MATCH (n1:`" + product + "`)- [rel] -> (n2) RETURN n1,type(rel),n2"
    answer = graph.run(c1).to_data_frame()
    answer = managedata(answer)
    for var in answer:
        end = querybyhurt(graph, var['n2'])
        # 查询每个节点与主节点的关系
        c2 = "MATCH (n1:product {name:\"" + product + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        temp = graph.run(c2).to_data_frame()
        temp = managedata(temp)
        for k in temp:
            end.append(k)
        products.append(end)
    return products


# 将产品信息格式化为1级标题-2级标题-3级标题形式
def managetitle(products):
    if products:
        p = products
        for product in p:
            sx_rel = []
            rels = []
            rel_1 = []  # 一级标题
            rel_2 = []  # 二级标题
            dict_2 = {}  # 二级标题字典表
            for var in product:
                if var['rel'] == '属性':
                    sx_rel.append(var)
                    rels.append(var['n2'])
            for var in sx_rel:
                if var['n1'] in rels:
                    rel_2.append(var['n2'])
                    dict_2[var['n2']] = var['n1']
                else:
                    rel_1.append(var['n2'])
            for var in product:
                if var['rel'] != "有关" and var['rel'] != "属性" and var['n1'] in rel_2:
                    var['rel'] = dict_2[var['n1']] + '-' + var['n1'] + '-' + var['rel']
                if var['rel'] != "有关" and var['rel'] != "属性" and var['n1'] in rel_1:
                    var['rel'] = var['n1'] + '-' + var['rel']
        return p
    else:
        return


# 获取所有产品的关系即作为列
def queryallproductrel(products):
    rel = ["消费品"]
    for product in products:
        for var in product:
            if var['rel'] != '有关' and var['rel'] != '属性' and var['rel'] not in rel:
                rel.append(var['rel'])
    return rel


# 查询单条信息将该显示的信息显示
def demoproduct(graph, product):
    products = querybyproduct(graph, product)
    products = managetitle(products)
    rel = queryallproductrel(products)
    end = [rel]
    # 处理数据一一对应
    for product in products:
        list1 = [product[0]['n1']]
        # 预处理list1
        for var in rel:
            list1.append('')
        list1.pop()
        for var in product:
            if var['rel'] in rel:
                index = rel.index(var['rel'])
                list1[index] = var['n2']
        end.append(list1)
    return end


# 根据某信息查询记录
def querybyinfo(graph, info):
    products = []
    # 根据伤害查询的记录
    c1 = "MATCH (n1:`" + info + "`)- [rel:`有关`] -> (n2) RETURN n1,type(rel),n2"
    answer = graph.run(c1).to_data_frame()
    answer = managedata(answer)
    if answer:
        for var in answer:
            # 查询product->伤害 进而查出该product
            c2 = "MATCH (n1:product)- [rel] -> (n2:" + var['n2'] + ") RETURN n1,type(rel),n2"
            product = graph.run(c2).to_data_frame()
            product = managedata(product)
            if product:
                product = product[0]['n1']
                product = querybyproduct(graph, product)
                for k in product:
                    products.append(k)
            # print(var['n2'], end)
            # c2 = "n1:product {name:\"" + product + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
    print(products)
    return products


# 列出所有信息条目
def queryall(graph):
    c = "MATCH (n1:product)- [rel] -> (n2) RETURN n1,type(rel),n2"
    answer = graph.run(c).to_data_frame()
    answer = managedata(answer)
    end = []
    if answer:
        products = []
        for var in answer:
            if var['n1'] not in products:
                products.append(var['n1'])
        for product in products:
            lists = querybyproduct(graph, product)
            lists = managetitle(lists)
            rel = queryallproductrel(lists)
            if product == products[0]:
                end = [rel]
            else:
                for o in rel:
                    if o not in end[0]:
                        end[0].append(o)
        for product in products:
            lists = querybyproduct(graph, product)
            lists = managetitle(lists)
            rel = end[0]
            # 处理数据一一对应
            for i in lists:
                list1 = [i[0]['n1']]
                # 预处理list1
                for var in rel:
                    list1.append('')
                list1.pop()
                for var in i:
                    if var['rel'] in rel:
                        index = rel.index(var['rel'])
                        list1[index] = var['n2']
                end.append(list1)
            print(end)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    # querybyinfo(graph, "消费者")
    # queryall(graph)
    # products = querybyproduct(graph, "按摩椅")
    # print(products)
    # p = managetitle(products)
    # print(p)
    # end = demoproduct(graph, "按摩椅")
    # print(end)
    s = "2008.1.25-2009.2.5"
    times = s.split("-")
    start = times[0]
    start_time = start.split(".")
    end = times[1]
    end_time = end.split(".")
    print(start_time)
    print(end_time)
    import datetime
    time = [datetime.datetime(int(start_time[0]), int(start_time[1]), int(start_time[2])),
            datetime.datetime(int(end_time[0]), int(end_time[1]), int(end_time[2]))]
    print(time)
