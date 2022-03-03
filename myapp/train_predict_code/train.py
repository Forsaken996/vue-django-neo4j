from predict import model_train
from py2neo import Graph, Node, Relationship, NodeMatcher
import pandas as pd
import csv
import time


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
    listcol = ['伤害类型', '小零件', '小零件']
    f = open('productinfos.csv', 'w', encoding='utf-8', newline='')
    csv_writer = csv.writer(f, delimiter='\t')
    csv_writer.writerow(columns)

    c = 'match (n:`事件`) return n;'
    data = graph.run(c).data()
    nodes = []
    if data:
        data = graph.run(c).to_data_frame()
        for row in data.values:
            if row[0]['name'] and '评估' not in row[0]['name']:
                nodes.append(row[0]['name'])
    count = 1
    for i in nodes:
        print('生成数据中~ 第', count, '%', len(nodes), '条')
        count = count + 1
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
                # print(row[0], row[2])

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
                        if row[2] not in eve[indexs] and row[2] != '-1':
                            eve[indexs].append(row[2])
                    elif row[2] != '-1':
                        eve[indexs] = [row[2]]

                elif row[1] in columns:
                    indexs = columns.index(row[1])
                    eve[indexs] = row[2]
            indexlittle_part = columns.index('小零件')
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

    print('生成数据文件完毕，训练模型中~')


def train(graph, Input_File):
    getFile(graph)
    # model_train(Input_File)


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


def Delete():
    grapha = Graph("http://localhost:7474", user="neo4j", password='123456', name='assessment')
    p = 'match (n)-[rel]-(m) delete n,rel,m'
    grapha.run(p)
    print('已删除')

    
if __name__ == "__main__":
    graph = Graph("http://localhost:7474", user="neo4j", password='123456', name='productinfos')
    # graph = 1
    Train_File = 'productinfos.csv'
    train(graph, Train_File)
    # print(getprenum(graph))
    # Delete()
