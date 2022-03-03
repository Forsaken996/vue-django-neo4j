# coding:utf-8
from django.http import JsonResponse
from py2neo import Graph, Node, Relationship, NodeMatcher
from django.http.request import QueryDict
import pandas as pd
import time
from django import forms


class QueryForm(forms.Form):
    start = forms.IntegerField(label="start", required=True)
    to = forms.IntegerField(label="to", required=True)
    col = forms.CharField(label="col", required=False)


class ModifyForm(forms.Form):
    evenum = forms.CharField(label="evenum", required=True)
    before = forms.CharField(label="before", required=False)
    after = forms.CharField(label="after", required=False)
    attribute = forms.CharField(label="attribute", required=True)


class ModifySort(forms.Form):
    evenum = forms.CharField(label="evenum", required=False)
    productname = forms.CharField(label='productname', required=False)
    before_sort1 = forms.CharField(label="before_sort1", required=True)
    after_sort1 = forms.CharField(label="after_sort1", required=True)
    before_sort2 = forms.CharField(label="before_sort2", required=False)
    after_sort2 = forms.CharField(label="after_sort2", required=False)


class DeleteForm(forms.Form):
    evenum = forms.CharField(label='evenum', required=True)


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


# 查询全部
def queryall(graph):
    i = 1
    columns = ['事件号', '伤害事件', '消费品名称', '消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '伤害类型', '小零件', '严重程度']
    lists = []
    while i:
        c = "MATCH (n1{name:\"事件" + str(i) + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c).data()
        if answer:
            answer = graph.run(c).to_data_frame()
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
                if eve[index]:
                    eve[index] = eve[index] + ',' + k['n2']
                else:
                    eve[index] = k['n2']
            demo.append(eve)
    return demo


# 获取总数
def gettotals(graph):
    c = "MATCH (n:`事件`) RETURN n"
    answer = graph.run(c).data()
    return len(answer)


# 查询
def Queryall(request):
    starttime = time.perf_counter()
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    response = {}
    if request.method == 'POST':
        try:
            alls = queryall(graph)
            totals = gettotals(graph)
            # print(totals)
            response['data'] = alls[1:]
            response['columns'] = alls[0]
            response['totals'] = totals
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


