<template>
  <div class="app-container">
      <div style="margin-bottom:20px">
          <el-input
            v-model="s_product"
            placeholder="请输入消费品"
            clearable
            style="width: 200px; margin-right: 10px"
        ></el-input>
        <el-button
            v-waves
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            @click="querymain"
            style="margin-left: 20px"
        >
            查询主要危害源
        </el-button>
      </div>
      
      <div style="margin-bottom:20px">
          <el-table
            v-loading="loading"
            element-loading-text="拼命加载中"
            element-loading-spinner="el-icon-loading"
            element-loading-background="rgba(0, 0, 0, 0.8)"
            :data="harmtable"
            stripe
            style="width: 100%"
            >
            <el-table-column
                v-for="(item, i) in harmtablecolumns"
                :key="i"
                :label="item"
                show-overflow-tooltip
            >
                <template slot-scope="scope">
                    {{ scope.row[i] }}
                </template>
            </el-table-column>
        </el-table>
      </div>

      <div style="margin-bottom:20px">
          <el-table
            v-loading="loading"
            element-loading-text="拼命加载中"
            element-loading-spinner="el-icon-loading"
            element-loading-background="rgba(0, 0, 0, 0.8)"
            :data="sourcetable"
            stripe
            style="width: 100%"
            >
            <el-table-column
                v-for="(item, i) in sourcetablecolumns"
                :key="i"
                :label="item"
                show-overflow-tooltip
            >
                <template slot-scope="scope">
                    {{ scope.row[i] }}
                </template>
            </el-table-column>
            </el-table>
      </div>

      <div
        style="width: 800px; height: 600px; margin-top: 20px"
        id="echartss"
      ></div>
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
        s_product : "",
        harmtable : [],
        harmtablecolumns : [],
        sourcetable : [],
        sourcetablecolumns : [],
        loading : "",
        xAxis : [],
        legend : [],
        series : [],
    };
  },
  created() {
  },
  methods: {
      querymain(){
          if(this.s_product){
                console.log('查询主要危害源');
                //var url = "http://localhost:8000/api/querymainharm/?proname=" + this.s_product;
                var url = config.DataServer + "querymainharm/?proname=" + this.s_product;
                axis
                .post(url)
                .then((response) => {
                    console.log("连接成功");
                    this.harmtable = response.data.harmtable;
                    this.harmtablecolumns = response.data.harmtablecolumns;
                    this.sourcetable = response.data.sourcetable;
                    this.sourcetablecolumns = response.data.sourcetablecolumns;
                    this.xAxis = response.data.xAxis;
                    this.legend = response.data.legend;
                    this.series = response.data.series;
                    this.drawinit();
                    console.log(response);
                })
                .catch((error) => {
                    console.log("连接失败");
                    console.log(error);
                });
          }else{
              alert('请输入消费品名称!');
          }
          
      },
      drawinit() {
        console.log(document.getElementById('echartss'))
        let myChart = echarts.init(document.getElementById("echartss")); // 指定图表的配置项和数据
        const posList = [
        'left',
        'right',
        'top',
        'bottom',
        'inside',
        'insideTop',
        'insideLeft',
        'insideRight',
        'insideBottom',
        'insideTopLeft',
        'insideTopRight',
        'insideBottomLeft',
        'insideBottomRight'
        ];
        app.configParameters = {
        rotate: {
            min: -90,
            max: 90
        },
        align: {
            options: {
            left: 'left',
            center: 'center',
            right: 'right'
            }
        },
        verticalAlign: {
            options: {
            top: 'top',
            middle: 'middle',
            bottom: 'bottom'
            }
        },
        position: {
            options: posList.reduce(function (map, pos) {
            map[pos] = pos;
            return map;
            }, {})
        },
        distance: {
            min: 0,
            max: 100
        }
        };
        app.config = {
        rotate: 90,
        align: 'left',
        verticalAlign: 'middle',
        position: 'insideBottom',
        distance: 15,
        onChange: function () {
            const labelOption = {
            rotate: app.config.rotate,
            align: app.config.align,
            verticalAlign: app.config.verticalAlign,
            position: app.config.position,
            distance: app.config.distance
            };
            myChart.setOption({
            series: [
                {
                label: labelOption
                },
                {
                label: labelOption
                },
                {
                label: labelOption
                },
                {
                label: labelOption
                }
            ]
            });
        }
        };
        const labelOption = {
        show: true,
        position: app.config.position,
        distance: app.config.distance,
        align: app.config.align,
        verticalAlign: app.config.verticalAlign,
        rotate: app.config.rotate,
        formatter: '{c}  {name|{a}}',
        fontSize: 16,
        rich: {
            name: {}
        }
        };
        let option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
            type: 'shadow'
            }
        },
        legend: {
            //data: ['Forest', 'Steppe', 'Desert', 'Wetland']
            data: this.legend
        },
        toolbox: {
            show: true,
            orient: 'vertical',
            left: 'right',
            top: 'center',
            feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false },
            magicType: { show: true, type: ['line', 'bar', 'stack'] },
            restore: { show: true },
            saveAsImage: { show: true }
            }
        },
        xAxis: [
            {
            type: 'category',
            axisTick: { show: false },
            //data: ['2012', '2013', '2014', '2015', '2016']
            data: this.xAxis,
            }
        ],
        yAxis: [
            {
            type: 'value'
            }
        ],
        series: this.series,
        // series: [
        //     {
        //     name: 'Forest',
        //     type: 'bar',
        //     barGap: 0,
        //     label: labelOption,
        //     emphasis: {
        //         focus: 'series'
        //     },
        //     data: [320, 332, 301, 334, 390]
        //     },
        //     {
        //     name: 'Steppe',
        //     type: 'bar',
        //     label: labelOption,
        //     emphasis: {
        //         focus: 'series'
        //     },
        //     data: [220, 182, 191, 234, 290]
        //     },
        //     {
        //     name: 'Desert',
        //     type: 'bar',
        //     label: labelOption,
        //     emphasis: {
        //         focus: 'series'
        //     },
        //     data: [150, 232, 201, 154, 190]
        //     },
        //     {
        //     name: 'Wetland',
        //     type: 'bar',
        //     label: labelOption,
        //     emphasis: {
        //         focus: 'series'
        //     },
        //     data: [98, 77, 101, 99, 40]
        //     }
        // ]
        };

        // 使用刚指定的配置项和数据显示图表。
        myChart.setOption(option);
    },
  }
};
</script>
