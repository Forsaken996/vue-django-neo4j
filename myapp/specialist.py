from py2neo import Graph
import pandas as pd
from django.http import JsonResponse
from django.http.request import QueryDict
from django import forms
from py2neo import Graph, Node, Relationship, NodeMatcher
import datetime
import time


class QueryForm(forms.Form):
    page = forms.IntegerField(label="page", required=True)


class ChangeAss(forms.Form):
    eve = forms.CharField(label="eve", required=True)
    value = forms.CharField(label="value", required=True)


class DeleteAss(forms.Form):
    eve = forms.CharField(label="eve", required=True)


# 创建节点的同时并创建关系
def createnode(graph, label_name, property_value, rela_name, node_name1):
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


# 获取第page页的评估事件
def getevent(graph, page):
    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    end = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name'] and '评估' in row[0]['name']:
                end.append(row[0]['name'])
        nodes_num = []
        for p in end:
            nodes_num.append(int(p.replace('评估', '')))
        nodes_num.sort()
        nodes = []
        for p in nodes_num:
            nodes.append('评估'+str(p))
        # print(page)
        # print(nodes)
        # print(nodes[page-1])
        return nodes[page-1]
    else:
        return []


# 获取总数
def gettotal(graph):
    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
    return len(data.values)


def queryinfos(graph, eventnum):
    c = 'match (m:`事件`{name:"' + eventnum + '"})-[r1]-(y:`评估值`) return y'
    # print('c', c)
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = data[0]['y']['name']
        data = eval(data)
        temp = data

        c1 = 'match (m:`事件`{name:"' + eventnum + '"})-[r1]-(y:`评估项`) return y'
        data = graph.run(c1).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        tp = [['事件', eventnum]]
        values = data[0]['y']['name']
        # print(values)
        values = values[:-1].\
            split('^')
        for p in values:
            q = p.split('@')
            tp.append(q)
        infocolumns = []
        infos = []
        # print(tp)
        for p in tp:
            infocolumns.append(p[0])
            infos.append(p[1])
        temp.update({'infocolumns': infocolumns, 'info': infos})
        # print(temp)
        return temp


def Queryinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            queryform = QueryForm(post)
            if queryform.is_valid():
                page = queryform.cleaned_data['page']
                try:
                    # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
                    eve = getevent(graph, page)
                    if eve:
                        re_data = queryinfos(graph, eve)
                        total = gettotal(graph)
                        response['msg'] = 'success'
                        response['data'] = re_data['data']
                        response['features'] = re_data['features']
                        response['info'] = re_data['info']
                        response['infocolumns'] = re_data['infocolumns']
                        response['total'] = total
                    else:
                        response['msg'] = 'null'
                        response['data'] = []
                        response['features'] = []
                        response['info'] = []
                        response['infocolumns'] = []
                        response['total'] = 0
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
                    return JsonResponse(response)
                except Exception as e:
                    response['msg'] = str(e)
                    response['error_num'] = 404
                    return JsonResponse(response)
        else:
            response['msg'] = '参数错误'
            response['error_num'] = 0
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
        return JsonResponse(response)


# 变更评估项的值
def changeass(graph, eve, value):
    c1 = 'match (m:`事件`{name:"' + eve + '"})-[r]-(y:`评估值`) delete r,y'
    graph.run(c1)
    node = createnode(graph, '事件', eve, '', '')
    createnode(graph, '评估值', value, '评估值', node)


def Changeass(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            queryform = ChangeAss(post)
            if queryform.is_valid():
                value = queryform.cleaned_data['value']
                eve = queryform.cleaned_data['eve']
                try:
                    # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
                    changeass(graph, eve, value)
                    response['msg'] = 'success'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
                    return JsonResponse(response)
                except Exception as e:
                    response['msg'] = str(e)
                    response['error_num'] = 404
                    return JsonResponse(response)
        else:
            response['msg'] = '参数错误'
            response['error_num'] = 0
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
        return JsonResponse(response)


def deleteass(graph, graph_ass, eve):
    c1 = 'match (n:`事件`{name:"' + eve + '"})-[r]-(m) delete n,r'
    graph_ass.run(c1)
    graph.run(c1)


def Deleteass(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            queryform = DeleteAss(post)
            if queryform.is_valid():
                eve = queryform.cleaned_data['eve']
                try:
                    # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    graph_ass = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
                    deleteass(graph, graph_ass, eve)
                    response['msg'] = 'success'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
                    return JsonResponse(response)
                except Exception as e:
                    response['msg'] = str(e)
                    response['error_num'] = 404
                    return JsonResponse(response)
        else:
            response['msg'] = '参数错误'
            response['error_num'] = 0
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
        return JsonResponse(response)


if __name__ == "__main__":
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
    # value = str({"data": [["电热灼伤", "中风险", "51.61%"], ["过敏反应", "可接受风险", "48.39%"]],
    #  "features": ["低温表面", "其它真核细胞微生物危害", "接触不良", "高温液体", "锐利边缘", "热辐射危害", "高温气体", "铁芯发热", "尖角", "盐酸", "散热不良", "低温液体",
    #               "部件空隙或开口"]})
    # changeass(graph, '评估1', value)
    # print(getevent(graph,3))