# 查询从from到to的信息
def queryinfos(graph, start, to, addcolumns):
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

    columns = ['事件', '已标注', '伤害事件', '消费品名称', '消费品一级类别', '消费品二级类别', '伤害类型', '小零件', '严重程度', '涉及的消费品数量', '消费品三级危害类型',
               '消费品二级危害类型',
               '消费品一级危害类型', '消费品危害类型']
    nolist = ['事件标题', '链接', '日期']
    nodes = getevent(graph, start, to)
    for i in nodes:
        c = "MATCH (n1{name:\"" + str(i) + "\"})- [rel] -> (n2) RETURN n1,type(rel),n2"
        answer = graph.run(c).data()
        if answer:
            answer = graph.run(c).to_data_frame()
            answer = managedata(answer)
            # print(answer)
            p = []
            for var in answer:
                if var['rel'] in addcolumns:
                    p.append(var)
                elif (var['n2'] != '0' and var['n2'] != '-1' and var['rel'] not in nolist) or var['rel'] == '已标注':
                    p.append(var)
                if var['rel'] not in columns and var['n2'] != '-1' and var['n2'] != '0' and var['rel'] not in nolist:
                    columns.append(var['rel'])
            lists.append(p)

    if addcolumns:
        for p in addcolumns:
            if p not in columns:
                columns.append(p)
            # print(lists)
    demo = [columns]
    # print(demo)
    count = 0
    for var in lists:
        count += 1
        # print("进度:", count, "%", len(lists))
        eve = []
        for k in columns:
            eve.append('')
        if var:
            # 事件号n
            listcol = ['小零件', '消费品三级危害类型', '伤害类型']
            nocol = ['小零件', '伤害类型', '严重程度', '消费品一级类别', '消费品二级类别', '消费品三级危害类型', '消费品二级危害类型',
                     '消费品一级危害类型', '消费品危害类型']
            numcol = ['涉及的消费品数量']
            for k in var:
                indexeve = columns.index('事件')
                eve[indexeve] = k['n1']
                if k['rel'] in columns:
                    index = columns.index(k['rel'])
                    if columns[index] in listcol and eve[index]:
                        # print(columns[index])
                        eve[index] = eve[index] + ',' + k['n2']
                        if columns[index] == '消费品三级危害类型':
                            index2 = columns.index('消费品二级危害类型')
                            index1 = columns.index('消费品一级危害类型')
                            index0 = columns.index('消费品危害类型')
                            if harm3_2[k['n2']] not in eve[index2]:
                                eve[index2] = eve[index2] + ',' + harm3_2[k['n2']]
                            if harm2_1[harm3_2[k['n2']]] not in eve[index1]:
                                eve[index1] = eve[index1] + ',' + harm2_1[harm3_2[k['n2']]]
                            if harm1_0[harm2_1[harm3_2[k['n2']]]] not in eve[index0]:
                                eve[index0] = eve[index0] + ',' + harm1_0[harm2_1[harm3_2[k['n2']]]]
                    # elif columns[index] == '严重程度':
                    #     if k['n2'] == '0':
                    #         eve[index] = '不确定'
                    #     elif k['n2'] == '1':
                    #         eve[index]
                    elif columns[index] == '已标注':
                        if k['n2'] == '0':
                            eve[index] = '×'
                        elif k['n2'] == '1':
                            eve[index] = '√'

                    elif k['rel'] == '数据来源':
                        if k['n2'] == '1':
                            eve[index] = '召回'
                        elif k['n2'] == '2':
                            eve[index] = '投诉'
                        elif k['n2'] == '3':
                            eve[index] = '实际发生新闻'

                    elif columns[index] == '严重程度':
                        if k['n2']:
                            severity = ['', '微弱', '一般', '严重', '非常严重']
                            risk = ['', "可接受风险", "低风险", "中风险", "高风险"]

                            if '事件' in k['n1']:
                                eve[index] = severity[int(k['n2'])]
                            elif '评估' in k['n1']:
                                eve[index] = risk[int(k['n2'])]
                            else:
                                eve[index] = ''
                        else:
                            eve[index] = ''
                    elif columns[index] == '健康状况':
                        if k['n2']:
                            health = ['', '差', '一般', '良好', '很好']
                            eve[index] = health[int(k['n2'])]
                        else:
                            eve[index] = ''
                    elif k['n2'] == '-1':
                        eve[index] = ''
                    elif k['n2'] == '0':
                        eve[index] = '否'
                    else:
                        if columns[index] not in numcol and k['n2'] == '1':
                            eve[index] = '是'
                        else:
                            eve[index] = k['n2']
                        if columns[index] == '消费品三级危害类型':
                            index2 = columns.index('消费品二级危害类型')
                            index1 = columns.index('消费品一级危害类型')
                            index0 = columns.index('消费品危害类型')
                            eve[index2] = harm3_2[eve[index]]
                            eve[index1] = harm2_1[eve[index2]]
                            eve[index0] = harm1_0[eve[index1]]

            # print(eve)
            demo.append(eve)
    return demo


def QueryInfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = QueryForm(post)
            if markform.is_valid():
                start = markform.cleaned_data['start']
                to = markform.cleaned_data['to']
                col = markform.cleaned_data['col']
                # print(start, to, col)
                try:
                    if col:
                        col = col.split(',')
                        # print(columns)
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    end = queryinfos(graph, start, to, col)
                    # print(end)
                    totals = gettotals(graph)
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


# 修改事件号为num before->after rel为attribute
def modifyinfos(graph, evenum, before, after, attribute):
    if attribute == '已标注' and before == '否' and after == '是':
        node = createnode(graph, '事件', str(evenum), '', '')
        c1 = "MATCH (n1:`事件`{name:\"" + str(evenum) + "\"})-[r:`已标注`]-(n2:`已标注`{name:\"0\"}) DELETE r"
        graph.run(c1)
        createnode(graph, '已标注', '1', '已标注', node)
        return
    # 首先删除关系
    if before == '否':
        before = '0'
    elif before == '是':
        before = '1'
    elif before == '不确定':
        before = '-1'

    if after == '否':
        after = '0'
    elif after == '是':
        after = '1'
    elif after == '不确定':
        after = '-1'

    harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
             '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
             '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面', '高温液体',
             '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气', '臭氧',
             '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸', '盐酸',
             '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
             'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
             '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
             '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']
    if before:
        c1 = "MATCH (n1:`事件`{name:\"" + str(
            evenum) + "\"})-[r:`" + attribute + "`]-(n2:`" + attribute + "`{name:\"" + before + "\"}) DELETE r"
        graph.run(c1)
        # print(c1)

        # 如果该关系是消费品三级危害类型还应该删除
        if attribute in harm3 and (after == '-1' or after == '0'):
            c2 = "MATCH (n1:`事件`{name:\"" + str(
                evenum) + "\"})-[r:`消费品三级危害类型`]-(n2:`消费品三级危害类型`{name:\"" + attribute + "\"}) DELETE r"
            graph.run(c2)
            # print(c2)

    if after:
        node = createnode(graph, '事件', str(evenum), '', '')
        createnode(graph, attribute, after, attribute, node)
        # 如果该关系是消费品三级危害类型还应该添加关系
        if attribute in harm3 and after == '1':
            createnode(graph, '消费品三级危害类型', attribute, '消费品三级危害类型', node)


