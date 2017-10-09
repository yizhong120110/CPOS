$(document).ready(function () {
    /**
    * 新增主机页面，给选中的监控信息追加选择类
    */
    $(".checklist input:checked").parent().addClass("selected");
    // 初始化主机信息
    get_zjjkxx();
    // 切换tab顺
    $('.sortable').sortable();
    // 限定编辑元素长度
    // 刷新频率
    $("#nspSxpl").next().children().attr("maxlength","3");
    // 服务器名称
    $("#txtServermc").next().children().attr("maxlength","20");
    // 服务器IP
    $("#txtServerip").next().children().attr("maxlength","15");
    // 刷新频率 秒
    var sxpl = $("#hidSxpl").val();
    // 变为毫秒
    sxpl = parseInt( sxpl, 10 ) * 1000 ;
    // 初始化调用每分钟调用一次函数
    setTimeout("countSecond()", sxpl);
    // 刷新频率配置
    $("#sxplpz").click(function(){
        sxpl_init_page();
    });
    // 当前页面刷新
    $("#dqymsx").click(function(){
        // 刷新整个页面
        window.location.reload();
    });
    // 刷新频率 保存
    $("#lbtnsxplpzSubmit").click(function (e) {
        e.preventDefault();
        sxpl_sub();
    });
    // 刷新频率 取消
    $("#lbtnsxplpzCancel").click(function () {
        $("#sxplpzWin").window("close");
    });
    // 添加监控主机 保存
    $("#lbtnAddSubmit").click(function (e) {
        e.preventDefault();
        add_server_sub();
    });
    // 添加监控主机 取消
    $("#lbtnAddCancel").click(function () {
        $("#addServerWin").window("close");
    });
});

