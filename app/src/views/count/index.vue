<template>
  <div class="app-container">
    <div class="filter-container">
      <div>
        <el-date-picker
          v-model="times"
          type="daterange"
          align="right"
          unlink-panels
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="yyyy.MM.dd"
          :picker-options="pickerOptions"
          style="margin-left: 10px; margin-right: 10px"
        >
        </el-date-picker>
        <el-select
          v-model="s_area"
          placeholder="请选择地区"
          clearable
          class="filter-item"
          style="width: 200px; margin-right: 10px"
        >
          <el-option
            v-for="item in area"
            :key="item.key"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-cascader
          placeholder="请选择消费品类型"
          :props="{ checkStrictly: true }"
          v-model="s_class"
          :options="classification"
          clearable
        >
        </el-cascader>
        <el-cascader
          :options="harm"
          v-model="s_harm"
          placeholder="请选择危害源"
          clearable
          :props="{ checkStrictly: true }"
        >
          <template slot-scope="{ node, data }">
            <span>{{ data.label }}</span>
            <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
          </template>
        </el-cascader>
        <el-button
          v-waves
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="countbycondition"
          style="margin-left: 20px"
        >
          统计前十伤害
        </el-button>
      </div>

      <div style="margin-top: 10px">
        <el-select
          v-model="s_hurt"
          placeholder="伤害"
          clearable
          class="filter-item"
          style="width: 200px; margin-left: 10px; margin-right: 10px"
        >
          <el-option
            v-for="item in hurt"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>
        <el-button
          v-waves
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="countproducthurtmost"
          style="margin-left: 20px"
        >
          统计造成该伤害最多的消费品大类
        </el-button>
        <el-button
          v-waves
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="counthurtarea"
          style="margin-left: 20px"
        >
          统计造成该伤害主要分布的区域
        </el-button>
      </div>
    </div>
    <div
      v-loading="loading"
      element-loading-text="拼命加载中"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)"
    >
      <el-table :data="count_values" stripe style="width: 100%">
        <el-table-column
          v-for="(item, i) in count_name"
          :key="i"
          :label="item"
          show-overflow-tooltip
        >
          <template slot-scope="scope">
            <span>{{ scope.row[i] }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div
        style="width: 800px; height: 600px; margin-top: 20px"
        id="echartss"
      ></div>
    </div>
    <!-- <div class="Table">
      <el-table
        stripe
        style="width: 100%">
        <el-table-column v-for="item in List.column" :key="item" :label="item" :value="item">
        </el-table-column>
      </el-table>
    </div> -->
  </div>
</template>

<script>
import waves from "@/directive/waves"; // waves directive
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import axis from "axios";
import * as echarts from "echarts";
import config from "../../assets/js/config";

export default {
  name: "ComplexTable",
  components: { Pagination },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: "success",
        draft: "info",
        deleted: "danger",
      };
      return statusMap[status];
    },
    typeFilter(type) {
      return calendarTypeKeyValue[type];
    },
  },
  data() {
    return {
      s_area: "", //选择的地区
      area: [],

      s_class: "", //选择的消费品分类
      classification: [],

      s_hurt: "",
      hurt: [],

      s_harm: "",
      harm: [],

      times: [],
      columns: [],
      tempList: [],
      count_values: [[""]],
      count_name: [],
      count_value: [],
      countdraw_name: [],
      countdraw_value: [],
      pickerOptions: {
        shortcuts: [
          {
            text: "最近一周",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
              picker.$emit("pick", [start, end]);
            },
          },
          {
            text: "最近一个月",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
              picker.$emit("pick", [start, end]);
            },
          },
          {
            text: "最近三个月",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
              picker.$emit("pick", [start, end]);
            },
          },
        ],
      },

      loading: true,
    };
  },
  created() {
    this.getops();
    this.getList();
  },
  methods: {
    //获取选择项
    getops() {
      var url = config.DataServer + 'getcountops/';
      //"http://localhost:8000/api/getcountops/";
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          this.area = response.data.area;
          this.classification = response.data.sort;
          this.hurt = response.data.hurt;
          this.harm = response.data.harm;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    getList() {
      this.loading = true;
      var query_url = config.DataServer + 'countbycondition/';
      //"http://localhost:8000/api/countbycondition/";
      axis
        .post(query_url)
        .then((response) => {
          console.log("连接成功");
          //console.log(response);
          this.count_name = response.data.count_name;
          this.count_value = response.data.count_value;
          this.count_values[0] = response.data.count_value;
          this.countdraw_name = response.data.countdraw_name;
          this.countdraw_value = response.data.countdraw_value;
          this.drawinit();
          this.loading = false;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    countbycondition() {
      this.loading = true;
      if (!this.times) {
        this.times = [];
      }
      if (
        this.times.length == 0 &&
        !this.s_class &&
        !this.s_area &&
        !this.s_hurt &&
        !this.s_harm
      ) {
        this.getList();
      } else {
        var query_url = config.DataServer + 'countbycondition/?';
        //"http://localhost:8000/api/countbycondition/?";
        //构造字符串
        var has_input = false;
        if (this.times.length != 0) {
          let start = this.times[0];
          let end = this.times[1];
          query_url = query_url + "time=" + start + "-" + end;
          has_input = true;
        }
        if (this.s_class) {
          if (has_input) {
            query_url = query_url + "&";
          }
          if (this.s_class.length == 2) {
            query_url =
              query_url +
              "class1=" +
              this.s_class[0] +
              "&class2=" +
              this.s_class[1];
          } else if (this.s_class.length == 1) {
            query_url = query_url + "class1=" + this.s_class[0];
          }

          has_input = true;
        }
        if (this.s_name) {
          if (has_input) {
            query_url = query_url + "&";
          }
          query_url = query_url + "productname=" + this.s_name;
          has_input = true;
        }
        if (this.s_harm && this.s_harm.length > 1) {
          if (has_input) {
            query_url = query_url + "&";
          }
          query_url = query_url + "harm=" + this.s_harm[this.s_harm.length - 1];
          has_input = true;
        }
        if (this.s_area) {
          if (has_input) {
            query_url = query_url + "&";
          }
          query_url = query_url + "area=" + this.s_area;
          has_input = true;
        }
        //console.log(query_url);
        axis
          .post(query_url)
          .then((response) => {
            console.log("连接成功");
            console.log(response);
            this.count_name = response.data.count_name;
            this.count_value = response.data.count_value;
            this.count_values[0] = response.data.count_value;
            this.countdraw_name = response.data.countdraw_name;
            this.countdraw_value = response.data.countdraw_value;
            this.drawinit();
            this.loading = false;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      }
    },
    countproducthurtmost() {
      this.loading = true;
      if (this.s_hurt) {
        var query_url = config.DataServer + 'countproducthurtmost/?hurt=' + this.s_hurt;
          //"http://localhost:8000/api/countproducthurtmost/?hurt=" + this.s_hurt;
        axis
          .post(query_url)
          .then((response) => {
            console.log("连接成功");
            this.count_name = response.data.count_name;
            this.count_value = response.data.count_value;
            this.count_values[0] = response.data.count_value;
            this.countdraw_name = response.data.countdraw_name;
            this.countdraw_value = response.data.countdraw_value;
            this.drawinit();
            this.loading = false;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      } else {
        alert("请选择危害");
      }
    },
    counthurtarea() {
      this.loading = true;
      if (this.s_hurt) {
        var query_url =  config.DataServer + 'counthurtarea/?hurt=' + this.s_hurt;
          //"http://localhost:8000/api/counthurtarea/?hurt=" + this.s_hurt;
        axis
          .post(query_url)
          .then((response) => {
            console.log("连接成功");
            this.count_name = response.data.count_name;
            this.count_value = response.data.count_value;
            this.count_values[0] = response.data.count_value;
            this.countdraw_name = response.data.countdraw_name;
            this.countdraw_value = response.data.countdraw_value;
            this.drawinit();
            this.loading = false;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      } else {
        alert("请选择危害");
      }
    },
    drawinit() {
      // 基于准备好的dom，初始化echarts实例
      let myChart = echarts.init(document.getElementById("echartss")); // 指定图表的配置项和数据
      var option = {
        title: {
          text: "伤害排名",
        },
        tooltip: {},
        legend: {
          data: ["伤害累计事件数"],
        },
        xAxis: {
          data: this.countdraw_name,
        },
        yAxis: {},
        series: [
          {
            name: "伤害累计事件数",
            type: "bar",
            data: this.countdraw_value,
          },
        ],
      };

      // 使用刚指定的配置项和数据显示图表。
      myChart.setOption(option);
    },
  },
};
</script>