def Modifyinfos(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = ModifyForm(post)
            if markform.is_valid():
                evenum = markform.cleaned_data['evenum']  # 编号
                before = markform.cleaned_data['before']  # 修改前
                after = markform.cleaned_data['after']  # 修改后
                attribute = markform.cleaned_data['attribute']  # 修改标题
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    modifyinfos(graph, evenum, before, after, attribute)
                    # print(end)
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


# 通过消费品名称修改
def modifysortbyproductname(graph, productname, before_sort1, after_sort1, before_sort2, after_sort2):
    c = "match (n:`事件`)-[r]-(n1:`消费品名称`{name:\"" + str(productname) + "\"}) return n;"
    # print(c)
    data = graph.run(c).data()
    nodes = []
    if data:
        data = graph.run(c).to_data_frame()
        json_records = data.to_json(orient="records")
        data = eval(json_records)
        data = pd.DataFrame(data)
        for row in data.values:
            modifysort(graph, row[0]['name'], before_sort1, after_sort1, before_sort2, after_sort2)


# 通过事件号修改某个事件的消费品分类
def modifysort(graph, evenum, before_sort1, after_sort1, before_sort2, after_sort2):
    if before_sort1 and after_sort1 and before_sort1 != after_sort1:
        c1 = "MATCH (n1:`事件`{name:\"" + str(evenum) + "\"})-[r:`消费品一级类别`]-(n2) DELETE r"
        graph.run(c1)
        # print(c1)
        node = createnode(graph, '事件', str(evenum), '', '')
        createnode(graph, '消费品一级类别', str(after_sort1), '消费品一级类别', node)
        c1 = "MATCH  (n1:`事件`{name:\"" + str(evenum) + "\"})-[r:`消费品二级类别`]-(n2) DELETE r"
        graph.run(c1)
    if before_sort2 != after_sort2:
        c1 = "MATCH  (n1:`事件`{name:\"" + str(evenum) + "\"})-[r:`消费品二级类别`]-(n2) DELETE r"
        graph.run(c1)
        # print(c1)
        node = createnode(graph, '事件', str(evenum), '', '')
        createnode(graph, '消费品二级类别', str(after_sort2), '消费品二级类别', node)


def Modifysort(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = ModifySort(post)
            if markform.is_valid():
                evenum = markform.cleaned_data['evenum']  # 编号
                before_sort1 = markform.cleaned_data['before_sort1']  # 修改前
                after_sort1 = markform.cleaned_data['after_sort1']  # 修改后
                before_sort2 = markform.cleaned_data['before_sort2']  # 修改前
                after_sort2 = markform.cleaned_data['after_sort2']  # 修改后
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    modifysort(graph, evenum, before_sort1, after_sort1, before_sort2, after_sort2)
                    # print(end)
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


def Modifysortbyproductname(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = ModifySort(post)
            if markform.is_valid():
                productname = markform.cleaned_data['productname']  # 编号
                before_sort1 = markform.cleaned_data['before_sort1']  # 修改前
                after_sort1 = markform.cleaned_data['after_sort1']  # 修改后
                before_sort2 = markform.cleaned_data['before_sort2']  # 修改前
                after_sort2 = markform.cleaned_data['after_sort2']  # 修改后
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    modifysortbyproductname(graph, productname, before_sort1, after_sort1, before_sort2, after_sort2)
                    # print(end)
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


def deleteevent(graph, evenum):
    c = "MATCH (n:`事件`{name:\"" + evenum + "\"})-[r]-(n1) DELETE n,r"
    graph.run(c)


def Deleteevent(request):
    starttime = time.perf_counter()
    response = {}
    if request.method == 'POST':
        if '?' in request.get_full_path():
            post = QueryDict(request.get_full_path().split('?')[1])
            markform = DeleteForm(post)
            if markform.is_valid():
                evenum = markform.cleaned_data['evenum']  # 编号
                # print(start, to, col)
                try:
                    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
                    deleteevent(graph, evenum)
                    # print(end)
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


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    # print(modifyinfos(graph, 1, '男', '女', '机械稳定性'))
    # print(queryinfos(graph, 0, 10, ''))
    # print(gettotals(graph))
    # modifysortbyproductname(graph, '密胺盘', '', '', '', '')
    deleteevent(graph, '事件1')
