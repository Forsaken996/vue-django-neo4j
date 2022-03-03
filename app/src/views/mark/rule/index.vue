<template>
  <div>
    <div style="display: flex">
      <el-select
        v-model="title"
        placeholder="请选择标注项"
        class="filter-item"
        style="width: 200px"
      >
        <el-option
          v-for="item in titles"
          :key="item.key"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-input
        v-if="title == '消费品名称' || title == '消费品问题部件'"
        v-model="markdata"
        placeholder="请输入消费品名称"
        clearable
        style="width: 200px; margin-left: 20px"
      />
      <el-input
        v-if="title == '小零件'"
        v-model="markdata"
        placeholder="请输入小零件关键字"
        clearable
        style="width: 200px; margin-left: 20px"
      />
      <el-cascader
        v-if="title == '消费品名称'"
        v-model="product_sort"
        :options="product_sorts"
        clearable
        placeholder="请选择消费品类型"
        style="width: 200px; margin-left: 20px"
      >
      </el-cascader>
      <el-select
        v-if="title == '伤害等级'"
        v-model="severity"
        placeholder="请选择严重程度"
        clearable
        class="filter-item"
        style="width: 200px; margin-left: 20px"
      >
        <el-option
          v-for="item in severities"
          :key="item.key"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-input
        v-if="title == '消费品问题部件'"
        v-model="problemcomponent"
        placeholder="请输入消费品问题部件"
        clearable
        style="width: 200px; margin-left: 20px"
      />
      <el-button @click="query()" style="margin-left: 10px">查询</el-button>
      <el-button @click="add()" style="margin-left: 20px">添加</el-button>
    </div>
    <el-table :data="tempList" style="width: 100%">
      <el-table-column label="标注项" prop="title">
        <template slot-scope="scope">
          <div>{{ scope.row.title }}</div>
        </template>
      </el-table-column>
      <el-table-column label="标注数据" prop="data">
        <template slot-scope="scope">
          <div v-if="!scope.row.isEdit">{{ scope.row.data }}</div>
          <div v-else>
            <div v-if="title == '伤害等级'">
              <el-select v-if="title == '伤害等级'" v-model="scope.row.data">
                <el-option
                  v-for="item in severities"
                  :key="item.key"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </div>
            <div v-else>
              <el-input v-model="scope.row.data"></el-input>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column v-if="sort_view" label="消费品一级类型" prop="sort">
        <template slot-scope="scope">
          <div v-if="!scope.row.isEdit">{{ scope.row.sort[0] }}</div>
          <div v-else>
            <el-cascader
              v-if="title == '消费品名称'"
              v-model="scope.row.sort"
              :options="product_sorts"
              style="width: 200px; margin-left: 20px"
            >
            </el-cascader>
          </div>
        </template>
      </el-table-column>
      <el-table-column v-if="sort_view" label="消费品二级类型" prop="sort">
        <template slot-scope="scope">
          <div>{{ scope.row.sort[1] }}</div>
        </template>
      </el-table-column>
      <el-table-column v-if="damage_view" prop="tag" label="伤害对应关键词">
        <template slot-scope="scope">
          <el-tag
            v-for="(item, i) in scope.row.key"
            :key="i"
            :label="item"
            :value="item"
            :type="i % 2 == 0 ? 'primary' : 'success'"
            :closable="scope.row.closetag ? true : false"
            :disable-transitions="false"
            @close="handleClose(item, scope.$index)"
          >
            {{ item }}</el-tag
          >
          <el-input
            class="input-new-tag"
            v-if="inputVisible && scope.row.closetag"
            v-model="inputValue"
            ref="saveTagInput"
            size="small"
            @keyup.enter.native="handleInputConfirm(scope.$index)"
            @blur="handleInputConfirm(scope.$index)"
          >
          </el-input>
          <el-button
            v-if="!inputVisible && scope.row.closetag"
            class="button-new-tag"
            size="small"
            @click="showInput"
            >+添加新的关键字</el-button
          >
        </template>
      </el-table-column>
      <el-table-column align="right">
        <template slot-scope="scope">
          <el-button @click="handleClick(scope.row, scope.$index)">
            {{ scope.row.isEdit ? "完成" : "编辑" }}
          </el-button>
          <el-button
            type="danger"
            v-if="scope.row.isEdit ? true : false"
            @click="handleDelete(scope.$index, scope.row)"
            >删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>



