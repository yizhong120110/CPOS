 $(document).ready(function() {
  /* ----------------- --------------------------
  -------------------业务主机---------------
  --------------------------------------------------*/
  // cpu
    var serversCpu = echarts.init($('#serversCpu')[0]);
    serversCpu.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,10,60,1,50,1,6, 35,1,10, 100]
            }
        ]
    });
 // CPU模拟更新数据
    var axisDataSerCpu =10;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataSerCpu = num;
        serversCpu .setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataSerCpu +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

        // 内存使用
         var serversMem = echarts.init($('#serversMem')[0]);
       serversMem.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
    var axisDataSerMem = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
       axisDataSerMem = num;
        serversMem.setOption({
                title : {
                    text: '内存使用率',
                    subtext:axisDataSerMem +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

     // I/O繁忙率
    var serversNum = echarts.init($('#serversNum')[0]);
    serversNum.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '30%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
    // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*30) ;
        serversNum.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext: num +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
  /* ----------------- --------------------------
  -------------------业务主机1---------------
  --------------------------------------------------*/
 // cpu
    var serversCpu1 = echarts.init($('#serversCpu1')[0]);
    serversCpu1.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,10,60,1,50,1,6, 35,1,10, 100]
            }
        ]
    });
 // CPU模拟更新数据
    var axisDataSerCpu1 =10;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataSerCpu1 = num;
        serversCpu1 .setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataSerCpu1 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
        // 内存使用
         var serversMem1 = echarts.init($('#serversMem1')[0]);
       serversMem1.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
   // 内存模拟更新数据
    var axisDataSerMem1 = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
        axisDataSerMem1 = num;
        serversMem1.setOption({
                title : {
                    text: '内存使用率',
                    subtext: axisDataSerMem1 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

    // I/O繁忙率
    var serversNum1 = echarts.init($('#serversNum1')[0]);
    serversNum1.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '30%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
    // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*25) ;
        serversNum1.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext: num +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);


   /* ----------------- --------------------------
  -------------------业务主机2---------------
  --------------------------------------------------*/
   // cpu
    var serversCpu2 = echarts.init($('#serversCpu2')[0]);
    serversCpu2.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,10,60,1,50,1,6, 35,1,10, 100]
            }
        ]
    });
   // CPU模拟更新数据
    var axisDataSerCpu2 =10;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataSerCpu2 = num;
        serversCpu2 .setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataSerCpu2 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

        // 内存使用
         var serversMem2 = echarts.init($('#serversMem2')[0]);
       serversMem2.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
  // 内存模拟更新数据
    var axisDataSerMem2 = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
        axisDataSerMem2 = num;
        serversMem2.setOption({
                title : {
                    text: '内存使用率',
                    subtext: axisDataSerMem2 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

    // I/O繁忙率
    var serversNum2 = echarts.init($('#serversNum2')[0]);
    serversNum2.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '40%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
    // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*5) ;
        serversNum2.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext: num +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
  /* ----------------- --------------------------
  -------------------通讯前置---------------
  --------------------------------------------------*/
    // cpu
    var commuCpu2 = echarts.init($('#commuCpu2')[0]);
    commuCpu2.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,10,60,1,50,1,6, 35,1,10, 100]
            }
        ]
    });
  // CPU模拟更新数据
    var axisDataCpu2 =10;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataCpu2 = num;
        commuCpu2 .setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataCpu2 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
        // 内存使用
         var commuMem2 = echarts.init($('#commuMem2')[0]);
       commuMem2.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','44','54','64','28','35','25','54','64','28','45','21', '2','5', '10','15','20','25','55','65','35','25','10','15','55','14','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,10,60,1,50,1,55,45,25,87,56,26,35,25,87,95,26, 35,1,10, 35,55,45,25,60,1,50,1,55,45,25,87,56,26,35,25,87,95, 100]
            }
        ]
    });
    // 内存模拟更新数据
    var axisDataMem2 = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
        axisDataMem2 = num;
        commuMem2.setOption({
                title : {
                    text: '内存使用率',
                    subtext: axisDataMem2 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
    // I/O繁忙率
    var commuNum2 = echarts.init($('#commuNum2')[0]);
    commuNum2.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '35%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '5', '10','25','10','15','55','14','44','54','64','28', '0',  '2','35','25','10','15','55','14','44','54','64','28', '0',  '2','5', '10','35','25','10','15','55','14','44','54','64','28','15','20','25','30','32','35','45','21', '2','5', '10','15','20','25','55','65','35','25','10','15','55','14','44','54','64','5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52,10,60,1,50,1,55,45,25,87,56,26,35,25,87,95,26, 35,1,55,52,10,60,1,50,1,55,45,10, 35,55,45,25,87,56,26,35,55,45,10,60,1,50,1,55,45,25,87,56,26,35,25,87,95,26, 35,1,10, 35,55,45,25,87,56,26,35,55,45, 45,30,40, 55,52,10,60,1,50,1,10, 35,55,45,25,87,56,26,100]
            }
        ]
    });
     // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*35) ;
        commuNum2.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext: num +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
 /* ----------------- --------------------------
  -------------------管理主机---------------
  --------------------------------------------------*/
    // cpu
    var manageCpu = echarts.init($('#manageCpu')[0]);
    manageCpu.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data :['35','25','10','20','25','30','32','35','45','21', '2','5', '10','15','20','25','55','65','35','25','10','15','55','14','44','54','64','28','99']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,30,20,18,68,25,22,66,35,10,90,1,50,1,55,15,25,27,56,26,35,25,87,95,26, 5,1,10, 95,2,100]
            }
        ]
    });
 // CPU模拟更新数据
    var axisDataCpu = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataCpu = num;
        manageCpu.setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataCpu +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
        // 内存使用
         var manageMem = echarts.init($('#manageMem')[0]);
       manageMem.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0',  '2','5', '10','15','20','25','30','35','45','55','65','35','25','10','15','99']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,30,2,12,35,60,60,50,50,55,10,5,3,52, 45,30,40, 80,20]
            }
        ]
    });
     // 内存模拟更新数据
    var axisDataMem = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
        axisDataMem = num;
        manageMem.setOption({
                title : {
                    text: '内存使用率',
                    subtext: axisDataMem +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

    // I/O繁忙率
    var manageNum = echarts.init($('#manageNum')[0]);
    manageNum.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '41%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '1', '2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20', '21', '22', '23', '24', '25', '26', '27', '28', '29','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20', '21', '22', '23', '24', '25', '26', '27', '28', '29','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20', '21', '22', '23', '24', '25', '26', '27', '28', '29']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[1,3,2,1,2,1,2,3,4,5,2,3,4,2,3,1,2,1,3,2,3,13,1,3,1,2,3,2,1,3,2,1,3,1,3,1,3,1,2,3,2,1,2,1,2,3,4,5,2,3,4,2,3,1,2,1,3,2,3,13,1,3,1,2,3,2,1,3,2,1,3,1,3,1,3,1,2,3,2,1,2,1,2,3,4,5,2,3,4,2,3,1,2,1,3,2,3,13,1,3,1,2,3,2,1,3,2,1,3,1,3,1,3,1,2,3,2,1,2,1,2,3,4,5,2,3,4,2,3,1,2,1,3,2,3,13,1,3,1,2,3,2,1,3,2,1,3,1,3,1,3,1,2]
            }
        ]
    });

    // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*30) ;
        manageNum.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext: num +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
 /* ----------------- --------------------------
  -------------------数据库主机---------------
  --------------------------------------------------*/
    // cpu
    var dataCpu = echarts.init($('#dataCpu')[0]);
    dataCpu.setOption({
        title : {
            text: 'CPU使用率',
            subtext: '17%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                // splitLine:{
                //     lineStyle:{color:'#8b12ae'}
                // },
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#117dbb',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'CPU使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f1f6fa',
                     },
                 lineStyle:{
                    color:'#117dbb',
                    width:1
                }   
            }
        },
                data:[70,10,60,1,50,1,6, 35,1,10, 100]
            }
        ]
    });
  // CPU模拟更新数据
    var axisDataCpu1 =10;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*38) ;
        axisDataCpu1 = num;
        dataCpu .setOption({
                title : {
                    text: 'CPU使用率',
                    subtext: axisDataCpu1 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

        // 内存使用
         var dataMem = echarts.init($('#dataMem')[0]);
       dataMem.setOption({
        title : {
            text: '内存使用率',
            subtext: '50%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#8b12ae',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'内存使用率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#f9f2f4',
                     },
                 lineStyle:{
                    color:'#8b12ae',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
   // 内存模拟更新数据
    var axisDataMem3 = 30;
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*45+11) ;
        axisDataMem3 = num;
        dataMem.setOption({
                title : {
                    text: '内存使用率',
                    subtext: axisDataMem3 +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);

    // I/O繁忙率
    var dataNum = echarts.init($('#dataNum')[0]);
    dataNum.setOption({
        title : {
            text: 'I/O繁忙率',
            subtext: '25%',
            x:'right',
            y: 'center',
            textStyle : {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            subtextStyle: {
                color:'#666',
                fontSize: '12',
                baseline:'top'
            },
        },
        grid: {
            x: 3,
            x2: 82,
            y: 7,
            y2: 3
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                axisLabel:{
                    show:false
                },
                axisTick:{
                    show:false
                },
                axisLine: {
                    onZero: false,
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
                data : ['0', '5', '10','15','20','25','30']
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel:{
                    show:false
                },

                axisLine: {
                    onZero: false,
                    axisLabel:{
                    show:false
                },
                    lineStyle:{
                        color:'#4da60c',
                        width:1
                    }
                },
            }
        ],
        series : [
            {
                name:'I/O繁忙率',
                type:'line',
                smooth:true,
                symbol:'none',
                itemStyle: {
                    normal: {
                    areaStyle: {
                       color:'#dbedce',
                     },
                 lineStyle:{
                    color:'#4da60c',
                    width:1
                }   
            }
        },
                data:[70,40,60,50,50,55,52, 45,30,40, 100]
            }
        ]
    });
    // I/O繁忙率模拟更新数据
    timeTicket = setInterval(function (){
        // axisData = (new Date()).format("HH:mm:ss");
        var num = Math.floor(Math.random()*30) ;
        dataNum.setOption({
                title : {
                    text: 'I/O繁忙率',
                    subtext:  num  +'%'
                }   
            }).addData([
            [
                0,        // 系列索引
                num, // 新增数据
                false,    // 新增数据是否从队列头部插入
                false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                // axisData  // 坐标轴标签
            ]
        ]);
    }, 3000);
    
    // 系统（软件）监控
    var jy_chart = echarts.init($('#jy_chart')[0]);
    var jy_data_length = 0;
    jy_chart.setOption({
        title: {
            text: '交易笔数',
            textStyle: {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            x: 8,
            y: 10
        },
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['总笔数','失败笔数','异常笔数'],
            y: 10
        },
        dataZoom : {
            show : true,
            realtime : true,
            start : 0,
            end : 100,
            height: 20,
            y: 240
        },
        grid: {
            x: 45,
            x2: 50,
            y: 50
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : (function (){
                    var now = new Date();
                    var res = [];
                    var len = 10;
                    var begin = Date.parse("08:00:00 "+now.format("MM/dd/yyyy"));
                    while (now>=begin) {
                        res.unshift(now.format("hh:mm:ss"));
                        now = new Date(now - 10*60*1000);
                    }
                    jy_data_length = res.length;
                    return res;
                })()
            }
        ],
        yAxis : [
            {
                name : '总笔数(千笔)',
                type : 'value',
                axisLabel : {
                    formatter: function(v){
                        return v/1000.0;
                    }
                }
            },
            {
                name : '失败/异常(千笔)',
                type : 'value',
                axisLabel : {
                    formatter: function(v){
                        return v/1000.0;
                    }
                }
            },
        ],
        series : [
            {
                name:'总笔数',
                type:'line',
                yAxisIndex:0,
                smooth:true,
                data: (function (){
                    var res = [];
                    var len = 0;
                    var last = 2000;
                    var random_lst = [Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random()];
                    while (len<jy_data_length) {
                        random = random_lst[parseInt(len/(jy_data_length/10))]+0.1;
                        last += parseInt(Math.random()*random*5000);
                        res.push( last );
                        len++;
                    }
                    return res;
                })(),
                itemStyle: {
                    normal: {
                        color: '#5AB1EF'
                    }
                }
            },
            {
                name:'失败笔数',
                type:'line',
                yAxisIndex:1,
                data: (function (){
                    var res = [];
                    var len = 0;
                    var last = 100;
                    var random_lst = [Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random()];
                    while (len<jy_data_length) {
                        random = random_lst[parseInt(len/(jy_data_length/10))]+0.1;
                        last += parseInt(Math.random()*random*200);
                        res.push( last );
                        len++;
                    }
                    return res;
                })(),
                itemStyle: {
                    normal: {
                        color: '#FF7F50'
                    }
                }
            },
            {
                name:'异常笔数',
                type:'line',
                yAxisIndex:1,
                data: (function (){
                    var res = [];
                    var len = 0;
                    var last = 50;
                    var random_lst = [Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random(), Math.random()];
                    while (len<jy_data_length) {
                        random = random_lst[parseInt(len/(jy_data_length/10))]+0.1;
                        last += parseInt(Math.random()*random*100);
                        res.push( last );
                        len++;
                    }
                    return res;
                })(),
                itemStyle: {
                    normal: {
                        color: 'red'
                    }
                }
            }
        ]
    });
    
    $("#jy_mx").datagrid({
        title: "业务交易明细",
        nowrap : true,
        fit : true,
        rownumbers : false,
        pagination : false,
        fitColumns : true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        url: "/static/_init/js/view/datagrid-data_jymx.json",
        columns: [[
            { field: 'ywmc', title: '业务名称', width: 35 },
            { field: 'total', title: '总数量', width: 17 },
            { field: 'success', title: '成功数量', width: 16 },
            { field: 'failed', title: '失败数量', width: 16 },
            { field: 'err', title: '异常数量', width: 16 }
        ]]/*,
        toolbar : '#jdcsal_tb_top'*/ /*[ {
            iconCls : 'icon-add',
            text : '新增',
            handler : function() {
                // 增加
                showHide('add');
            }
        }] */
    });
    
    var session_chart = echarts.init($('#session_chart')[0]);
    session_chart.setOption({
        title: {
            text: '数据库会话数',
            textStyle: {
                color:'#333',
                fontSize: '14',
                baseline:'top'
            },
            x: 8,
            y: 10
        },
        tooltip : {
            trigger: 'axis'
        },
        grid: {
            x: 45,
            x2: 50,
            y: 50
        },
        legend: {
            data:['会话数','报警阈值'],
            y: 10
        },
        dataZoom : {
            show : true,
            realtime : true,
            start : 0,
            end : 100,
            height: 20,
            y: 240
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : (function (){
                    var now = new Date();
                    var res = [];
                    var len = 10;
                    while (len--) {
                        res.unshift(now.format("hh:mm:ss"));
                        now = new Date(now - 60000);
                    }
                    return res;
                })()
            }
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name:'会话数',
                type:'line',
                data:[11, 11, 14, 13, 10, 13, 8, 12, 13, 9],
                markPoint : {
                    data : [
                        {type : 'max', name: '最大值'},
                        {type : 'min', name: '最小值'}
                    ]
                },
                markLine : {
                    data : [
                        {type : 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'报警阈值',
                type:'line',
                data:[50, 50, 50, 50, 50, 50, 50, 50, 50, 50],
                itemStyle: {
                    normal: {
                        color: 'red',
                        lineStyle: {width: 3}
                    }
                }
            }
        ]
    });
    
    window.onresize = charts_resize;
    function charts_resize() {
        jy_chart.resize();
        session_chart.resize();
    };
    
});

Date.prototype.format = function(format) {
    var o = {
        "M+" : this.getMonth()+1, //month
        "d+" : this.getDate(),    //day
        "h+" : this.getHours(),   //hour
        "m+" : this.getMinutes(), //minute
        "s+" : this.getSeconds(), //second
        "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
        "S" : this.getMilliseconds() //millisecond
    }
    if(/(y+)/.test(format)) {
        format=format.replace(RegExp.$1,(this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
    for(var k in o) {
        if(new RegExp("("+ k +")").test(format)) {
             format = format.replace(RegExp.$1,RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length));
        }
    }
    return format;
}

$(function() {
    $('.sortable').sortable();
});
// (function() {
//   $(function() {
//     $('.gridly').gridly();
//     $('.gridly').gridly('draggable');
//   });
// }).call(this);