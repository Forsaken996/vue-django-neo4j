<template>
  <div class="app-container">
    <div style="display: flex">
      <el-cascader :options="ops" v-model="op">
        <template slot-scope="{ node, data }">
          <span>{{ data.label }}</span>
          <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
        </template>
      </el-cascader>

      <el-button @click="addrow()" style="margin-left: 20px">
        {{ "添加该项数据" }}
      </el-button>
    </div>
    <el-table
      v-loading="loading"
      element-loading-text="拼命加载中"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)"
      :data="tempList"
      stripe
      width="100%"
    >
      <el-table-column label="序号" type="index">
        <template slot-scope="scope">
          <span>{{
            (ListQuery.currentPage - 1) * ListQuery.pageSize + scope.$index + 1
          }}</span>
        </template>
      </el-table-column>
      <el-table-column
        v-for="(item, i) in columns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="110%"
      >
        <template slot-scope="scope">
          <div v-if="!scope.row.isEdit || cantmodify.includes(columns[i])">
            {{ scope.row[i] }}
          </div>
          <div v-else-if="columns[i] == '消费者性别'">
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
                <el-option
                  v-for="item in gender"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
          <div v-else-if="inputmodify.includes(columns[i])">
            <el-input v-model="scope.row[i]">scope.row[i]</el-input>
          </div>
          <div v-else-if="columns[i] == '伤害类型'">
            <template>
              <el-select
                v-model="scope.row[i]"
                multiple
                collapse-tags
                placeholder="请选择"
              >
                <el-option
                  v-for="item in damage"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
          <div v-else-if="columns[i] == '健康状况'">
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
                <el-option
                  v-for="item in health"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
          <div
            v-else-if="
              columns[i] == '严重程度' && scope.row[0].includes('事件')
            "
          >
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
                <el-option
                  v-for="item in severity"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
          <div
            v-else-if="
              columns[i] == '严重程度' && scope.row[0].includes('预测')
            "
          >
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
                <el-option
                  v-for="item in risk"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
          <div v-else-if="columns[i] == '消费品一级类别'">
            <el-cascader v-model="scope.row[i]" :options="product_sorts">
            </el-cascader>
          </div>
          <div v-else>
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
                <el-option
                  v-for="item in normalops"
                  :key="item.key"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column align="right" min-width="150%">
        <template slot-scope="scope">
          <el-button @click="handleClick(scope.row, scope.$index)">
            {{ scope.row.isEdit ? "完成" : "编辑" }}
          </el-button>
          <template v-if="scope.row.isEdit ? true : false">
            <el-popconfirm
              confirm-button-text="删除"
              cancel-button-text="否"
              icon="el-icon-info"
              icon-color="red"
              confirm-button-type="danger"
              title="确定删除该行信息吗"
              @onConfirm="handleDelete(scope.$index, scope.row)"
            >
              <el-button slot="reference" type="danger">删除</el-button>
            </el-popconfirm>
          </template>
        </template>
      </el-table-column>
    </el-table>
    <div class="paginationClass">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page.sync="ListQuery.currentPage"
        :page-sizes="[5, 10, 20, 50, 100]"
        :page-size="ListQuery.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="ListQuery.total"
      >
      </el-pagination>
    </div>
  </div>
</template>

