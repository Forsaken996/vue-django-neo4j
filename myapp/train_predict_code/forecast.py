# -*- coding:utf-8 -*-
from django.http import JsonResponse
from django.http.request import QueryDict
from django import forms

from .predict import model_train
from .tese import model_test
# from predict import model_train
# from tese import model_test

from py2neo import Graph, Node, Relationship, NodeMatcher
from .Interface import Dbresearch_littlepart
import pandas as pd
import csv
import time
exist = False


class PreForm(forms.Form):
    value = forms.CharField(label="value", required=True)


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


def train(Input_File):
    model_train(Input_File)


# 数据入评估库 评估号保持一致
def assess(graph, graph_ass, value, re_data):
    p = getprenum(graph)
    node = createnode(graph_ass, '事件', '评估' + str(p), '', '')
    createnode(graph_ass, '评估项', str(value), '评估项', node)
    createnode(graph_ass, '评估值', str(re_data), '评估值', node)
    # print('创建节点:评估', str(p), '评估项:', value, '评估值:', re_data)


# 判断该数据是否已经在评估库
def judge(graph_ass, value):
    c = 'match (n:`评估项`{name:"' + str(value) + '"})-[r]-(m:`事件`) with n,r,m match (m:`事件`)-[r1]-(y:`评估值`) return y'
    # print('c', c)
    data = graph_ass.run(c).data()
    if data:
        return True
    else:
        return False


# 获取评估库数据
def getass(graph_ass, value):
    c = 'match (n:`评估项`{name:"' + str(value) + '"})-[r]-(m:`事件`) with n,r,m match (m:`事件`)-[r1]-(y:`评估值`) return y'
    # print('c', c)
    data = graph_ass.run(c).data()
    if data:
        data = graph_ass.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = data[0]['y']['name']
        data = eval(data)
        return data


