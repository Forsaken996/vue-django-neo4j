from django.http import JsonResponse
from py2neo import Graph, Node, Relationship, NodeMatcher
from django.http.request import QueryDict
import pandas as pd
import time
from django import forms


class MarkRulesForm(forms.Form):
    sortindex = forms.IntegerField(label="sortindex", required=True)  # 分类 0消费品名称 1小零件 2伤害类型
    before = forms.CharField(label="before", required=True)  # 修改前的
    after = forms.CharField(label="after", required=True)  # 修改后的
    before_sort1 = forms.CharField(label="before_sort1", required=False)
    before_sort2 = forms.CharField(label="before_sort2", required=False)
    after_sort1 = forms.CharField(label="after_sort1", required=False)
    after_sort2 = forms.CharField(label="after_sort2", required=False)
    damagename = forms.CharField(label="damagename", required=False)


class InsertMarksForm(forms.Form):
    sortindex = forms.IntegerField(label="sortindex", required=True)  # 分类 0消费品名称 1小零件 2伤害类型
    name = forms.CharField(label="name", required=True)  # 添加项名称
    addition = forms.CharField(label="addition", required=False)  # 额外项


class DeleteMarksForm(forms.Form):
    sortindex = forms.IntegerField(label="sortindex", required=True)  # 分类 0消费品名称 1小零件 2伤害类型
    name = forms.CharField(label="name", required=True)  # 删除项名称
    problempart = forms.CharField(label="problempart", required=False)


class DamageKey(forms.Form):
    damage = forms.CharField(label="damage", required=True)
    key = forms.CharField(label="key", required=True)


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


# 获取标注分类 获取库中的所有标注分类
def getSorts(graph):
    c = "match (n) return labels(n)"
    data = graph.run(c).data()
    sorts = []
    for row in data:
        if row['labels(n)'][0] not in sorts:
            sorts.append(row['labels(n)'][0])
    return sorts


# 查询消费品名称所有标注信息
def queryproductmarkinfos(graph):
    c = "MATCH (n1:`消费品名称`)-[r:`二级消费品类型`]->(n2) RETURN n1,type(r),n2"
    data = graph.run(c).data()
    end = {}
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # print(data.values)
        for row in data.values:
            end.update({row[0]['name']: row[2]['name']})

    c = "MATCH (n1:`消费品名称`)-[r:`一级消费品类型`]->(n2) RETURN n1,type(r),n2"
    data = graph.run(c).data()
    ans = []
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # print(data.values)
        for row in data.values:
            if row[0]['name'] in end:
                p = {'title': '消费品名称', 'data': row[0]['name'], 'sort': [row[2]['name'], end[row[0]['name']]]}
            else:
                p = {'title': '消费品名称', 'data': row[0]['name'], 'sort': [row[2]['name'], '']}
            if p not in ans:
                ans.append(p)
        return ans


# 查询消费品名称所有标注信息
def querylittlepartmarkinfos(graph):
    c = "MATCH (n:`小零件`) RETURN n"
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        end = []
        # print(data.values)
        for row in data.values:
            p = {'title': '小零件', 'data': row[0]['name']}
            if p not in end:
                end.append(p)
        return end


# 查询输出伤害类型，严重程度
def querydamagetype(graph):
    c1 = "MATCH (n1:`伤害类型`)-[r]->(n2) RETURN n1,type(r),n2"
    data = graph.run(c1).data()
    if data:
        data = graph.run(c1).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # print(data)
        damages = []
        keys = {}
        for row in data.values:
            if row[1] == '严重程度':
                p = {'title': row[0]['name'], 'data': row[2]['name']}
                damages.append(p)
            elif row[1] == '关键词':
                if row[0]['name'] not in keys:
                    q = {row[0]['name']: [row[2]['name']]}
                    keys.update(q)
                else:
                    keys[row[0]['name']].append(row[2]['name'])
        for var in damages:
            if var['title'] in keys:
                q = {'key': keys[var['title']]}
                var.update(q)
            else:
                q = {'key': []}
                var.update(q)
        return damages
    #     end = []
    #     for row in data.values:
    #         p = {'title': row[0]['name'], 'data': row[2]['name']}
    #         end.append(p)
    # c2 = "MATCH (n1:`伤害类型`)-[r:`严重程度`]->(n2) RETURN n1,type(r),n2"