/**
* 查看主机详细信息 打开新页面 TODO
*/
function view_server(name, ip){
    newTab(name + "-主机详细信息", "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/index_view?ip=" + ip);
}
/**
* 获取主机监控信息
*/
function get_zjjkxx(){
//    $.ajax({
//        type: 'POST',
//        dataType: 'text',
//        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/page_reload_view",
//        data: {},
//        success: function(data){
//            // 反馈信息
//            data = $.parseJSON( data );
//            // 获取数据成功
//            if( data.state == true ){
//                // 刷新频率
//                $("#hidSxpl").val( data.sxpl );
//                // 初始化主机
//                init_zj( data.zjxx_lst );
//                // 初始化交易笔数
//                init_jybs( data.jybs_dic );
//                // 初始化业务交易明细
//                init_ywjymx( data.ywjymx_lst );
//                // 初始化数据库回话数
//                init_sjkhhs( data.sjkhhs_dic );
//            }else{
//                // 失败，将错误信息展示给用户
//                afterAjax(data, '', '');
//            }
//        },
//        error: function(){
//            // 请求异常，给用户提示
//            errorAjax();
//        }
//    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/page_reload_zjxx_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 刷新频率
                $("#hidSxpl").val( data.sxpl );
                // 初始化主机
                init_zj( data.zjxx_lst );
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/page_reload_jybs_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始交易笔数
                init_jybs( data.jybs_dic );
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/page_reload_ywjymx_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化业务交易明细
                init_ywjymx( data.ywjymx_lst );
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/page_reload_sjkhhs_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化数据库回话数
                init_sjkhhs( data.sjkhhs_dic );
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}
/**
* 初始化主机信息
*/
function init_zj( zjxx_lst ){
    // 根据后台反馈主机监控信息进行初始化页面
    for( var i = 0; i < zjxx_lst.length; i++ ){
        // 主机详情
        var zjxx_dic = zjxx_lst[i]
        // 主机状态
        // 先删除类(样式)
        $('#img_' + zjxx_dic.zj_id).removeClass( 'btn-default' );
        $('#img_' + zjxx_dic.zj_id).removeClass( 'btn-success' );
        $('#img_' + zjxx_dic.zj_id).removeClass( 'btn-warning' );
        $('#img_' + zjxx_dic.zj_id).removeClass( 'btn-danger' );
        // 正常
        if( zjxx_dic.yjjb == '1' ){
            // 新增类
            $('#img_' + zjxx_dic.zj_id).addClass("btn-success");
            // 隐藏异常图片
            $('#yc_' + zjxx_dic.zj_id).hide();
        }else if( zjxx_dic.yjjb == '2' ){
            // 预警
            $('#img_' + zjxx_dic.zj_id).addClass("btn-warning");
            $('#yc_' + zjxx_dic.zj_id).html( zjxx_dic.yjsl );
            $('#yc_' + zjxx_dic.zj_id).show();
            
        }else if( zjxx_dic.yjjb == '3' ){
            // 异常
            $('#img_' + zjxx_dic.zj_id).addClass("btn-danger");
            $('#yc_' + zjxx_dic.zj_id).html( zjxx_dic.yjsl );
            $('#yc_' + zjxx_dic.zj_id).show();
        }else{
            $('#img_' + zjxx_dic.zj_id).addClass("btn-default");
            $('#yc_' + zjxx_dic.zj_id).hide();
        }
        // cpu
        var serversCpu = echarts.init($('#cup_' + zjxx_dic.zj_id)[0]);
        // 根据后台反馈信息初始化各个主机的cup信息
        serversCpu.setOption({
            title: {
                text: 'CPU使用率',//标题
                subtext: zjxx_dic.cpu_subtext,//副标题
                x: 'right',
                y: 'center',//标题位置
                textStyle: {
                    color: '#333',
                    fontSize: '14',
                    baseline: 'top'//垂直对齐方式
                },
                subtextStyle: {
                    color: '#666',
                    fontSize: '12',
                    baseline: 'top'
                },
            },
            grid: {
                x: 3,
                x2: 82,
                y: 7,
                y2: 3
            },
            xAxis: [
                {
                    type: 'category',
                    boundaryGap: false,
                    axisLabel: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    axisLine: {
                        onZero: false,
                        lineStyle: {
                            color: '#117dbb',
                            width: 1
                        }
                    },
                    data: zjxx_dic.cpu_lst
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        show: false
                    },
                    axisLine: {
                        onZero: false,
                        lineStyle: {
                            color: '#117dbb',
                            width: 1
                        }
                    },
                }
            ],
            series: [
                {
                    name: 'CPU使用率',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        normal: {
                            areaStyle: {
                                color: '#f1f6fa',
                            },
                            lineStyle: {
                                color: '#117dbb',
                                width: 1
                            }
                        }
                    },
                    data: zjxx_dic.cpu_lst
                }
            ]
        });
        
        // 内存使用
        var serversMem = echarts.init($('#mem_' + zjxx_dic.zj_id)[0]);
        serversMem.setOption({
            title: {
                text: '内存使用率',
                subtext: zjxx_dic.mem_subtext,
                x: 'right',
                y: 'center',
                textStyle: {
                    color: '#333',
                    fontSize: '14',
                    baseline: 'top'
                },
                subtextStyle: {
                    color: '#666',
                    fontSize: '12',
                    baseline: 'top'
                },
            },
            grid: {
                x: 3,
                x2: 82,
                y: 7,
                y2: 3
            },
            xAxis: [
                {
                    type: 'category',
                    boundaryGap: false,
                    axisLabel: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    axisLine: {
                        onZero: false,
                        lineStyle: {
                            color: '#8b12ae',
                            width: 1
                        }
                    },
                    data: zjxx_dic.mem_lst
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        show: false
                    },
                    axisLine: {
                        onZero: false,
                        axisLabel: {
                            show: false
                        },
                        lineStyle: {
                            color: '#8b12ae',
                            width: 1
                        }
                    },
                }
            ],
            series: [
                {
                    name: '内存使用率',
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    itemStyle: {
                        normal: {
                            areaStyle: {
                                color: '#f9f2f4',
                            },
                            lineStyle: {
                                color: '#8b12ae',
                                width: 1
                            }
                        }
                    },
                    data: zjxx_dic.mem_lst
                }
            ]
        });
    }
}

