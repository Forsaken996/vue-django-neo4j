# coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse
from py2neo import Graph, Node, Relationship, NodeMatcher
from django.http.request import QueryDict
from .models import User
from django import forms
from django.http import HttpResponse
graph = Graph("http://localhost:7474/", user="neo4j", password='123456', name='usersinfo')


class UserForm(forms.Form):
    username = forms.CharField(label='username', required=False)
    password = forms.CharField(label='password', required=False)


def wirte_info(code=404, data="fail", info="未知错误"):
    res = {"code": code, "data": data, "info": info}
    return res


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


def reg(request):
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        userform = UserForm(post)
        # print("debug:", post)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            # print("debug.username:", username)
            # print("debug.password:", password)
            # 查询数据库中是否已有该用户
            Exist = graph.run("MATCH (n1:username {name:\"" + username + "\"})- [rel] -> (n2) RETURN n1,rel,n2").data()
            if Exist:
                res = wirte_info(403, "fail", "用户名已存在")
                return JsonResponse(res)
            else:
                node = createnode("username", username, "", "")
                createnode("password", password, "密码", node)
                res = wirte_info(200, "success", "注册成功")
                return JsonResponse(res)
        else:
            # print(request.POST)
            # print(userform.errors)
            res = wirte_info(400, "fail", "请求错误")
            return JsonResponse(res)
    res = wirte_info(404, "fail", "未知错误")
    return JsonResponse(res)


def login(request):
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        userform = UserForm(post)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']

            # 查询数据库中是否已有该用户
            Exist = graph.run("MATCH (n1:username {name:\"" + username + "\"})- [rel] -> (n2:password {name:\""
                              + password + "\"}) RETURN n1,rel,n2").data()
            if Exist:
                res = wirte_info(200, "success", "登录成功")
                return JsonResponse(res)
            else:
                UserExist = graph.run("MATCH (n1:username {name:\""
                                      + username + "\"})- [rel] -> (n2) RETURN n1,rel,n2").data()
                if UserExist:
                    res = wirte_info(403, "fail", "密码错误！")
                    return JsonResponse(res)
                else:
                    res = wirte_info(403, "fail", "该用户不存在！")
                    return JsonResponse(res)
    else:
        res = wirte_info(400, "fail", "请求错误！")
        return JsonResponse(res)
    res = wirte_info(404, "fail", "未知错误")
    return JsonResponse(res)


