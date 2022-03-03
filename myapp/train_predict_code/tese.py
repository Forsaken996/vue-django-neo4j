import numpy as np
# np.set_printoptions(threshold=np.inf)
import scipy as sp
import pydotplus
from sklearn import tree
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import classification_report
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib
from .Interface import Dbresearch_badscore
from .Interface import Dbresearch_countlist
from .Interface import Dbresearch_old
from .Interface import Dbresearch_pro


def model_test(traindata, testdata, sort, hurtbylittlepart, harm_num, littlepart_num):  # modelpath,countlist,old,pro
    print('debug')
    end = []
    clf = joblib.load('myapp/train_predict_code/tree.model')  # modelpath
    dict = {'划伤': 1, '挫伤': 2, '勒伤': 3, '弹伤': 4, '砸伤': 5, '扭伤': 6, '挤压伤': 7, '骨折': 8, '内脏损伤或破裂': 9, '肢体离断': 10,
            '切割伤': 11, '穿刺伤': 12, '窒息': 13, '体内异物': 14, '烧伤': 15, '烫伤': 16, '电击伤': 17, '电热灼伤': 18, '视力损伤': 19,
            '心血管系统损伤': 20, '生殖系统损伤': 21, '听力损伤': 22, '心脏血管损伤': 23, '内部器官损伤': 24, '爆炸损伤': 25, '植物人': 26, '死亡': 27,
            '化学性刺激': 28, '过敏反应': 29, '全身中毒': 30, '致癌': 31, '致畸': 32, '生物性感染': 33, '环境风险': 34, '脑震荡': 35, '脑挫裂伤': 36,
            '其他': 37}
    dict1 = {1: '划伤', 2: '挫伤', 3: '勒伤', 4: '弹伤', 5: '砸伤', 6: '扭伤', 7: '挤压伤', 8: '骨折', 9: '内脏损伤或破裂', 10: '肢体离断',
             11: '切割伤', 12: '穿刺伤', 13: '窒息', 14: '体内异物', 15: '烧伤', 16: '烫伤', 17: '电击伤', 18: '电热灼伤', 19: '视力损伤',
             20: '心血管系统损伤', 21: '生殖系统损伤', 22: '听力损伤', 23: '心脏血管损伤', 24: '内部器官损伤', 25: '爆炸损伤', 26: '植物人', 27: '死亡',
             28: '化学性刺激', 29: '过敏反应', 30: '全身中毒', 31: '致癌', 32: '致畸', 33: '生物性感染', 34: '环境风险', 35: '脑震荡', 36: '脑挫裂伤',
             37: '其他'}
    data = []
    labels = []
    columns = ['事件号', '消费品一级危害类型', '消费品二级危害类型', '消费品危害类型', '伤害类型', '小零件', '其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒',
               '其它原生微生物危害', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌',
               '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害', '甲醛', '乙醛', '丙烯醛', '蒽类化合物', '菲类化合物', '芘类化合物',
               'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '有机氟化物', '有机氯化物', '有机溴化物', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢', '砷及其化合物',
               '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '硫酸', '盐酸', '氢氧化钠', '氢氰酸', '氰化钾', '警示标识缺失',
               '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体',
               '明火', '[高低]电压', '过热', '漏电', '短路', '接触不良', '铁芯发热', '散热不良', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控', '尺寸',
               '光滑表面', '粗糙表面', '绳索及类似物', '不透气', '填充物', '锐利边缘', '部件空隙或开口', '尖角', '消费者年龄', '消费者性别', '涉及的消费品数量', '昼夜',
               '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射', '湿度', '腐蚀物', '海拔', '温度', '坎坷', '爬坡', '下坡', '速度', '稳定性', '腐蚀性',
               '严重程度']
    # marklist=np.zeros(38)
    """
    with open("E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/数据2.txt") as ifile:
            for line in ifile:
                tokens = line.strip().split('\t')
                data.append([float(tk) for tk in tokens[0:116]])
                count=1
                for tk in tokens[116:]:
                    if count == 44:
                        labels.append(count)
                        break
                    if int(tk)>0:
                        labels.append(count)
                        break
                    count=count+1
    """
    # "E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/test_out.txt"
    '''评估集的读取与预处理'''
    Features_Dict = {}
    with open(testdata, encoding='utf-8') as ifile:
        num = 1
        for line in ifile:
            print('line', line)
            if num == 1:
                num = num + 1
                # columns = line.strip().split('\t')
                # print(columns)
                continue
            tokens = line.strip().split('\t')
            count = 1
            #       print(tokens)
            temp = []
            templist = []
            testcount = 0
            mark = 1
            for tk in tokens:
                if tk == '[]' and count == 5:
                    mark = 0
                    break
                elif count == 5:
                    # 修改
                    # if tk[0]=='[':
                    #     temp=tk[2:-2].split(',')
                    #     print(temp)
                    # else:
                    #     temp.append(tk[1:-1])
                    if tk:
                        if ',' in tk:
                            temp = tk.split(',')
                            # print(temp)
                        else:
                            temp.append(tk)
                if count == 93:
                    # print(tk)
                    if tk == '':
                        testcount = 1
                    else:
                        testcount = int(tk)

                if count > 6 and count != 82 and count != 93 and count != 94 and count != 111:
                    if count == 92:
                        if tk == '男':
                            templist.append(0)
                        else:
                            templist.append(1)
                    else:
                        if tk == '':
                            templist.append(0)
                        else:
                            templist.append(int(tk))

                # Features_Dict.update({count: columns[count-1]})
                # print(Features_Dict)
                count = count + 1
            if mark == 0:
                continue
            for i in temp:
                for j in range(testcount):
                    labels.append(i.strip())
                    data.append(templist)
    # print(labels)
    #################注意，此处要修改###############################################
    # print('data', data)
    # print(len(data))
    print('labels', labels)
    x_test = data[0]
    x = np.array(data)
    y = np.array(labels)
    print('x;y',x,y)
    # marklist = getmarklist(traindata)
    marklist = []
    with open('myapp/train_predict_code/marklist.txt', 'r') as f:
        line = f.readline()
        marklist.append(line[:-1])
        while line:
            line = f.readline()
            if line:
                marklist.append(line[:-1])
    ifile.close()
    print('marklist', marklist)
    # marklist=np.unique(labels)#对所有已有样本的标签进行去重唯一化
    # print(marklist)
    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)
    # answer2=clf.predict(x_test[1,:].reshape(1,-1))
    # answer = clf.predict_proba(x_test[1,:].reshape(1,-1)) #获得横向对比危害概率
    # 修改||
    # print(x.reshape(1,-1))
    # print(x.reshape(1,-1).shape)
    # print(x)
    if len(x) == 1:
        answer2 = clf.predict(x[0,].reshape(1, -1))
        answer = clf.predict_proba(x[0,].reshape(1, -1))  # 获得横向对比危害概率
    else:
        answer2 = clf.predict(x[1, :].reshape(1, -1))
        answer = clf.predict_proba(x[1, :].reshape(1, -1))  # 获得横向对比危害概率
    # print(y_test[1])
    # print(answer)
    # print(answer2)
    # print(marklist)
    answerlist = answer.argsort()
    # countlist = []
    print('anserlist', answerlist)
    print('answer', answer)
    # counts = Dbresearch_countlist()
    # for p in marklist[answerlist[0]]:
    #     if p in counts:
    #         countlist.append(counts[p])
    #     else:
    #         countlist.append(0)
    # countlist.reverse()
    # countlist = [10, 10, 10, 5, 8, 7, 4, 3, 4, 10]  # 伤害频次countlist=dbresearch_countlist(answerlist[0])这里应依据伤害类型查询数据库
    # old = int(Dbresearch_old(sort))
    # old = 1  # 商品平均年龄or商品类型是否满足年龄，根据商品类型查询人群调用数据库查询 old=dbresearch_old()
    print('answerlist[0]', answerlist[0])
    #################注意，此处要修改###############################################
    # pro = [1, 1, 1, 1, 3, 2, 3, 4, 1]  # 专家修正值,这里根据伤害类型调用数据库查询 pro=dbresearch_pro(answerlist[0])
    # pro = []
    # prodict = Dbresearch_pro()
    # for p in marklist[answerlist[0]]:
    #     if p in prodict:
    #         pro.append(prodict[p])
    #     else:
    #         pro.append(0)
    # pro.reverse()
    # print('pro', pro)
    # badscore = [1, 2, 0, 4, 3, 2, 3, 4, 2]  # 伤害严重程度，调用数据库查询严重程度 badscore=dbresearch_badscore(answerlist[0])
    badscore = []
    hurtdict = Dbresearch_badscore()
    print('hurtdict', hurtdict)
    print('answerlist[0]', answerlist[0])
    for p in answerlist[0]:
        q = marklist[p]
        if q in hurtdict:
            badscore.append(hurtdict[q])
        else:
            badscore.append(0)
    badscore.reverse()
    bad_dic = {"高风险": 4, "中风险": 3, "低风险": 2, "可接受风险": 1}
    features = []
    hurts = []
    for i in reversed(answerlist[0]):  # 对所有可能危害进行风险评估
        if answer[0, i] > 0:
            # print("概率值:" + str(answer[0, i]))
            #        print(marklist[i])
            # temp = answer[0, i] * countlist[i]  # 计算风险值
            # print(answer[0, i], countlist[i], pro[i])
            # temp = answer[0, i] * pro[i]  # 计算风险值
            # if old == 1:  # 商品平均年龄满足条件乘以权重
            #    temp = temp * 1.5
            hurts.append(marklist[i])
            if hurtbylittlepart and marklist[i] in hurtbylittlepart:
                answer[0, i] = answer[0, i] * (float(harm_num - littlepart_num) / float(harm_num)) + hurtbylittlepart[
                    marklist[i]] * (float(littlepart_num) / float(harm_num))
            else:
                answer[0, i] = answer[0, i] * (float(harm_num - littlepart_num) / float(harm_num))
            dicts = {'划伤': 1, '擦伤': 1, '挫伤': 1, '勒伤': 2, '弹伤': 1, '砸伤': 1, '扭伤': 1, '挤压伤': 2, '骨折': 2, '内脏损伤或破裂': 3,
                     '肢体离断': 3, '切割伤': 3, '穿刺伤': 2, '窒息': 3, '体内异物': 2, '烧伤': 2, '烫伤': 2, '电击伤': 2, '电热灼伤': 3,
                     '视力损伤': 3, '心血管系统损伤': 4, '生殖系统损伤': 4, '听力损伤': 4, '心脏血管损伤': 4, '内部器官损伤': 4, '爆炸损伤': 4, '植物人': 4,
                     '死亡': 4, '化学性刺激': 3, '过敏反应': 2, '全身中毒': 4, '致癌': 4, '致畸': 4, '生物性感染': 2, '环境风险': 2, '脑震荡': 4,
                     '脑挫裂伤': 4, '其他': 2}
            temp = dicts[marklist[i]] * answer[0, i]
            # if badscore[i] == 0 or badscore[i] == 1:
            if temp >= 1.5:
                level = "高风险"
            elif temp >= 1:
                level = "中风险"
            elif temp >= 0.5:
                level = "低风险"
            elif temp >= 0:
                level = "可接受风险"

            ####################################

            # print(marklist[i],level)
            # print(f"危害为：{marklist[i]}，危害等级:{slevel}")
            pre = [marklist[i], level, answer[0, i]]
            end.append(pre)
    if hurtbylittlepart:
        for p in hurtbylittlepart:
            if p not in hurts and p != '小零件':
                q = hurtbylittlepart[p] * (float(littlepart_num) / float(harm_num))
                dicts = {'划伤': 1, '擦伤': 1, '挫伤': 1, '勒伤': 2, '弹伤': 1, '砸伤': 1, '扭伤': 1, '挤压伤': 2, '骨折': 2, '内脏损伤或破裂': 3,
                         '肢体离断': 3, '切割伤': 3, '穿刺伤': 2, '窒息': 3, '体内异物': 2, '烧伤': 2, '烫伤': 2, '电击伤': 2, '电热灼伤': 3,
                         '视力损伤': 3, '心血管系统损伤': 4, '生殖系统损伤': 4, '听力损伤': 4, '心脏血管损伤': 4, '内部器官损伤': 4, '爆炸损伤': 4, '植物人': 4,
                         '死亡': 4, '化学性刺激': 3, '过敏反应': 2, '全身中毒': 4, '致癌': 4, '致畸': 4, '生物性感染': 2, '环境风险': 2, '脑震荡': 4,
                         '脑挫裂伤': 4, '其他': 2}
                temp = dicts[p] * q
                # if badscore[i] == 0 or badscore[i] == 1:
                if temp >= 1.5:
                    level = "高风险"
                elif temp >= 1:
                    level = "中风险"
                elif temp >= 0.5:
                    level = "低风险"
                elif temp >= 0:
                    level = "可接受风险"
                pre = [p, level, q]
                end.append(pre)
        if '小零件' in hurtbylittlepart:
            for q in hurtbylittlepart['小零件']:
                features.append('小零件:' + q)
    featurelist = clf.feature_importances_
    # print('dege11', featurelist)
    sortfeature = featurelist.argsort()
    # print('debug11', x)
    # print('debug12', x[0])
    # print('debug', x[0][1,:])
    xx = x[0, :]
    # print(sortfeature)
    # print('debug18')
    columns2 = ['其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒',
                '其它原生微生物危害', '皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌',
                '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害', '甲醛', '乙醛', '丙烯醛', '蒽类化合物', '菲类化合物', '芘类化合物',
                'N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物', '有机氟化物', '有机氯化物', '有机溴化物', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢', '砷及其化合物',
                '镉及其化合物', '铬及其化合物', '铜及其化合物', '汞及其化合物', '镍及其化合物', '铅及其化合物', '硫酸', '盐酸', '氢氧化钠', '氢氰酸', '氰化钾', '警示标识缺失',
                '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射', '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体',
                '明火', '[高低]电压', '过热', '漏电', '短路', '接触不良', '铁芯发热', '散热不良', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控',
                '光滑表面', '粗糙表面', '绳索及类似物', '不透气', '填充物', '锐利边缘', '部件空隙或开口', '尖角', '消费者年龄', '消费者性别',
                '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射', '湿度', '腐蚀物', '海拔', '温度', '坎坷', '爬坡', '下坡', '速度', '稳定性', '腐蚀性']
    for i in reversed(sortfeature):
        if xx[i] > 0 and i != 84:
            features.append(i)
            print(i, columns2[i])
    # print(f"影响危害的主要特征为:{features}")
    # for i in features:
    #     if xx[i]>0:
    #         featurename.append(labelname[i])
    forecastend = {'data': end, 'features': features}
    # print(forecastend)
    # print('debug19')
    return forecastend


