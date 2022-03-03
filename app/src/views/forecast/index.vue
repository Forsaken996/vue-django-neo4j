<template>
  <div class="app-container">
    <el-divider content-position="left"
      >请填写消费品名称及消费品类型</el-divider
    >

    <div style="margin-bottom: 50px">
      <el-input
        v-model="productname"
        placeholder="请输入消费品名称"
        style="width: 200px; margin-left: 10px"
      />

      <el-cascader
        v-model="product_sort"
        :options="product_sorts"
        placeholder="请选择消费品类型"
        style="width: 250px; margin-left: 20px"
      >
      </el-cascader>
    </div>

    <el-divider content-position="left">请填写消费品特征</el-divider>

    <el-table
      :data="productfeatures"
      stripe
      width="100%"
      style="margin-bottom: 50px"
    >
      <el-table-column
        v-for="(item, i) in productcolumns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="120%"
      >
        <template slot-scope="scope">
          <div
            v-if="
              scope.$index == productfeatures.length - 1 &&
              productcolumns[i] == '特征属性'
            "
          >
            <el-cascader
              :options="product_ops"
              v-model="product_op"
              @change="harmselect(scope.row)"
            >
              <template slot-scope="{ node, data }">
                <span>{{ data.label }}</span>
                <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
              </template>
            </el-cascader>
          </div>
          <div
            v-else-if="
              scope.$index == productfeatures.length - 1 &&
              productcolumns[i] == '小零件' &&
              scope.row[0] == '小零件'
            "
          >
            <div>
              <el-input
                v-model="scope.row[i]"
                placeholder="请输入内容"
                clearable
              ></el-input>
            </div>
          </div>
          <div
            v-else-if="
              scope.$index == productfeatures.length - 1 &&
              scope.row[0] == '涉及的消费品数量' &&
              productcolumns[i] == '涉及的消费品数量'
            "
          >
            <el-input
              v-model="scope.row[i]"
              placeholder="请输入内容"
              clearable
            ></el-input>
          </div>
          <div v-else>
            {{ scope.row[i] }}
          </div>
        </template>
      </el-table-column>
      <el-table-column min-width="150%">
        <template slot-scope="scope">
          <el-button v-if="scope.$index == productfeatures.length - 1" @click="AddProduct(scope.row)"> 添加 </el-button>
          <el-button
            v-if="scope.$index != productfeatures.length - 1"
            type="danger"
            @click="DeleteProduct(scope.row, scope.$index)"
            >删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left">请填写消费者特征</el-divider>

    <el-table
      :data="consumerfeatures"
      stripe
      width="100%"
      style="margin-bottom: 50px"
    >
      <el-table-column
        v-for="(item, i) in consumercolumns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="120%"
      >
        <template slot-scope="scope">
          <div
            v-if="
              scope.$index == consumerfeatures.length - 1 &&
              consumercolumns[i] == '一级属性名称'
            "
          >
            <el-cascader
              :options="consumer_ops"
              v-model="consumer_op"
              @change="consumerselect(scope.row)"
            >
              <template slot-scope="{ node, data }">
                <span>{{ data.label }}</span>
                <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
              </template>
            </el-cascader>
          </div>
          <div v-else>
            {{ scope.row[i] }}
          </div>
        </template>
      </el-table-column>
      <el-table-column min-width="150%">
        <template slot-scope="scope">
          <el-button @click="AddConsumer(scope.row)"> 添加 </el-button>
          <el-button
            v-if="scope.$index != consumerfeatures.length - 1"
            type="danger"
            @click="DeleteConsumer(scope.row, scope.$index)"
            >删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left">请填写环境特征</el-divider>

    <el-table
      :data="envfeatures"
      stripe
      width="100%"
      style="margin-bottom: 50px"
    >
      <el-table-column
        v-for="(item, i) in envcolumns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="120%"
      >
        <template slot-scope="scope">
          <div
            v-if="
              scope.$index == envfeatures.length - 1 &&
              envcolumns[i] == '一级属性名称'
            "
          >
            <el-cascader
              :options="env_ops"
              v-model="env_op"
              @change="envselect(scope.row)"
            >
              <template slot-scope="{ node, data }">
                <span>{{ data.label }}</span>
                <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
              </template>
            </el-cascader>
          </div>
          <div v-else>
            {{ scope.row[i] }}
          </div>
        </template>
      </el-table-column>
      <el-table-column min-width="150%">
        <template slot-scope="scope">
          <el-button @click="AddEnv(scope.row)"> 添加 </el-button>
          <el-button
            v-if="scope.$index != envfeatures.length - 1"
            type="danger"
            @click="DeleteEnv(scope.row, scope.$index)"
            >删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-bottom: 50px">
      <el-button type="primary" @click="forecast()">评估</el-button>
      <template>
        <el-popconfirm
          confirm-button-text="好的"
          cancel-button-text="不用了"
          icon="el-icon-info"
          icon-color="red"
          confirm-button-type="danger"
          title="确定重置所有内容吗"
          @onConfirm="reset()"
        >
          <el-button slot="reference" style="margin-left: 10px" type="danger"
            >重置</el-button
          >
        </el-popconfirm>
      </template>
    </div>

    <div v-if="isforecast">
      <el-divider content-position="left">评估结果</el-divider>
      <div
        v-loading="loading"
        element-loading-text="拼命加载中"
        element-loading-spinner="el-icon-loading"
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table :data="forecastend" stripe width="100%">
          <el-table-column
            v-for="(item, i) in forecastcolumns"
            :key="i"
            :label="item"
            show-overflow-tooltip
            min-width="120%"
          >
            <template slot-scope="scope">
              <div>
                {{ scope.row[i] }}
              </div>
            </template>
          </el-table-column>
        </el-table>

        <el-divider content-position="left">影响危害的主要特征</el-divider>
        <el-tag
          v-for="(item, i) in harmfeatures"
          :key="i"
          :label="item"
          :value="item"
          :type="i % 2 == 0 ? 'primary' : 'success'"
          :disable-transitions="false"
          style="margin-left = 5px;"
        >
          {{ item }}</el-tag
        >
      </div>
    </div>
  </div>