# 查询消费品问题部件
def queryproblempart(graph):
    c1 = "MATCH (n1:`消费品名称`)-[r:`消费品问题部件`]-(n2) RETURN n1,r,n2;"
    data = graph.run(c1).data()
    if data:
        data = graph.run(c1).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        end = []
        for row in data.values:
            p = {'title': row[0]['name'], 'data': row[2]['name']}
            end.append(p)
        return end


# 查询所有标注信息 返回{'标注标题':'xx', '数据':'xx'}形式
def queryallmarkinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        try:
            graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
            productname = queryproductmarkinfos(graph)
            littlepart = querylittlepartmarkinfos(graph)
            damagetype = querydamagetype(graph)
            problempart = queryproblempart(graph)
            response['problempart'] = problempart
            response['productname'] = productname
            response['littlepart'] = littlepart
            response['damagetype'] = damagetype
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 404
        return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
    endtime = time.perf_counter()
    print("The function run time is : %.03f seconds" % (
            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds


# 更改标注信息 sort = [0消费品名称, 1小零件, 2伤害等级]
def changemarkinfo(graph, sortindex, before, after, before_sort1='', after_sort1='', before_sort2='', after_sort2='', damagename=''):
    sort = ['消费品名称', '小零件', '伤害类型']
    if sortindex == 1 or sortindex == 3:
        c = "MATCH (n:`" + sort[sortindex] + "`{name:\"" + before + "\"}) SET n.name = \"" + after + "\""
        graph.run(c)
        print("已将->", sort[sortindex], '下的->', before, '修改为->', after)
    elif sortindex == 0:
        if before and after:
            c = "MATCH (n:`" + sort[sortindex] + "`{name:\"" + before + "\"}) SET n.name = \"" + after + "\""
            # print(c)
            graph.run(c)
        if before_sort1 and after_sort1 and before_sort1 != after_sort1:
            c1 = "MATCH (n1:`" + sort[sortindex] + "`{name:\"" + after + "\"})-[r:`一级消费品类型`]-(n2) DELETE r"
            graph.run(c1)
            # print(c1)
            node = createnode(graph, '消费品名称', str(after), '', '')
            createnode(graph, '一级消费品类型', str(after_sort1), '一级消费品类型', node)
        if before_sort2 != after_sort2:
            c1 = "MATCH (n1:`" + sort[sortindex] + "`{name:\"" + after + "\"})-[r:`二级消费品类型`]-(n2) DELETE r"
            graph.run(c1)
            # print(c1)
            node = createnode(graph, '消费品名称', str(after), '', '')
            createnode(graph, '二级消费品类型', str(after_sort2), '二级消费品类型', node)
    elif sortindex == 2 and damagename:
        c = "MATCH (n1:`" + sort[sortindex] + "`{name:\"" + damagename + "\"})-[r:`严重程度`]-(n2) DELETE r"
        graph.run(c)
        node = createnode(graph, '伤害类型', str(damagename), '', '')
        createnode(graph, '严重程度', str(after), '严重程度', node)


def changemarkinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = MarkRulesForm(post)
            if markform.is_valid():
                sortindex = markform.cleaned_data['sortindex']  # 分类 0消费品名称 1小零件 2伤害类型
                before = markform.cleaned_data['before']  # 修改前的数据
                after = markform.cleaned_data['after']  # 修改后的数据
                before_sort1 = markform.cleaned_data['before_sort1']  # 修改前的分类
                before_sort2 = markform.cleaned_data['before_sort2']
                after_sort1 = markform.cleaned_data['after_sort1']  # 修改后的分类
                after_sort2 = markform.cleaned_data['after_sort2']
                damagename = markform.cleaned_data['damagename']  # 伤害
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
                    changemarkinfo(graph, sortindex, before, after, before_sort1, after_sort1, before_sort2, after_sort2, damagename)
                    response['msg'] = 'success'
                    response['error_num'] = 0
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
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


# 插入消费品名称标注信息
def insertproductmarkinfo(graph, name, sort):
    node = createnode(graph, '消费品名称', str(name), '', '')
    createnode(graph, '消费品类型', str(sort), '消费品分类', node)
    print("已创建消费品:", name, "该消费品分类属于:", sort)


# 插入小零件标注信息
def insertlittlepartmarkinfo(graph, name):
    node = createnode(graph, '小零件', str(name), '', '')
    print("已创建小零件:", name)


# 插入危害等级标注信息
def insertdamagetypemarkinfo(graph, name, damage):
    node = createnode(graph, '伤害类型', str(name), '', '')
    createnode(graph, '严重程度', str(damage), '严重程度', node)
    print("已创建伤害类型:", name, "严重程度为:", damage)


# 插入消费品问题部件
def insertproblempart(graph, name, addition):
    node = createnode(graph, '消费品名称', str(name), '', '')
    createnode(graph, '消费品问题部件', str(addition), '消费品问题部件', node)
    print("已创建消费品:", name, "消费品问题部件为:", addition)


def insertmarkinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = InsertMarksForm(post)
            if markform.is_valid():
                sortindex = markform.cleaned_data['sortindex']  # 分类 0消费品名称 1小零件 2伤害类型
                names = markform.cleaned_data['name']  # 添加项名称
                addition = markform.cleaned_data['addition']  # 额外项
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
                    response['msg'] = 'success'
                    if sortindex == 0:
                        insertproductmarkinfo(graph, names, addition)
                    elif sortindex == 1:
                        insertlittlepartmarkinfo(graph, names)
                    elif sortindex == 2:
                        insertdamagetypemarkinfo(graph, names, addition)
                    elif sortindex == 3:
                        insertproblempart(graph, names, addition)
                    else:
                        response['msg'] = 'false'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
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


def deletemark(graph, sortindex, name, problempart=''):
    sort = ['消费品名称', '小零件', '伤害类型', '消费品问题部件']
    if sortindex == 1:
        c = "MATCH (n:`" + sort[sortindex] + "`{name:\"" + name + "\"}) DELETE n"
        # print(c)
        graph.run(c)
    elif sortindex == 0 or sortindex == 2:
        c1 = "MATCH (n1:`" + sort[sortindex] + "`{name:\"" + name + "\"})-[r]-(n2) DELETE n1,r;"
        # print(c1)
        graph.run(c1)
    elif sortindex == 3 and problempart:
        c = "MATCH (n1:`消费品名称`{name:\"" + name + "\"})-[r:`消费品问题部件`]-(n2:`消费品问题部件`{name:\"" + problempart + "\"}) DELETE r;"
        # print(c)
        graph.run(c)


def deletemarks(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = DeleteMarksForm(post)
            if markform.is_valid():
                sortindex = markform.cleaned_data['sortindex']  # 分类 0消费品名称 1小零件 2伤害类型
                names = markform.cleaned_data['name']  # 删除项名称
                problempart = markform.cleaned_data['problempart'] #  问题部件
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
                    deletemark(graph, sortindex, names, problempart)
                    response['msg'] = 'success'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
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


# 插入伤害对应的关键字
def insertdamagekey(graph, damage, key):
    node = createnode(graph, '伤害类型', damage, '', '')
    createnode(graph, "关键词", key, '关键词', node)


# 删除对应伤害的关键字
def deletedamagekey(graph, damage, key):
    c = "MATCH (n1:`伤害类型`{name:\"" + damage + "\"})-[r:`关键词`]-(n2:`关键词`{name:\"" + key + "\"}) DELETE r,n2"
    graph.run(c)
    # print(c)


def InsertDamageKey(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = DamageKey(post)
            if markform.is_valid():
                damage = markform.cleaned_data['damage']  # 伤害类型
                key = markform.cleaned_data['key']  # 关键词
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
                    insertdamagekey(graph, damage, key)
                    response['msg'] = 'success'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
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


def DeleteDamageKey(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = DamageKey(post)
            if markform.is_valid():
                damage = markform.cleaned_data['damage']  # 伤害类型
                key = markform.cleaned_data['key']  # 关键词
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
                    deletedamagekey(graph, damage, key)
                    response['msg'] = 'success'
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
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


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
    # print(queryproductmarkinfos(graph))
    # changemarkinfo(graph, 0, '台扇', '大台扇')
    # print(querydamagetype(graph))
    # sorts = getSorts(graph)
    # print(sorts)
    # print(querylittlepartmarkinfos(graph))
    # print(changemarkinfo(graph, 0, '儿童平衡', '儿童平衡车', '其他', '儿童衣服'))
    # print(changemarkinfo(graph, 2, '4', '1', '', '', '全身中毒'))
    # print(changemarkinfo(graph, 1, '笔帽', '笔尖', '', '', ''))
    deletemark(graph, 3, '铅笔', '笔尖')
    # deletedamagekey(graph, '划伤', '划痕')
