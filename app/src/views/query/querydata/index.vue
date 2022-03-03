<template>
  <div class="app-container">
    <div class="filter-container">
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
      <el-input
        v-model="s_product"
        placeholder="请输入内容"
        clearable
        style="width: 200px; margin-right: 10px"
      ></el-input>
      <el-select
        v-model="s_area"
        placeholder="地区"
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
      <!-- <el-select
        v-model="s_class"
        placeholder="产品大类"
        clearable
        class="filter-item"
        style="width: 200px; margin-right: 10px"
      > -->
      <el-cascader
          placeholder="请选择消费品类型"
          :props="{ checkStrictly: true }"
          v-model="s_class"
          :options="classification"
          clearable
        >
      </el-cascader>
        <!-- <el-option
          v-for="item in classification"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select> -->
      <el-select
        v-model="s_hurt"
        placeholder="伤害"
        clearable
        class="filter-item"
        style="width: 200px; margin-right: 5px"
      >
        <el-option
          v-for="item in hurt"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-cascader :options="harm" v-model="s_harm" clearable>
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
        @click="querybycondition"
        style="margin-left: 20px"
      >
        查询
      </el-button>
    </div>
    <el-table
      v-loading="loading"
      element-loading-text="拼命加载中"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)"
      :data="tempList"
      stripe
      style="width: 100%"
    >
      <el-table-column v-if="show" label="序号" type="index">
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
        :width="colwidth[i]"
        show-overflow-tooltip
      >
        <template slot-scope="scope">
          {{ scope.row[i] }}
        </template>
      </el-table-column>
    </el-table>
    <!-- <div class="Table">
      <el-table
        stripe
        style="width: 100%">
        <el-table-column v-for="item in List.column" :key="item" :label="item" :value="item">
        </el-table-column>
      </el-table>
    </div> -->
    <div class="paginationClass">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page.sync="ListQuery.currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="ListQuery.pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="ListQuery.total"
      >
      </el-pagination>
    </div>
  </div>
</template>

<script>
import waves from "@/directive/waves"; // waves directive
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import axis from "axios";
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
      query: false,
      s_product: "", //输入的消费品
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
      ListQuery: {
        total: 0, //默认数据总数
        pagesize: 10, //每页的数据条数
        currentPage: 1, //默认开始页面
      },
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
      value1: "",
      value2: "",
      loading: true,
      colwidth: [],
    };
  },
  created() {
    this.getops();
    this.handleCurrentChange(1);
  },
  methods: {
    getList() {
      let from = (this.ListQuery.currentPage - 1) * this.ListQuery.pageSize;
      let to = this.ListQuery.currentPage * this.ListQuery.pageSize - 1;
      this.loading = true;
      var url =
        config.DataServer + 'queryinfos/?start='
        //"http://localhost:8000/api/queryinfos/?start=" 
        + from + "&to=" + to;
      //console.log(url);
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          this.tempList = JSON.parse(JSON.stringify(response.data.data));
          this.ListQuery.total = response.data.totals;
          this.columns = response.data.columns;
          this.setwidth();
          this.loading = false;
          this.show = true;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    //获取选择项
    getops() {
      //var url = "http://localhost:8000/api/getops/";
      var url = config.DataServer + "getops/"
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

    setwidth() {
      for (let i = 0; i < this.columns.length; i++) {
        this.colwidth.push(90);
      }
      for (let i = 0; i < this.tempList.length; i++) {
        for (let k = 0; k < this.tempList[i].length; k++) {
          if (this.columns[k] != "伤害事件") {
            let len = this.tempList[i][k].length * 10 + 20;
            if (this.colwidth[k] < len) {
              this.colwidth[k] = len;
            }
            if (this.columns[k] == "链接") {
              this.colwidth[k] = 500;
            }
          }
        }
      }
    },

    querybycondition() {
      //console.log(this.s_harm);
      if (!this.times) {
        this.times = [];
      }
      this.loading = true;
      let from = (this.ListQuery.currentPage - 1) * this.ListQuery.pageSize;
      let to = this.ListQuery.currentPage * this.ListQuery.pageSize - 1;
      if (
        this.times.length == 0 &&
        !this.s_class &&
        !this.s_area &&
        !this.s_hurt &&
        this.s_harm.length == 0 &&
        !this.s_product
      ) {
        this.getList(from, to);
      } else {
        //console.log(this.s_harm[2]);
        var query_url =
          config.DataServer + 'querybycondition/?start='
          //"http://localhost:8000/api/querybycondition/?start=" 
          +
          from +
          "&to=" +
          to;
        //构造字符串
        if (this.times.length != 0) {
          let start = this.times[0];
          let end = this.times[1];
          query_url = query_url + "&time=" + start + "-" + end;
        }
        if (this.s_class) {
          if (this.s_class.length == 2) {
            query_url =
              query_url +
              "&class1=" +
              this.s_class[0] +
              "&class2=" +
              this.s_class[1];
          } else if (this.s_class.length == 1) {
            query_url = query_url + "&class1=" + this.s_class[0];
          }
        }
        if (this.s_area) {
          query_url = query_url + "&area=" + this.s_area;
        }
        if (this.s_hurt) {
          query_url = query_url + "&hurt=" + this.s_hurt;
        }
        if (this.s_harm.length != 0) {
          query_url = query_url + "&harm=" + this.s_harm[3];
        }
        if (this.s_product) {
          query_url = query_url + "&product=" + this.s_product;
        }

        //console.log(query_url);
        axis
          .post(query_url)
          .then((response) => {
            console.log("连接成功");
            this.tempList = JSON.parse(JSON.stringify(response.data.data));
            this.ListQuery.total = response.data.totals;
            this.columns = response.data.columns;
            this.setwidth();
            this.loading = false;
            this.show = true;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      }
    },

    //分页方法（重点）
    currentChangePage(currentPage) {
      if (!this.ListQuery.pageSize) {
        this.ListQuery.pageSize = 10;
      }
      let from = (currentPage - 1) * this.ListQuery.pageSize + 1;
      let to = currentPage * this.ListQuery.pageSize;
      if (
        this.times.length != 0 ||
        this.s_class ||
        this.s_area ||
        this.s_hurt ||
        this.s_harm ||
        this.s_product
      ) {
        this.querybycondition();
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
