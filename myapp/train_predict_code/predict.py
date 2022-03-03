import numpy as np
import scipy as sp
from sklearn import tree
import pydotplus
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import classification_report
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib 


def model_train(filename):
#''' 数据读入 '''
    dict={'擦伤':1,'挫伤':2,'勒伤':3,'弹伤':4,'砸伤':5,'扭伤':6,'挤压伤':7,'骨折':8,'内脏损伤或破裂':9,'肢体离断':10,'切割伤':11,'穿刺伤':12,'窒息':13,'体内异物':14,'烧伤':15,'烫伤':16,'电击伤':17,'电热灼伤':18,'视力损伤':19,'心血管系统损伤':20,'生殖系统损伤':21,'听力损伤':22,'心脏血管损伤':23,'内部器官损伤':24,'爆炸损伤':25,'植物人':26,'死亡':27,'化学性刺激':28,'过敏反应':29,'全身中毒':30,'致癌':31,'致畸':32,'生物性感染':33,'环境风险':34,'脑震荡':35,'脑挫裂伤':36,'其他':37}
    
    data   = []
    labels = []
#"""

#"""
#with open("E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/数据2.txt") as ifile:
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
#‘’‘csv文件读取与预处理’‘’
    with open(filename, encoding='utf-8') as ifile:
        num=1
        for line in ifile:
            if num==1:
                num=num+1
                continue
            tokens = line.strip().split('\t')
            count=1;
     #       print(tokens)
            temp=[]
            templist=[]
            testcount=0
            mark=1
            for tk in tokens:
                if tk=='[]' and count==5:
                    mark=0
                    break
                elif count==5:
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
                if count==93:
                    if tk=='':
                        testcount=1;
                    else:
                        testcount=int(tk)


                if count>6 and count!=82 and count!=93 and count!=94 and count!=111:
                    if count ==92:
                        if tk=='男':
                            templist.append(0)
                        else:
                            templist.append(1)
                    else:
                        if tk=='' or tk == '0.0':
                            templist.append(0)
                        elif tk == '-1.0':
                            templist.append(-1)
                        elif tk == '1.0':
                            templist.append(1)
                        else:
                            templist.append(int(tk))
                count=count+1
            if mark==0:
                continue
            for i in temp:
                for j in range(testcount):
               
                    labels.append(i.strip())
                    data.append(templist)
#        print(labels)
#        print(templist)
#        print(temp)
#        print(testcount)
#‘’‘数据集‘’‘

    x = np.array(data)
    y = np.array(labels)

    print(x.shape)
    print(y.shape)
    np.set_printoptions(threshold=np.inf)
    # print(temp)

 
    ''' 拆分训练数据与测试数据 '''
    #x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)
    x_train=x
    y_train=y
    ''' 使用信息熵作为划分标准，对决策树进行训练 '''
    clf = tree.DecisionTreeClassifier(criterion='entropy')
    print(clf)
    clf.fit(x_train, y_train)
    ''' 保存训练好的决策树模型，这里会保存到本地 '''
    joblib.dump(clf,'tree.model')
    ''' 把决策树结构写入文件 '''
    feature=[]
    for i in range(0,116):
        feature.append(str(i))
    classn=["1","2","3","4","5","6","7","9","12","13","15","20","23","26","31","32","33","36","44"]
    #for i in range(0,44):
    #    classn.append(str(i))
    with open("tree.dot", 'w') as f:
        dot_data = tree.export_graphviz(clf, out_file=None,filled=True,rounded=True)
        f.write(dot_data)
        graph = pydotplus.graph_from_dot_data(dot_data)
        graph.write_pdf("tree.pdf")
    ''' 系数反映每个特征的影响力。越大表示该特征在分类中起到的作用越大 '''
    print(clf.feature_importances_)
    getmarklist(filename, 'marklist.txt')
    '''测试结果的打印'''
    """
    answer = clf.predict(x_test)
    #print(x_train)
    print(answer)
    #print(y_train)
    print(np.mean( answer == y_test))
     """
    #graph=graphviz.Source()
    '''准确率与召回率'''
    #precision, recall, thresholds = precision_recall_curve(y_train, clf.predict(x_train))
    #answer = clf.predict_proba(x)[:,1]
    #print(classification_report(y, answer, target_names = ['thin', 'fat']))


def main():
    # 接口调用，这里调用模型进行训练，传入训练集的路径，由于数据处理那里还在修改，这里我会提供一个测试用训练集
    model_train("E:/111暑期项目/项目1/riskEstimation-main/data/苏然之前完成的BP评估/测试/test_out.txt")


def getmarklist(filename, savefile):
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
    print(marklist)
    ifile.close()
    with open(savefile, 'w') as ifile:
        for q in marklist:
            ifile.writelines(q)
            ifile.writelines("\n")
    ifile.close()



if __name__ == "__main__":
    main()