/**
* 初始化交易笔数
*/
function init_jybs( jybs_dic ){
    // 系统监控
    var jy_chart = echarts.init($('#divJybs')[0]);
    jy_chart.setOption({
        title: {
            text: '交易笔数',
            textStyle: {
                color: '#333',
                fontSize: '12',
                baseline: 'top'
            },
            x: 8,
            y: 10
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['总笔数', '正常笔数', '失败笔数', '异常笔数'],
            y: 10,
            x: 60
        },
        dataZoom: {
            show: true,
            realtime: true,
            start: 0,
            end: 100,
            height: 20,
            y: 240
        },
        grid: {
            x: 45,
            x2: 50,
            y: 50
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: jybs_dic.sjd_lst
            }
        ],
        yAxis: [
            {
                name: '总笔数',
                type: 'value',
                axisLabel: {
                    formatter: function (v) {
                        return v;
                    }
                }
            },
            {
                name: '失败/异常',
                type: 'value',
                axisLabel: {
                    formatter: function (v) {
                        return v;
                    }
                }
            },
        ],
        series: [
            {
                name: '总笔数',
                type: 'line',
                yAxisIndex: 0,
                smooth: true,
                data: jybs_dic.jyzbs_lst,
                itemStyle: {
                    normal: {
                        color: '#5AB1EF'
                    }
                }
            },
            {
                name: '正常笔数',
                type: 'line',
                yAxisIndex: 0,
                smooth: true,
                data: jybs_dic.cgzbs_lst,
                itemStyle: {
                    normal: {
                        color: '#5cb85c'
                    }
                }
            },
            {
                name: '失败笔数',
                type: 'line',
                yAxisIndex: 1,
                data: jybs_dic.sbzbs_lst,
                itemStyle: {
                    normal: {
                        color: '#FF7F50'
                    }
                }
            },
            {
                name: '异常笔数',
                type: 'line',
                yAxisIndex: 1,
                data: jybs_dic.yczbs_lst,
                itemStyle: {
                    normal: {
                        color: 'red'
                    }
                }
            }
        ]
    });
}
/**
* 业务交易明细
* ywjymx_lst: 业务交易明细列表
*/
function init_ywjymx( ywjymx_lst ){
    $("#dgJybsmx").datagrid({
        title: "业务交易明细",
        nowrap: false,
        fit: true,
        rownumbers: false,
        pagination: false,
        fitColumns: true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        data: ywjymx_lst,
        columns: [[
            {field: 'ywmc', title: '业务名称', width: 35},
            {field: 'total', title: '总数量', width: 17, halign: 'center', align:'right'},
            {field: 'success', title: '成功数量', width: 16, halign: 'center', align:'right'},
            {field: 'failed', title: '失败数量', width: 16, halign: 'center', align:'right'},
            {field: 'err', title: '异常数量', width: 16, halign: 'center', align:'right'}
        ]]
    });
}
/**
* 初始化数据库会话信息
* sjkhhs_dic: 数据库会话字典:
* sjkhhs_dic.username_lst: 用户列表
* sjkhhs_dic.sjd_lst: 时间点列表
* sjkhhs_dic.user_hhs_lst： 各个用户对应各个时间点会话数
*/
function init_sjkhhs( sjkhhs_dic ){
    var session_chart = echarts.init($('#session_chart')[0]);
    session_chart.setOption({
        title: {
            text: '数据库会话数',
            textStyle: {
                color: '#333',
                fontSize: '12',
                baseline: 'top'
            },
            x: 8,
            y: 10
        },
        tooltip: {
            trigger: 'axis'
        },
        grid: {
            x: 45,
            x2: 50,
            y: 50
        },
        legend: {
            data: sjkhhs_dic.username_lst,
            y: 10,
            x: 90
        },
        dataZoom: {
            show: true,
            realtime: true,
            start: 0,
            end: 100,
            height: 20,
            y: 240
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: sjkhhs_dic.sjd_lst
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: function(){
            var serie=[];
            var user_hhs_lst = sjkhhs_dic.user_hhs_lst;
            for( var i=0;i < user_hhs_lst.length;i++){
                var item={
                    name: user_hhs_lst[i].username,
                    type: 'line',
                    data: user_hhs_lst[i].hhs_lst
                }
                serie.push(item);
            };
            return serie;
        }()
    });
}
/**
* 根据刷新频率刷新页面监控图表
*/
function countSecond(){
    // 刷新页面
    get_zjjkxx();
    // 刷新频率 秒
    var sxpl = $("#hidSxpl").val();
    // 变为毫秒
    sxpl = parseInt( sxpl, 10 ) * 1000 ;
    setTimeout("countSecond()", sxpl);
}
/**
* 更新刷新频率页面初始化
*/
function sxpl_init_page(){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    newWindow($("#sxplpzWin"), "刷新频率配置", "300px", "200px");
    // 刷新频率赋值
    // 获取隐藏域中刷新频率
    var sxpl = $("#hidSxpl").val();
    // 将罪行的刷新频率幅值到修改页面
    $("#nspSxpl").numberspinner('setValue', sxpl);
}
/**
* 刷新频率修改提交
*/
function sxpl_sub(){
    // 添加遮罩
    ajaxLoading();
    // 最新刷新频率
    var sxpl = $("#nspSxpl").textbox("getValue");
    var ysxpl = $("#hidSxpl").val();
    // 判断是否未为空
    var ret = checkNull( sxpl, '页面刷新频率', 'nspSxpl' );
    if( ret == false )
        return false
    // 不为空进行提交
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/sxpl_edit_view",
        data: { 'sxpl': sxpl, 'ysxpl': ysxpl },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 将最新的刷新频率幅值到隐藏域内
                // 刷新频率 秒
                $("#hidSxpl").val( sxpl );
                // 弹出提示，关闭窗口
                afterAjax(data, '', 'sxplpzWin');
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}
/**
* 添加监控服务器 打开新窗口
*/
function add_server() {
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/server_add_sel_view",
        data: {},
        success: function(data){
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 打开窗口
                newWindow($("#addServerWin"), "添加监控服务器", 750, 380);
                // 初始化页面元素
                pageInit( data );
                // 重新初始化tabindex
                $('#fmZjAdd').tabSort();
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}
/**
* 初始化主机新增页面
*/
function pageInit( data ){
    // 主机类型
    $('#selZjlx').combobox({
        editable:false,
        data:data.zjxx_lst,
        valueField:'value',
        textField:'text'
    });
}
/**
* 添加监控服务器 提交
*/
function add_server_sub(){
    // 添加遮罩
    ajaxLoading();
    // 服务器名称
    var servermc = $("#txtServermc").textbox("getValue");
    // 服务器地址
    var serverip = $("#txtServerip").textbox('getValue');
    // 服务器类型
    var zjlx = $("#selZjlx").combobox('getValue');
    // 判断是否未为空
    // 服务器名称判空
    var ret = checkNull( servermc, '服务器名称', 'txtServermc' );
    if( ret == false ){
        // 取消遮罩
        ajaxLoadEnd();
        return false
    } else {
        // 服务器地址判空
        ret = checkNull( serverip, '服务器hostname', 'txtServerip' );
    }
    if( ret == false ){
        // 取消遮罩
        ajaxLoadEnd();
        return false
    }else{
        // 服务器地址判空格式
        ret = checkBm2( serverip, '服务器hostname', 'txtServerip' );
    }    
    if( ret == false ){
        // 取消遮罩
        ajaxLoadEnd();
        return false;
    }else{
        // 服务器类型判空
        ret = checkNull( zjlx, '服务器类型', 'selZjlx' );
    }    
    if( ret == false ){
        // 取消遮罩
        ajaxLoadEnd();
        return false;
    }
    // 校验通过，提交后台
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/server_add_view",
        data: { 'servermc': servermc, 'serverip': serverip, 'zjlx': zjlx },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 关闭窗口
                $('#addServerWin').window('close');
                // 提示成功，确定后刷新页面
                $.messager.alert('提示', data.msg.replace("\n", "<br/>"), 'info', function() {
                    // 刷新整个页面
                    window.location.reload();
                });
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}