<script>
import axis from "axios";
import config from "../../../assets/js/config";
export default {
  data() {
    return {
      tableinfo: [{ title: "消费品名称", data: "鼠标", sort: ["其他", ""] }],
      tempList: [{ title: "消费品名称", data: "鼠标", sort: ["其他", ""] }],
      search: "",
      title: "消费品名称",
      titles: ["消费品名称", "小零件", "伤害等级", "消费品问题部件"],
      markdata_view: "请选择消费品名称",
      productname: [],
      littlepart: [],
      damagetype: [],
      problempart: [],
      severities: [1, 2, 3, 4],
      severity: "", //严重程度
      problemcomponent: "", //消费品问题部件输入
      sort_view: true, //消费品名称是否显示sort模块
      damage_view: false, //是否显示伤害对应的关键词
      inputVisible: false,
      problem_part: false, //是否显示问题部件如输入框
      inputValue: "",
      markdata: "",
      ListQuery: {
        total: 0, //默认数据总数
        pagesize: 5, //每页的数据条数
        currentPage: 1, //默认开始页面
      },
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
      ], //消费品的类型选择项们
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      var query_url =
      config.DataServer + 'api/querymarkinfo/';
      // "http://localhost:8000/api/querymarkinfo/";
      axis
        .post(query_url)
        .then((response) => {
          console.log("连接成功");
          this.tableinfo = response.data.data;
          this.productname = response.data.productname;
          this.littlepart = response.data.littlepart;
          this.damagetype = response.data.damagetype;
          this.problempart = response.data.problempart;
          this.tempList = JSON.parse(JSON.stringify(this.productname));
          console.log(response);
        })
        .catch((error) => {
          console.log("连接失败");
          console.log(error);
        });
    },
    handleClick(row, index) {
      // 动态设置数据并通过这个数据判断显示方式
      if (row.isEdit) {
        //console.log(row);
        //console.log(index);
        this.$delete(row, "isEdit");
        let sortindex = -1;
        let before = "";
        let after = "";
        let before_sort1 = "";
        let before_sort2 = "";
        let after_sort1 = "";
        let after_sort2 = "";
        if (this.title == "消费品名称") {
          sortindex = 0;
          before = this.productname[index]["data"];
          before_sort1 = this.productname[index]["sort"][0];
          before_sort2 = this.productname[index]["sort"][1];
        } else if (this.title == "小零件") {
          sortindex = 1;
          before = this.littlepart[index]["data"];
        } else if (this.title == "伤害等级") {
          sortindex = 2;
          before = this.damagetype[index]["data"];
          this.$delete(row, "closetag", true);
        } else if (this.title == "消费品问题部件") {
          sortindex = 3;
          before = this.problempart[index]["data"];
        }
        after = row.data;
        after_sort1 = row.sort[0];
        if (row.sort[1]) {
          after_sort2 = row.sort[1];
        } else {
          after_sort2 = "";
        }
        // console.log(sortindex);
        // console.log(before);
        // console.log(after);
        // console.log(before_sort1);
        // console.log(before_sort2);
        // console.log(after_sort1);
        // console.log(after_sort2);
        var query_url =
          config.DataServer + 'changerulesmark/?sortindex=' +
          //"http://localhost:8000/api/changerulesmark/?sortindex=" + 
          sortindex;
        if ((sortindex == 1 || sortindex == 3) && before != after) {
          query_url = query_url + "&before=" + before + "&after=" + after;
          axis
            .post(query_url)
            .then((response) => {
              console.log("连接成功");
              console.log(response);
            })
            .catch((error) => {
              console.log("连接失败");
              console.log(error);
            });
        } else if (
          sortindex == 0 &&
          (before != after ||
            before_sort1 != after_sort1 ||
            before_sort2 != after_sort2)
        ) {
          query_url =
            query_url +
            "&before=" +
            before +
            "&after=" +
            after +
            "&before_sort1=" +
            before_sort1 +
            "&after_sort1=" +
            after_sort1 +
            "&before_sort2=" +
            before_sort2 +
            "&after_sort2=" +
            after_sort2;
          axis
            .post(query_url)
            .then((response) => {
              console.log("连接成功");
              console.log(response);
            })
            .catch((error) => {
              console.log("连接失败");
              console.log(error);
            });
        } else if (sortindex == 2 && before != after) {
          query_url =
            query_url +
            "&before=" +
            before +
            "&after=" +
            after +
            "&damagename=" +
            this.damagetype[index]["title"];
          axis
            .post(query_url)
            .then((response) => {
              console.log("连接成功");
              console.log(response);
            })
            .catch((error) => {
              console.log("连接失败");
              console.log(error);
            });
        }

        if (
          (before_sort1 != after_sort1 || before_sort2 != after_sort2) &&
          before == after
        ) {
          //添加axis
          var url =
            config.DataServer + 'modifysortbyproductname/?before_sort1=' +
            //"http://localhost:8000/api/modifysortbyproductname/?before_sort1=" +
            before_sort1 +
            "&after_sort1=" +
            after_sort1 +
            "&productname=" +
            before;
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
        }
      } else {
        this.$set(row, "isEdit", true);
        if (this.title == "伤害等级") {
          this.$set(row, "closetag", true);
        }
      }
    },
    add() {
      // console.log("添加");
      if (this.title && this.markdata) {
        let sortindex = -1;
        let addition = "";
        var p = {};
        let exist = false;
        var query_url = config.DataServer + 'insertrulesmark/?sortindex='
        //"http://localhost:8000/api/insertrulesmark/?sortindex=";
        if (this.title == "消费品名称" && this.product_sort.length) {
          if (this.product_sort.length) {
            sortindex = 0;
            if (this.product_sort.length > 1) {
              addition = this.product_sort[1];
            } else {
              addition = this.product_sort[0];
            }
            this.sort_view = true;
            p = { title: this.title, data: this.markdata, sort: addition };
            query_url =
              query_url +
              sortindex +
              "&name=" +
              this.markdata +
              "&addition=" +
              addition;
          } else {
            alert("请选择消费品类型!");
          }
        } else if (this.title == "小零件") {
          sortindex = 1;
          this.sort_view = false;
          p = { title: this.title, data: this.markdata };
          query_url = query_url + sortindex + "&name=" + this.markdata;
        } else if (this.title == "伤害类型" && this.severity) {
          if (this.severity) {
            sortindex = 2;
            addition = this.severity;
            this.sort_view = false;
            p = { title: this.markdata, data: this.severity };
            for (let t = 0; t < this.tempList.length; t++) {
              if (this.tempList[t].title == this.markdata) {
                exist = true;
                break;
              }
            }
            query_url =
              query_url +
              sortindex +
              "&name=" +
              this.markdata +
              "&addition=" +
              addition;
          } else {
            alert("请选择伤害类型!");
          }
        } else if (this.title == "消费品问题部件" && this.problemcomponent) {
          sortindex = 3;
          this.sort_view = false;
          p = { title: this.markdata, data: this.problemcomponent };
          query_url =
            query_url +
            sortindex +
            "&name=" +
            this.markdata +
            "&addition=" +
            this.problemcomponent;
        }
        if (exist) {
          alert("该数据项已存在!");
        } else {
          var temp = [p];
          for (let i = 0; i < this.tempList.length; i++) {
            temp.push(this.tempList[i]);
          }
          if (sortindex == 0) {
            this.productname.push(p);
          } else if (sortindex == 1) {
            this.littlepart.push(p);
          } else if (sortindex == 2) {
            this.damagetype.push(p);
          } else if (sortindex == 3) {
            this.problempart.push(p);
          }
          this.tempList = temp;
          axis
            .post(query_url)
            .then((response) => {
              console.log("连接成功");
              console.log(response);
            })
            .catch((error) => {
              console.log("连接失败");
              console.log(error);
            });
        }
      } else {
        alert("请选择标注项并输入全部标注数据!");
      }
    },
    query() {
      //console.log("查询");
      var temp = [];
      if (this.title == "消费品名称") {
        this.tempList = JSON.parse(JSON.stringify(this.productname));
        var p = this.tempList;
        if (this.markdata != "") {
          for (var i = 0; i < p.length; i++) {
            if (p[i].data.indexOf(this.markdata) != -1) {
              temp.push(p[i]);
            }
          }
          //标注分类筛选
          if (this.product_sort.length) {
            var tp = [];
            for (var i = 0; i < temp.length; i++)
              if (this.product_sort.length > 1) {
                if (temp[i].sort == this.product_sort[1]) {
                  tp.push(temp[i]);
                }
              } else {
                if (temp[i].sort == this.product_sort[0]) {
                  tp.push(temp[i]);
                }
              }
            temp = tp;
          }
          this.tempList = JSON.parse(JSON.stringify(temp));
        } else {
          //标注分类筛选
          if (this.product_sort.length) {
            var tp = [];
            for (var i = 0; i < p.length; i++) {
              if (this.product_sort.length > 1) {
                if (p[i].sort == this.product_sort[1]) {
                  tp.push(p[i]);
                }
              } else {
                if (p[i].sort == this.product_sort[0]) {
                  tp.push(p[i]);
                }
              }
              this.tempList = tp;
            }
          }
        }
      } else if (this.title == "小零件") {
        this.tempList = JSON.parse(JSON.stringify(this.littlepart));
        var p = this.tempList;
        if (this.markdata != "") {
          var temp = [];
          for (var i = 0; i < p.length; i++) {
            if (p[i].data.indexOf(this.markdata) != -1) {
              temp.push(p[i]);
            }
          }
          this.tempList = JSON.parse(JSON.stringify(temp));
        }
      } else if (this.title == "伤害等级") {
        this.tempList = JSON.parse(JSON.stringify(this.damagetype));
        var p = this.tempList;
        var temp = [];
        if (this.markdata != "") {
          for (var i = 0; i < p.length; i++) {
            if (p[i].title.indexOf(this.markdata) != -1) {
              temp.push(p[i]);
            }
          }
          //标注严重程度筛选
          if (this.severity) {
            var tp = [];
            for (var i = 0; i < temp.length; i++) {
              // console.log(this.severity);
              // console.log(temp[i].data);
              if (this.severity == temp[i].data) {
                tp.push(temp[i]);
              }
            }
            temp = tp;
          }
          this.tempList = JSON.parse(JSON.stringify(temp));
        } else {
          //标注严重程度筛选
          if (this.severity) {
            var tp = [];
            for (var i = 0; i < p.length; i++)
              if (this.severity == p[i].data) {
                tp.push(p[i]);
              }
            this.tempList = tp;
          }
        }
      } else if (this.title == "消费品问题部件") {
        this.tempList = JSON.parse(JSON.stringify(this.problempart));
        var p = this.tempList;
        var temp = [];
        //console.log(this.markdata);
        if (this.markdata) {
          for (var i = 0; i < p.length; i++) {
            //console.log(p[i]);
            if (p[i].title.indexOf(this.markdata) != -1) {
              temp.push(p[i]);
              //console.log(this.markdata);
              //console.log(p[i].title);
            }
          }
          //console.log(temp);
          //标注严重程度筛选
          if (this.problemcomponent) {
            var tp = [];
            for (var i = 0; i < temp.length; i++) {
              //console.log(this.problemcomponent);
              //console.log(temp[i].data);
              if (temp[i].data.indexOf(this.problemcomponent) != -1) {
                tp.push(temp[i]);
              }
            }
            temp = tp;
          }
          this.tempList = JSON.parse(JSON.stringify(temp));
        } else {
          //标注严重程度筛选
          if (this.problemcomponent) {
            var tp = [];
            for (var i = 0; i < p.length; i++)
              if (p[i].data.indexOf(this.problemcomponent) != -1) {
                tp.push(p[i]);
              }
            this.tempList = tp;
          }
        }
      }

      if (this.title == "消费品名称") {
        this.sort_view = true;
      } else {
        this.sort_view = false;
      }
      if (this.title == "伤害等级") {
        this.damage_view = true;
      } else {
        this.damage_view = false;
      }
      if (this.title == "消费品问题部件") {
        this.problem_part = true;
      } else {
        this.problem_part = false;
      }
    },
    handleDelete(index, row) {
      //console.log(index, row);
      var sortindex = -1;
      let names = "";
      let temp = [];
      for (let i = 0; i < this.tempList.length; i++) {
        if (i != index) {
          temp.push(this.tempList[i]);
        }
      }
      this.tempList = temp;
      if (this.title == "消费品名称") {
        sortindex = 0;
        names = this.productname[index]["data"];
        this.productname = temp;
      } else if (this.title == "小零件") {
        sortindex = 1;
        names = this.littlepart[index]["data"];
        this.littlepart = temp;
      } else if (this.title == "伤害等级") {
        sortindex = 2;
        names = this.damagetype[index]["title"];
        this.damagetype = temp;
      } else if (this.title == "消费品问题部件") {
        sortindex = 3;
        names = this.problempart[index]["title"];
        let problemparts = this.problempart[index]["data"];
        this.problempart = temp;
        var url =
          config.DataServer + 'deletemark/?sortindex=' +
          //"http://localhost:8000/api/deletemark/?sortindex=" +
          sortindex +
          "&name=" +
          names +
          "&problempart=" +
          problemparts;
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
        return;
      }
      //console.log("test");
      var url =
        config.DataServer + 'deletemark/?sortindex=' +
        //"http://localhost:8000/api/deletemark/?sortindex=" +
        sortindex +
        "&name=" +
        names;
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
    //删除标签
    handleClose(tag, index) {
      this.tempList[index].key.splice(this.tempList[index].key.indexOf(tag), 1);
      //console.log(tag);
      var url =
        config.DataServer + 'deletedamagekey/?damage=' +
        //"http://localhost:8000/api/deletedamagekey/?damage=" +
        this.tempList[index].title +
        "&key=" +
        tag;
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
    showInput() {
      this.inputVisible = true;
      this.$nextTick((_) => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },

    handleInputConfirm(index) {
      let inputValue = this.inputValue;
      if (inputValue) {
        this.tempList[index].key.push(inputValue);
        //入库
        var url =
          config.DataServer + 'insertdamagekey/?damage=' +
          //"http://localhost:8000/api/insertdamagekey/?damage=" +
          this.tempList[index].title +
          "&key=" +
          inputValue;
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
      this.inputVisible = false;
      this.inputValue = "";
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
  height: 32px;
  padding-top: 0;
  padding-bottom: 0;
  background-color: #80ffff;
}
.input-new-tag {
  margin-right: 10px;
  width: 90px;
  vertical-align: bottom;
}
</style>