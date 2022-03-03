from py2neo import Graph
import pandas as pd
from django.http import JsonResponse
from django.http.request import QueryDict
from django import forms
import datetime
import time


class CountForm(forms.Form):
    time = forms.CharField(label='time', required=False)  # 时间
    class1 = forms.CharField(label='class1', required=False)  # 消费品类别1
    class2 = forms.CharField(label='class2', required=False)  # 消费品类别2
    area = forms.CharField(label='area', required=False)  # 名称
    hurt = forms.CharField(label='hurt', required=False)  # 伤害
    harm = forms.CharField(label='harm', required=False)  # 危害


# 统计某种情况下造成的伤害前10
def countbycondition(graph, nowtime, class1, class2, area, harm):
    c = "MATCH (n1:`事件`)-[rel]->(n:`伤害类型`) RETURN n,count(*)"
    class1_tp = class1
    class2_tp = class2
    if class2 == '其他':
        class2_tp = '-1'
    if nowtime:
        # 时间形式为"2008.1.25-2009.2.5"
        times = nowtime.split("-")
        start = times[0]
        end = times[1]
        start = start.replace('.', '-')
        end = end.replace('.', '-')
        c = "MATCH (n1:`事件`)-[rel2]->(n2:`日期`) WHERE datetime(n2.name) > datetime(\"" + start + \
            "\") AND  datetime(n2.name) < datetime(\"" + end + "\") WITH n1,rel2,n2 " + c
    if class1_tp and not class2_tp:
        c = "MATCH (n1:`事件`)-[rel3]->(n3:`消费品一级类别`{name:\"" + class1_tp + "\"})" \
                                                                               " WITH n1,rel3,n3 " + c
    if area:
        c = "MATCH (n1:`事件`)-[rel4]->(n4:`区域`{name:\"" + area + "\"})" \
                                                                " WITH n1,rel4,n4 " + c

    if class2_tp:
        c = "MATCH (n1:`事件`)-[rel5]->(n5:`消费品二级类别`{name:\"" + class2_tp + "\"})" \
                                                                       " WITH n1,rel5,n5 " + c
    if harm:
        harm0 = ['物理危害', '化学危害', '生物危害']
        harm1 = ['机械危害', '爆炸危害', '噪声危害', '电气危害', '高/低温物质危害', '辐射危害', '警示标识缺失', '无机毒物危害', '有机毒物', '致病微生物危害', '致病生物危害']
        harm2 = ['形状和表面性能危害', '潜在能量危害', '动能危害', '气相爆炸危害', '液相爆炸危害', '固相爆炸危害', '稳定性噪音危害', '变动性噪音危害', '脉冲性噪音危害', '触电危害', '电气爆炸', '高温物质危害', '低温物质危害', '热辐射危害', '射线辐射危害', '电磁辐射危害', '警示标识缺失', '有毒气体危害', '有毒重金属及其化合物危害', '有毒酸碱类危害', '无机氰化物危害', '有毒荃类化合物', '有毒芳香稠环类化合物', '有毒杂环类化合物', '有毒有机氯化物', '原核细胞微生物危害', '真核细胞微生物危害', '原生微生物危害', '寄生虫危害']
        harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
                 '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
                 '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面',
                 '高温液体',
                 '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气',
                 '臭氧',
                 '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸',
                 '盐酸',
                 '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
                 'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
                 '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
                 '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']
        if harm in harm3:
            c = "MATCH (n1:`事件`)-[rel6]->(n6:`消费品三级危害类型`{name:\"" + harm + "\"})" \
                                                                       " WITH n1,rel6,n6 " + c
        elif harm in harm2:
            c = "MATCH (n6:`消费品三级危害类型`)-[rel7:`消费品二级危害类型`]->(n7:`消费品二级危害类型`{name:\"" + harm + "\"})" \
                                                                       " WITH n6,rel7,n7 MATCH (n1:`事件`)-[rel6]->(n6:`消费品三级危害类型`) WITH n1,rel6,n6 " + c

        elif harm in harm1:
            c = "MATCH (n7:`消费品二级危害类型`)-[rel8:`消费品一级危害类型`]->(n8:`消费品一级危害类型`{name:\"" + harm + "\"}) WITH n7,rel8,n8 MATCH (n6:`消费品三级危害类型`)-[rel7:`消费品二级危害类型`]->(n7:`消费品二级危害类型`) WITH n6,rel7,n7 MATCH (n1:`事件`)-[rel6]->(n6:`消费品三级危害类型`) WITH n1,rel6,n6 " + c

        elif harm in harm0:
            c = "MATCH (n8:`消费品一级危害类型`)-[rel9:`消费品危害类型`]->(n9:`消费品危害类型`{name:\"" + harm + "\"}) WITH n8,rel9,n9 MATCH (n7:`消费品二级危害类型`)-[rel8:`消费品一级危害类型`]->(n8:`消费品一级危害类型`) WITH n7,rel8,n8 MATCH (n6:`消费品三级危害类型`)-[rel7:`消费品二级危害类型`]->(n7:`消费品二级危害类型`) WITH n6,rel7,n7 MATCH (n1:`事件`)-[rel6]->(n6:`消费品三级危害类型`) WITH n1,rel6,n6 " + c
    # print(c)
    count_name = []
    count_value = []
    countdraw_name = []
    countdraw_value = []
    data = graph.run(c).data()
    # print(data)
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # 最终把数据转化为json格式
        data = data.to_dict('records')
        for row in data:
            # print(row)
            # if row['n']['name'] != '-1' and row['n']['name'] != '其他':
            if row['n']['name'] != '-1':
                countdraw_name.append(row['n']['name'])
                countdraw_value.append(row['count(*)'])
            if row['n']['name'] == '-1':
                count_name.append('其他')
            else:
                count_name.append(row['n']['name'])
            count_value.append(row['count(*)'])

        for i in range(0, len(countdraw_name)):
            for k in range(i + 1, len(countdraw_name)):
                if countdraw_value[i] < countdraw_value[k]:
                    temp = countdraw_value[i]
                    countdraw_value[i] = countdraw_value[k]
                    countdraw_value[k] = temp
                    temp = countdraw_name[i]
                    countdraw_name[i] = countdraw_name[k]
                    countdraw_name[k] = temp

        for i in range(0, len(count_name)):
            for k in range(i + 1, len(count_name)):
                if count_value[i] < count_value[k]:
                    temp = count_value[i]
                    count_value[i] = count_value[k]
                    count_value[k] = temp
                    temp = count_name[i]
                    count_name[i] = count_name[k]
                    count_name[k] = temp

        # print(count_name, count_value)
        end = {'count_name': count_name, 'count_value': count_value, 'countdraw_name': countdraw_name[0:10],
               'countdraw_value': countdraw_value[0:10]}
        return end


