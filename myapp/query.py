from py2neo import Graph
import pandas as pd
from django.http import JsonResponse
from django.http.request import QueryDict
from django import forms
import datetime
import time


class QueryForm(forms.Form):
    time = forms.CharField(label='time', required=False)  # 时间
    class1 = forms.CharField(label='class1', required=False)  # 消费品类别1
    class2 = forms.CharField(label='class2', required=False)  # 消费品类别2
    area = forms.CharField(label='area', required=False)  # 名称
    hurt = forms.CharField(label='hurt', required=False)  # 伤害
    harm = forms.CharField(label='harm', required=False)  # 危害
    product = forms.CharField(label='product', required=False)  # 产品
    start = forms.IntegerField(label='start', required=True)
    to = forms.IntegerField(label='to', required=True)


class QueryInfosForm(forms.Form):
    start = forms.IntegerField(label='start', required=True)
    to = forms.IntegerField(label='to', required=False)


class CountForm(forms.Form):
    time = forms.CharField(label='time', required=False)  # 时间
    classification = forms.CharField(label='classification', required=False)  # 消费品类别
    area = forms.CharField(label='area', required=False)  # 名称
    hurt = forms.CharField(label='hurt', required=False)  # 伤害
    harm = forms.CharField(label='harm', required=False)  # 危害


class QueryMain(forms.Form):
    proname = forms.CharField(label='proname', required=True)


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


# 列出所有信息条目
def queryall(graph):
    # c = "MATCH (n1)- [rel] -> (n2) RETURN n1,type(rel),n2"
    # answer = graph.run(c).to_data_frame()
    # answer = managedata(answer)
    # print(answer)
    i = 1
    columns = ['事件号']
    lists = []
    while i:
        c = "MATCH (n1{name:\"事件" + str(i) + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c).data()
        if answer:
            answer = graph.run(c).to_data_frame()
            # print(answer)
            answer = managedata(answer)
            for var in answer:
                if var['rel'] not in columns:
                    columns.append(var['rel'])
            lists.append(answer)
            i = i + 1
        else:
            break
    demo = [columns]
    count = 0
    # print(columns)
    for var in lists:
        count += 1
        # print("进度:", count, "%", len(lists))
        eve = []
        for k in columns:
            eve.append('')
        if var:
            # 事件号n
            eve[0] = var[0]['n1']
            for k in var:
                index = columns.index(k['rel'])
                if k['rel'] == '伤害类型' or k['rel'] == '消费品三级危害类型':
                    # print(eve[index])
                    # print(k['n2'])
                    if eve[index]:
                        eve[index] = eve[index] + ',' + k['n2']
                    else:
                        eve[index] = k['n2']
                else:
                    eve[index] = k['n2']
            # print(eve)
            demo.append(eve)
    return demo


