from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.http import JsonResponse
import json
from py2neo import Graph
import pandas as pd
import numpy as np
from .models import Relation
from django.http.request import QueryDict
from django import forms
import datetime


class UserForm(forms.Form):
    info = forms.CharField(label='info', required=False)


class QueryForm(forms.Form):
    time = forms.CharField(label='time', required=False)  # 时间
    classification = forms.CharField(label='classification', required=False)  # 消费品类别
    productname = forms.CharField(label='productname', required=False)  # 名称
    hurt = forms.CharField(label='hurt', required=False)  # 伤害
    harm = forms.CharField(label='harm', required=False)  # 危害


def wirte_info(code=404, data="fail", info="未知错误"):
    res = {"code": code, "data": data, "info": info}
    return res


def get_initial_graph(request):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    try:
        c1 = "MATCH (n1)- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c1).to_data_frame()
        answer.columns = ['n1', 'rel', 'n2']
        # 初次转化数据
        json_records = answer.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        for row in data.values:
            row[0] = row[0]['name']
            row[2] = row[2]['name']
        # 最终把数据转化为json格式
        end = data.to_json(orient="records")
        response['data'] = end
        response['msg'] = 'success'
        response['error_num'] = 0
        return JsonResponse(response)
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = 1
    return JsonResponse(response)


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


# 关系查询:实体1
def findRelationByEntity1(graph, entity1):
    if graph and entity1:
        # 预处理
        c = "MATCH (n1:`" + entity1 + "`})- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c).data()
        if answer is None:
            return None
        else:
            answer = graph.run(c).to_data_frame()
            answer = managedata(answer)
            return answer


# 关系查询:实体1+实体2
def finRelationByEntities(graph, entity1, entity2):
    if graph and entity1 and entity2:
        # 预处理
        answer = graph.run(
            "MATCH (n1:`" + entity1 + "`)- [rel] -> (n2:`" + entity2 + "`) RETURN n1,type(rel),n2").data()
        if answer:
            answer = graph.run("MATCH (n1:`" + entity1 + "`)-[rel] -> (n2:`" + entity2 +
                               "`) RETURN n1,type(rel),n2").to_data_frame()
            answer = managedata(answer)
            return answer
        else:
            return None


# 根据单条伤害输出结果 hurt为伤害名称
def querybyhurt(graph, hurt):
    if graph and hurt:
        c1 = "MATCH (n1)- [rel] -> (n2:`" + hurt + "`) RETURN n1,type(rel),n2"
        answer1 = graph.run(c1).data()
        if answer1:
            # answer[0]为产品名
            c = "MATCH (n1:`product`)- [rel] -> (n2:`" + hurt + "`) RETURN n1,type(rel),n2"
            answer = graph.run(c).data()
            if answer:
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
    if product and graph:
        products = []
        # 根据伤害查询的记录
        c1 = "MATCH (n1:product{name:\"" + product + "\"})- [rel:`有关`] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c1).data()
        if answer:
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
    if products:
        rel = ["消费品"]
        for product in products:
            for var in product:
                if var['rel'] != '有关' and var['rel'] != '属性' and var['rel'] not in rel:
                    rel.append(var['rel'])
        return rel


# 查询单条信息将该显示的信息显示
def demoproduct(request):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        userform = UserForm(post)
        if userform.is_valid():
            info = userform.cleaned_data['info']
            try:
                products = querybyinfo(graph, info)
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
                response['data'] = end
                response['msg'] = 'success'
                response['error_num'] = 0
            except Exception as e:
                response['msg'] = str(e)
                response['error_num'] = 404
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400


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
            c2 = "MATCH (n1:product)- [rel] -> (n2:`" + var['n2'] + "`) RETURN n1,type(rel),n2"
            product = graph.run(c2).to_data_frame()
            product = managedata(product)
            if product:
                product = product[0]['n1']
                product = querybyproduct(graph, product)
                for k in product:
                    products.append(k)
            # print(var['n2'], end)
            # c2 = "n1:product {name:\"" + product + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
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
    return end


