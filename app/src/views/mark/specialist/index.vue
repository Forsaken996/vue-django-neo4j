<template>
  <div
    class="app-container"
    v-loading="loading"
    element-loading-text="拼命加载中"
    element-loading-spinner="el-icon-loading"
    element-loading-background="rgba(0, 0, 0, 0.8)"
  >
    <el-divider content-position="left">消费品特征</el-divider>

    <el-table :data="info" stripe width="100%" key="info">
      <el-table-column
        v-for="(item, i) in infocolumns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="120%"
      >
        <template slot-scope="scope">
          <div>{{ scope.row[i] }}</div>
        </template>
      </el-table-column>
      <el-table-column align="right" min-width="100%">
        <template slot-scope="scope">
          <el-popconfirm
            confirm-button-text="删除"
            cancel-button-text="否"
            icon="el-icon-info"
            icon-color="red"
            confirm-button-type="danger"
            title="确定删除该行信息吗"
            @onConfirm="Delete()"
          >
            <el-button slot="reference" type="danger">删除</el-button>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-divider content-position="left">评估项</el-divider>

    <el-table :data="forecastend" stripe width="100%" key="end">
      <el-table-column
        v-for="(item, i) in forecastcolumns"
        :key="i"
        :label="item"
        show-overflow-tooltip
        min-width="120%"
      >
        <template slot-scope="scope">
          <div v-if="!scope.row.isEdit">{{ scope.row[i] }}</div>
          <div v-else-if="forecastcolumns[i] == '危害类型'">
            <template>
              <el-select v-model="scope.row[i]" placeholder="请选择">
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
          <div v-else-if="forecastcolumns[i] == '风险等级'">
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
          <div v-else-if="forecastcolumns[i] == '概率'">
            <template>
              <el-input v-model="scope.row[i]"></el-input>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column align="right" min-width="100%">
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
              @onConfirm="handleDelete(scope.$index)"
            >
              <el-button slot="reference" type="danger">删除</el-button>
            </el-popconfirm>
          </template>
          <template>
            <el-popconfirm
              confirm-button-text="添加"
              cancel-button-text="否"
              icon="el-icon-info"
              icon-color="green"
              confirm-button-type="success"
              title="确定添加一行信息吗"
              @onConfirm="Add()"
            >
              <el-button slot="reference" type="success">添加</el-button>
            </el-popconfirm>
          </template>
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
      :closable="inputVisible ? true : false"
      :disable-transitions="false"
      @close="handleClose(item)"
    >
      {{ item }}</el-tag
    >
    <el-input
      class="input-new-tag"
      v-if="inputVisible"
      v-model="inputValue"
      ref="saveTagInput"
      size="small"
      @keyup.enter.native="handleInputConfirm()"
      @blur="handleInputConfirm()"
    >
    </el-input>
    <el-button
      v-if="inputVisible"
      class="button-new-tag"
      size="small"
      @click="showInput"
      >+添加新的关键字</el-button
    >
    <el-button align="right" @click="changetags()">{{
      inputVisible ? "完成" : "编辑"
    }}</el-button>
    <div class="paginationClass">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page.sync="ListQuery.currentPage"
        :page-sizes="[1]"
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
      forecastcolumns: ["危害类型", "风险等级", "概率"],
      forecastend: [],
      templist: [],
      harmfeatures: [],
      info: [[""]],
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
      risk: ["可接受风险", "低风险", "中风险", "高风险"],
      infocolumns: [],
      ListQuery: {
        total: 0, //默认数据总数
        pagesize: 1, //每页的数据条数
        currentPage: 1, //默认开始页面
      },
      loading: false,
      inputVisible: false,
      inputValue: "",
    };
  },
  created() {
    this.handleCurrentChange(1);
  },
  methods: {
    getList(currentPage) {
      this.loading = true;
      let url =
        config.DataServer + 'querypreinfo/?page=' + String(currentPage);
        //"http://localhost:8000/api/querypreinfo/?page=" + String(currentPage);
      //console.log(url);
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          console.log(response);
          if (response.data.msg == "empty") {
            alert("数据为空");
            this.loading = false;
          } else {
            this.forecastend = JSON.parse(JSON.stringify(response.data.data));
            this.templist = JSON.parse(JSON.stringify(response.data.data));
            this.harmfeatures = response.data.features;
            this.info[0] = response.data.info;
            this.infocolumns = response.data.infocolumns;
            this.ListQuery.total = response.data.total;
            this.loading = false;
            //console.log(this.info);
          }
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },
    //分页方法（重点）
    currentChangePage(currentPage) {
      if (!this.ListQuery.pageSize) {
        this.ListQuery.pageSize = 1;
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
      this.getList(currentPage);
    },

    handleClick(row, index) {
      // 动态设置数据并通过这个数据判断显示方式
      if (row.isEdit) {
        //console.log(row, index);
        this.$delete(row, "isEdit");
        var tp = [];
        for (let i = 0; i < this.forecastend.length; i++) {
          if (i != index) {
            tp.push(this.templist[i]);
          } else {
            tp.push(row);
          }
        }
        if (JSON.stringify(tp) != JSON.stringify(this.templist)) {
          let temp = {};
          temp = { data: tp, features: this.harmfeatures };
          let p = JSON.stringify(temp);
          let url =
            config.DataServer + "changeass/?eve=" +
            //"http://localhost:8000/api/changeass/?eve=" +
            this.info[0][0] +
            "&value=" +
            p;
          //console.log(url)
          axis
            .post(url)
            .then((response) => {
              console.log("连接成功");
              console.log(response);
              this.loading = false;
            })
            .catch((error) => {
              console.log("连接失败");
              console.log(error);
            });
          this.templist = tp;
        }
      } else {
        this.$set(row, "isEdit", true);
      }
    },

    handleDelete(index) {
      let temp = [];
      for (let i = 0; i < this.forecastend.length; i++) {
        if (i != index) {
          temp.push(this.forecastend[i]);
        }
      }
      this.forecastend = temp;
      let tp = {};
      tp = { data: temp, features: this.harmfeatures };
      let p = JSON.stringify(tp);
      let url =
        config.DataServer + "changeass/?eve=" +
        //"http://localhost:8000/api/changeass/?eve=" +
        this.info[0][0] +
        "&value=" +
        p;
      //console.log(url)
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          console.log(response);
          this.loading = false;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
      this.templist = tp;
    },

    Delete() {
      let url = config.DataServer + "deleteass/?eve=" + this.info[0][0];
      //"http://localhost:8000/api/deleteass/?eve=" + this.info[0][0];
      //console.log(url)
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          console.log(response);
          this.handleCurrentChange(1);
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    Add() {
      this.forecastend.push(["", "", ""]);
      this.templist.push(["", "", ""]);
    },

    //删除标签
    handleClose(tag) {
      this.harmfeatures.splice(this.harmfeatures.indexOf(tag), 1);
      let temp = { data: this.forecastend, features: this.harmfeatures };
      let p = JSON.stringify(temp);
      let url =
        config.DataServer + 'changeass/?eve=' +
        //"http://localhost:8000/api/changeass/?eve=" +
        this.info[0][0] +
        "&value=" +
        p;
      //console.log(url)
      axis
        .post(url)
        .then((response) => {
          console.log("连接成功");
          console.log(response);
          this.loading = false;
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },

    showInput() {
      this.inputVisible = true;
      this.$nextTick((_) => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },

    handleInputConfirm() {
      let inputValue = this.inputValue;
      if (inputValue) {
        this.harmfeatures.push(inputValue);
        let temp = { data: this.forecastend, features: this.harmfeatures };
        let p = JSON.stringify(temp);
        let url =
          config.DataServer + 'changeass/?eve=' +
          //"http://localhost:8000/api/changeass/?eve=" +
          this.info[0][0] +
          "&value=" +
          p;
        //console.log(url)
        axis
          .post(url)
          .then((response) => {
            console.log("连接成功");
            console.log(response);
            this.loading = false;
          })
          .catch((error) => {
            console.log("连接失败");
            console.log(error);
          });
      }
      this.inputValue = "";
    },

    changetags() {
      if (this.inputVisible) {
        this.inputVisible = false;
      } else {
        this.inputVisible = true;
      }
    },
  },
};
</script>

<style>
.el-tag {
  margin-right: 10px;
}
.button-new-tag {
  margin-right: 10px;
  margin-top: 20px;
  height: 40px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  margin-right: 10px;
  width: 90px;
  vertical-align: bottom;
}
</style>