# 查询所有商品信息
def queryallproducts(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        try:
            all = queryall(graph)
            # print(all)
            classification = []  # 消费品类别
            productname = []  # 名称
            hurt = []  # 伤害
            harm = []  # 危害
            c = ["MATCH (n:`消费品一级类别`) RETURN n;", "MATCH (n:`消费品名称`) RETURN n;"
                , "MATCH (n:`伤害类型`) RETURN n;", "MATCH (n:`消费品问题部件`) RETURN n;"]
            for i in range(0, 4):
                data = graph.run(c[i]).data()
                if data:
                    data = graph.run(c[i]).to_data_frame()
                    data = data.to_json(orient="records")
                    data = eval(data)
                    for k in data:
                        k['n'] = k['n']['name']
                    if i == 0:
                        for var in data:
                            classification.append(var['n'])
                    elif i == 1:
                        for var in data:
                            productname.append(var['n'])
                    elif i == 2:
                        for var in data:
                            hurt.append(var['n'])
                    elif i == 3:
                        for var in data:
                            harm.append(var['n'])
            response['data'] = all
            response['classification'] = classification
            response['productname'] = productname
            response['hurt'] = hurt
            response['harm'] = harm
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


# 按照所给条件筛选查询
def querybycondition(graph, nowtime, class1, class2, area, hurt, harm, product):
    c = ""
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
    if hurt:
        c = "MATCH (n1:`事件`)-[rel5]->(n5:`伤害类型`{name:\"" + hurt + "\"})" \
                                                                  " WITH n1,rel5,n5 " + c
    if harm:
        c = "MATCH (n1:`事件`)-[rel6]->(n6:`消费品三级危害类型`{name:\"" + harm + "\"})" \
                                                                       " WITH n1,rel6,n6 " + c
    if class2_tp:
        c = "MATCH (n1:`事件`)-[rel7]->(n7:`消费品二级类别`{name:\"" + class2_tp + "\"})" \
                                                                          " WITH n1,rel7,n7 " + c
    nodes = []
    if product:
        c = c + ' MATCH (n1:`事件`)-[rel8]-(n8:`消费品名称`) return n1,n8'
        data = graph.run(c).data()
        if data:
            data = graph.run(c).to_data_frame()
            for row in data.values:
                if row[0]['name'] and product in row[1]['name']:
                    nodes.append(row[0]['name'])
    else:
        c = c + "MATCH (n1:`事件`) RETURN n1"
        data = graph.run(c).data()
        if data:
            data = graph.run(c).to_data_frame()
            for row in data.values:
                if row[0]['name']:
                    nodes.append(row[0]['name'])
    # print(c)
    # print(nodes)
    pre = []
    eve = []
    for p in nodes:
        if '评估' in p:
            pre.append(p)
        else:
            eve.append(p)
    for p in pre:
        eve.append(p)
    return eve


def Querybycondition(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            queryform = QueryForm(post)
            if queryform.is_valid():
                nowtime = queryform.cleaned_data['time']  # 时间
                class1 = queryform.cleaned_data['class1']  # 消费品类别
                class2 = queryform.cleaned_data['class2']  # 消费品类别
                area = queryform.cleaned_data['area']  # 区域
                hurt = queryform.cleaned_data['hurt']  # 伤害
                harm = queryform.cleaned_data['harm']  # 危害
                product = queryform.cleaned_data['product']
                start = queryform.cleaned_data['start']
                to = queryform.cleaned_data['to']
                try:
                    nodes = querybycondition(graph, nowtime, class1, class2, area, hurt, harm, product)
                    eventnum = nodes[start:to + 1]
                    end = queryinfos(graph, eventnum)
                    response['msg'] = 'success'
                    response['data'] = end[1:]
                    response['columns'] = end[0]
                    response['totals'] = len(nodes)
                    endtime = time.perf_counter()
                    print("The function run time is : %.03f seconds" % (
                            endtime - starttime))  # 输出 ：The function run time is : 2.999 seconds
                except Exception as e:
                    response['msg'] = str(e)
                    response['error_num'] = 404
                return JsonResponse(response)
        else:
            all = queryall(graph)
            response['data'] = all
            response['msg'] = 'success'
            response['error_num'] = 0
            return JsonResponse(response)
    else:
        response['msg'] = "请求错误"
        response['error_num'] = 400
        return JsonResponse(response)


# 查询造成某种伤害的主要危害原因
def querymostreason(graph, hurt, start, to):
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
    nodes = getevent(graph, start, to + 40)
    # print(nodes)
    eventnum = nodes
    end = queryinfos(graph, eventnum)
    links = []
    indexp = end[0].index('消费品名称')
    indexh3 = end[0].index('消费品三级危害类型')
    data = [{
        'name': hurt,
        'des': hurt,
        'symbolSize': 70,
        'category': 0
    }]
    for var in end[1:]:
        if len(links) > 100:
            break
        if var[indexp]:
            p = {
                'name': var[indexp],
                'des': var[indexp],
                'symbolSize': 50,
                'category': 1
            }
            if p not in data:
                data.append(p)
            link = {
                'source': var[indexp],
                'target': hurt,
                'name': '造成伤害',
                'des': '造成伤害'
            }
            if link not in links:
                links.append(link)

            if var[indexh3]:
                harm3 = var[indexh3].split(',')
                for i in harm3:
                    p = {
                        'name': i,
                        'des': i,
                        'symbolSize': 40,
                        'category': 2
                    }
                    if p not in data:
                        data.append(p)
                    link = {
                        'source': var[indexp],
                        'target': i,
                        'name': '具有三级危害因素',
                        'des': '具有三级危害因素'
                    }
                    if link not in links:
                        links.append(link)

                    h2 = harm3_2[i]
                    h2p = {
                        'name': h2,
                        'des': h2,
                        'symbolSize': 30,
                        'category': 3
                    }
                    if h2p not in data:
                        data.append(h2p)
                    link = {
                        'source': i,
                        'target': h2,
                        'name': '二级危害因素',
                        'des': '二级危害因素'
                    }
                    if link not in links:
                        links.append(link)

                    h1 = harm2_1[h2]
                    h1p = {
                        'name': h1,
                        'des': h1,
                        'symbolSize': 20,
                        'category': 4
                    }
                    if h1p not in data:
                        data.append(h1p)
                    link = {
                        'source': h2,
                        'target': h1,
                        'name': '一级危害因素',
                        'des': '一级危害因素'
                    }
                    if link not in links:
                        links.append(link)

                    h0 = harm1_0[h1]
                    h0p = {
                        'name': h0,
                        'des': h0,
                        'symbolSize': 10,
                        'category': 5
                    }
                    if h0p not in data:
                        data.append(h0p)
                    link = {
                        'source': h1,
                        'target': h0,
                        'name': '危害因素',
                        'des': '危害因素'
                    }
                    if link not in links:
                        links.append(link)
    end = queryinfos(graph, nodes[start: start + 5])
    draw = {'data': data, 'link': links, 'end': end, 'totals': len(nodes)}
    return draw


def Querymostreason(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        post = QueryDict(request.get_full_path().split('?')[1])
        queryform = QueryForm(post)
        if queryform.is_valid():
            hurt = queryform.cleaned_data['hurt']  # 危害
            start = queryform.cleaned_data['start']
            to = queryform.cleaned_data['to']
            try:
                draw = querymostreason(graph, hurt, start, to)
                response['draw_link'] = draw['link']
                response['draw_data'] = draw['data']
                response['data'] = draw['end'][1:]
                response['columns'] = draw['end'][0]
                response['totals'] = draw['totals']
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


def test(graph):
    all = queryall(graph)
    # print(all)
    classification = []  # 消费品类别
    productname = []  # 名称
    hurt = []  # 伤害
    harm = []  # 危害
    c = ["MATCH (n:`消费品一级类别`) RETURN n;", "MATCH (n:`消费品名称`) RETURN n;", "MATCH (n:`伤害类型`) RETURN n;"
        , "MATCH (n:`消费品问题部件`) RETURN n;"]
    for i in range(0, 4):
        data = graph.run(c[i]).data()
        if data:
            data = graph.run(c[i]).to_data_frame()
            data = data.to_json(orient="records")
            data = eval(data)
            for k in data:
                k['n'] = k['n']['name']
            if i == 0:
                for var in data:
                    classification.append(var['n'])
            elif i == 1:
                for var in data:
                    productname.append(var['n'])
            elif i == 2:
                for var in data:
                    hurt.append(var['n'])
            elif i == 3:
                for var in data:
                    harm.append(var['n'])


def getevent(graph, start, to):
    c = 'match (n:`事件`) return n;'
    pre = []
    data = graph.run(c).data()
    end = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name'] and '评估' not in row[0]['name']:
                end.append(row[0]['name'])
            elif '评估' in row[0]['name']:
                pre.append(row[0]['name'])
    for p in pre:
        end.append(p)
    return end[start:to + 1]


def queryinfos(graph, eventnum):
    harm = ['物理危害', '化学危害', '生物危害']
    harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
             '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
             '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面', '高温液体',
             '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气', '臭氧',
             '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸', '盐酸',
             '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
             'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
             '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
             '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']

    harm0_1 = {'物理危害': ['机械危害', '爆炸危害', '噪声危害', '电气危害', '高/低温物质危害', '辐射危害', '警示标识缺失'], '化学危害': ['无机毒物危害', '有机毒物'],
               '生物危害': ['致病微生物危害', '致病生物危害']}
    harm1_2 = {'机械危害': ['形状和表面性能危害', '潜在能量危害', '动能危害'], '爆炸危害': ['气相爆炸危害', '液相爆炸危害', '固相爆炸危害'],
               '噪声危害': ['稳定性噪音危害', '变动性噪音危害', '脉冲性噪音危害'], '电气危害': ['触电危害', '电气爆炸'], '高/低温物质危害': ['高温物质危害', '低温物质危害'],
               '辐射危害': ['热辐射危害', '射线辐射危害', '电磁辐射危害'], '警示标识缺失': ['警示标识缺失'],
               '无机毒物危害': ['有毒气体危害', '有毒重金属及其化合物危害', '有毒酸碱类危害', '无机氰化物危害'],
               '有机毒物': ['有毒荃类化合物', '有毒芳香稠环类化合物', '有毒杂环类化合物', '有毒有机氯化物'],
               '致病微生物危害': ['原核细胞微生物危害', '真核细胞微生物危害', '原生微生物危害'], '致病生物危害': ['寄生虫危害']}
    harm2_3 = {'形状和表面性能危害': ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口'],
               '潜在能量危害': ['机械稳定性', '机械强度', '弹性组件失控', '压力空间失控'], '动能危害': ['移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压'],
               '气相爆炸危害': ['爆炸性气体', '爆炸性粉尘', '爆炸性喷雾'], '液相爆炸危害': ['聚合爆炸', '蒸发爆炸', '液体混合爆炸'],
               '固相爆炸危害': ['爆炸性化合物', '固体爆炸性物质'], '稳定性噪音危害': ['稳定性噪音危害'], '变动性噪音危害': ['变动性噪音危害'], '脉冲性噪音危害': ['脉冲性噪音危害'],
               '触电危害': ['高/低压', '过热', '漏电', '短路'], '电气爆炸': ['过热', '短路', '接触不良', '铁芯发热', '散热不良'],
               '高温物质危害': ['明火', '高温表面', '高温液体', '高温气体'], '低温物质危害': ['低温表面', '低温液体', '低温气体'], '热辐射危害': ['热辐射危害'],
               '射线辐射危害': ['激光辐射', '紫外线辐射', 'X光线辐射'], '电磁辐射危害': ['高频电磁辐射', '低频电磁辐射'], '警示标识缺失': ['警示标识缺失'],
               '有毒气体危害': ['一氧化碳', '一氧化氮', '氯气', '臭氧', '氯化氢', '硫化氢', '其它'],
               '有毒重金属及其化合物危害': ['砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它'],
               '有毒酸碱类危害': ['硫酸', '盐酸', '氢氧化钠', '其它'], '无机氰化物危害': ['氢氰酸', '氰化钾', '氯化氢', '其它'],
               '有毒荃类化合物': ['甲醛', '乙醛', '丙烯醛', '其它'], '有毒芳香稠环类化合物': ['蒽类化合物', '菲类化合物', '芘类化合物', '其它'],
               '有毒杂环类化合物': ['N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它'], '有毒有机氯化物': ['有机氟化物', '有机氯化物', '有机溴化物', '其它'],
               '原核细胞微生物危害': ['大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它'],
               '真核细胞微生物危害': ['皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它'],
               '原生微生物危害': ['甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒', '其它'], '寄生虫危害': ['尘螨', '蛔虫卵', '绦虫卵', '其它']}

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
    lists = []

    columns = ['事件标题', '日期', '国家', '区域', '产品大类', '消费品名称', '伤害事件', '危害源', '事件来源', '伤害类别', '伤害类型', '严重程度', '链接',
               '涉及的消费品数量',
               '产品小类', '消费品危害类型', '消费品一级危害类型', '消费品二级危害类型', '消费品三级危害类型']
    nolist = ['消费品一级类别', '消费品二级类别', '尺寸']
    for i in eventnum:
        # print(i)
        c = "MATCH (n1{name:\"" + str(i) + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c).data()
        if answer:
            answer = graph.run(c).to_data_frame()
            answer = managedata(answer)
            p = []
            for var in answer:
                if var['n2'] != '0' and var['n2'] != '-1':
                    p.append(var)
                if var['rel'] in nolist:
                    continue
                if var['rel'] not in columns and var['n2'] != '-1' and var['n2'] != '0':
                    columns.append(var['rel'])
            lists.append(p)
            # print(p)
    # print(columns)
    # print(lists)
    demo = [columns]
    count = 0
    indexbig = columns.index('产品大类')
    indexlittle = columns.index('产品小类')
    index3 = columns.index('消费品三级危害类型')
    index2 = columns.index('消费品二级危害类型')
    index1 = columns.index('消费品一级危害类型')
    index0 = columns.index('消费品危害类型')
    indexw = columns.index('危害源')
    indexs = columns.index('严重程度')
    pcol = ['消费品一级类别', '消费品二级类别', '消费品三级危害类型', '消费品二级危害类型', '消费品一级危害类型', '消费品危害类型', '危害源', '尺寸']
    # print(columns)
    for var in lists:
        # print(count)
        count += 1
        eve = []
        for k in columns:
            eve.append('')
        harm3 = []
        harm2 = []
        harm1 = []
        harm0 = []
        for p in var:
            print(p)
            if p['rel'] not in pcol:
                index = columns.index(p['rel'])
            if p['rel'] == '消费品一级类别':
                eve[indexbig] = p['n2']

            elif p['rel'] == '伤害类型':
                if eve[index]:
                    eve[index] = eve[index] + ',' + p['n2']
                else:
                    eve[index] = p['n2']

            elif p['rel'] == '消费品二级类别':
                eve[indexlittle] = p['n2']

            elif p['rel'] == '尺寸':
                continue

            elif p['rel'] == '消费品三级危害类型':
                harm3.append(p['n2'])

            elif p['rel'] == '严重程度':
                severity = ['', '微弱', '一般', '严重', '非常严重']
                risk = ['', "可接受风险", "低风险", "中风险", "高风险"]

                if '事件' in p['n1']:
                    eve[index] = severity[int(p['n2'])]
                elif '评估' in p['n1']:
                    eve[index] = risk[int(p['n2'])]

            elif p['rel'] == '已标注':
                if p['n2'] == '0':
                    eve[index] = '×'
                elif p['n2'] == '1':
                    eve[index] = '√'

            elif p['rel'] == '日期':
                try:
                    str2date = datetime.datetime.strptime(p['n2'], "%Y%m%d")  # 字符串转化为date形式
                    eve[index] = str2date.strftime("%Y/%m/%d")  # date形式转化为str
                except:
                    continue


            elif p['rel'] == '涉及的消费品数量':
                eve[index] = p['n2']

            elif p['rel'] == '健康状况':
                health = ['', '差', '一般', '良好', '很好']
                eve[index] = health[int(p['n2'])]

            elif p['rel'] == '小零件':
                if eve[index]:
                    eve[index] = eve[index] + ',' + p['n2']
                else:
                    eve[index] = p['n2']

            elif p['n2'] == '0':
                eve[index] = '否'

            elif p['n2'] == '1':
                eve[index] = '是'

            elif p['n2'] == '-1':
                eve[index] = ''

            else:
                eve[index] = p['n2']

        if harm3:
            for k in harm3:
                if eve[index3]:
                    eve[index3] = eve[index3] + ',' + k
                else:
                    eve[index3] = k

                if harm3_2[k] not in harm2:
                    harm2.append(harm3_2[k])

        if harm2:
            for k in harm2:
                if eve[index2]:
                    eve[index2] = eve[index2] + ',' + k
                else:
                    eve[index2] = k

                if harm2_1[k] not in harm1:
                    harm1.append(harm2_1[k])
            eve[indexw] = eve[index2]

        if harm1:
            for k in harm1:
                if eve[index1]:
                    eve[index1] = eve[index1] + ',' + k
                else:
                    eve[index1] = k

                if harm1_0[k] not in harm0:
                    harm0.append(harm1_0[k])

        if harm0:
            for k in harm0:
                if eve[index0]:
                    eve[index0] = eve[index0] + ',' + k
                else:
                    eve[index0] = k

        demo.append(eve)
    return demo


def getnum(graph):
    c = 'match (n:`事件`) return count(n);'
    data = graph.run(c).data()
    return data[0]['count(n)']


def Queryinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = QueryInfosForm(post)
            if markform.is_valid():
                start = markform.cleaned_data['start']
                to = markform.cleaned_data['to']
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    eventnum = getevent(graph, start, to)
                    end = queryinfos(graph, eventnum)
                    # print(end)
                    totals = getnum(graph)
                    # print(end)
                    response['msg'] = 'success'
                    response['data'] = end[1:]
                    response['columns'] = end[0]
                    response['totals'] = totals
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


def getops(graph):
    # 获取地区
    area = []
    c1 = 'match (n:`区域`) return n;'
    data = graph.run(c1).data()
    if data:
        data = graph.run(c1).to_data_frame()
        for row in data.values:
            if row[0]['name'] != '-1':
                area.append(row[0]['name'])
    # print(area)

    # 获取产品大类
    # sort = ['儿童用品']
    # c2 = 'match (n:`消费品一级类别`) return n;'
    # data = graph.run(c2).data()
    # if data:
    #     data = graph.run(c2).to_data_frame()
    #     for row in data.values:
    #         if row[0]['name'] != '其他' and row[0]['name'] != '儿童用品':
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
    c3 = 'match (n:`伤害类型`) return n;'
    data = graph.run(c3).data()
    if data:
        data = graph.run(c3).to_data_frame()
        for row in data.values:
            if row[0]['name'] != '其他' and row[0]['name'] != '-1':
                hurt.append(row[0]['name'])
    hurt.append('其他')
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
        p.append(h0)
    ops = {'area': area, 'sort': sort, 'hurt': hurt, 'harm': p}
    return ops


def Getops(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        try:
            graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
            ops = getops(graph)
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


def getmainharmeve(graph, proname):
    c = 'match (m:`消费品名称`)-[rel]-(n:`事件`) return n,m'
    data = graph.run(c).data()
    eve = []
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        for row in data.values:
            if proname in row[1]['name']:
                # print(row,row[0]['name'])
                eve.append(row[0]['name'])
            # if proname in row[0]['name']:
    return eve


def querymainharm(graph, eventnum):
    dicts = {}
    if eventnum:
        c = 'match (n:`事件`)-[rel]-(m:`伤害类型`) with n,rel,m match (n:`事件`)-[rel1]-(p:`涉及的消费品数量`) with n,rel,m,rel1,p match (n:`事件`)-[rel2]-(q:`消费品三级危害类型`) return n,m,p,q'
        data = graph.run(c).data()
        if data:
            data = graph.run(c).to_data_frame()
            json_records = data.to_json(orient="records")
            data = eval(json_records)
            data = pd.DataFrame(data)
            for row in data.values:
                if row[0]['name'] in eventnum:
                    if row[1]['name'] not in dicts:
                        dicts.update({row[1]['name']: {row[3]['name']: int(row[2]['name'])}})
                    else:
                        if row[3]['name'] not in dicts[row[1]['name']]:
                            dicts[row[1]['name']].update({row[3]['name']: int(row[2]['name'])})
                        else:
                            tp = dicts[row[1]['name']][row[3]['name']]
                            dicts[row[1]['name']].update({row[3]['name']: int(row[2]['name']) + tp})
        # print(dicts)
    return dicts


def getmainharmtable(harmdicts):
    table_harm = [['序号', '伤害名', '次数', '主要危害源']]
    temp = []
    count = 0
    print(harmdicts)
    for p in harmdicts:
        q = ['伤害', p]
        # 最多伤害
        maxharm = []
        numharm = []
        # print(p)
        counts = 0
        for t in harmdicts[p]:
            # print(t)
            counts = counts + harmdicts[p][t]
            if len(maxharm) < 3:
                maxharm.append(t)
                numharm.append(harmdicts[p][t])
            else:
                for i in range(0, len(numharm)):
                    min_num = min(numharm)
                    if min_num < harmdicts[p][t]:
                        min_index = numharm.index(min_num)
                        maxharm[min_index] = t
                        numharm[min_index] = harmdicts[p][t]
        harms = maxharm[0]
        for t in range(1, len(maxharm)):
            harms = harms + ',' + maxharm[t]
        q.append(counts)
        q.append(harms)
        temp.append(q)

    # print(temp)
    for p in range(0, len(temp)):
        for q in range(p, len(temp)):
            if temp[p][3] > temp[q][3]:
                tp = temp[p]
                temp[p] = temp[q]
                temp[q] = tp

    for p in temp:
        count = count + 1
        p[0] = p[0] + str(count)
        table_harm.append(p)

    print(table_harm)
    return table_harm


def queryarea(graph, dicts):
    temp = {}
    if dicts:
        c = 'match (n:`事件`)-[rel]-(m:`区域`) with n,rel,m match (n:`事件`)-[rel1]-(p:`涉及的消费品数量`) with n,rel,m,rel1,p match (n:`事件`)-[rel2]-(q:`伤害类型`) return m,q,p'
        data = graph.run(c).data()
        if data:
            data = graph.run(c).to_data_frame()
            json_records = data.to_json(orient="records")
            data = eval(json_records)
            data = pd.DataFrame(data)
            for row in data.values:
                # print(row)
                if row[0]['name'] == '-1':
                    row[0]['name'] = '其他'
                if row[1]['name'] in dicts:
                    if row[0]['name'] not in temp:
                        temp.update({row[0]['name']: {row[1]['name']: int(row[2]['name'])}})
                    else:
                        if row[1]['name'] not in temp[row[0]['name']]:
                            temp[row[0]['name']].update({row[1]['name']: int(row[2]['name'])})
                        else:
                            tp = temp[row[0]['name']][row[1]['name']]
                            temp[row[0]['name']].update({row[1]['name']: int(row[2]['name']) + tp})
                            # print(tp, temp[row[0]['name']][row[1]['name']])
            for row in temp:
                tp = 0
                for p in temp[row]:
                    tp = int(temp[row][p]) + tp
                temp[row].update({'总计': tp})
    print(temp)
    return temp


def querysource(graph, dicts):
    temp = {}
    if dicts:
        hurt = []
        for p in dicts:
            hurt.append(p)
        c = 'match (n:`事件`)-[rel]-(m:`事件来源`) with n,rel,m match (n:`事件`)-[rel1]-(p:`涉及的消费品数量`) with n,rel,m,rel1,p match (n:`事件`)-[rel2]-(q:`伤害类型`) return m,q,p'
        data = graph.run(c).data()
        if data:
            data = graph.run(c).to_data_frame()
            json_records = data.to_json(orient="records")
            data = eval(json_records)
            data = pd.DataFrame(data)
            for row in data.values:
                if row[1]['name'] in hurt:
                    if row[0]['name'] not in temp:
                        temp.update({row[0]['name']: {row[1]['name']: int(row[2]['name'])}})
                    else:
                        if row[1]['name'] not in temp[row[0]['name']]:
                            temp[row[0]['name']].update({row[1]['name']: int(row[2]['name'])})
                        else:
                            tp = temp[row[0]['name']][row[1]['name']]
                            temp[row[0]['name']].update({row[1]['name']: int(row[2]['name']) + tp})
        print(temp)
        return temp


def getsourcetable(sourcedicts):
    if sourcedicts:
        # print(sourcedicts)
        hurts = ['来源']
        for p in sourcedicts:
            for q in sourcedicts[p]:
                if q not in hurts and q != '其他':
                    hurts.append(q)
        hurts.append('其他')
        hurts.append('总计')
        table_source = [hurts]
        temp = []
        # print(hurts)
        for p in sourcedicts:
            add = 0
            z = [p]
            for q in hurts[1:-1]:
                if q in sourcedicts[p]:
                    z.append(sourcedicts[p][q])
                    add = add + int(sourcedicts[p][q])
                else:
                    z.append(0)
            z.append(add)
            temp.append(z)
        # print(temp)
        for i in range(0, len(temp)):
            for k in range(i, len(temp)):
                if temp[i][-1] < temp[k][-1]:
                    tp = temp[i]
                    temp[i] = temp[k]
                    temp[k] = tp
        # print(temp)
        for p in temp:
            table_source.append(p)
        print(table_source)
        return table_source
    else:
        return []


def getareatable(areadicts):
    if areadicts:
        # print(sourcedicts)
        areas = []
        for p in areadicts:
            if p not in areas and p != '其他':
                areas.append(p)
        areas.append('其他')

        hurts = []
        for p in areadicts:
            for q in areadicts[p]:
                if q not in hurts and q != '其他' and q != '总计':
                    hurts.append(q)
        hurts.append('其他')
        print(hurts)
        table_source = [areas, hurts]
        temp = []
        # print(hurts)

        # {
        #     name: 'Forest',
        #     type: 'bar',
        #     barGap: 0,
        #     label: labelOption,
        #     emphasis: {
        #         focus: 'series'
        #     },
        #     data: [320, 332, 301, 334, 390]
        # },
        tp = []
        for p in hurts:
            datas = []
            for q in areadicts:
                if p in areadicts[q]:
                    datas.append(areadicts[q][p])
                else:
                    datas.append(0)
            tps = {
                'name': p,
                'type': 'bar',
                'barGap': 0,
                'label': 'labelOption',
                'emphasis': {
                    'focus': 'series'
                },
                'data': datas
            }
            tp.append(tps)
        table_source.append(tp)
        print(table_source)
        return table_source
    else:
        return []


def Querymainharm(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = QueryMain(post)
            if markform.is_valid():
                proname = markform.cleaned_data['proname']
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    eve = getmainharmeve(graph, proname)
                    harmdicts = querymainharm(graph, eve)
                    areadicts = queryarea(graph, harmdicts)
                    sourcedicts = querysource(graph, harmdicts)
                    harmtable = getmainharmtable(harmdicts)
                    sourcetable = getsourcetable(sourcedicts)
                    areatable = getareatable(areadicts)

                    response['msg'] = 'success'
                    response['harmtable'] = harmtable[1:]
                    response['harmtablecolumns'] = harmtable[0]
                    response['areatable'] = areatable
                    response['xAxis'] = areatable[0]
                    response['legend'] = areatable[1]
                    response['series'] = areatable[2]
                    response['sourcetable'] = sourcetable[1:]
                    response['sourcetablecolumns'] = sourcetable[0]
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


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    getmainharmeve(graph, '儿童')
    # print(querymainharm(graph, getmainharmeve(graph, '儿童')))
    # queryarea(graph, querymainharm(graph, getmainharmeve(graph, '儿童')))
    # querysource(graph, querymainharm(graph, getmainharmeve(graph, '儿童')))
    # getmainharmtable(querymainharm(graph, getmainharmeve(graph, '儿童')))
    # getsourcetable(querysource(graph, querymainharm(graph, getmainharmeve(graph, '儿童'))))
    print(getareatable(queryarea(graph, querymainharm(graph, getmainharmeve(graph, '儿童')))))