def Countbycondition(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        nowtime = ''
        class1 = ''
        class2 = ''
        area = ''
        harm = ''
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            queryform = CountForm(post)
            if queryform.is_valid():
                nowtime = queryform.cleaned_data['time']  # 时间
                class1 = queryform.cleaned_data['class1']  # 消费品类别
                class2 = queryform.cleaned_data['class2']  # 消费品类别
                area = queryform.cleaned_data['area']  # 名称
                harm = queryform.cleaned_data['harm']  # 危害
        try:
            end = countbycondition(graph, nowtime, class1, class2, area, harm)
            response['count_name'] = end['count_name']
            response['count_value'] = end['count_value']
            response['countdraw_name'] = end['countdraw_name']
            response['countdraw_value'] = end['countdraw_value']
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
        response['msg'] = "请求错误"
        response['error_num'] = 400


# 统计造成某伤害最多的消费品
def countproducthurtmost(graph, hurt):
    c = "MATCH (n1:`事件`)-[rel]->(n2:`伤害类型`{name:\"" \
        + hurt + "\"}) WITH n1,rel,n2 MATCH (n1:`事件`)-[rel1]->(n:`消费品一级类别`) RETURN n,count(*)"
    # print(c)
    count_name = []
    count_value = []
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # 最终把数据转化为json格式
        nodes = data.to_dict('records')
        for row in nodes:
            if row['n']['name']:
            # if row['n']['name'] != '其他':
                count_name.append(row['n']['name'])
                count_value.append(row['count(*)'])
        for i in range(0, len(count_name)):
            for k in range(i + 1, len(count_name)):
                if count_value[i] < count_value[k]:
                    temp = count_value[i]
                    count_value[i] = count_value[k]
                    count_value[k] = temp
                    temp = count_name[i]
                    count_name[i] = count_name[k]
                    count_name[k] = temp
        # print(count_name, count_value)
        end = {'count_name': count_name, 'count_value': count_value, 'countdraw_name': count_name[0:10],
               'countdraw_value': count_value[0:10]}
        return end


def Countproducthurtmost(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        queryform = CountForm(post)
        if queryform.is_valid():
            hurt = queryform.cleaned_data['hurt']  # 危害
            try:
                end = countproducthurtmost(graph, hurt)
                response['count_name'] = end['count_name']
                response['count_value'] = end['count_value']
                response['countdraw_name'] = end['countdraw_name']
                response['countdraw_value'] = end['countdraw_value']
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
        response['msg'] = "请求错误"
        response['error_num'] = 400


# 统计伤害主要分布的区域
def counthurtarea(graph, hurt):
    c = "MATCH (n1:`事件`)-[rel]->(n2:`伤害类型`{name:\"" \
        + hurt + "\"}) WITH n1,rel,n2 MATCH (n1:`事件`)-[rel1]->(n:`区域`) RETURN n,count(*)"
    # print(c)
    count_name = []
    count_value = []
    data = graph.run(c).data()
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # 最终把数据转化为json格式
        nodes = data.to_dict('records')
        for row in nodes:
            if row['n']['name']:
                # if row['n']['name'] != '其他':
                if row['n']['name'] == '-1':
                    count_name.append('其他')
                else:
                    count_name.append(row['n']['name'])
                count_value.append(row['count(*)'])
        for i in range(0, len(count_name)):
            for k in range(i + 1, len(count_name)):
                if count_value[i] < count_value[k]:
                    temp = count_value[i]
                    count_value[i] = count_value[k]
                    count_value[k] = temp
                    temp = count_name[i]
                    count_name[i] = count_name[k]
                    count_name[k] = temp
        # print(count_name, count_value)
        end = {'count_name': count_name, 'count_value': count_value, 'countdraw_name': count_name[0:10],
               'countdraw_value': count_value[0:10]}
        return end


def Counthurtarea(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        queryform = CountForm(post)
        if queryform.is_valid():
            hurt = queryform.cleaned_data['hurt']  # 危害
            try:
                end = counthurtarea(graph, hurt)
                response['count_name'] = end['count_name']
                response['count_value'] = end['count_value']
                response['countdraw_name'] = end['countdraw_name']
                response['countdraw_value'] = end['countdraw_value']
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
        response['msg'] = "请求错误"
        response['error_num'] = 400


def getcountops(graph):
    # 获取地区
    global sort
    area = []
    c1 = 'match (n:`区域`) return n;'
    data = graph.run(c1).data()
    if data:
        data = graph.run(c1).to_data_frame()
        for row in data.values:
            if row[0]['name'] != '-1':
                # print(row)
                area.append(row[0]['name'])
    # print(area)

    # 获取产品大类 讲儿童用品前置
    # sort = ['儿童用品']

    # c2 = 'match (n:`消费品一级类别`) return n;'
    # data = graph.run(c2).data()
    # if data:
    #     data = graph.run(c2).to_data_frame()
    #     for row in data.values:
    #         if row[0]['name'] != '其他' and row[0]['name'] != '儿童用品':
    #             print(row)
    #             sort.append(row[0]['name'])
    # sort.append('其他')
    # print(sort)
    c2_1 = 'match (n:`事件`)-[r2:`消费品二级类别`]-(m2:`消费品二级类别`) with n,r2,m2 match(n:`事件`)-[r1:`消费品一级类别`]-(m1:`消费品一级类别`) return m1,m2'
    s = {}
    data = graph.run(c2_1).data()
    if data:
        data = graph.run(c2_1).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        # 最终把数据转化为json格式
        data = data.to_dict('records')
        for row in data:
            # print(row)
            if row['m1']['name'] in s:
                if row['m2']['name'] not in s[row['m1']['name']]:
                    s[row['m1']['name']].append(row['m2']['name'])
            elif row['m1']['name'] not in s:
                s.update({row['m1']['name']: [row['m2']['name']]})
        # print(s)
        # print(data)
        sort = []
        if '儿童用品' in s:
            s1 = {'value': '儿童用品', 'label': '儿童用品', 'children': []}
            for p in s['儿童用品']:
                if p == '-1':
                    s2 = {'value': '其他', 'label': '其他'}
                    s1['children'].append(s2)
                else:
                    s2 = {'value': p, 'label': p}
                    s1['children'].append(s2)
            sort.append(s1)

        for p in s:
            if p != '儿童用品' and p != '其他':
                if s[p] == ['-1']:
                    s1 = {'value': p, 'label': p}
                    sort.append(s1)
                else:
                    s1 = {'value': p, 'label': p, 'children': []}
                    for q in s[p]:
                        if s[p] == ['-1']:
                            s2 = {'value': '其他', 'label': '其他'}
                            s1['children'].append(s2)
                        else:
                            s2 = {'value': q, 'label': q}
                            s1['children'].append(s2)
                    sort.append(s1)

        if '其他' in s:
            s1 = {'value': '其他', 'label': '其他'}
            sort.append(s1)
        # print(sort)

    # 获取伤害
    hurt = []
    c3 = "MATCH (n1:`事件`)-[rel]->(n2:`伤害类型`) WITH n1,rel,n2 MATCH (n1:`事件`)-[rel1]->(n:`消费品一级类别`) RETURN n,n2,count(*)"
    data = graph.run(c3).data()
    if data:
        data = graph.run(c3).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        for row in data.values:
            if row[1]['name'] != '-1' and row[1]['name'] != '其他' and row[1]['name'] not in hurt:
                # print(row)
                hurt.append(row[1]['name'])
    # print(hurt)

    # 获取危害源
    harm3 = []
    harm2 = []
    harm1 = []
    harm0 = []
    c4 = 'match (n1:`事件`)-[r]-(n2:`消费品三级危害类型`) return n2;'
    data = graph.run(c4).data()
    if data:
        data = graph.run(c4).to_data_frame()
        for row in data.values:
            if row[0]['name'] not in harm3:
                harm3.append(row[0]['name'])
    harm1_0 = {'机械危害': '物理危害', '爆炸危害': '物理危害', '噪声危害': '物理危害', '电气危害': '物理危害', '高/低温物质危害': '物理危害', '辐射危害': '物理危害',
               '警示标识缺失': '物理危害', '无机毒物危害': '化学危害', '有机毒物': '化学危害', '致病微生物危害': '生物危害', '致病生物危害': '生物危害'}
    harm2_1 = {'形状和表面性能危害': '机械危害', '潜在能量危害': '机械危害', '动能危害': '机械危害', '气相爆炸危害': '爆炸危害', '液相爆炸危害': '爆炸危害',
               '固相爆炸危害': '爆炸危害', '稳定性噪音危害': '噪声危害', '变动性噪音危害': '噪声危害', '脉冲性噪音危害': '噪声危害', '触电危害': '电气危害',
               '电气爆炸': '电气危害', '高温物质危害': '高/低温物质危害', '低温物质危害': '高/低温物质危害', '热辐射危害': '辐射危害', '射线辐射危害': '辐射危害',
               '电磁辐射危害': '辐射危害', '警示标识缺失': '警示标识缺失', '有毒气体危害': '无机毒物危害', '有毒重金属及其化合物危害': '无机毒物危害', '有毒酸碱类危害': '无机毒物危害',
               '无机氰化物危害': '无机毒物危害', '有毒荃类化合物': '有机毒物', '有毒芳香稠环类化合物': '有机毒物', '有毒杂环类化合物': '有机毒物', '有毒有机氯化物': '有机毒物',
               '原核细胞微生物危害': '致病微生物危害', '真核细胞微生物危害': '致病微生物危害', '原生微生物危害': '致病微生物危害', '寄生虫危害': '致病生物危害'}
    harm3_2 = {'绳索及类似物': '形状和表面性能危害', '不透气': '形状和表面性能危害', '填充物': '形状和表面性能危害', '小零件': '形状和表面性能危害', '尖角': '形状和表面性能危害',
               '锐利边缘': '形状和表面性能危害', '光滑表面': '形状和表面性能危害', '粗糙表面': '形状和表面性能危害', '部件空隙或开口': '形状和表面性能危害', '机械稳定性': '潜在能量危害',
               '机械强度': '潜在能量危害', '弹性组件失控': '潜在能量危害', '压力空间失控': '潜在能量危害', '移动状态撞击': '动能危害', '旋转部件牵扯': '动能危害',
               '飞行物体撞击': '动能危害', '移动部件挤压': '动能危害', '爆炸性气体': '气相爆炸危害', '爆炸性粉尘': '气相爆炸危害', '爆炸性喷雾': '气相爆炸危害',
               '聚合爆炸': '液相爆炸危害', '蒸发爆炸': '液相爆炸危害', '液体混合爆炸': '液相爆炸危害', '爆炸性化合物': '固相爆炸危害', '固体爆炸性物质': '固相爆炸危害',
               '稳定性噪音危害': '稳定性噪音危害', '变动性噪音危害': '变动性噪音危害', '脉冲性噪音危害': '脉冲性噪音危害', '高/低压': '触电危害', '过热': '电气爆炸',
               '漏电': '触电危害', '短路': '电气爆炸', '接触不良': '电气爆炸', '铁芯发热': '电气爆炸', '散热不良': '电气爆炸', '明火': '高温物质危害',
               '高温表面': '高温物质危害', '高温液体': '高温物质危害', '高温气体': '高温物质危害', '低温表面': '低温物质危害', '低温液体': '低温物质危害',
               '低温气体': '低温物质危害', '热辐射危害': '热辐射危害', '激光辐射': '射线辐射危害', '紫外线辐射': '射线辐射危害', 'X光线辐射': '射线辐射危害',
               '高频电磁辐射': '电磁辐射危害', '低频电磁辐射': '电磁辐射危害', '警示标识缺失': '警示标识缺失', '一氧化碳': '有毒气体危害', '一氧化氮': '有毒气体危害',
               '氯气': '有毒气体危害', '臭氧': '有毒气体危害', '氯化氢': '无机氰化物危害', '硫化氢': '有毒气体危害', '其它': '寄生虫危害',
               '砷及其化合物': '有毒重金属及其化合物危害', '镉及其化合物': '有毒重金属及其化合物危害', '铬及其化合物': '有毒重金属及其化合物危害', '铜及其化合物': '有毒重金属及其化合物危害',
               '汞及其化合物': '有毒重金属及其化合物危害', '镍及其化合物': '有毒重金属及其化合物危害', '铅及其化合物': '有毒重金属及其化合物危害', '硫酸': '有毒酸碱类危害',
               '盐酸': '有毒酸碱类危害', '氢氧化钠': '有毒酸碱类危害', '氢氰酸': '无机氰化物危害', '氰化钾': '无机氰化物危害', '甲醛': '有毒荃类化合物', '乙醛': '有毒荃类化合物',
               '丙烯醛': '有毒荃类化合物', '蒽类化合物': '有毒芳香稠环类化合物', '菲类化合物': '有毒芳香稠环类化合物', '芘类化合物': '有毒芳香稠环类化合物',
               'N-杂环化合物': '有毒杂环类化合物', 'S-杂环化合物': '有毒杂环类化合物', 'O-杂环化合物': '有毒杂环类化合物', '有机氟化物': '有毒有机氯化物',
               '有机氯化物': '有毒有机氯化物', '有机溴化物': '有毒有机氯化物', '大肠杆菌': '原核细胞微生物危害', '沙门氏菌': '原核细胞微生物危害', '副溶血性弧菌': '原核细胞微生物危害',
               '金黄色葡萄球菌': '原核细胞微生物危害', '腊样芽孢肝菌': '原核细胞微生物危害', '皮肤癣真菌': '真核细胞微生物危害', '着色真菌': '真核细胞微生物危害',
               '孢子丝菌': '真核细胞微生物危害', '新生隐球菌': '真核细胞微生物危害', '假丝酵母菌': '真核细胞微生物危害', '曲霉': '真核细胞微生物危害', '毛霉': '真核细胞微生物危害',
               '卡氏肺孢菌': '真核细胞微生物危害', '甲肝病毒': '原生微生物危害', '甲型流感病毒': '原生微生物危害', '轮状病毒': '原生微生物危害', '禽流感病毒': '原生微生物危害',
               '尘螨': '寄生虫危害', '蛔虫卵': '寄生虫危害', '绦虫卵': '寄生虫危害'}
    for i in harm3:
        h3 = i
        if harm3_2[h3] not in harm2:
            harm2.append(harm3_2[h3])
        h2 = harm3_2[h3]

        if harm2_1[h2] not in harm1:
            harm1.append(harm2_1[h2])
        h1 = harm2_1[h2]

        if harm1_0[h1] not in harm0:
            harm0.append(harm1_0[h1])
    p = []
    for q0 in harm0:
        h0 = {'value': q0, 'label': q0, 'children': []}
        for q1 in harm1:
            if harm1_0[q1] == q0:
                h1 = {'value': q1, 'label': q1, 'children': []}
                for q2 in harm2:
                    if harm2_1[q2] == q1:
                        h2 = {'value': q2, 'label': q2, 'children': []}
                        for q3 in harm3:
                            if harm3_2[q3] == q2:
                                h3 = {'value': q3, 'label': q3}
                                if h3 not in h2['children']:
                                    h2['children'].append(h3)
                        if h2 not in h1['children']:
                            h1['children'].append(h2)
                if h1 not in h0['children']:
                    h0['children'].append(h1)
        # print(h0)
        p.append(h0)
    ops = {'area': area, 'sort': sort, 'hurt': hurt, 'harm': p}
    return ops


def Getcountops(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        try:
            graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
            ops = getcountops(graph)
            # print(end)
            response['msg'] = 'success'
            response['area'] = ops['area']
            response['sort'] = ops['sort']
            response['hurt'] = ops['hurt']
            response['harm'] = ops['harm']
            endtime = time.perf_counter()
            print("The function run time is : %.03f seconds" % (
                    endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
            return JsonResponse(response)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 404
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
        return JsonResponse(response)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    # queryinfos(graph, getevent(graph, 281, 290))
    # getops(graph)
    # print(getevent(graph, 280, 290))
    # querybycondition(graph, '', '', '', '', '')
    # print(querymostreason(graph, '烧伤'))
    # countproducthurtmost(graph, '烧伤')
    # print(countbycondition(graph, '', '', '', '', '物理危害'))
    # getcountops(graph)
