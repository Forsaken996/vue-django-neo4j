# -*- encoding: utf-8 -*-
'''
@Description:       :
@Date     :2021/08/12 00:12:23
@Author      :hellone
@version      :1.0
'''
import re
import pandas as pd
import csv
# from . import clean_data


class Item_data():
    """正则匹配

    Attributes:
            objfpath: 目标输出文件路径
    """
    def __init__(self, objfpath):
        """
        param  :
        -------
        -    #### objfpath:目标文件路径
        """
        self.F_Little_Part = './dicts/Little_Part'
        self.F_TypeOfDmg = './dicts/TypeOfDmg.csv'
        self.F_DmgOfContent = './dicts/DmgTypeOfContent'
        self.F_GoodsName = './dicts/All_Goods'
        self.F_Problem_Part = './dicts/Problem_Part'
        self.F_city = './dicts/city_lv3'
        self.csv_list = []
        self.item_dict = {}
        self.item_dict['消费品一级危害类型'] = ''
        self.item_dict['消费品二级危害类型'] = ''
        self.item_dict['消费品危害类型'] = ''
        self.item_dict['小零件'] = ''
        self.item_dict['消费品问题部件'] = ''
        self.objfilepath = objfpath
        self.city_dict = []
        self.Dict_Dmg, self.DmgTypeMap, self.LPart, self.PPart = self.DictInit()
        self.country_list = []
        self.region_list = ['河北', '山西', '辽宁', '吉林', '黑龙', '江苏', '浙江', '安徽', '福建', '江西', \
            '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', \
            '内蒙古', '广西', '西藏', '宁夏', '新疆', '北京', '天津', '上海', '重庆', '香港', '澳门']

    def DictInit(self):
        '''加载伤害类型及严重程度字典'''
        dict_dmg, dmgtype = {}, []
        l_part, p_part = [], []
        city_dict = None
        with open(self.F_city, 'r', encoding='utf-8') as f:
            city_dict = csv.DictReader(f)
            for _ in city_dict:
                self.city_dict.append(_)

        with open(self.F_TypeOfDmg, 'r', encoding='utf-8') as f:
            dicts = csv.DictReader(f)
            for dict in dicts:
                dict_dmg[dict['伤害类型']] = int(dict['严重程度'])
        with open(self.F_DmgOfContent, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                dmgtype.append(line.strip().split('\t'))
        with open(self.F_Little_Part, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                l_part.append(line.strip())
        with open(self.F_Problem_Part, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                p_part.append(line.strip())
        return dict_dmg, dmgtype, l_part, p_part

    def bool_match(self, content):   
        '''生物危害'''     
        # 致病生物危害--寄生虫危害
        bool_js = bool_yh = bool_zh = bool_ys = 0  
        jsc = ('尘螨', '蛔虫卵', '绦虫卵')
        # _is_jsc = re.compile('|'.join(jsc))
        for _ in jsc:
            if re.search(_, content):
                self.item_dict[_] = '有'
            else:
                self.item_dict[_] = '无'
        # for _ in _is_jsc.findall(content):
        #     if  _ in jsc:
        #         bool_js = self.item_dict[_] = 1
        #     else:
        #         self.item_dict[_] = 0
        if re.search(r'其[他它她]寄生虫', content): 
            bool_js, self.item_dict['其它寄生虫危害'] = 1, '有'
        else: 
            self.item_dict['其它寄生虫危害'] = '无'
        if bool_js: 
            self.item_dict['消费品二级危害类型'] += '寄生虫危害,'
            self.item_dict['消费品一级危害类型'] += '致病生物危害,'

        #致病微生物危害--原生微生物危害
        ys = ('甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒')
        ys_et = ('其它原生微生物', '其她原生微生物', '其他原生微生物', '过滤效率.{0,10}(达不到|不符合)', '病毒.{0,10}气溶胶')
        _is_ys = re.compile('|'.join(ys))
        _is_ys_et = re.compile('|'.join(ys_et))
        for _ in ys:
            if _ in _is_ys.findall(content):
                bool_ys, self.item_dict[_] = 1, '有' 
            else: 
                self.item_dict[_] = '无'
        if _is_ys_et.findall(content):
            bool_ys, self.item_dict['其它原生微生物危害'] = 1, '有' 
        else:
            self.item_dict['其它原生微生物危害'] = '无'
        if bool_ys: 
            self.item_dict['消费品二级危害类型'] += '原生微生物危害,'

        #致病微生物危害--真核细胞微生物危害
        zh = ('皮肤癣真菌', '着色真菌', '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌')
        zh_et = ('其它真核细胞微生物', '其她真核细胞微生物', '其他真核细胞微生物', '过滤效率.{0,10}(达不到|不符合)')
        _is_zh = re.compile('|'.join(zh))
        _is_zh_et = re.compile('|'.join(zh_et))
        for _ in zh:
            if _ in _is_zh.findall(content):
                bool_zh, self.item_dict[_] = 1, '有'
            else: 
                self.item_dict[_] = '无'
        if _is_zh_et.findall(content):
            bool_zh, self.item_dict['其它真核细胞微生物危害'] = 1, '有'
        else:
            self.item_dict['其它真核细胞微生物危害'] = '无'
        if bool_zh: 
            self.item_dict['消费品二级危害类型'] += '真核细胞微生物危害,'

        #致病微生物危害--原核细胞微生物危害
        yh = ('大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌')
        yh_et = ('其它原核细胞微生物', '其她原核细胞微生物', '其他原核细胞微生物', '过滤效率.{0,10}(达不到|不符合)')
        _is_yh = re.compile('|'.join(yh))
        _is_yh_et = re.compile('|'.join(yh_et))
        for _ in yh:
            if _ in _is_yh.findall(content):
                bool_yh, self.item_dict[_] = 1, '有'
            else:
                self.item_dict[_] = '无'
        if _is_yh_et.findall(content):
            bool_yh, self.item_dict['其它原核细胞微生物危害'] = 1, '有'
        else:
            self.item_dict['其它原核细胞微生物危害'] = '无'
        if bool_yh: 
            self.item_dict['消费品二级危害类型'] += '原核微生物危害,'

        self.item_dict['消费品一级危害类型'] += '致病微生物危害,' if bool_yh or bool_zh or bool_ys else ''
        self.item_dict['消费品危害类型'] += '生物危害,' if bool_js or bool_yh or bool_zh or bool_ys and '生物危害' not in self.item_dict['消费品危害类型'] else ''

    def chemistry(self, content):
        '''化学危害'''
        a = self.youji(content)
        b = self.wuji(content)
        if a or b and '化学危害' not in self.item_dict['消费品危害类型']:
            self.item_dict['消费品危害类型'] += '化学危害,'

    def youji(self, content):
        #有机毒物--有毒荃类化合物
        flag = 0
        ydq = ('甲醛', '乙醛', '丙烯醛')
        _is_ydq = re.compile('|'.join(ydq))
        for _ in ydq:
            self.item_dict[_] = '有' if _ in _is_ydq.findall(content) else '未知'
        if re.search(r'其[她它他]?有毒醛类?', content):
            self.item_dict['其它有毒醛类'] = '有'
            self.item_dict['消费品二级危害类型'] += '其它有毒醛类,'
            flag = 1
        else:
            self.item_dict['其它有毒醛类'] = '未知'

        #有机毒物--有毒芳香稠环类化合物
        ydfxc = 0
        if re.search(r'苯并（a）芘|芘类化合物', content):
            self.item_dict['芘类化合物'] = '有'
            ydfxc = 1
        else:
            self.item_dict['芘类化合物'] = '未知'

        if re.search(r'苯并（a）蒽|蒽类化合物', content):
            self.item_dict['蒽类化合物'] = '有'
            ydfxc = 1
        else:
            self.item_dict['蒽类化合物'] = '未知'
        if re.search(r'苯并（a）菲|菲类化合物', content):
            self.item_dict['菲类化合物'] = '有'
            ydfxc = 1
        else:
            self.item_dict['菲类化合物'] = '未知'
            
        ydfx_et = '(?:其[她它他])有毒芳香稠环类化合物|邻苯二甲酸|DEHP|DBP|BBP|䓛|三亚苯|苯并（b）荧蒽|苯并（k）荧蒽|二苯并（a，h）蒽|香精己基肉桂醛|芳樟醇|d-柠檬烯|香茅醇|香叶醇'
        _is_ydfx_et = re.compile(ydfx_et)
        if _is_ydfx_et.search(content):
            self.item_dict['其它有毒芳香稠环类化合物类'] = '有'
            ydfxc = 1
            flag = 1
        else:
            self.item_dict['其它有毒芳香稠环类化合物类'] = '未知'
        if ydfxc:
            self.item_dict['消费品二级危害类型'] += '有毒芳香稠环类化合物,'

        #有机毒物--有毒杂环类化合物
        ydzh = ('N-杂环化合物', 'S-杂环化合物', 'O-杂环化合物')
        ydzh_et = '(?:其[她它他])杂环类?化合物'
        _is_ydzh = re.compile('|'.join(ydzh))
        _is_ydzh_et = re.compile(ydzh_et)
        for _ in ydzh:
            self.item_dict[_] = '有' if _ in _is_ydzh.findall(content) else '未知'
        if _is_ydzh_et.search(content):
            self.item_dict['其它有毒杂环类化合物'] = '有'
            self.item_dict['消费品二级危害类型'] += '有毒杂环类化合物,'
            flag = 1
        else:
            self.item_dict['其它有毒杂环类化合物'] = '未知'

        #有机毒物--有毒有机氯化物
        ydyjl = ('有机氟化物', '有机氯化物', '有机溴化物')
        ydyjl_et = '(?:其[她它他])有毒有机氯化物'
        _is_ydyjl = re.compile('|'.join(ydyjl))
        _is_ydyjl_et = re.compile(ydyjl_et)
        for _ in ydyjl:
            self.item_dict[_] = '有' if _ in _is_ydyjl.findall(content) else '未知'
        if _is_ydyjl_et.search(content):
            self.item_dict['其它有毒有机氯化物'] = '有'
            self.item_dict['消费品二级危害类型'] += '有毒有机氯化物,'
            flag = 1
        else:
            self.item_dict['其它有毒有机氯化物'] = '未知'

        if flag == 1:
            self.item_dict['消费品一级危害类型'] += '有机毒物,'
        return flag

    def wuji(self, content):
        #无机毒物--有毒气体
        flag = 0
        ydq = ('一氧化氮', '一氧化碳', '氯气', '臭氧', '氯化氢', '硫化氢')
        ydq_et = '(?:其[她它他])有毒气体'
        _is_ydq = re.compile('|'.join(ydq))
        _is_ydq_et = re.compile(ydq_et)
        for _ in ydq:
            self.item_dict[_] = '有' if _ in _is_ydq.findall(content) else '未知'
        if _is_ydq_et.search(content):
            self.item_dict['其它有毒气体'] = '有'
            self.item_dict['消费品二级危害类型'] += '有毒气体危害,'
            flag = 1
        else:
            self.item_dict['其它有毒气体'] = '未知'

        #无机毒物--有毒重金属及其化合物危害
        ydfx = ('砷', '镉', '铬', '铜', '汞', '镍', '铅')
        ydfx_et = '(?:其[她它他]|等)?有毒重金属(?:及其)?化合物|硼.{0,4}(迁移|含量|量).{0,4}高|过量.{0,2}硼'
        _is_ydfx = re.compile('|'.join(ydfx))
        _is_ydfx_et = re.compile(ydfx_et)
        for _ in ydfx:
            self.item_dict[_] = '有' if _ in _is_ydfx.findall(content) else '未知'
        if _is_ydfx_et.search(content):
            self.item_dict['其它有毒重金属及其化合物'] = '有'
            self.item_dict['消费品二级危害类型'] += '有毒重金属及其化合物危害,'
            flag = 1
        else:
            self.item_dict['其它有毒重金属及其化合物'] = '未知'
            
        #无机毒物--有毒酸碱类危害
        ydzh = ('硫酸', '盐酸', '氢氧化钠')
        _is_ydzh = re.compile('|'.join(ydzh))
        ydsj = 0
        for _ in ydzh:
            self.item_dict[_] = '有' if _ in _is_ydzh.findall(content) else '未知'
        if re.search(r'(?:其[她它他])有毒酸碱类?|p[hH]值(超标|偏高|偏低)|酸碱度平衡', content):
            self.item_dict['其它有毒酸碱类物'] = '有'
            ydsj = flag = 1
        else:
            self.item_dict['其它有毒酸碱类物'] = '未知'
        if ydsj:
            self.item_dict['消费品二级危害类型'] += '有毒酸碱类危害,'

        #无机毒物--无机氰化物危害
        yh = ('氢氰酸', '氰化钾', '氰化氢')
        yh_et = '(?:其[她它他])无机氰化物'
        _is_yh = re.compile('|'.join(yh))
        _is_yh_et = re.compile(yh_et)
        for _ in yh:
            self.item_dict[_] = '有' if _ in _is_yh.findall(content) else '未知'
        if _is_yh_et.search(content):
            self.item_dict['其它无机氰化物'] = '未知'
            self.item_dict['消费品二级危害类型'] += '无机氰化物危害,'
            flag = 1
        else:
            self.item_dict['其它无机氰化物'] = '未知'

        if flag == 1:
            self.item_dict['消费品一级危害类型'] += '无机毒物危害,'
        return flag

    def env_match(self, content):
        '''使用环境危害-等'''
        # self.item_dict['消费者年龄'] = '空'
        _age = re.compile(r'(年龄|年纪)?[为|有]?([0-9]{0,3})[岁]')
        self.item_dict['消费者年龄'] = _.group(2) if (_ := _age.search(content)) != None else '未知'

        _sex_nv = re.compile(r'女士?|女性?')
        _sex_nan = re.compile(r'男士?|男性?')
        _sex = '女' if len(_sex_nv.findall(content)) > len(_sex_nan.findall(content)) else '男' if len(_sex_nan.findall(content)) >= 0 else '未知'
        self.item_dict['消费者性别'] = _sex

        if self.item_dict['涉及的消费品数量'] == 1:
            _numb = re.compile(r'数量[为有：:共计]+([0-9]*)[个位头袋只台包条张件撮勺合升斗石盘碗碟叠桶笼盆盒杯钟斛锅簋篮盘桶罐瓶壶卮盏箩箱煲啖袋钵]')
            self.item_dict['涉及的消费品数量'] = _.group(1) if (_ := _numb.search(content)) != None else 1

        self.item_dict['昼夜'] = '夜间' if re.search(r'黑?夜[晚间]?|晚上|傍晚|半夜', content) else '白天' if re.search(r'白天|昼|日间|上午|下午', content) else '未知'

        _fric = re.compile(r'(?:地面|陆地).{0,2}摩擦力?(大|小)')
        self.item_dict['地面摩擦'] = _.group(1) if (_ := _fric.search(content)) != None else '未知'

        self.item_dict['斜坡'] = '是' if re.search(r'斜坡', content) else '未知'
        self.item_dict['楼梯'] = '是' if re.search(r'楼梯', content) else '未知'
        self.item_dict['灰尘'] = '是' if re.search(r'灰尘|浮尘|浮灰', content) else '未知'
        self.item_dict['静电'] = '是' if re.search(r'静电', content) else '未知'
        self.item_dict['辐射'] = '是' if re.search(r'[^无]辐射', content) else '否' if re.search(r'无辐射', content) else '未知'
        
        _sem = re.compile(r'湿度[为有a-zA-Z]{0,2}([0-9.]{0,4})(%rh)?', re.I)
        self.item_dict['湿度'] = _.group(1) if (_ := _sem.search(content)) != None else '空'

        self.item_dict['腐蚀物'] = '有' if re.search(r'腐蚀物', content) else '无'

        _altitude = re.compile(r'海拔[为有]?([1-9]\d{0,5}.?\d{0,3}(km|m|米|千米))', re.I)
        self.item_dict['海拔'] = _.group(1) if (_ := _altitude.search(content)) != None else '空'

        _tem = re.compile(r'温度[为有a-zA-Z]{0,2}([0-9.]{1,4})[华摄氏度°]?')
        self.item_dict['温度'] = _.group(1) if (_ := _tem.search(content)) != None else '空'

        self.item_dict['坎坷'] = '是' if re.search(r'坎坷', content) else '未知'
        self.item_dict['爬坡'] = '是' if re.search(r'爬坡', content) else '未知'
        self.item_dict['下坡'] = '是' if re.search(r'下坡', content) else '未知'

        _speed = re.compile(r'(速度|时速|秒速)[为是有]?([0-9a-zA-Z]*[/每][s秒分钟时mhSMHd天])')
        self.item_dict['速度'] = _.group(2) if (_ := _speed.search(content)) != None else '空'

        self.item_dict['稳定性'] = '否' if re.search(r'不稳定', content) else '是' if re.search(r'稳定', content) else '空'
        self.item_dict['腐蚀性'] = '是' if re.search(r'腐蚀性', content) else '否'

    def physic_damage(self, content):
        '''物理危害'''
        a = self.warning_loss(content)
        b = self.radio_damage(content)
        c = self.temp_damage(content)
        d = self.elec_damage(content)
        e = self.noise_damage(content)
        f = self.bomb_damage(content)
        g = self.machine_damage(content)

        if a or b or c or d or e or f or g and '物理危害' not in self.item_dict['消费品危害类型']:
            self.item_dict['消费品危害类型'] += '物理危害,'

    def warning_loss(self, content):
        '''警示标识缺失'''
        r_loss = re.compile('警[示告戒][标识牌][丢遗缺]失?|[无少失丢遗缺][少失弃掉]?.{0,4}警[示告戒][标识牌]?')
        if r_loss.search(content):
            self.item_dict['警示标识丢失'] = '是'
            self.item_dict['消费品二级危害类型'] += '警示标识缺失,'
            self.item_dict['消费品一级危害类型'] += '警示标识缺失,'
            return 1
        else:
            self.item_dict['警示标识缺失'] = '未知'
            return 0

    def radio_damage(self, content):
        '''辐射危害'''
        flag = 0
        # 热辐射危害
        _is_hot = re.compile('热辐射')
        if _is_hot.search(content):
            self.item_dict['热辐射危害'] = '是'
            self.item_dict['消费品二级危害类型'] += '热辐射危害,'
        else:
            self.item_dict['热辐射危害'] = '未知'
        # 射线辐射危害
        _is_laser = re.compile('激光(辐射)?')
        _is_ultray = re.compile('紫外线(辐射)?')
        _is_xray = re.compile('[xX]-?[光射]线(辐射)?')
        if _is_laser.search(content) or _is_ultray.search(content) or _is_xray.search(content):
            self.item_dict['消费品二级危害类型'] += '射线辐射危害,'
            flag = 1
        self.item_dict['激光辐射'] = '有' if _is_laser.search(content) else '无'
        self.item_dict['紫外线辐射'] = '有' if _is_ultray.search(content) else '无'
        self.item_dict['X光线辐射'] = '有' if _is_xray.search(content) else '无'
        # 电磁辐射危害
        _is_high = re.compile('高频电磁(辐射)?')
        _is_low = re.compile('低频电磁(辐射)?')
        if _is_high.search(content) or _is_low.search(content):
            self.item_dict['消费品二级危害类型'] += '电磁辐射危害,'
            flag = 1
        self.item_dict['高频电磁辐射'] = '是' if _is_high.search(content) else '未知'
        self.item_dict['低频电磁辐射'] = '是' if _is_low.search(content) else '未知'

        if flag:
            self.item_dict['消费品一级危害类型'] += '辐射危害,'
        return flag

    def temp_damage(self, content):
        '''高/低温物质危害'''
        '''TODO'''
        flag, hdmg, ldmg = 0, 0, 0
        # 高低温物质危害
        sl = ('高温气体', '低温表面', '低温液体', '低温气体', '明火')
        _is_tmpdmg = re.compile('|'.join(sl))
        tmp = _is_tmpdmg.findall(content)
        for _ in sl:
            self.item_dict[_] = '有' if _ in tmp else '未知'
        if re.search(r'[高超].{0,10}[度°].{0,10}[水液]|高温液体', content):
            self.item_dict['高温液体'] = '有'
            hdmg = flag = 1
        else:
            self.item_dict['高温液体'] = '未知'
        if re.search(r'烧伤|烫伤|高温表面', content):
            self.item_dict['高温表面'] = '有'
            hdmg = flag = 1
        else:
            self.item_dict['高温表面'] = '未知'

        if tmp != []:
            flag = 1
            for _ in tmp:
                if '高' or '明火' in _:
                    hdmg = 1
                if '低' in _:
                    ldmg = 1

        if re.search(r'起火|燃烧|火灾', content):
            self.item_dict['明火'] = '是'
            hdmg = flag = 1
        else:
            self.item_dict['明火'] = '未知'

        self.item_dict['消费品二级危害类型'] += '高温物质危害,' if hdmg else ''
        self.item_dict['消费品二级危害类型'] += '低温物质危害,' if ldmg else ''
        self.item_dict['消费品一级危害类型'] += '高/低温物质危害,' if flag else ''
        return flag

    def elec_damage(self, content):
        '''电器危害'''
        flag, bool_cd, bool_dq = 0, 0, 0
        '''触电危害'''
        sl = ('接触不良', '铁芯发热', '散热不良')
        _is_cddmg = re.compile('|'.join(sl))
        tmp = _is_cddmg.findall(content)

        if re.search(r'短路', content):
            self.item_dict['短路'] = '是'
            bool_cd = 1
        else:
            self.item_dict['短路'] = '未知'

        if re.search(r'漏电|触电', content):
            self.item_dict['漏电'] = '是'
            bool_cd = 1
        else:
            self.item_dict['漏电'] = '未知'
        if re.search(r'电压高|电压.{0,5}击穿|[高低]电压', content):
            self.item_dict['高低电压'] = '是'
            bool_cd = 1
        else:
            self.item_dict['高低电压'] = '未知' 
        if re.search(r'过热|耐热.{0,5}不[合符合]', content):
            self.item_dict['过热'] = '是'
            bool_cd = 1
        else:
            self.item_dict['过热'] = '未知'
        if bool_cd: self.item_dict['消费品二级危害类型'] += '触电危害,'

        '''电气爆炸'''
        for _ in sl:
            self.item_dict[_] = '是' if _ in tmp else '未知'
            if _ in tmp:    bool_dq = 1
        if re.search(r'电[动瓶](自行)?车.{0,15}(火灾|起火|引燃|爆燃|烧毁)|(火灾|起火|爆燃|引燃|烧毁).{0,15}电[动瓶](自行)?车', content):
            bool_dq = 1
            self.item_dict['过热'] = '是'
        if bool_dq: self.item_dict['消费品二级危害类型'] += '电气爆炸,'

        flag = bool_cd or bool_dq
        if flag: self.item_dict['消费品一级危害类型'] += '电气危害,'
        return flag

    def noise_damage(self, content):
        ''''''
        flag = 0
        self.item_dict['稳定性噪音危害'] = '未知'
        self.item_dict['变动性噪音危害'] = '未知'
        self.item_dict['脉冲性噪音危害'] = '未知'

        if re.search(r'稳定[性]噪[音声]危?伤?害?|声压.{0,4}大', content):
            self.item_dict['稳定性噪音危害'] = '有'
            self.item_dict['消费品二级危害类型'] += '稳定性噪音危害,'
            flag = 1
        if re.search(r'变动[性]噪[音声]危?伤?害?', content):
            self.item_dict['变动性噪音危害'] = '有'
            self.item_dict['消费品二级危害类型'] += '变动性噪音危害,'
            flag = 1
        if re.search(r'脉冲[性]噪[音声]危?伤?害?', content):
            self.item_dict['脉冲性噪音危害'] = '有'
            self.item_dict['消费品二级危害类型'] += '脉冲性噪音危害,'
            flag = 1
        if flag:    self.item_dict['消费品一级危害类型'] += '噪声危害,'
        return flag

    def bomb_damage(self, content):
        '''爆炸危害'''
        flag, bq, bf, bp, jb, zb, yb, bh, gb, qx, yx, gx= 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        if re.search(r'爆炸性气[体]', content):
            flag = bq = qx = 1
        if re.search(r'爆炸[性]粉尘', content):
            flag = bf = qx = 1
        if re.search(r'爆炸[性]喷雾', content):
            flag = bp = qx = 1
        self.item_dict['消费品二级危害类型'] += '气相爆炸危害,' if qx else ''
        if re.search(r'聚合爆炸', content):
            flag = jb = yx = 1
        if re.search(r'蒸发爆炸', content):
            flag = zb = yx = 1
        if re.search(r'液体混合爆炸|煤气罐.{0,8}爆炸', content):
            flag = yb = yx = 1
        self.item_dict['消费品二级危害类型'] += '液相爆炸危害,' if yx else ''
        if re.search(r'爆炸[性]化合物', content):
            flag = bh = gx = 1
        if re.search(r'固体爆炸性物质|(手机|空调|冰箱|电器).{0,10}爆炸', content):
            flag = gb = gx = 1

        self.item_dict['爆炸性气体'] = '有' if bq else '未知'
        self.item_dict['爆炸性化合物'] = '有' if bh else '未知'
        self.item_dict['爆炸性粉尘'] = '有' if bf else '未知'
        self.item_dict['爆炸性喷雾'] = '有' if bp else '未知'
        self.item_dict['聚合爆炸'] = '有' if jb else '未知'
        self.item_dict['蒸发爆炸'] = '有' if zb else '未知'
        self.item_dict['液体混合爆炸'] = '有' if yb else '未知'
        self.item_dict['固体爆炸性物质'] = '有' if gb else '未知'

        if gx:
            self.item_dict['消费品二级危害类型'] += '固相爆炸危害,'
        if flag:
            self.item_dict['消费品一级危害类型'] += '爆炸危害,' 
        return flag

    def machine_damage(self, content):
        '''机械危害'''
        a = self.latent_damage(content)
        b = self.move_damage(content)
        c = self.shape_damage(content)
        if a or b or c:
            self.item_dict['消费品一级危害类型'] += '机械危害,'
            return 1
        return 0

    def move_damage(self, content):
        '''动能危害'''
        flag = 0
        self.item_dict['爆炸性气体'] = '未知'
        self.item_dict['旋转部件牵扯'] = '未知'
        self.item_dict['飞行物体撞击'] = '未知'
        self.item_dict['移动部件挤压'] = '未知'

        if re.search(r'移动状态撞击', content):
            self.item_dict['爆炸性气体'] = '是'
            flag = 1
        if re.search(r'旋转部件牵扯', content):
            self.item_dict['旋转部件牵扯'] = '是'
            flag = 1
        if re.search(r'飞行物体撞击', content):
            self.item_dict['飞行物体撞击'] = '是'
            flag = 1
        if re.search(r'移动部件挤压', content):
            self.item_dict['移动部件挤压'] = '是'
            flag = 1
        self.item_dict['消费品二级危害类型'] += '动能危害,' if flag else ''
        return flag

    def latent_damage(self, content):
        '''潜在能量危害'''
        flag = wd = qd = tx = yl = 0
        wd = 1
        if re.search(r'机械较?[不]稳定|断裂', content):
            flag, wd = 1, 0
        if re.search(r'机械强度[较略]?[低少劣差]|机械强度不够|断裂强力.{0,4}不符', content): 
            flag = qd = 1 
        if re.search(r'弹性(组件|部件)失控', content): 
            flag = tx = 1 
        if re.search(r'压力空间失控', content): 
            flag = yl = 1 
        self.item_dict['机械稳定性'] = '是' if wd else '未知'
        self.item_dict['机械强度'] = '是' if qd else '未知'
        self.item_dict['弹性组件失控'] = '是' if tx else '未知'
        self.item_dict['压力空间失控'] = '是' if yl else '未知'
        if flag:
            self.item_dict['消费品二级危害类型'] += '潜在能量危害,'
        return flag

    def shape_damage(self, content):
        '''形状和表面性能危害'''
        _size = re.compile(r'(规格|尺寸|型号)[为]?(.{0,8}(ml|m))?[，）]?')
        self.item_dict['尺寸'] = _.group(2) if (_ := _size.search(content)) != None else '未知'
        
        flag = lines = butx = fill = kongxi = rl = jianj = 0

        if re.search(r'绳索|口罩带', content):
            flag = lines = 1
        if re.search(r'不透气|气密性不足', content):
            flag = butx = 1
        if re.search(r'填充物', content):
            flag = fill = 1
        if re.search(r'[部组]件[有含]?空隙|开口|[空孔间].{0,2}[隙洞].{0,2}不符|孔洞', content):
            flag = kongxi = 1
        if re.search(r'尖角|锐利尖端|尖端', content):
            flag = jianj = 1
        if  re.search(r'[锋锐]利边[缘部角]?|锐利边', content):
            flag = rl = 1
        
        for _ in self.LPart:
            if re.search(_, content):
                self.item_dict['小零件'] += _ + ','
                flag = 1
        if self.item_dict['小零件'] == '':
            if re.search(r'(产生|形成)小[部零]件', content):
                self.item_dict['小零件'] += '有'

        for _ in self.PPart:
            if re.search(_, content):
                self.item_dict['消费品问题部件'] += _ + ','
                flag = 1

                
        if re.search(r'光滑表面?|表[面.]光滑', content):
            self.item_dict['光滑表面'], self.item_dict['粗糙表面'] = '是', '否'
        elif re.search(r'粗糙表面?|表[面.]粗糙', content):
            self.item_dict['光滑表面'], self.item_dict['粗糙表面'] = '否', '是'
        else:
            self.item_dict['光滑表面'] = self.item_dict['粗糙表面'] = '未知'
        self.item_dict['绳索及类似物'] = '有' if lines else '未知'
        self.item_dict['不透气'] = '是' if butx else '否'
        self.item_dict['填充物'] = '有' if fill else '未知'
        self.item_dict['锐利边缘'] = '有' if rl else '未知'
        self.item_dict['部件空隙或开口'] = '有' if kongxi else '未知'
        self.item_dict['尖角'] = '有' if jianj else '未知'

        if flag:
            self.item_dict['消费品二级危害类型'] += '形状和表面性能危害,'
        return flag

    def damage_type(self, content):
        '''伤害类型'''
        self.item_dict['严重程度'] = 0
        self.item_dict['伤害类型'] = ''
        for _ in self.DmgTypeMap:
            if re.search('|'.join(_[1:]), content):
                self.item_dict['伤害类型'] += _[0] + ','
                self.item_dict['严重程度'] = max(self.item_dict['严重程度'], self.Dict_Dmg[_[0]])


    def findCity(self, dict):
        tmp = []
        for i in self.city_dict:
            # print(i)
            if i['deep'] == '1' or i['deep'] == '0':
                tmp.append(i)
            if i['id'] == dict['pid'] and i['deep'] == '0':
                return i['name']
            elif i['id'] == dict['pid']:
                while tmp and int(tmp[-1]['deep']) > 0:
                    # print(tmp)
                    tmp.pop()
                return tmp[-1]['name'] if tmp else '不详'

    def other_re(self, content):

        self.item_dict['伤害事件'] = content
        '''匹配商品名字及商品类型'''
        if self.item_dict['消费品名称'] == '' or self.item_dict['消费品一级类别'] == '':
            # print(self.item_dict['消费品名称'])
            with open(self.F_GoodsName, 'r', encoding='utf-8') as part:
                goods = csv.DictReader(part)
                for good in goods:
                    # print(good)
                    _ = good['消费品名称'].replace('(', '\(').replace(')', '\)')
                    if re.search(_, content) or re.search(_, self.item_dict['事件标题']):
                        if self.item_dict['消费品名称'] == '':
                            self.item_dict['消费品名称'] = good['消费品名称']
                        if self.item_dict['消费品一级类别'] == '':
                            self.item_dict['消费品一级类别'] = good['消费品一级类别']
                        if self.item_dict['消费品二级类别'] == '空' and good['消费品二级类别']:
                            self.item_dict['消费品二级类别'] = good['消费品二级类别']
                        break
                    # TODO
                    # 多个名称相匹配 找出最优解
                    # example: 东风汽车 东风汽车V型
        if self.item_dict['区域'] == '不详' and self.item_dict['国家'] == '中国':
            # print(self.city_dict)
            flag = 1
            if re.search(r'(.{2})省(.{1,6})市', content):
                self.item_dict['区域'] = re.search(r'(.{2})省(.{1,6})市', content).group(1)
            else:
                # print(self.city_dict)
                for _ in self.city_dict:
                    if re.search(f"{_['name']}[市区]", content):
                        if _['deep'] == '0':
                            self.item_dict['区域'] = _['name']
                        else:
                            # print(_, 123)
                            self.item_dict['区域'] = self.findCity(_)
                            # print(self.item_dict['区域'])
                        flag = 0
                        break
                if flag:
                    for _ in self.city_dict:
                        if re.search(_['name'], content) or re.search(_['name'], self.item_dict['事件标题']):
                            if _['deep'] == '0':
                                self.item_dict['区域'] = _['name']
                            else:
                                # print(_, 123)
                                self.item_dict['区域'] = self.findCity(_)
                                # print(self.item_dict['区域'])
                            break

        '''消费者受教育程度，职业等'''

        self.item_dict['消费者受教育程度'] = '未知'
        if re.search('(初中|小学).*学?[历位][毕肆业]?', content):
            self.item_dict['消费者受教育程度'] = '初中以下'
        elif re.search('(中专|高中)的?(学历|毕业|肆业)|技校(毕业|肆业)?', content):
            self.item_dict['消费者受教育程度'] = '高中/中专/技校'
        elif re.search('大专[毕肆业]?(学位)?', content):
            self.item_dict['消费者受教育程度'] = '大专'
        elif re.search('本科|大学生|研究生|硕士|博士|博士后|副教授|教授|院士|学士', content):
            self.item_dict['消费者受教育程度'] = '本科及以上'

        self.item_dict['消费者职业'] = '未知'
        self.item_dict['健康状况'] = '未知'
        if not re.search(r'[危害不亚].{0,4}健康', content) and re.search(r'身体(条件|状况|情况)?(良好|健康)', content):
            self.item_dict['健康状况'] = 4
        elif re.search(r'亚健康|身体(状况|情况|状态)(较好|一般)', content):
            self.item_dict['健康状况'] = 3
        elif re.search(r'身体(条件|状况|情况)?较?(不好|差)', content):
            self.item_dict['健康状况'] = 2
        elif re.search(r'重病', content):
            self.item_dict['健康状况'] = 1

        if re.search(r'国家机关|党群组织|(企业|事业)单位负责人', content):
            self.item_dict['消费者职业'] = '国家机关/党群组织/企业/事业单位负责人'
        elif re.search(r'专业技术人员', content):
            self.item_dict['消费者职业'] = '专业技术人员'
        elif re.search(r'办事人员|有关人员', content):
            self.item_dict['消费者职业'] = '办事人员和有关人员'
        elif re.search(r'(商|服务)[行从]业?人员|店员|服务员', content):
            self.item_dict['消费者职业'] = '商业/服务业人员'
        elif re.search(r'农民|伐木工|牧民|渔民|水利工作者|水利工作人员', content):
            self.item_dict['消费者职业'] = '农/林/牧/渔/水利业生产人员'
        elif re.search(r'(生产|运输)设备操作人员及有关人员', content):
            self.item_dict['消费者职业'] = '生产/运输设备操作人员及有关人员'
        elif re.search(r'武警|伞兵|空降兵|火箭军|军人|士兵|军官|[^过程][上中下大少][士尉校将]', content):
            self.item_dict['消费者职业'] = '军人'
        elif re.search(r'特殊行业', content):
            self.item_dict['消费者职业'] = '其它'

    def add_3rdDmg(self):
        phsics = ['机械危害', '爆炸危害', '噪声危害', '电气危害', '高/低温物质危害', '警示标识缺失', '辐射危害']
        chemis = ['无机毒物危害', '有机毒物']
        biolog = ['致病微生物危害', '致病生物危害']
        if '物理危害' not in self.item_dict['消费品危害类型']:
            for w in phsics:
                if w in self.item_dict['消费品一级危害类型']:
                    self.item_dict['消费品危害类型'] += '物理危害,'
                    break
        if '化学危害' not in self.item_dict['消费品危害类型']:
            for w in chemis:
                if w in self.item_dict['消费品一级危害类型']:
                    self.item_dict['消费品危害类型'] += '化学危害,'
                    break
        if '生物危害' not in self.item_dict['消费品危害类型']:
            for w in biolog:
                if w in self.item_dict['消费品一级危害类型']:
                    self.item_dict['消费品危害类型'] += '生物危害,'
                    break
    def final(self, data):
        for k in data:
            if '一级危害因素' in k and data[k] not in self.item_dict['消费品一级危害类型']:
                self.item_dict['消费品一级危害类型']  += data[k]
            if '二级危害因素' in k or '二级级危害因素' in k and data[k] not in self.item_dict['消费品二级危害类型']:
                self.item_dict['消费品二级危害类型']  += data[k]
        if self.item_dict['消费品一级危害类型']:
            self.add_3rdDmg()


    def discrib(self, data, _from, country, cond='', src=''):

        self.item_dict['危害情况'] = '人身安全' if not cond else data[cond]
        self.item_dict['危害源'] = data[src] if src else '空'

        self.item_dict['事件来源'] = _from
        self.item_dict['消费品名称'] = ''
        self.item_dict['消费品一级类别'] = ''
        self.item_dict['消费品二级类别'] = '空'
        self.item_dict['消费品一级危害类型'] = ''
        self.item_dict['消费品二级危害类型'] = ''
        self.item_dict['链接'] = data['链接'] if '链接' in data else data['页面地址'] if '页面地址' in data else '空'
        self.item_dict['区域'] = '不详'
        self.item_dict['日期'] = data['日期'] if '日期' in data else data['召回时间'] if '召回时间' in data else '空'
        self.item_dict['涉及的消费品数量'] = 1
        self.item_dict['事件标题'] = '空'
        for k in data:
            if '数量' in k:
                try:
                    self.item_dict['涉及的消费品数量'] = int(data[k].replace(',', '').replace('、', ''))
                except:
                    pass
                # print(self.item_dict['涉及的消费品数量'])
            if '标题' in k:
                self.item_dict['事件标题'] = data[k]
            if '日期' in k:
                self.item_dict['日期'] = data[k]
            if '发布国家' in k:
                self.item_dict['国家'] = data[k] if data[k] != '未知' else '不详'
            if '产品名称' in k or '具体产品' in k:
                self.item_dict['消费品名称'] = data[k]
                # print(self.item_dict['消费品名称'])
            if '产品类别' in k or '产品分类' in k or '产品大类' in k:
                self.item_dict['消费品一级类别'] = data[k]
            # if '一级危害因素' in k:
            #     self.item_dict['消费品一级危害类型']  += data[k]
            # if '二级级危害因素' in k:
            #     self.item_dict['消费品二级危害类型']  += data[k]

            ##### 令人窒息的bug！！！！！    
            # if '召回地区' in k or '区域' in k:
            #     # print(k)
            #     if data[k] in self.country_list:
            #         self.item_dict['国家'] = data[k]
            #     elif data[k] in self.region_list:
            #         self.item_dict['区域'] = data[k]
            #     else:
            #         self.item_dict['区域'] = '不详'
        # print(self.item_dict['区域'])
        if country or '国家' not in self.item_dict:
            self.item_dict['国家'] = country

        # self.item_dict['事件标题'] = data['事件标题'] if '事件标题' in data else data['标题内容'] if '标题内容' in data else '空'

    def build_dict(self, data):
        '''build dict list of data'''
        for _ in data:
            self.add_item(_)

    def add_item(self, data, content, _from, cond, country, src):

        '''添加一条数据至csv_list'''
        self.discrib(data, _from, country, cond, src)
        self.bool_match(content)
        self.chemistry(content)
        self.physic_damage(content)
        self.env_match(content)
        self.damage_type(content)
        # print(self.item_dict)
        self.other_re(content)
        self.final(data)
        self.item_dict['消费品一级危害类型'] = self.item_dict['消费品一级危害类型'].rstrip(',')
        self.item_dict['消费品二级危害类型'] = self.item_dict['消费品二级危害类型'].rstrip(',')
        self.item_dict['消费品危害类型'] = self.item_dict['消费品危害类型'].rstrip(',')
        self.item_dict['伤害类型'] = self.item_dict['伤害类型'].rstrip(',')
        self.item_dict['小零件'] = self.item_dict['小零件'].rstrip(',')
        self.item_dict['消费品问题部件'] = self.item_dict['消费品问题部件'].rstrip(',')
        for k in self.item_dict:
            if self.item_dict[k] == '':
                self.item_dict[k] = '未知'
        # if self.item_dict['消费品名称'] != '未知' and self.item_dict['伤害类型'] != '未知' and self.item_dict['消费品危害类型'] != '未知':
            # self.csv_list.append(self.item_dict)
        if self.item_dict['消费品名称'] != '未知':
            self.csv_list.append(self.item_dict)
        self.item_dict = {}
        self.item_dict['消费品危害类型'] = ''
        self.item_dict['小零件'] = ''
        self.item_dict['消费品问题部件'] = ''

    def writetocsv(self, encoding='utf-8'):
        """
        ## description  :
        将csv_list写入objfpath对应的csv文件
        """
        out = pd.DataFrame(self.csv_list)
        header = [
            '日期', '事件标题', '国家', '区域', '消费品名称', '涉及的消费品数量', '伤害事件', '事件来源', '消费品一级类别', '消费品二级类别', '链接', '伤害类型', '严重程度', '危害情况', '危害源', '消费品危害类型', '消费品一级危害类型', '消费品二级危害类型', '消费者年龄', '消费者受教育程度', '消费者职业', '健康状况', '消费品问题部件',
            '尺寸', '绳索及类似物', '不透气', '填充物', '锐利边缘', '部件空隙或开口', '尖角', '光滑表面', '粗糙表面', '小零件', '昼夜', '温度', '湿度', '海拔',
            '稳定性', '腐蚀性', '速度', '腐蚀物', '坎坷', '爬坡', '下坡', '地面摩擦', '斜坡', '楼梯', '灰尘', '静电', '辐射', '警示标识缺失',
            '高温表面', '高温液体', '高温气体', '低温表面', '低温液体', '低温气体', '明火', '高低电压', '过热', '漏电', '短路', '接触不良', '铁芯发热', '散热不良',
            '稳定性噪音危害', '变动性噪音危害', '脉冲性噪音危害', '爆炸性气体', '爆炸性粉尘', '爆炸性喷雾', '聚合爆炸', '蒸发爆炸', '液体混合爆炸', '爆炸性化合物', '固体爆炸性物质',
            '爆炸性气体', '旋转部件牵扯', '飞行物体撞击', '移动部件挤压', '机械稳定性', '机械强度', '弹性组件失控', '压力空间失控',
            '热辐射危害', '激光辐射', '紫外线辐射', 'X光线辐射', '高频电磁辐射', '低频电磁辐射',
            '甲醛', '乙醛', '丙烯醛', '其它有毒醛类', '蒽类化合物', '菲类化合物', '芘类化合物', '其它有毒芳香稠环类化合物类', 'N-杂环化合物', 'S-杂环化合物', 
            'O-杂环化合物', '其它有毒杂环类化合物', '有机氟化物', '有机氯化物', '有机溴化物', '其它有毒有机氯化物', '一氧化氮', '一氧化碳', '氯气', '臭氧', 
            '氯化氢', '硫化氢', '其它有毒气体', '砷', '镉', '铬', '铜', '汞', '镍', '铅', '其它有毒重金属及其化合物', '硫酸', '盐酸', '氢氧化钠', '其它有毒酸碱类物', 
            '氢氰酸', '氰化钾', '氰化氢', '其它无机氰化物',
            '尘螨', '蛔虫卵', '绦虫卵', '其它寄生虫危害', '甲肝病毒', '甲型流感病毒', '轮状病毒', '禽流感病毒', '其它原生微生物危害', '皮肤癣真菌', '着色真菌', 
            '孢子丝菌', '新生隐球菌', '假丝酵母菌', '曲霉', '毛霉', '卡氏肺孢菌', '其它真核细胞微生物危害', '大肠杆菌', '沙门氏菌', '副溶血性弧菌', '金黄色葡萄球菌', '腊样芽孢肝菌', '其它原核细胞微生物危害'
            ]
        out.to_csv(self.objfilepath, encoding=encoding, sep='\t', columns=header, na_rep='')
        
if __name__ == '__main__':
    a = Item_data('')
    text = '本次召回规格为100只装170ml的井甜加厚航空杯，涉及数量为780袋。本次召回范围内的加厚航空杯产品在称装了一定量的高于80°的液体之后会出现较大变形甚至爆炸，导致消费者在使用过程中将难以拿捏，手握时易变形，如水温更高，可能会造成烫伤，存在安全隐患，'
    datas = {'召回时间':1, '标题内容': 1, '召回地区': 1, '页面地址': 1 }
    # # text = '200ml航空杯，涉及数量分别为260台、52台。 本次召回范围内的航空杯，由于在生产过程中擦伤工艺设置不合理，死亡导致负重性能不达标，可能存在烫伤使用者的安全隐患'
    # # a.latent_damage(text)
    print('源文本', text)
    a.add_item(datas, text)
    print('抽取部分关键特征：')
    print('消费品名称', a.csv_list[0]['消费品名称'])
    print('涉及的消费品数量', a.csv_list[0]['涉及的消费品数量'])
    print('尺寸', a.csv_list[0]['尺寸'])
    print('伤害事件', a.csv_list[0]['伤害事件'])
    print('伤害类型', a.csv_list[0]['伤害类型'])
    print('严重程度', a.csv_list[0]['严重程度'])
    print('消费品危害类型', a.csv_list[0]['消费品危害类型'])
    print('消费品一级危害类型', a.csv_list[0]['消费品一级危害类型'])
    print('消费品二级危害类型', a.csv_list[0]['消费品二级危害类型'])
    
    # # res = re.findall('划伤|划烂|划破', text)
    # # print(res)
    # # print('|'.join(a.DmgTypeMap[0][1:]))
    # # a.writetocsv() 
    # # 
    # out = pd.DataFrame(a.csv_list)
    # objfilepath = '../data/result/aaaaa.tsv'
    # out.to_csv(objfilepath, encoding='utf-8', sep='\t', na_rep='')
    # for h in header:
    #     print(a.csv_list[0][h])
    # print(len(header))