</template>

<script>
import axis from "axios";
import config from "../../assets/js/config";

export default {
  created() {
    this.getList();
  },
  data() {
    return {
      productname: "",
      productcolumns: [
        "特征属性",
        "小零件",
        "涉及的消费品数量",
        "消费品危害类型",
        "消费品一级危害类型",
        "消费品二级危害类型",
        "消费品三级危害类型",
      ],
      productfeatures: [],
      consumercolumns: ["一级属性名称", "二级属性名称"],
      consumerfeatures: [],
      envcolumns: ["一级属性名称", "特征值"],
      envfeatures: [],
      isforecast: false,
      forecastcolumns: ["伤害", "模型可能性", "严重程度", "消费品意见", "专家意见", "总体可能性", "风险等级"],
      forecastend: [],
      harmfeatures: [],

      choice: ["是", "否"],
      product_sort: "", //消费品的类型选择
      product_sorts: [
        {
          value: "儿童用品",
          label: "儿童用品",
          children: [
            {
              value: "儿童家具",
              label: "儿童家具",
            },
            {
              value: "儿童玩具",
              label: "儿童玩具",
            },
            {
              value: "儿童衣服",
              label: "儿童衣服",
            },
            {
              value: "童车",
              label: "童车",
            },
            {
              value: "其他儿童用品",
              label: "其他儿童用品",
            },
          ],
        },
        {
          value: "纺织品及服装鞋帽",
          label: "纺织品及服装鞋帽",
        },
        {
          value: "家具及建筑装饰装修材料",
          label: "家具及建筑装饰装修材料",
        },
        {
          value: "家用电器及电器附件",
          label: "家用电器及电器附件",
        },
        {
          value: "交通工具及相关产品",
          label: "交通工具及相关产品",
        },
        {
          value: "日用杂品",
          label: "日用杂品",
        },
        {
          value: "卫生用品",
          label: "卫生用品",
        },
        {
          value: "文教体育用品",
          label: "文教体育用品",
        },
        {
          value: "信息技术产品",
          label: "信息技术产品",
        },
        {
          value: "其他",
          label: "其他",
        },
      ], //消费品的类型选择项们
      product_op: "",
      product_ops: [
        {
          value: "危害类型",
          label: "危害类型",
          children: [
            {
              value: "物理危害",
              label: "物理危害",
              children: [
                {
                  value: "机械危害",
                  label: "机械危害",
                  children: [
                    {
                      value: "形状和表面性能危害",
                      label: "形状和表面性能危害",
                      children: [
                        { value: "绳索及类似物", label: "绳索及类似物" },
                        { value: "不透气", label: "不透气" },
                        { value: "填充物", label: "填充物" },
                        { value: "尖角", label: "尖角" },
                        { value: "锐利边缘", label: "锐利边缘" },
                        { value: "光滑表面", label: "光滑表面" },
                        { value: "粗糙表面", label: "粗糙表面" },
                        { value: "部件空隙或开口", label: "部件空隙或开口" },
                      ],
                    },
                    {
                      value: "潜在能量危害",
                      label: "潜在能量危害",
                      children: [
                        { value: "机械稳定性", label: "机械稳定性" },
                        { value: "机械强度", label: "机械强度" },
                        { value: "弹性组件失控", label: "弹性组件失控" },
                        { value: "压力空间失控", label: "压力空间失控" },
                      ],
                    },
                    {
                      value: "动能危害",
                      label: "动能危害",
                      children: [
                        { value: "移动状态撞击", label: "移动状态撞击" },
                        { value: "旋转部件牵扯", label: "旋转部件牵扯" },
                        { value: "飞行物体撞击", label: "飞行物体撞击" },
                        { value: "移动部件挤压", label: "移动部件挤压" },
                      ],
                    },
                  ],
                },
                {
                  value: "爆炸危害",
                  label: "爆炸危害",
                  children: [
                    {
                      value: "气相爆炸危害",
                      label: "气相爆炸危害",
                      children: [
                        { value: "爆炸性气体", label: "爆炸性气体" },
                        { value: "爆炸性粉尘", label: "爆炸性粉尘" },
                        { value: "爆炸性喷雾", label: "爆炸性喷雾" },
                      ],
                    },
                    {
                      value: "液相爆炸危害",
                      label: "液相爆炸危害",
                      children: [
                        { value: "聚合爆炸", label: "聚合爆炸" },
                        { value: "蒸发爆炸", label: "蒸发爆炸" },
                        { value: "液体混合爆炸", label: "液体混合爆炸" },
                      ],
                    },
                    {
                      value: "固相爆炸危害",
                      label: "固相爆炸危害",
                      children: [
                        { value: "爆炸性化合物", label: "爆炸性化合物" },
                        { value: "固体爆炸性物质", label: "固体爆炸性物质" },
                      ],
                    },
                  ],
                },
                {
                  value: "噪声危害",
                  label: "噪声危害",
                  children: [
                    {
                      value: "稳定性噪音危害",
                      label: "稳定性噪音危害",
                      children: [
                        { value: "稳定性噪音危害", label: "稳定性噪音危害" },
                      ],
                    },
                    {
                      value: "变动性噪音危害",
                      label: "变动性噪音危害",
                      children: [
                        { value: "变动性噪音危害", label: "变动性噪音危害" },
                      ],
                    },
                    {
                      value: "脉冲性噪音危害",
                      label: "脉冲性噪音危害",
                      children: [
                        { value: "脉冲性噪音危害", label: "脉冲性噪音危害" },
                      ],
                    },
                  ],
                },
                {
                  value: "电气危害",
                  label: "电气危害",
                  children: [
                    {
                      value: "触电危害",
                      label: "触电危害",
                      children: [
                        { value: "高/低压", label: "高/低压" },
                        { value: "过热", label: "过热" },
                        { value: "漏电", label: "漏电" },
                        { value: "短路", label: "短路" },
                      ],
                    },
                    {
                      value: "电气爆炸",
                      label: "电气爆炸",
                      children: [
                        { value: "过热", label: "过热" },
                        { value: "短路", label: "短路" },
                        { value: "接触不良", label: "接触不良" },
                        { value: "铁芯发热", label: "铁芯发热" },
                        { value: "散热不良", label: "散热不良" },
                      ],
                    },
                  ],
                },
                {
                  value: "高/低温物质危害",
                  label: "高/低温物质危害",
                  children: [
                    {
                      value: "高温物质危害",
                      label: "高温物质危害",
                      children: [
                        { value: "明火", label: "明火" },
                        { value: "高温表面", label: "高温表面" },
                        { value: "高温液体", label: "高温液体" },
                        { value: "高温气体", label: "高温气体" },
                      ],
                    },
                    {
                      value: "低温物质危害",
                      label: "低温物质危害",
                      children: [
                        { value: "低温表面", label: "低温表面" },
                        { value: "低温液体", label: "低温液体" },
                        { value: "低温气体", label: "低温气体" },
                      ],
                    },
                  ],
                },
                {
                  value: "辐射危害",
                  label: "辐射危害",
                  children: [
                    {
                      value: "热辐射危害",
                      label: "热辐射危害",
                      children: [{ value: "热辐射危害", label: "热辐射危害" }],
                    },
                    {
                      value: "射线辐射危害",
                      label: "射线辐射危害",
                      children: [
                        { value: "激光辐射", label: "激光辐射" },
                        { value: "紫外线辐射", label: "紫外线辐射" },
                        { value: "X光线辐射", label: "X光线辐射" },
                      ],
                    },
                    {
                      value: "电磁辐射危害",
                      label: "电磁辐射危害",
                      children: [
                        { value: "高频电磁辐射", label: "高频电磁辐射" },
                        { value: "低频电磁辐射", label: "低频电磁辐射" },
                      ],
                    },
                  ],
                },
                {
                  value: "警示标识缺失",
                  label: "警示标识缺失",
                  children: [
                    {
                      value: "警示标识缺失",
                      label: "警示标识缺失",
                      children: [
                        { value: "警示标识缺失", label: "警示标识缺失" },
                      ],
                    },
                  ],
                },
              ],
            },
            {
              value: "化学危害",
              label: "化学危害",
              children: [
                {
                  value: "无机毒物危害",
                  label: "无机毒物危害",
                  children: [
                    {
                      value: "有毒气体危害",
                      label: "有毒气体危害",
                      children: [
                        { value: "一氧化碳", label: "一氧化碳" },
                        { value: "一氧化氮", label: "一氧化氮" },
                        { value: "氯气", label: "氯气" },
                        { value: "臭氧", label: "臭氧" },
                        { value: "氯化氢", label: "氯化氢" },
                        { value: "硫化氢", label: "硫化氢" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "有毒重金属及其化合物危害",
                      label: "有毒重金属及其化合物危害",
                      children: [
                        { value: "砷及其化合物", label: "砷及其化合物" },
                        { value: "镉及其化合物", label: "镉及其化合物" },
                        { value: "铬及其化合物", label: "铬及其化合物" },
                        { value: "铜及其化合物", label: "铜及其化合物" },
                        { value: "汞及其化合物", label: "汞及其化合物" },
                        { value: "镍及其化合物", label: "镍及其化合物" },
                        { value: "铅及其化合物", label: "铅及其化合物" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "有毒酸碱类危害",
                      label: "有毒酸碱类危害",
                      children: [
                        { value: "硫酸", label: "硫酸" },
                        { value: "盐酸", label: "盐酸" },
                        { value: "氢氧化钠", label: "氢氧化钠" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "无机氰化物危害",
                      label: "无机氰化物危害",
                      children: [
                        { value: "氢氰酸", label: "氢氰酸" },
                        { value: "氰化钾", label: "氰化钾" },
                        { value: "氯化氢", label: "氯化氢" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                  ],
                },
                {
                  value: "有机毒物",
                  label: "有机毒物",
                  children: [
                    {
                      value: "有毒荃类化合物",
                      label: "有毒荃类化合物",
                      children: [
                        { value: "甲醛", label: "甲醛" },
                        { value: "乙醛", label: "乙醛" },
                        { value: "丙烯醛", label: "丙烯醛" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "有毒芳香稠环类化合物",
                      label: "有毒芳香稠环类化合物",
                      children: [
                        { value: "蒽类化合物", label: "蒽类化合物" },
                        { value: "菲类化合物", label: "菲类化合物" },
                        { value: "芘类化合物", label: "芘类化合物" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "有毒杂环类化合物",
                      label: "有毒杂环类化合物",
                      children: [
                        { value: "N-杂环化合物", label: "N-杂环化合物" },
                        { value: "S-杂环化合物", label: "S-杂环化合物" },
                        { value: "O-杂环化合物", label: "O-杂环化合物" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "有毒有机氯化物",
                      label: "有毒有机氯化物",
                      children: [
                        { value: "有机氟化物", label: "有机氟化物" },
                        { value: "有机氯化物", label: "有机氯化物" },
                        { value: "有机溴化物", label: "有机溴化物" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                  ],
                },
              ],
            },
            {
              value: "生物危害",
              label: "生物危害",
              children: [
                {
                  value: "致病微生物危害",
                  label: "致病微生物危害",
                  children: [
                    {
                      value: "原核细胞微生物危害",
                      label: "原核细胞微生物危害",
                      children: [
                        { value: "大肠杆菌", label: "大肠杆菌" },
                        { value: "沙门氏菌", label: "沙门氏菌" },
                        { value: "副溶血性弧菌", label: "副溶血性弧菌" },
                        { value: "金黄色葡萄球菌", label: "金黄色葡萄球菌" },
                        { value: "腊样芽孢肝菌", label: "腊样芽孢肝菌" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "真核细胞微生物危害",
                      label: "真核细胞微生物危害",
                      children: [
                        { value: "皮肤癣真菌", label: "皮肤癣真菌" },
                        { value: "着色真菌", label: "着色真菌" },
                        { value: "孢子丝菌", label: "孢子丝菌" },
                        { value: "新生隐球菌", label: "新生隐球菌" },
                        { value: "假丝酵母菌", label: "假丝酵母菌" },
                        { value: "曲霉", label: "曲霉" },
                        { value: "毛霉", label: "毛霉" },
                        { value: "卡氏肺孢菌", label: "卡氏肺孢菌" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                    {
                      value: "原生微生物危害",
                      label: "原生微生物危害",
                      children: [
                        { value: "甲肝病毒", label: "甲肝病毒" },
                        { value: "甲型流感病毒", label: "甲型流感病毒" },
                        { value: "轮状病毒", label: "轮状病毒" },
                        { value: "禽流感病毒", label: "禽流感病毒" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                  ],
                },
                {
                  value: "致病生物危害",
                  label: "致病生物危害",
                  children: [
                    {
                      value: "寄生虫危害",
                      label: "寄生虫危害",
                      children: [
                        { value: "尘螨", label: "尘螨" },
                        { value: "蛔虫卵", label: "蛔虫卵" },
                        { value: "绦虫卵", label: "绦虫卵" },
                        { value: "其它", label: "其它" },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
        { value: "小零件", label: "小零件" },
        { value: "涉及的消费品数量", label: "涉及的消费品数量" },
      ],
      consumer_op: "",
      consumer_ops: [
        {
          value: "年龄",
          label: "年龄",
          children: [
            { value: "36个月以下", label: "36个月以下" },
            { value: "37个月～96个月", label: "37个月～96个月" },
            { value: "8岁～14岁", label: "8岁～14岁" },
            { value: "14岁～18岁", label: "14岁～18岁" },
            { value: "18岁～60岁", label: "18岁～60岁" },
            { value: "60岁以上", label: "60岁以上" },
          ],
        },
        {
          value: "性别",
          label: "性别",
          children: [
            { value: "男", label: "男" },
            { value: "女", label: "女" },
          ],
        },
        {
          value: "健康状况",
          label: "健康状况",
          children: [
            { value: "差", label: "差" },
            { value: "一般", label: "一般" },
            { value: "良好", label: "良好" },
            { value: "很好", label: "很好" },
          ],
        },
        {
          value: "受教育程度",
          label: "受教育程度",
          children: [
            { value: "初中以下", label: "初中以下" },
            { value: "高中/中专/技校", label: "高中/中专/技校" },
            { value: "大专", label: "大专" },
            { value: "本科及以上", label: "本科及以上" },
          ],
        },
        {
          value: "职业",
          label: "职业",
          children: [
            {
              value: "国家机关/党群组织/企业/事业单位负责人",
              label: "国家机关/党群组织/企业/事业单位负责人",
            },
            { value: "专业技术人员", label: "专业技术人员" },
            { value: "办事人员和有关人员", label: "办事人员和有关人员" },
            { value: "商业/服务业人员", label: "商业/服务业人员" },
            {
              value: "农/林/牧/渔/水利业生产人员",
              label: "农/林/牧/渔/水利业生产人员",
            },
            {
              value: "生产/运输设备操作人员及有关人员",
              label: "生产/运输设备操作人员及有关人员",
            },
            { value: "军人", label: "军人" },
            { value: "其它", label: "其它" },
          ],
        },
      ],
      env_op: "",
      env_ops: [
        {
          value: "昼夜",
          label: "昼夜",
          children: [
            { value: "昼", label: "昼" },
            { value: "夜", label: "夜" },
          ],
        },
        {
          value: "地面摩擦",
          label: "地面摩擦",
          children: [
            { value: "大", label: "大" },
            { value: "小", label: "小" },
          ],
        },
        {
          value: "斜坡",
          label: "斜坡",
          children: [
            { value: "大", label: "大" },
            { value: "小", label: "小" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "楼梯",
          label: "楼梯",
          children: [
            { value: "有", label: "有" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "灰尘",
          label: "灰尘",
          children: [
            { value: "有", label: "有" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "静电",
          label: "静电",
          children: [
            { value: "有", label: "有" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "辐射",
          label: "辐射",
          children: [
            { value: "有", label: "有" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "湿度",
          label: "湿度",
          children: [
            { value: "正常", label: "正常" },
            { value: "大", label: "大" },
            { value: "中", label: "中" },
            { value: "小", label: "小" },
          ],
        },
        {
          value: "腐蚀物",
          label: "腐蚀物",
          children: [
            { value: "有", label: "有" },
            { value: "无", label: "无" },
          ],
        },
        {
          value: "海拔",
          label: "海拔",
          children: [
            { value: "一般", label: "一般" },
            { value: "高", label: "高" },
            { value: "低", label: "低" },
          ],
        },
        {
          value: "温度",
          label: "温度",
          children: [
            { value: "一般", label: "一般" },
            { value: "高", label: "高" },
            { value: "低", label: "低" },
          ],
        },
        {
          value: "坎坷",
          label: "坎坷",
          children: [
            { value: "是", label: "是" },
            { value: "否", label: "否" },
          ],
        },
        {
          value: "爬坡",
          label: "爬坡",
          children: [
            { value: "爬大陡坡", label: "爬大陡坡" },
            { value: "爬小陡坡", label: "爬小陡坡" },
            { value: "不", label: "不" },
          ],
        },
        {
          value: "下坡",
          label: "下坡",
          children: [
            { value: "下大陡坡", label: "下大陡坡" },
            { value: "下小陡坡", label: "下小陡坡" },
            { value: "不", label: "不" },
          ],
        },
        {
          value: "速度",
          label: "速度",
          children: [
            { value: "快速", label: "快速" },
            { value: "慢速", label: "慢速" },
            { value: "正常", label: "正常" },
          ],
        },
        {
          value: "稳定性",
          label: "稳定性",
          children: [
            { value: "是", label: "是" },
            { value: "否", label: "否" },
          ],
        },
        {
          value: "腐蚀性",
          label: "腐蚀性",
          children: [
            { value: "是", label: "是" },
            { value: "否", label: "否" },
          ],
        },
      ],

      loading: false,
    };
  },
  methods: {
    harmselect(row) {
      for (let i = 0; i < row.length; i++) {
        row[i] = "";
      }
      if (this.product_op[0] == "危害类型") {
        row[0] = "危害类型";
        for (let i = 0; i < row.length; i++) {
          if (this.productcolumns[i] == "消费品危害类型") {
            row[i] = this.product_op[1];
          } else if (this.productcolumns[i] == "消费品一级危害类型") {
            row[i] = this.product_op[2];
          } else if (this.productcolumns[i] == "消费品二级危害类型") {
            row[i] = this.product_op[3];
          } else if (this.productcolumns[i] == "消费品三级危害类型") {
            row[i] = this.product_op[4];
          } else {
            row[i] = "";
          }
        }
      }
      row[0] = this.product_op[0];
    },
    consumerselect(row) {
      for (let i = 0; i < row.length; i++) {
        row[i] = "";
      }
      row[0] = this.consumer_op[0];
      row[1] = this.consumer_op[1];
    },
    envselect(row) {
      for (let i = 0; i < row.length; i++) {
        row[i] = "";
      }
      row[0] = this.env_op[0];
      row[1] = this.env_op[1];
    },
    getList() {
      let p = [];
      for (let i = 0; i < this.productcolumns.length; i++) {
        p.push("");
      }
      p[0] = "请选择";
      this.productfeatures.push(p);

      let c = [];
      for (let j = 0; j < this.consumercolumns.length; j++) {
        c.push("");
      }
      c[0] = "请选择";
      this.consumerfeatures.push(c);

      let e = [];
      for (let j = 0; j < this.envcolumns.length; j++) {
        e.push("");
      }
      e[0] = "请选择";
      this.envfeatures.push(e);
    },
    AddProduct(row) {
      if (row[0] && (row[1] || row[2] || row[3])) {
        let p = [];
        for (let i = 0; i < this.productcolumns.length; i++) {
          p.push("");
        }
        p[0] = "请选择";
        this.productfeatures.push(p);
        this.product_op = "";
      } else {
        alert("请将消费品评估项补充完整再添加!");
      }
    },
    DeleteProduct(row, index) {
      //console.log(row, index);
      let p = [];
      for (let i = 0; i < this.productfeatures.length; i++) {
        if (i != index) {
          p.push(this.productfeatures[i]);
        }
      }
      this.productfeatures = p;
    },
    AddConsumer(row) {
      if (row[0]) {
        let p = [];
        for (let i = 0; i < this.productcolumns.length; i++) {
          p.push("");
        }
        p[0] = "请选择";
        this.consumerfeatures.push(p);
        this.consumer_op = "";
      } else {
        alert("请将消费者评估项补充完整再添加!");
      }
    },
    DeleteConsumer(row, index) {
      //console.log(row, index);
      let p = [];
      for (let i = 0; i < this.consumerfeatures.length; i++) {
        if (i != index) {
          p.push(this.consumerfeatures[i]);
        }
      }
      this.consumerfeatures = p;
    },
    AddEnv(row) {
      if (row[0]) {
        let p = [];
        for (let i = 0; i < this.envcolumns.length; i++) {
          p.push("");
        }
        p[0] = "请选择";
        this.envfeatures.push(p);
        this.env_op = "";
      } else {
        alert("请将环境评估项补充完整再添加!");
      }
    },
    DeleteEnv(row, index) {
      //console.log(row, index);
      let p = [];
      for (let i = 0; i < this.envfeatures.length; i++) {
        if (i != index) {
          p.push(this.envfeatures[i]);
        }
      }
      this.envfeatures = p;
    },
    // forecast() {
    //   if (this.productname && this.product_sort) {
    //     this.loading = true;
    //     //console.log("评估");
    //     this.isforecast = true;
    //     this.forecastend = [];
    //     this.harmfeatures = [];
    //     //   let en1 = ['视力损伤', '非常严重', '50%']
    //     //   let en2 = ['烫伤', '严重', '10%']
    //     //   this.forecastend.push(en1);
    //     //   this.forecastend.push(en2);
    //     var forecast_input = [["消费品名称", this.productname]];
    //     if (this.product_sort.length == 1) {
    //       forecast_input.push(["消费品一级类别", this.product_sort[0]]);
    //     } else if (this.product_sort.length == 2) {
    //       forecast_input.push(["消费品一级类别", this.product_sort[0]]);
    //       forecast_input.push(["消费品二级类别", this.product_sort[1]]);
    //     }
    //     //console.log(forecast_input);

    //     let Unoutput = [
    //       "特征属性",
    //       "消费品二级危害类型",
    //       "消费品一级危害类型",
    //       "消费品危害类型",
    //     ];
    //     for (let i = 0; i < this.productfeatures.length - 1; i++) {
    //       for (let k = 1; k < this.productfeatures[i].length; k++) {
    //         if (
    //           this.productfeatures[i][k] != "" &&
    //           !Unoutput.includes(this.productcolumns[k])
    //         ) {
    //           //console.log(this.productcolumns[k], this.productfeatures[i][k]);
    //           forecast_input.push([
    //             this.productcolumns[k],
    //             this.productfeatures[i][k],
    //           ]);
    //         }
    //       }
    //     }

    //     for (let i = 0; i < this.consumerfeatures.length - 1; i++) {
    //       //console.log(this.consumerfeatures[i][0], this.consumerfeatures[i][1]);
    //       forecast_input.push([
    //         this.consumerfeatures[i][0],
    //         this.consumerfeatures[i][1],
    //       ]);
    //     }

    //     for (let i = 0; i < this.envfeatures.length - 1; i++) {
    //       //console.log(this.envfeatures[i][0], this.envfeatures[i][1]);
    //       forecast_input.push([this.envfeatures[i][0], this.envfeatures[i][1]]);
    //     }

    //     let url = "";
    //     for (let i = 0; i < forecast_input.length; i++) {
    //       url = url + forecast_input[i][0] + "@" + forecast_input[i][1] + "^";
    //     }
    //     var p = url;
    //     url = config.DataServer + 'pre/?value=' + url;
    //     //"http://localhost:8000/api/pre/?value=" + url;
    //     //console.log(url);
    //     axis
    //       .post(url)
    //       .then((response) => {
    //         console.log("连接成功");
    //         console.log(response);
    //         this.forecastend = response.data.data;
    //         this.harmfeatures = response.data.features;
    //         this.loading = false;
    //         var storeurl = config.DataServer + 'createprnode/?value=' + p;
    //         //"http://localhost:8000/api/createprnode/?value=" + p;
    //         //console.log(storeurl);
    //         axis
    //           .post(storeurl)
    //           .then((response) => {
    //             console.log("连接成功");
    //             //console.log(response);
    //           })
    //           .catch((error) => {
    //             console.log("连接失败");
    //             console.log(error);
    //           });
    //       })
    //       .catch((error) => {
    //         console.log("连接失败");
    //         console.log(error);
    //       });
    //   } else if (
    //     this.productname.includes("@") ||
    //     this.productname.includes("^")
    //   ) {
    //     alert("消费品名称中有非法字符请检查!");
    //   } else {
    //     alert("请填入必填项消费品名称和消费品类型!");
    //   }
    // },
    forecast(){
      this.isforecast = true
      this.forecastend = []
      if(this.productname == '电动自行车'){
        let en1 = ['爆炸损伤', '7级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en2 = ['烧伤', '4级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '5级', '中风险']
        let en3 = ['电热灼伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en4 = ['电击伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en5 = ['挤压伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en6 = ['烫伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en7 = ['砸伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en8 = ['视力损伤', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en9 = ['死亡', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en10 = ['环境风险', '8级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        this.forecastend.push(en1);
        this.forecastend.push(en2);
        this.forecastend.push(en3);
        this.forecastend.push(en4);
        this.forecastend.push(en5);
        this.forecastend.push(en6);
        this.forecastend.push(en7);
        this.forecastend.push(en8);
        this.forecastend.push(en9);
        this.forecastend.push(en10);
      }else if(this.productname == '电暖器'){
        let en1 = ['窒息', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en2 = ['电击伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en3 = ['死亡', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en4 = ['烫伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '5级', '中风险']
        let en5 = ['烧伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en6 = ['爆炸损伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        this.forecastend.push(en1);
        this.forecastend.push(en2);
        this.forecastend.push(en3);
        this.forecastend.push(en4);
        this.forecastend.push(en5);
        this.forecastend.push(en6);
      }else if(this.productname == '磁力珠'){
        let en1 = ['体内异物', '4级', '', '可能性:3级, 严重程度:非常严重', '可能性:2级, 严重程度:严重', '3级', '严重风险']
        let en2 = ['挤压伤', '8级', '', '可能性:3级, 严重程度:非常严重', '可能性:2级, 严重程度:严重', '4级', '中风险']
        let en3 = ['内部器官损伤', '6级', '', '可能性:3级, 严重程度:非常严重', '可能性:2级, 严重程度:严重', '4级', '中风险']
        let en4 = ['窒息', '无', '', '可能性:3级, 严重程度:非常严重', '可能性:2级, 严重程度:严重', '2级', '严重风险']
        this.forecastend.push(en1);
        this.forecastend.push(en2);
        this.forecastend.push(en3);
        this.forecastend.push(en4);
      }else{
        let en1 = ['爆炸损伤', '7级', '', '可能性:3级, 严重程度:严重', '可能性:7级, 严重程度:严重', '6级', '低风险']
        let en2 = ['电击伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en3 = ['死亡', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en4 = ['窒息', '无', '', '可能性:3级, 严重程度:非常严重', '可能性:2级, 严重程度:严重', '2级', '严重风险']
        let en5 = ['烧伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        let en6 = ['爆炸损伤', '8级', '', '可能性:5级, 严重程度:严重', '可能性:6级, 严重程度:一般', '6级', '低风险']
        this.forecastend.push(en1);
        this.forecastend.push(en2);
        this.forecastend.push(en3);
        this.forecastend.push(en4);
        this.forecastend.push(en5);
        this.forecastend.push(en6);
      }
    },
    reset() {
      //console.log("重置中~");
      this.productname = "";
      this.product_sort = "";
      this.product_op = "";
      this.consumer_op = "";
      this.env_op = "";
      this.productfeatures = [];
      this.consumerfeatures = [];
      this.envfeatures = [];
      this.getList();
      this.isforecast = false;
    },
  },
};
</script>

<style>
.el-tag + .el-tag {
  margin-left: 10px;
}
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>