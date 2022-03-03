# 连接Neo4j数据库并从excel文件导入数据并建立知识图谱
# 所用库：py2neo, pandas
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
import csv


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


def CreateHarmDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品属性与所属危害因素类别的关系字典表', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("危害类型", str(var[0]), '', '')
        node1 = createnode("一级危害因素", str(var[1]), '', '')
        node2 = createnode("二级危害因素", str(var[2]), '', '')
        node3 = createnode("三级危害因素", str(var[3]), '', '')
        createnode("一级危害因素", str(var[1]), '一级危害因素', node)
        createnode("二级危害因素", str(var[2]), '二级危害因素', node1)
        createnode("三级危害因素", str(var[3]), '三级危害因素', node2)


def CreateEnvDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品使用环境属性字典表', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("一级属性名称", str(var[1]), '', '')
        node1 = createnode("特征值", str(var[2]), '', '')
        createnode("特征值", str(var[2]), '特征值', node)


def CreateSortDictionary(graph):
    # 连接neo4j数据库，输入地址、用户名、密码
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品与消费品类别', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        print(data[i])
    count = 0
    for var in data:
        count = count + 1
        print("进度", count, "%", len(data))
        node = createnode("消费品类别", str(var[0]), '', '')
        node1 = createnode("消费品一级类别", str(var[1]), '', '')
        node2 = createnode("消费品名称", str(var[2]), '', '')
        createnode("消费品一级类别", str(var[1]), '消费品一级类别', node)
        createnode("消费品名称", str(var[2]), '消费品名称', node1)


def CreateProductsDictionary(graph):
    count = len(open(r'all_goods.txt', 'r', encoding='utf-8').readlines())
    print(count)
    file = open('all_goods.txt', 'r', encoding='utf-8')
    counts = 0
    while 1:
        line = file.readline()
        counts = counts + 1
        if line:
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            print(line)
            print("已创建节点:", line, "进度", counts, "%", count)
            node = createnode("消费品名称", str(line), '', '')
            createnode("一级消费品类型", "其他", "一级消费品类型", node)
            createnode("二级消费品类型", '', "二级消费品类型", node)
        if not line:
            break
    file.close()


def CreateLittlePartsDictionary(graph):
    count = len(open(r'little_part.txt', 'r', encoding='utf-8').readlines())
    print(count)
    file = open('little_part.txt', 'r', encoding='utf-8')
    counts = 0
    while 1:
        line = file.readline()
        counts = counts + 1
        if line:
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            print("已创建节点:", line, "进度", counts, "%", count)
            createnode("小零件", str(line), '', '')
        else:
            break
    file.close()


def CreateDamageType(graph):
    data = pd.read_csv("TypeOfDamage.csv")
    # print(data.values)
    counts = 0
    da = []
    type = []
    for var in data.values:
        counts += 1
        var[0] = var[0].replace("\n", "")
        var[0] = var[0].replace(" ", "")
        print("已创建节点:", var, "进度", counts, "%", len(data.values))
        node = createnode("伤害类型", str(var[0]), '', '')
        createnode("严重程度", str(var[1]), '严重程度', node)
        da.append(var[0])
        type.append(var[1])
    print(da)
    print(type)


# 生成关键词测试样例
def CreateKey(graph):
    data = pd.read_csv("TypeOfDamage.csv")
    # print(data.values)
    counts = 0
    for var in data.values:
        counts += 1
        var[0] = var[0].replace("\n", "")
        var[0] = var[0].replace(" ", "")
        print("已创建节点:", var, "进度", counts, "%", len(data.values))
        node = createnode("伤害类型", str(var[0]), '', '')
        createnode("关键词", str(var[0]), '关键词', node)
    node = createnode("伤害类型", '划伤', '', '')
    createnode("关键词", '划痕', '关键词', node)


# 消费品问题部件
def CreateProblemPart(graph):
    node = createnode("消费品名称", '铅笔', '', '')
    createnode("消费品问题部件", '笔尖', '消费品问题部件', node)
    node = createnode("消费品名称", '钢笔', '', '')
    createnode("消费品问题部件", '钢笔头', '消费品问题部件', node)
    node = createnode("消费品名称", '纸巾', '', '')
    createnode("消费品问题部件", '纸巾', '消费品问题部件', node)
    node = createnode("消费品名称", '电线', '', '')
    createnode("消费品问题部件", '电线', '消费品问题部件', node)
    node = createnode("消费品名称", '吉他', '', '')
    createnode("消费品问题部件", '吉他弦', '消费品问题部件', node)
    node = createnode("消费品名称", '水果刀', '', '')
    createnode("消费品问题部件", '刀尖', '', node)


def Getharm():
    df = pd.read_excel('reldata.xlsx', sheet_name='消费品属性与所属危害因素类别的关系字典表', keep_default_na=False)
    print(df)
    data = df.values.tolist()
    columns = df.columns.values
    print(columns)
    print(data)
    p = {}
    o = []
    z = ''
    for i in range(1, len(data)):
        for k in range(0, len(data[i])):
            if data[i][k] == '':
                data[i][k] = data[i - 1][k]
        z = data[i][2]
        # p.update({data[i][0]: z})
        if z not in p:
            p.update({z: [data[i][3]]})
        elif data[i][3] not in p[z]:
            p[z].append(data[i][3])
        if data[i][3] not in z:
            o.append(data[i][3])
        print(data[i])
    count = 0
    print(o)


# 处理数据成选项数据
def Changedata():
    # 处理伤害类型
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
    p = [{'value': '伤害类型',
          'label': '伤害类型',
          'children': []}]
    print(p)


if __name__ == '__main__':
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='rules')
    # graph.delete_all()  # 清除neo4j中原有的结点等所有信息
    # CreateHarmDictionary(graph)
    # CreateEnvDictionary(graph)
    # CreateSortDictionary(graph)
    CreateDamageType(graph)
    CreateProductsDictionary(graph)
    CreateLittlePartsDictionary(graph)
    CreateKey(graph)
    CreateProblemPart(graph)
    Changedata()