# 按照所给条件筛选查询
def querybycondition(request):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        queryform = QueryForm(post)
        if queryform.is_valid():
            time = queryform.cleaned_data['time']  # 时间
            classification = queryform.cleaned_data['classification']  # 消费品类别
            productname = queryform.cleaned_data['productname']  # 名称
            hurt = queryform.cleaned_data['hurt']  # 伤害
            harm = queryform.cleaned_data['harm']  # 危害
            count_list1 = []
            count_list2 = []
            try:
                all = queryall(graph)
                # 依次判断是否输入
                if time:
                    # 时间形式为"2008.1.25-2009.2.5"
                    times = time.split("-")
                    start = times[0]
                    end = times[1]
                    start_time = start.split(".")
                    end_time = end.split(".")
                    times = [datetime.datetime(int(start_time[0]), int(start_time[1]), int(start_time[2])),
                             datetime.datetime(int(end_time[0]), int(end_time[1]), int(end_time[2]))]
                    # 循环判断是否符合要求
                    temp = [all[0]]
                    # 获取时间所代表的index 然后通过分割转换成datetime形式与时间进行比较
                    index = all[0].index('时间')
                    for var in all:
                        # 两种间隔符均考虑
                        if var != all[0]:
                            if "." in var[index]:
                                now_time = var[index].split(".")
                            else:
                                now_time = var[index].split("-")
                            now_time = datetime.datetime(int(now_time[0]), int(now_time[1]), int(now_time[2]))
                            if times[0] <= now_time <= times[1] or times[1] <= now_time <= times[0]:
                                temp.append(var)
                    all = temp

                if classification:
                    temp = [all[0]]
                    index = all[0].index('消费品-产品类别')
                    # 循环判断是否符合要求
                    for var in all:
                        if var != all[0]:
                            if var[index] == classification:
                                temp.append(var)
                    all = temp

                if productname:
                    temp = [all[0]]
                    index = all[0].index('消费品')
                    # 循环判断是否符合要求
                    for var in all:
                        if var != all[0]:
                            if var[index] == productname:
                                temp.append(var)
                    all = temp

                if hurt:
                    temp = [all[0]]
                    index = all[0].index('伤害严重性')
                    # 循环判断是否符合要求
                    for var in all:
                        if var != all[0]:
                            if var[index] == hurt:
                                temp.append(var)
                    all = temp

                if harm:
                    # 机械危害/电气危害
                    rel = all[0]
                    index = []
                    for r in rel:
                        if harm in r:
                            index.append(all[0].index(r))
                    # 循环判断是否符合要求
                    temp = [all[0]]
                    for i in index:
                        for var in all:
                            if var != all[0]:
                                if var[i]:
                                    temp.append(var)
                    all = temp
                # 删除空余的列
                end = []
                for i in all:
                    end.append([i[0]])
                hurt_index = all[0].index('伤害严重性')
                for i in range(1, len(all[0])):
                    Empty = True
                    for var in all:
                        if var[i] and var[i] != all[0][i]:
                            Empty = False
                    if not Empty:
                        for k in range(0, len(all)):
                            end[k].append(all[k][i])

                for i in range(1, len(all)):
                    if all[i][hurt_index] not in count_list1 and all[i][hurt_index]:
                        count_list1.append(all[i][hurt_index])
                        count_list2.append(1)
                    elif all[i][hurt_index] in count_list1 and all[i][hurt_index]:
                        p = count_list1.index(all[i][hurt_index])
                        count_list2[p] = count_list2[p] + 1

                # 对count进行排序操作
                for i in range(0, len(count_list2)):
                    for k in range(i, len(count_list2)):
                        if count_list2[i] < count_list2[k]:
                            temp = count_list2[i]
                            count_list2[i] = count_list2[k]
                            count_list2[k] = temp
                            temp = count_list1[i]
                            count_list1[i] = count_list1[k]
                            count_list1[k] = temp
                list1 = []
                list2 = []

                if len(count_list1) > 9:
                    for i in range(0, 10):
                        list1.append(count_list1[i])
                        list2.append(count_list2[i])
                    count = [list1, list2]
                else:
                    count = [count_list1, count_list2]
                response['data'] = end
                response['count'] = count
                response['msg'] = 'success'
                response['error_num'] = 0
            except Exception as e:
                response['msg'] = str(e)
                response['error_num'] = 404
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400


# 查询所有商品信息
def queryallproducts(request):
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        try:
            all = queryall(graph)
            time_index = all[0].index('时间')
            # 将事件根据时间排序调整
            for i in range(1, len(all)):
                for k in range(i, len(all)):
                    time_i = all[i][time_index]
                    time_k = all[k][time_index]
                    time_i = time_i.split("-")
                    time_k = time_k.split("-")
                    times = [datetime.datetime(int(time_i[0]), int(time_i[1]), int(time_i[2])),
                             datetime.datetime(int(time_k[0]), int(time_k[1]), int(time_k[2]))]
                    # 将时间转换后比较
                    if times[0] < times[1]:
                        temp = all[i]
                        all[i] = all[k]
                        all[k] = temp
            time = []  # 时间
            classification = []  # 消费品类别
            productname = []  # 名称
            hurt = []  # 伤害
            harm = []  # 危害
            count = []  # 伤害排名
            count_list1 = []
            count_list2 = []
            class_index = all[0].index('消费品-产品类别')
            name_index = all[0].index('消费品')
            hurt_index = all[0].index('伤害严重性')
            harm_index = []
            for var in all[0]:
                if "危害" in var:
                    harm_index.append(all[0].index(var))
            for i in range(1, len(all)):
                if all[i][time_index] not in time and all[i][time_index]:
                    time.append(all[i][time_index])
                if all[i][class_index] not in classification and all[i][class_index]:
                    classification.append(all[i][class_index])
                if all[i][name_index] not in productname and all[i][name_index]:
                    productname.append(all[i][name_index])
                if all[i][hurt_index] not in hurt and all[i][hurt_index]:
                    hurt.append(all[i][hurt_index])
                    count_list1.append(all[i][hurt_index])
                    count_list2.append(1)
                elif all[i][hurt_index] in count_list1 and all[i][hurt_index]:
                    p = count_list1.index(all[i][hurt_index])
                    count_list2[p] = count_list2[p] + 1
                for k in harm_index:
                    if all[i][k] not in harm and all[i][k] and all[i][k] != '有':
                        harm.append(all[i][k])
                    if all[i][k] == '有':
                        harm.append(all[0][k])

            # 对count进行排序操作
            for i in range(0, len(count_list2)):
                for k in range(i, len(count_list2)):
                    if count_list2[i] < count_list2[k]:
                        temp = count_list2[i]
                        count_list2[i] = count_list2[k]
                        count_list2[k] = temp
                        temp = count_list1[i]
                        count_list1[i] = count_list1[k]
                        count_list1[k] = temp
            list1 = []
            list2 = []
            if len(count_list1) > 9:
                for i in range(0, 10):
                    list1.append(count_list1[i])
                    list2.append(count_list2[i])
                count = [list1, list2]
            else:
                count = [count_list1, count_list2]
            response['data'] = all
            response['time'] = time
            response['classification'] = classification
            response['productname'] = productname
            response['hurt'] = hurt
            response['harm'] = harm
            response['count'] = count
            response['msg'] = 'success'
            response['error_num'] = 0
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 404
        return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400