def getmarklist(filename):
    dict = {'擦伤': 1, '挫伤': 2, '勒伤': 3, '弹伤': 4, '砸伤': 5, '扭伤': 6, '挤压伤': 7, '骨折': 8, '内脏损伤或破裂': 9, '肢体离断': 10,
            '切割伤': 11, '穿刺伤': 12, '窒息': 13, '体内异物': 14, '烧伤': 15, '烫伤': 16, '电击伤': 17, '电热灼伤': 18, '视力损伤': 19,
            '心血管系统损伤': 20, '生殖系统损伤': 21, '听力损伤': 22, '心脏血管损伤': 23, '内部器官损伤': 24, '爆炸损伤': 25, '植物人': 26, '死亡': 27,
            '化学性刺激': 28, '过敏反应': 29, '全身中毒': 30, '致癌': 31, '致畸': 32, '生物性感染': 33, '环境风险': 34, '脑震荡': 35, '脑挫裂伤': 36,
            '其他': 37}

    data = []
    labels = []
    # """

    # """
    # with open("E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/数据2.txt") as ifile:
    #        for line in ifile:
    #            tokens = line.strip().split('\t')
    #            data.append([float(tk) for tk in tokens[0:116]])
    #            count=1
    #            for tk in tokens[116:]:
    #                if count == 44:
    #                   temp[43]=1
    #                   labels.append(count)
    #                   break
    #               if int(tk)>0:
    #                   labels.append(count)
    #                   temp[count-1]=1
    #                   break
    #               count=count+1
    #     "E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/test_out.txt"
    # ‘’‘csv文件读取与预处理’‘’
    with open(filename, encoding='utf-8') as ifile:
        num = 1
        for line in ifile:
            print('line', line)
            if num == 1:
                num = num + 1
                continue
            tokens = line.strip().split('\t')
            count = 1;
            #       print(tokens)
            temp = []
            templist = []
            testcount = 0
            mark = 1
            for tk in tokens:
                if tk == '[]' and count == 5:
                    mark = 0
                    break
                elif count == 5:
                    # 修改
                    # if tk[0]=='"':
                    #     temp=tk[2:-2].split(',')
                    # else:
                    #     temp.append(tk[1:-1])
                    if tk:
                        if ',' in tk:
                            temp = tk.split(',')
                        else:
                            temp.append(tk)
                if count == 93:
                    if tk == '':
                        testcount = 1;
                    else:
                        testcount = int(tk)

                if count > 6 and count != 78 and count != 79 and count != 80 and count != 81 and count != 82 and count != 85 and count != 91 and count != 93 and count != 94 and count != 95 and count != 101 and count != 103 and count != 104 and count != 108:
                    if count == 92:
                        if tk == '男':
                            templist.append(0)
                        else:
                            templist.append(1)
                    else:
                        if tk == '' or tk == '0.0':
                            templist.append(0)
                        elif tk == '-1.0':
                            templist.append(-1)
                        elif tk == '1.0':
                            templist.append(1)
                        else:
                            templist.append(int(tk))
                count = count + 1
            if mark == 0:
                continue
            for i in temp:
                for j in range(testcount):
                    labels.append(i.strip())
                    data.append(templist)
    #        print(templist)
    #        print(temp)
    #        print(testcount)
    # ‘’‘数据集‘’‘
    for p in labels:
        p = p.replace('\"', '')
    marklist = np.unique(labels)  # 对所有已有样本的标签进行去重唯一化
    return marklist


def main():
    '''接口调用,调用模型进行评估，传入用户输入'''
    model_test("E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/test_out.txt")


if __name__ == "__main__":
    main()

# print(y_test)
# print(np.mean( answer == y_test))

# feature=[]
# for i in range(0,116):
#    feature.append(str(i))
# classn=[]
# for i in range(0,44):
#    classn.append(str(i))

# print(x_test)


# tt=[]
# for i in range(0,116):
#    if i==85:
#        tt.append(1)
#    else:
#        tt.append(0)
# nt=[]
# nt.append(tt)
# nt=np.array(nt)

# print(nt)
# answer = clf.predict(nt)
# print(answer)

# 1,2,3,4,5,6,7,9,12,13,15,20,23,26,31,32,33,36,44
