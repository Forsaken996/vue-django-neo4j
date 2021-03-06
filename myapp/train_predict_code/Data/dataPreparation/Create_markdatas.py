# 连接Neo4j数据库并从excel文件导入数据并建立知识图谱
# 所用库：py2neo, pandas
# encoding = GBK
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
import csv
import ast


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


def Getnum(graph):
    c = 'match (n:`事件`) return count(n);'
    data = graph.run(c).data()
    return data[0]['count(n)']


def Createdata(graph, files, source):  # 数据库名称, 文件路径/文件名, 数据来源[1 召回 2 投诉 3 实际发生新闻]
    harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
             '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
             '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面', '高温液体',
             '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气', '臭氧',
             '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸', '盐酸',
             '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
             'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
             '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
             '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']
    count = len(open(files, 'r', encoding='utf-8').readlines())
    # print(count)
    file = open(files, 'r', encoding='utf-8')
    # last = Getnum(graph)  # 库中共有事件数
    counts = 0
    columns = []
    while 1:
        line = file.readline()
        counts = counts + 1
        line = line.replace("\n", "")
        line = line.replace(" ", "")
        p = line.split('\t')
        if line:
            print(p)
            if counts == 1:
                columns = p
                che = ['砷', '镉', '铬', '铜', '汞', '镍', '铅']
                chemistry = ['砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物']
                for m in columns:
                    if m in che:
                        temp = m
                        m = m + '及其化合物'
                        print('标题: 已将', temp, '修改为', m)
                    else:
                        print('标题：', m)
                continue
            else:
                node = createnode(graph, '事件', '事件' + str(counts - 1), '', '')
                createnode(graph, '数据来源', str(source), '数据来源', node)
                createnode(graph, '已标注', '0', '已标注', node)
                severity = []
                for i in range(1, len(columns)):
                    if columns[i] == '消费品一级危害类型' or columns[i] == '消费品二级危害类型' or columns[i] == '消费品危害类型':
                        print('忽略节点:', str(columns[i]))
                        print('进度:', '事件' + str(counts - 1), '%事件' + str(count - 1), '剩余子节点:',
                              str(len(columns) - i - 1))
                        continue
                    elif p[i] == '否' or p[i] == '0' or p[i] == '无' or p[i] == '0.0':
                        createnode(graph, columns[i], '0', columns[i], node)
                        print('已创建节点:', str(columns[i]), '属性值:', '0')

                    elif p[i] == '空' or p[i] == '' or p[i] == '-1' or p[i] == [] or p[i] == '[]':
                        if columns[i] == '消费品一级类别':
                            createnode(graph, columns[i], '其他', columns[i], node)
                            print('已创建节点:', str(columns[i]), '属性值:', '其他')
                        else:
                            createnode(graph, columns[i], '-1', columns[i], node)
                            print('已创建节点:', str(columns[i]), '属性值:', '-1')

                    elif p[i] == '有' or p[i] == '是' or p[i] == '1':
                        if columns[i] in harm3:
                            createnode(graph, '消费品三级危害类型', columns[i], '消费品三级危害类型', node)
                            print('已创建节点:', '消费品三级危害类型', '属性值:', columns[i])
                        createnode(graph, columns[i], '1', columns[i], node)
                        print('已创建节点:', str(columns[i]), '属性值:', '1')

                    elif ('[' in p[i] or ']' in p[i]) and columns[i] != '伤害事件':
                        p[i] = ast.literal_eval(p[i])
                        for q in p[i]:
                            createnode(graph, columns[i], q, columns[i], node)
                            print('已创建节点:', str(columns[i]), '属性值:', q)

                    elif ',' in p[i] and columns[i] != '伤害事件':
                        q = p[i].split(',')
                        for var in q:
                            createnode(graph, columns[i], var, columns[i], node)
                            print('已创建节点:', str(columns[i]), '属性值:', var)

                    elif columns[i] == '严重程度':
                        severity.append(p[i])
                        print('已记录严重程度', str(columns[i]), '属性值:', p[i])

                    else:
                        createnode(graph, columns[i], p[i], columns[i], node)
                        print('已创建节点:', str(columns[i]), '属性值:', p[i])

                    print('进度:', '事件' + str(counts - 1), '%事件' + str(count - 1), '剩余子节点:',
                          str(len(columns) - i - 1), '刚创建事件:', str(columns[i]), '属性值:', p[i])

                createnode(graph, '严重程度', max(severity), '严重程度', node)
                print('已创建节点: 严重程度 属性值:', max(severity))

        else:
            break


def Harminitialization(graph):
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

    harm3 = ['绳索及类似物', '不透气', '填充物', '小零件', '尖角', '锐利边缘', '光滑表面', '粗糙表面', '部件空隙或开口', '机械稳定性', '机械强度', '弹性组件失控',
             '压力空间失控', '移动状态撞击', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸',
             '爆炸性化合物', '固体爆炸性物质', '高/低压', '过热', '漏电', '短路', '过热', '短路', '接触不良', '铁芯发热', '散热不良', '明火', '高温表面', '高温液体',
             '高温气体', '低温表面', '低温液体', '低温气体', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '一氧化碳', '一氧化氮', '氯气', '臭氧',
             '氯化氢', '硫化氢', '其它', '砷及其化合物', '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '其它', '硫酸', '盐酸',
             '氢氧化钠', '其它', '氢氰酸', '氰化钾', '氯化氢', '其它', '甲醛', '乙醛', '丙烯醛', '其它', '蒽类化合物', '菲类化合物', '芘类化合物', '其它',
             'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '其它', '有机氟化物', '有机溴化物', '其它', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌',
             '腊样芽孢肝菌', '其它', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它', '甲肝病毒', '甲型流感病毒',
             '轮状病毒', '禽流感病毒', '其它', '尘螨', '蛔虫卵', '绦虫卵', '其它']
    for p in harm3:
        node3 = createnode(graph, '消费品三级危害类型', str(p), '', '')
        harm2 = harm3_2[p]
        node2 = createnode(graph, '消费品二级危害类型', str(harm2), '消费品二级危害类型', node3)
        harm1 = harm2_1[harm2]
        node1 = createnode(graph, '消费品一级危害类型', str(harm1), '消费品一级危害类型', node2)
        harms = harm1_0[harm1]
        createnode(graph, '消费品危害类型', str(harms), '消费品危害类型', node1)
        print('已创建节点 危害类型:' + harms + ' 一级:' + harm1 + ' 二级:' + harm2 + ' 三级:' + p)


def getrel(graph):
    c = "match (n1{name:'事件1'})-[r]-(n2) return type(r)"
    data = graph.run(c).data()
    end = []
    if data:
        data = graph.run(c).to_data_frame()
        print(data)
        for row in data.values:
            if row[0]:
                end.append(row[0])
    print(end)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    getrel(graph)
    graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    Harminitialization(graph)
    Createdata(graph, '消费品召回.txt', 1)  # 数据库名称, 文件路径/文件名, 数据来源[1 召回 2 投诉 3 实际发生新闻]
    # # Getnum(graph)