<script>
import axis from "axios";
import config from "../../../assets/js/config";
export default {
  data() {
    return {
      tempList: [],
      tableinfo: [],
      columns: [],
      addcolumns: [],
      ListQuery: {
        total: 0, //默认数据总数
        pagesize: 10, //每页的数据条数
        currentPage: 1, //默认开始页面
      },
      op: "",
      ops: [
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
                        { value: "小零件", label: "小零件" },
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
        {
          value: "消费者",
          label: "消费者",
          children: [
            { value: "消费者年龄", label: "消费者年龄" },
            { value: "消费者性别", label: "消费者性别" },
            { value: "消费者健康状况", label: "消费者健康状况" },
            { value: "消费者受教育程度", label: "消费者受教育程度" },
            { value: "消费者职业", label: "消费者职业" },
          ],
        },
        {
          value: "环境",
          label: "环境",
          children: [
            { value: "昼夜", label: "昼夜" },
            { value: "地面摩擦", label: "地面摩擦" },
            { value: "斜坡", label: "斜坡" },
            { value: "楼梯", label: "楼梯" },
            { value: "灰尘", label: "灰尘" },
            { value: "静电", label: "静电" },
            { value: "辐射", label: "辐射" },
            { value: "湿度", label: "湿度" },
            { value: "腐蚀物", label: "腐蚀物" },
            { value: "海拔", label: "海拔" },
            { value: "温度", label: "温度" },
            { value: "坎坷", label: "坎坷" },
            { value: "爬坡", label: "爬坡" },
            { value: "下坡", label: "下坡" },
            { value: "速度", label: "速度" },
            { value: "稳定性", label: "稳定性" },
            { value: "腐蚀性", label: "腐蚀性" },
          ],
        },
      ],
      cantmodify: [
        "编号",
        "详细信息",
        "消费品三级危害类型",
        "消费品二级危害类型",
        "消费品一级危害类型",
        "消费品危害类型",
        "已标注",
        "消费品二级类别",
        "数据来源",
      ],
      inputmodify: ["尺寸", "小零件", "涉及的消费品数量", "区域", "消费品名称"],
      gender: ["男", "女", "不确定"],
      damage: [
        "划伤",
        "擦伤",
        "挫伤",
        "勒伤",
        "弹伤",
        "砸伤",
        "扭伤",
        "挤压伤",
        "骨折",
        "内脏损伤或破裂",
        "肢体离断",
        "切割伤",
        "穿刺伤",
        "窒息",
        "体内异物",
        "烧伤",
        "烫伤",
        "电击伤",
        "电热灼伤",
        "视力损伤",
        "心血管系统损伤",
        "生殖系统损伤",
        "听力损伤",
        "心脏血管损伤",
        "内部器官损伤",
        "爆炸损伤",
        "植物人",
        "死亡",
        "化学性刺激",
        "过敏反应",
        "全身中毒",
        "致癌",
        "致畸",
        "生物性感染",
        "环境风险",
        "脑震荡",
        "脑挫裂伤",
        "其他",
      ],
      normalops: ["是", "否", "不确定"],
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
          value: "食品相关产品",
          label: "食品相关产品",
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
      ],
      health: ["差", "一般", "良好", "很好"],
      severity: ["微弱", "一般", "严重", "非常严重"],
      risk: ["可接受风险", "低风险", "中风险", "高风险"],
      loading: true,
    };
  },
  created() {
    this.handleCurrentChange(1);
    this.getList();
  },
  methods: {
    getList() {
      this.loading = true;
      let from = (this.ListQuery.currentPage - 1) * this.ListQuery.pageSize + 1;
      let to = this.ListQuery.currentPage * this.ListQuery.pageSize;
      var url = "";
      for (let i = 0; i < this.addcolumns.length; i++) {
        if (url) {
          url = url + "," + this.addcolumns[i];
        } else {
          url = this.addcolumns[i];
        }
      }
      url =
        config.DataServer + "querymarkinfos/?start=" +
        //"http://localhost:8000/api/querymarkinfos/?start=" +
        from +
        "&to=" +
        to +
        "&col=" +
        url;
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          this.tempList = JSON.parse(JSON.stringify(response.data.data));
          this.tableinfo = JSON.parse(JSON.stringify(response.data.data));
          this.columns = response.data.columns;
          this.ListQuery.total = response.data.totals;
          console.log(response);
          this.loading = false;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },
    //分页方法（重点）
    currentChangePage(currentPage) {
      if (!this.ListQuery.pageSize) {
        this.ListQuery.pageSize = 10;
      }
      let from = (currentPage - 1) * this.ListQuery.pageSize + 1;
      let to = currentPage * this.ListQuery.pageSize;
      this.getList();
    },

    handleSizeChange: function (pageSize) {
      // 每页条数切换
      this.ListQuery.pageSize = pageSize;
      this.handleCurrentChange(this.ListQuery.currentPage);
    },

    handleCurrentChange: function (currentPage) {
      //页码切换
      this.ListQuery.currentPage = currentPage;
      this.currentChangePage(currentPage);
    },

    handleClick(row, index) {
      // 动态设置数据并通过这个数据判断显示方式
      if (row.isEdit) {
        //console.log(row, index);
        this.$delete(row, "isEdit");
        for (let i = 0; i < row.length; i++) {
          let before = this.tableinfo[index][i]; //修改前
          let after = row[i]; //修改后
          let attribute = this.columns[i]; //修改项标题
          let evenum = row[0]; //事件号
          let p = this.columns.indexOf("已标注");
          let q = this.columns.indexOf("消费品一级类别");
          let u = this.columns.indexOf("消费品二级类别");
          let h = this.columns.indexOf("伤害类型");
          let product = this.columns.indexOf("消费品名称");
          let before_type = this.columns.indexOf("严重程度");
          let health_type = this.columns.indexOf("健康状况");
          if (before == "") {
            before = "-1";
          }
          if (after == "") {
            after = "-1";
          }
          if (i == h) {
            let b_c = before.split(",");
            //console.log(b_c);
            //console.log(row[h]);
            if (b_c != after) {
              for (let k = 0; k < row[h].length; k++) {
                //如果before不存在 after存在就添加
                if (!b_c.includes(row[h][k])) {
                  let url =
                    config.DataServer + "modifyinfos/?after=" +
                    //"http://localhost:8000/api/modifyinfos/?after=" +
                    row[h][k] +
                    "&attribute=" +
                    attribute +
                    "&evenum=" +
                    evenum;
                  //console.log(url,"添加伤害");
                  axis
                    .post(url)
                    .then((response) => {
                      console.log("连接成功");
                      //console.log(response);
                    })
                    .catch((error) => {
                      console.log("连接失败");
                      console.log(error);
                    });
                }
              }

              for (let k = 0; k < b_c.length; k++) {
                //如果before存在 after不存在就删除
                if (!after.includes(b_c[k])) {
                  let url =
                  config.DataServer + 'modifyinfos/?before=' +
                    //"http://localhost:8000/api/modifyinfos/?before=" +
                    b_c[k] +
                    "&attribute=" +
                    attribute +
                    "&evenum=" +
                    evenum;
                  //console.log(url,"删除伤害");
                  axis
                    .post(url)
                    .then((response) => {
                      console.log("连接成功");
                      //console.log(response);
                    })
                    .catch((error) => {
                      console.log("连接失败");
                      console.log(error);
                    });
                }
              }

              let newstr = "";
              //console.log(row[h]);
              for (let k = 0; k < row[h].length; k++) {
                if (k == 0) {
                  newstr = row[h][k];
                  continue;
                }
                newstr = newstr + "," + row[h][k];
              }
              row[h] = newstr;
              this.tableinfo[index][i] = newstr;
              continue;
            }
          }
          if (i == q || i == u) {
            if (i == q) {
              if (row[i] instanceof Array) {
                row[u] = row[i][1];
                row[q] = row[i][0];
              } else {
                row[q] = row[i];
                row[u] = "";
              }
              let before_sort1 = this.tableinfo[index][q];
              let after_sort1 = row[q];
              let before_sort2 = this.tableinfo[index][u];
              let after_sort2 = row[u];
              if (before_sort1 != after_sort1 || before_sort2 != after_sort2) {
                //添加axis
                var url =
                  config.DataServer + 'modifysort/?before_sort1=' +
                  //"http://localhost:8000/api/modifysort/?before_sort1=" +
                  before_sort1 +
                  "&after_sort1=" +
                  after_sort1 +
                  "&evenum=" +
                  evenum;
                if (before_sort2 != after_sort2) {
                  if (before_sort2) {
                    url = url + "&before_sort2=" + before_sort2;
                  }
                  if (after_sort2) {
                    url = url + "&after_sort2=" + after_sort2;
                  }
                }
                //console.log(url);
                axis
                  .post(url)
                  .then((response) => {
                    console.log("连接成功");
                    console.log(response);
                  })
                  .catch((error) => {
                    console.log("连接失败");
                    console.log(error);
                  });

                //规则库同样需要修改
                var rules_url =
                config.DataServer + 'changerulesmark/?sortindex=0&before=' +
                  //"http://localhost:8000/api/changerulesmark/?sortindex=0&before=" +
                  row[product] +
                  "&after=" +
                  row[product] +
                  "&before_sort1=" +
                  before_sort1 +
                  "&after_sort1=" +
                  after_sort1;
                if (before_sort2 != after_sort2) {
                  if (before_sort2) {
                    rules_url = rules_url + "&before_sort2=" + before_sort2;
                  }
                  if (after_sort2) {
                    rules_url = rules_url + "&after_sort2=" + after_sort2;
                  }
                }
                //console.log(rules_url);
                axis
                  .post(rules_url)
                  .then((response) => {
                    console.log("连接成功");
                    console.log(response);
                  })
                  .catch((error) => {
                    console.log("连接失败");
                    console.log(error);
                  });
                if (row[p] == "×") {
                  row[p] = "√";
                  let urls =
                    config.DataServer + 'modifyinfos/?before=否&after=是&attribute=已标注&evenum=' +
                    //"http://localhost:8000/api/modifyinfos/?before=否&after=是&attribute=已标注&evenum=" +
                    evenum;
                  //console.log(urls);
                  axis
                    .post(urls)
                    .then((response) => {
                      console.log("连接成功");
                      console.log(response);
                    })
                    .catch((error) => {
                      console.log("连接失败");
                      console.log(error);
                    });
                }
              }
            }
            continue;
          }
          this.tableinfo[index][i] = row[i];
          //console.log(p);
          if (before != after) {
            if (row[p] == "×") {
              row[p] = "√";
              let urls =
                config.DataServer + 'modifyinfos/?before=否&after=是&attribute=已标注&evenum=' +
                //"http://localhost:8000/api/modifyinfos/?before=否&after=是&attribute=已标注&evenum=" +
                evenum;
              //console.log(urls);
              axis
                .post(urls)
                .then((response) => {
                  console.log("连接成功");
                  console.log(response);
                })
                .catch((error) => {
                  console.log("连接失败");
                  console.log(error);
                });
            }
            if (this.columns[i] == "严重程度") {
              if (before == "微弱" || before == "可接受风险") {
                before = "1";
              } else if (before == "一般" || before == "低风险") {
                before = "2";
              } else if (before == "严重" || before == "中风险") {
                before = "3";
              } else if (before == "非常严重" || before == "高风险") {
                before = "4";
              }

              if (after == "微弱" || after == "可接受风险") {
                after = "1";
              } else if (after == "一般" || after == "低风险") {
                after = "2";
              } else if (after == "严重" || after == "中风险") {
                after = "3";
              } else if (after == "非常严重" || after == "高风险") {
                after = "4";
              }
            }
            if (this.columns[i] == "健康状况") {
              if (before == "差") {
                before = "1";
              } else if (before == "一般") {
                before = "2";
              } else if (before == "良好") {
                before = "3";
              } else if (before == "很好") {
                before = "4";
              }

              if (after == "差") {
                after = "1";
              } else if (after == "一般") {
                after = "2";
              } else if (after == "良好") {
                after = "3";
              } else if (after == "很好") {
                after = "4";
              }
            }
            var url =
              config.DataServer + 'modifyinfos/?before=' +
              //"http://localhost:8000/api/modifyinfos/?before=" +
              before +
              "&after=" +
              after +
              "&attribute=" +
              attribute +
              "&evenum=" +
              evenum;
            //console.log(url);
            axis
              .post(url)
              .then((response) => {
                console.log("连接成功");
                console.log(response);
              })
              .catch((error) => {
                console.log("连接失败");
                console.log(error);
              });
          }
          this.loading = false;
        }
      } else {
        this.$set(row, "isEdit", true);
        let u = this.columns.indexOf("伤害类型");
        row[u] = row[u].split(",");
        //console.log(row[u]);
      }
    },

    handleDelete(index, row) {
      let evenum = row[0];
      let temp = [];
      for (let i = 0; i < this.tempList.length; i++) {
        if (i != index) {
          temp.push(this.tempList[i]);
        }
      }
      this.tempList = temp;
      var url = 
      config.DataServer + 'deleteevent/?&evenum=' +
      //"http://localhost:8000/api/deleteevent/?&evenum="
       + evenum;
      //console.log(url);
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          console.log(response);
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    //添加一列显示信息
    addrow() {
      //console.log(this.op);
      if (this.op.length) {
        let p = this.op[this.op.length - 1];
        if (!this.addcolumns.includes(p) && !this.columns.includes(p)) {
          this.addcolumns.push(p);
          this.handleCurrentChange(1);
        } else {
          alert("不能添加已有的项!");
        }
      }
      //console.log(this.addcolumns);
    },
  },
};
</script>

