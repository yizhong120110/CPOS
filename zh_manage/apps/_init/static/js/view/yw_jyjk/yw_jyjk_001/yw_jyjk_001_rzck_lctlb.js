$(document).ready(function() {
    // 交易日期
    var jyrq = $('#hidJyrq').val();
    // 流水号
    var lsh = $('#hidLsh').val();
    // 流程类型
    var lclx = $('#hidLclx').val();
    // 流程层级
    var lccj = $('#hidLccj').val();
    // 禁用第一个开始节点和结束节点
    if( lclx == 'zlc' ){
        $('#tbsLctlb').tabs('disableTab', 0); 
        $('#tbsLctlb').tabs('disableTab', $('#tbsLctlb').tabs('tabs').length-2);
        $('#tbsLctlb').tabs('select', 1);
        var jdid = $("#tbsLctlb iframe")[1].id;
        var jdbm = $($("#tbsLctlb iframe")[1]).data("jdbm");
        var jdlx = $($("#tbsLctlb iframe")[1]).data("jdlx");
        var jdlx_start = '0'
        // 请求信息函数，默认是请求节点信息
        var view = 'lctlb_jdrzck_view?';
        // 当节点类型为子流程时，获取子流程的输入、输出、日志信息
        if( jdlx == 'zlc' ){
            view = 'lctlb_zlcrzck_view?'
        }
        var cs_str = 'jyrq=' + jyrq + '&lsh=' + lsh + '&jdid=' + jdid + '&jdbm=' + jdbm + '&jdlx_start=' + jdlx_start + '&lczx=' + lczx + '&zlc_dic=' + zlc_dic + '&lclx=' + lclx + '&lccj=' + lccj;
        $("#tbsLctlb iframe")[1].src = "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/" + view + cs_str;
    }else{
        $('#tbsLctlb').tabs('select', 0);
        var jdid = $("#tbsLctlb iframe")[0].id;
        var jdbm = $($("#tbsLctlb iframe")[0]).data("jdbm");
        var jdlx = $($("#tbsLctlb iframe")[0]).data("jdlx");
        var jdlx_start = '1'
        // 请求信息函数，默认是请求节点信息
        var view = 'lctlb_jdrzck_view?';
        // 当节点类型为子流程时，获取子流程的输入、输出、日志信息
        if( jdlx == 'zlc' ){
            view = 'lctlb_zlcrzck_view?'
        }
        var cs_str = 'jyrq=' + jyrq + '&lsh=' + lsh + '&jdid=' + jdid + '&jdbm=' + jdbm + '&jdlx_start=' + jdlx_start + '&lczx=' + lczx + '&zlc_dic=' + zlc_dic + '&lclx=' + lclx + '&lccj=' + lccj;
        $("#tbsLctlb iframe")[0].src = "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/" + view + cs_str;
    }
    // 初始化各个选项连接信息
    $('#tbsLctlb').tabs({
        fit: true,
        border: false,
        tabPosition: 'left',
        headerWidth: 195,
        tools: '#tab-tools',
        onSelect: function(title,index){
            // 查看全部日志
            if( title == '查看全部日志' ){
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/lcrzck_view",
                    data: {'jyrq': jyrq, 'lsh': lsh, 'lclx': lclx, 'lccj': lccj},
                    success: function(data){
                        // 反馈信息初始化页面
                        data = $.parseJSON(data);
                        // 获取数据成功
                        if( data.state == true ){
                            $("#preLcrznr").html($('<div/>').text(data.rznr).html());
                        }else{
                            afterAjax(data, "", "");
                        }
                    },
                    error : function(){
                        errorAjax();
                    }
                });
            }else{
            // 查看节点日志
                var jdid = $("#tbsLctlb iframe")[index].id;
                var jdbm = $($("#tbsLctlb iframe")[index]).data("jdbm");
                var jdlx = $($("#tbsLctlb iframe")[index]).data("jdlx");
                var jdlx_start = '0'
                if( index == '0' ){
                    jdlx_start = '1'
                }
                // 请求信息函数，默认是请求节点信息
                var view = 'lctlb_jdrzck_view?';
                // 当节点类型为子流程时，获取子流程的输入、输出、日志信息
                if( jdlx == 'zlc' ){
                    view = 'lctlb_zlcrzck_view?'
                }
                var cs_str = 'jyrq=' + jyrq + '&lsh=' + lsh + '&jdid=' + jdid + '&jdbm=' + jdbm + '&jdlx_start=' + jdlx_start + '&lczx=' + lczx + '&zlc_dic=' + zlc_dic + '&lclx=' + lclx + '&lccj=' + lccj;
                $("#tbsLctlb iframe")[index].src = "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/" + view + cs_str;
            }
        }
    }).find(".tabs-header ul.tabs>li").each(function(i, li) {
        // 气泡
        $(li).ttip({
            ttipEvent: 'h',
            msg: $(li).find("a>span").first().text()
        });
        $(li).find("a>span").eq(0).css({
            "padding": 0,
            "text-overflow": "ellipsis",
            "display": "block",
            "width": "138px",
            "overflow": "hidden"
        }).end().eq(1).css({
            "right": "20px",
            "left": "initial"
        });
    });
});