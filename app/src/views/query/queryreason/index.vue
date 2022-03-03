<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select
        v-model="s_hurt"
        placeholder="伤害"
        clearable
        class="filter-item"
        style="width: 200px"
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
        查询造成该伤害的主要危害原因
      </el-button>
    </div>
    <div
      v-loading="loading"
      element-loading-text="拼命加载中"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)"
    >
      <el-table :data="tempList" stripe style="width: 100%">
        <el-table-column v-if="show" label="序号" type="index">
          <template slot-scope="scope">
            <span>{{
              (ListQuery.currentPage - 1) * ListQuery.pageSize +
              scope.$index +
              1
            }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-for="(item, i) in columns"
          :key="i"
          :label="item"
          show-overflow-tooltip
        >
          <template slot-scope="scope">
            {{ scope.row[i] }}
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
      <div
        style="width: 800px; height: 800px; margin-top: 20px"
        id="form"
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
import config from "../../../assets/js/config";

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
      show: false,
      tempList: [],
      columns: [],

      s_hurt: "",
      hurt: [],

      draw_data: [
        {
          name: "node01",
          des: "nodedes01",
          symbolSize: 70,
          category: 0,
        },
        {
          name: "node02",
          des: "nodedes02",
          symbolSize: 50,
          category: 1,
        },
        {
          name: "node03",
          des: "nodedes3",
          symbolSize: 50,
          category: 1,
        },
        {
          name: "node04",
          des: "nodedes04",
          symbolSize: 50,
          category: 1,
        },
        {
          name: "node05",
          des: "nodedes05",
          symbolSize: 50,
          category: 1,
        },
      ],
      draw_link: [
        {
          source: "node01",
          target: "node02",
          name: "link01",
          des: "link01des",
        },
        {
          source: "node01",
          target: "node03",
          name: "link02",
          des: "link02des",
        },
        {
          source: "node01",
          target: "node04",
          name: "link03",
          des: "link03des",
        },
        {
          source: "node01",
          target: "node05",
          name: "link04",
          des: "link05des",
        },
      ],
      ListQuery: {
        total: 0, //默认数据总数
        pagesize: 5, //每页的数据条数
        currentPage: 1, //默认开始页面
      },
      loading: false,
    };
  },
  created() {
    this.getops();
    this.handleCurrentChange(1);
  },
  methods: {
    getList() {
      this.loading = true;
      let from = (this.ListQuery.currentPage - 1) * this.ListQuery.pageSize;
      let to = this.ListQuery.currentPage * this.ListQuery.pageSize - 1;
      this.loading = true;
      var url =
        "http://localhost:8000/api/queryinfos/?start=" + from + "&to=" + to;
      //console.log(url);
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          this.tempList = JSON.parse(JSON.stringify(response.data.data));
          this.ListQuery.total = response.data.totals;
          this.columns = response.data.columns;
          this.loading = false;
          this.show = true;
          this.loading = false;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },
    //获取选择项
    getops() {
      //var url = "http://localhost:8000/api/getops/";
      var url = config.DataServer + "getops/";
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          this.hurt = response.data.hurt;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },
    countproducthurtmost() {
      if (this.s_hurt) {
        this.loading = true;
        let from = (this.ListQuery.currentPage - 1) * this.ListQuery.pageSize;
        let to = this.ListQuery.currentPage * this.ListQuery.pageSize - 1;
        var query_url =
          config.DataServer + "querymostreason/?start=" +
          //"http://localhost:8000/api/querymostreason/?start=" +
          from +
          "&to=" +
          to +
          "&hurt=" +
          this.s_hurt;
        axis
          .post(query_url)
          .then((response) => {
            console.log("连接成功");
            //console.log(response.data);
            this.tempList = response.data.data;
            this.draw_data = response.data.draw_data;
            this.draw_link = response.data.draw_link;
            this.columns = response.data.columns;
            this.ListQuery.total = response.data.totals;
            this.show = true;
            this.drawinit();
            this.loading = false;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      } else {
        alert("请选择伤害！");
      }
    },
    drawinit() {
      var myChart = echarts.init(document.getElementById("form"));
      var categories = [];
      for (var i = 0; i < 5; i++) {
        categories[i] = {
          name: "节点" + i,
        };
      }
      var option = {
        // 图的标题
        title: {
          text: "ECharts 关系图",
        },
        // 提示框的配置
        tooltip: {
          formatter: function (x) {
            return x.data.des;
          },
        },
        // 工具箱
        toolbox: {
          // 显示工具箱
          show: true,
          feature: {
            mark: {
              show: true,
            },
            // 还原
            restore: {
              show: true,
            },
            // 保存为图片
            saveAsImage: {
              show: true,
            },
          },
        },
        legend: [
          {
            // selectedMode: 'single',
            data: categories.map(function (a) {
              return a.name;
            }),
          },
        ],
        series: [
          {
            type: "graph", // 类型:关系图
            layout: "force", //图的布局，类型为力导图
            symbolSize: 40, // 调整节点的大小
            roam: true, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移,可以设置成 'scale' 或者 'move'。设置成 true 为都开启
            layoutAnimation: false,
            edgeSymbol: ["circle", "arrow"],
            edgeSymbolSize: [2, 5],
            edgeLabel: {
              normal: {
                textStyle: {
                  fontSize: 20,
                },
              },
            },
            force: {
              repulsion: 1000,
              edgeLength: [10, 50],
              layoutAnimation: false,
            },
            draggable: true,
            lineStyle: {
              normal: {
                width: 2,
                color: "#4b565b",
              },
            },
            edgeLabel: {
              normal: {
                show: true,
                formatter: function (x) {
                  return x.data.name;
                },
              },
            },
            label: {
              normal: {
                show: true,
                textStyle: {},
              },
            },

            // 数据
            data: this.draw_data,
            links: this.draw_link,
            categories: categories,
          },
        ],
      };
      myChart.setOption(option);
    },
    //分页方法（重点）
    currentChangePage(currentPage) {
      if (!this.ListQuery.pageSize) {
        this.ListQuery.pageSize = 5;
      }
      let from = (currentPage - 1) * this.ListQuery.pageSize + 1;
      let to = currentPage * this.ListQuery.pageSize;
      if (this.s_hurt) {
        this.countproducthurtmost();
      } else {
        this.getList();
      }
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
  },
};
</script>