def createpredictnode(graph, value):
    columns = ['序号', '消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '伤害类型', '小零件', '其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒',
               '其它原生微生物危害', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌',
               '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害', '甲醛', '乙醛', '丙烯醛', '蒽类化合物', '菲类化合物', '芘类化合物',
               'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '有机氟化物', '有机氯化物', '有机溴化物', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢', '砷及其化合物',
               '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '硫酸', '盐酸', '氢氧化钠', '氢氰酸', '氰化钾', '警示标识缺失',
               '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射',
               '高频电磁辐射', '低频电磁辐射', '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体', '明火', '[高低]电压', '过热', '漏电', '短路',
               '接触不良', '铁芯发热', '散热不良', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控', '尺寸', '光滑表面', '粗糙表面', '绳索及类似物', '不透气',
               '填充物', '锐利边缘', '部件空隙或开口', '尖角', '消费者年龄', '消费者性别', '涉及的消费品数量', '昼夜', '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射',
               '湿度', '腐蚀物', '海拔', '温度', '坎坷', '爬坡', '下坡', '速度', '稳定性', '腐蚀性', '严重程度']

    harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
             '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
             '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面', '高温液体',
             '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气', '臭氧',
             '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸', '盐酸',
             '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
             'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
             '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
             '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']
    lists = ['消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '小零件']
    prenum = getprenum(graph)
    eve = []
    node = createnode(graph, '事件', '评估' + str(prenum), '', '')
    nowtime = time.strftime('%Y%m%d', time.localtime(time.time()))
    # print(nowtime)
    title = '评估' + str(prenum)
    hurtevent = '评估'  # 需要修改
    createnode(graph, '日期', nowtime, '日期', node)
    createnode(graph, '伤害事件', hurtevent, '伤害事件', node)
    createnode(graph, '事件标题', title, '事件标题', node)
    createnode(graph, '区域', '-1', '区域', node)
    createnode(graph, '数据来源', '评估', '数据来源', node)
    createnode(graph, '已标注', '0', '已标注', node)
    # 标注涉及的消费品数量

    for var in columns:
        if var in lists:
            eve.append([])
        elif var == '涉及的消费品数量':
            eve.append(1)
        elif var == '序号':
            eve.append(prenum)
        else:
            eve.append(-1)

    for p in value:
        if p[0] == '消费品一级类别':
            createnode(graph, '消费品一级类别', p[1], '消费品一级类别', node)
        elif p[0] == '消费品二级类别':
            createnode(graph, '消费品二级类别', p[1], '消费品二级类别', node)
        elif p[0] == '消费品名称':
            createnode(graph, '消费品名称', p[1], '消费品名称', node)

        if p[0] in columns:
            i = columns.index(p[0])
            if eve[i]:
                eve[i] = str(eve[i]) + ',' + str(p[1])
            else:
                eve[i] = p[1]

    for i in range(1, len(columns)):
        if columns[i] == '消费品一级危害类型' or columns[i] == '消费品二级危害类型' or columns[i] == '消费品危害类型':
            print('忽略节点:', str(columns[i]))
            continue
        elif eve[i] == '0' or eve[i] == 0:
            createnode(graph, columns[i], '0', columns[i], node)
            print('已创建节点:', str(columns[i]), '属性值:', '0')

        elif eve[i] == '' or eve[i] == '-1' or eve[i] == -1 or eve[i] == [] or eve[i] == '[]':
            if columns[i] == '消费品一级类别':
                createnode(graph, columns[i], '其他', columns[i], node)
                print('已创建节点:', str(columns[i]), '属性值:', '其他')
            else:
                createnode(graph, columns[i], '-1', columns[i], node)
                print('已创建节点:', str(columns[i]), '属性值:', '-1')

        elif eve[i] == '1' or eve[i] == 1:
            if columns[i] in harm3:
                createnode(graph, '消费品三级危害类型', columns[i], '消费品三级危害类型', node)
                print('已创建节点:', '消费品三级危害类型', '属性值:', columns[i])
            createnode(graph, columns[i], '1', columns[i], node)
            print('已创建节点:', str(columns[i]), '属性值:', '1')

        elif type(eve[i]) == dict:
            for var in eve[i]:
                createnode(graph, columns[i], var, columns[i], node)
                print('已创建节点:', str(columns[i]), '属性值:', var)

        elif ',' in eve[i] and columns[i] != '伤害事件':
            q = eve[i].split(',')
            for var in q:
                createnode(graph, columns[i], var, columns[i], node)
                print('已创建节点:', str(columns[i]), '属性值:', var)

        else:
            createnode(graph, columns[i], eve[i], columns[i], node)
            print('已创建节点:', str(columns[i]), '属性值:', eve[i])

        print('剩余子节点:', str(len(columns) - i - 1), '刚创建事件:', str(columns[i]), '属性值:', eve[i])


def Createpredictnode(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = PreForm(post)
            if markform.is_valid():
                value = markform.cleaned_data['value']
                try:
                    # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    graph_ass = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
                    values = value[:-1].split('^')
                    temp = []
                    if judge(graph_ass, value):
                        response['msg'] = 'exist'

                    else:
                        for p in values:
                            tp = p.split('@')
                            temp.append(tp)
                        createpredictnode(graph, temp)
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


def predict(graph, Train_File, values):
    columns = ['事件号', '消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '伤害类型', '小零件', '其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒',
               '其它原生微生物危害', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌',
               '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害', '甲醛', '乙醛', '丙烯醛', '蒽类化合物', '菲类化合物', '芘类化合物',
               'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '有机氟化物', '有机氯化物', '有机溴化物', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢', '砷及其化合物',
               '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '硫酸', '盐酸', '氢氧化钠', '氢氰酸', '氰化钾', '警示标识缺失',
               '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射',
               '高频电磁辐射', '低频电磁辐射', '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体', '明火', '[高低]电压', '过热', '漏电', '短路',
               '接触不良', '铁芯发热', '散热不良', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控', '尺寸', '光滑表面', '粗糙表面', '绳索及类似物', '不透气',
               '填充物', '锐利边缘', '部件空隙或开口', '尖角', '消费者年龄', '消费者性别', '涉及的消费品数量', '昼夜', '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射',
               '湿度', '腐蚀物', '海拔', '温度', '坎坷', '爬坡', '下坡', '速度', '稳定性', '腐蚀性', '严重程度']

    eve = []

    Feature_Dict = {0: '其它寄生虫危害', 1: '甲肝病毒', 2: '甲型流感病毒', 3: '轮状病毒', 4: '禽流感病毒', 5: '其它原生微生物危害', 6: '皮肤癣真菌', 7: '着色真菌', 8: '孢子丝菌', 9: '新生隐球菌', 10: '假丝酵母菌', 11: '曲霉', 12: '毛霉', 13: '卡氏肺孢菌', 14: '其它真核细胞微生物危害', 15: '大肠杆菌', 16: '沙门氏菌', 17: '副溶血性弧菌', 18: '金黄色葡萄球菌', 19: '腊样芽孢肝菌', 20: '其它原核细胞微生物危害', 21: '甲醛', 22: '乙醛', 23: '丙烯醛', 24: '蒽类化合物', 25: '菲类化合物', 26: '芘类化合物', 27: 'N-杂环化合物', 28: 'S-杂环化合物', 29: 'O-杂环化合物', 30: '有机氟化物', 31: '有机氯化物', 32: '有机溴化物', 33: '一氧化碳', 34: '氯气', 35: '臭氧', 36: '氯化氢', 37: '硫化氢', 38: '砷及其化合物', 39: '镉及其化合物', 40: '铬及其化合物', 41: '铜及其化合物', 42: '汞及其化合物', 43: '镍及其化合物', 44: '铅及其化合物', 45: '硫酸', 46: '盐酸', 47: '氢氧化钠', 48: '氢氰酸', 49: '氰化钾', 50: '警示标识缺失', 51: '热辐射危害', 52: '激光辐射', 53: '紫外线辐射', 54: 'X光线辐射', 55: '高频电磁辐射', 56: '低频电磁辐射', 57: '高温表面', 58: '高温液体', 59: '高温气体', 60: '低温表面', 61: '低温液体', 62: '低温气体', 63: '明火', 64: '[高低]电压', 65: '过热', 66: '漏电', 67: '短路', 68: '接触不良', 69: '铁芯发热', 70: '散热不良', 71: '机械稳定性', 72: '机械强度', 73: '弹性组件失控', 74: '压力空间失控', 75: '光滑表面', 76: '粗糙表面', 77: '绳索及类似物', 78: '不透气', 79: '填充物', 80: '锐利边缘', 81: '部件空隙或开口', 82: '尖角', 83: '消费者年龄', 84: '消费者性别', 85: '地面摩擦', 86: '斜坡', 87: '楼梯', 88: '灰尘', 89: '静电', 90: '辐射', 91: '湿度', 92: '腐蚀物', 93: '海拔', 94: '温度', 95: '坎坷', 96: '爬坡', 97: '下坡', 98: '速度', 99: '稳定性', 100: '腐蚀性'}

    lists = ['消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '小零件']

    prenum = getprenum(graph)
    # print(prenum)
    for var in columns:
        # print(var)
        if var in lists:
            eve.append([])
        elif var == '涉及的消费品数量':
            eve.append(1)
        elif var == '事件号':
            eve.append(prenum)
        else:
            eve.append(-1)
    sort = ''
    product = ''
    temp = []
    little_parts = []
    for p in values:
        tp = p.split('@')
        temp.append(tp)
    # print(temp)
    harm_num = 0
    for p in temp:
        print(type(p), p)
        print(eve)
        if p[1] != '消费品一级类别' and p[1] != '涉及的消费品数量':
            harm_num = harm_num + 1

        if p[0] == '小零件':
            i = columns.index(p[0])
            little_parts.append(p[1])
            print(eve[i])
            if eve[i]:
                eve[i].append(p[1])
            else:
                eve[i] = [p[1]]
        elif p[1] in columns:
            i = columns.index(p[1])
            if p[0] != '小零件':
                eve[i] = 1
        elif p[0] == '消费品一级类别':
            sort = p[1]

        elif p[0] == '消费品名称':
            product = p[1]
    print('eve', eve)
    f = open('myapp/train_predict_code/forecast.csv', 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(f, delimiter='\t')
    csv_writer.writerow(columns)
    csv_writer.writerow(eve)
    f.close()

    Forcast_File = 'myapp/train_predict_code/forecast.csv'
    hurtbylittlepart = Dbresearch_littlepart(product, little_parts)
       
    littlepart_num = 1
    if '小零件' in hurtbylittlepart:
        littlepart_num = littlepart_num + len(hurtbylittlepart['小零件'])
        
    print('lens', len(eve))
    end = model_test(Train_File, Forcast_File, sort, hurtbylittlepart, harm_num, littlepart_num)
    print('end', end)
    temp = []
    for p in end['data']:
        if float(p[2] >= 0.01):
            p[2] = "%.2f%%" % (p[2] * 100)
            temp.append(p)

    for i in range(0, len(temp)):
        for k in range(i, len(temp)):
            if temp[i][2] < temp[k][2]:
                tp = temp[i][2]
                temp[i][2] = temp[k][2]
                temp[k][2] = tp

    Features = []
    for p in end['features']:
        if '小零件:' in str(p):
            Features.append(p)
        else:
            Features.append(Feature_Dict[int(p)])
    re_data = {'data': temp, 'features': Features}
    # print(re_data)
    return re_data


def Predict(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = PreForm(post)
            if markform.is_valid():
                value = markform.cleaned_data['value']
                try:
                    # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    graph_ass = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
                    Train_File = 'myapp/train_predict_code/productinfos.csv'
                    values = value[:-1].split('^')
                    temp = []
                    print(judge(graph_ass, values))
                    if judge(graph_ass, value):
                        re_data = getass(graph_ass, value)
                    else:
                        re_data = predict(graph, Train_File, values)
                        assess(graph, graph_ass, value, re_data)
                    response['msg'] = 'success'
                    response['data'] = re_data['data']
                    response['features'] = re_data['features']
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


def getFile(graph):
    columns = ['事件', '消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '伤害类型', '小零件', '其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒',
               '其它原生微生物危害', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌',
               '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害', '甲醛', '乙醛', '丙烯醛', '蒽类化合物', '菲类化合物', '芘类化合物',
               'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '有机氟化物', '有机氯化物', '有机溴化物', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢', '砷及其化合物',
               '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '硫酸', '盐酸', '氢氧化钠', '氢氰酸', '氰化钾', '警示标识缺失',
               '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射',
               '高频电磁辐射', '低频电磁辐射', '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体', '明火', '[高低]电压', '过热', '漏电', '短路',
               '接触不良', '铁芯发热', '散热不良', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控', '尺寸', '光滑表面', '粗糙表面', '绳索及类似物', '不透气',
               '填充物', '锐利边缘', '部件空隙或开口', '尖角', '消费者年龄', '消费者性别', '涉及的消费品数量', '昼夜', '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射',
               '湿度', '腐蚀物', '海拔', '温度', '坎坷', '爬坡', '下坡', '速度', '稳定性', '腐蚀性', '严重程度']
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
    listcol = ['伤害类型', '小零件']
    f = open('productinfos.csv', 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(f, delimiter='\t')
    csv_writer.writerow(columns)

    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    nodes = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name']:
                nodes.append(row[0]['name'])

    for i in nodes:
        eve = []
        for k in columns:
            eve.append('')
        eve[0] = str(i)
        c1 = "MATCH (n1{name:\"" + str(i) + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        data = graph.run(c1).data()
        if data:
            data = graph.run(c1).to_data_frame()
            json_records = data.to_json(orient="records")
            data = eval(json_records)
            data = pd.DataFrame(data)
            # print(data)
            for row in data.values:
                row[0] = row[0]['name']
                row[2] = row[2]['name']
                if row[1] == '消费品三级危害类型':
                    harm3 = row[2]
                    harm2 = harm3_2[harm3]
                    harm1 = harm2_1[harm2]
                    harm0 = harm1_0[harm1]
                    if eve[1]:
                        if harm1 not in eve[1]:
                            eve[1].append(harm1)
                    else:
                        eve[1] = [harm1]

                    if eve[2]:
                        if harm2 not in eve[2]:
                            eve[2].append(harm2)
                    else:
                        eve[2] = [harm2]

                    if eve[3]:
                        if harm0 not in eve[3]:
                            eve[3].append(harm0)
                    else:
                        eve[3] = [harm0]

                elif row[1] in listcol:
                    indexs = columns.index(row[1])
                    if eve[indexs]:
                        if row[2] not in eve[indexs]:
                            eve[indexs].append(row[2])
                    else:
                        eve[indexs] = [row[2]]

                elif row[1] in columns:
                    indexs = columns.index(row[1])
                    eve[indexs] = row[2]
            indexlittle_part = indexs = columns.index('小零件')
            if eve[indexlittle_part] == '':
                eve[indexlittle_part] = []

            indexhurt = columns.index('伤害类型')
            temp = eve[indexhurt]
            eve[indexhurt] = ''
            for p in temp:
                if eve[indexhurt]:
                    eve[indexhurt] = str(eve[indexhurt]) + ',' + str(p)
                else:
                    eve[indexhurt] = str(p)
            # print(eve[indexhurt])

            csv_writer.writerow(eve)
            # lists.append(p)


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


# 获取事件数编号确定新的事件编号
def geteventnum(graph):
    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    nodes = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name'] and '事件' in row[0]['name']:
                nodes.append(row[0]['name'])
        nodes_num = []
        for p in nodes:
            nodes_num.append(int(p.replace('事件', '')))
        if nodes_num:
            return max(nodes_num) + 1
        else:
            return 1


# 获取评估数编号确定新的评估编号
def getprenum(graph):
    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    nodes = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name'] and '评估' in row[0]['name']:
                nodes.append(row[0]['name'])
        nodes_num = []
        for p in nodes:
            nodes_num.append(int(p.replace('评估', '')))
        if nodes_num:
            return max(nodes_num) + 1
        else:
            return 1
    else:
        return 1


if __name__ == "__main__":
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    # graph_ass = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
    # Get_File = 'E:\\Study\\code\\NowdaysCode\\python\\riskEstimation\\code\\framebycg\\dataPreparation\\test_out.csv'
    Train_File = 'productinfos.csv'
    # Forecast_File = 'myapp/train_predict_code/forecast.csv'
    # # getFile(graph)
    # # train(Train_File)
    # # forecast(Train_File, Forecast_File)
    # value = [['评估', '测试1'], ['消费品一级类别', '儿童用品'], ['消费品二级类别', '其他'], ['涉及的消费品数量', 100]]
    # predict(graph, Train_File, value)
    # value = '评估@测试1\t消费品一级类别@儿童用品'
    # values = value.split('\t')
    # temp = []
    # for a in values:
    #     z = a.split('@')
    #     temp.append(z)
    # print(temp)
    # getprenum(graph)
    Delete()
