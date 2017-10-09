$(document).ready(function() {
    $("#tishi").hide();
    // 默认渲染
    getData($("#divTable0").data('sjkmxdyid'), $("#divTable0").data('sjbid'), $("#divTable0").data('sjbjc'));

    // 选择页卡,渲染表格信息
    var busnessTab = $("#tbsDemosjb").tabs({
        fit: true,
        border: true,
        showOption: true,
        enableNewTabMenu: true,
        tabPosition: 'top',
        headerWidth: 100,
        onSelect: function(title, index) {
            // 渲染数据
            getData($("#divTable" + index).data('sjkmxdyid'), $("#divTable" + index).data('sjbid'), $("#divTable" + index).data('sjbjc'));
        }
    });

    // 获取表结构的信息
    function getData(sjkmxdyid, sjbid, sjbjc) {
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/csal_demo_datagrid_view",
            data: {
                "sjkmxdyid": sjkmxdyid,
                "sjbid": sjbid
            },
            success: function(data) {
                if(data.rows.length < 1 && data.columns.length < 1){
                   // 隐藏datagrid
                   $("#demo").hide();
                   $("#tishi").show();
                }else{
                   $("#tishi").hide();
                   renderingDatagrid(data,sjkmxdyid,sjbjc);
                }
            }
        });
    }

    // 渲染表格
    function renderingDatagrid(data, sjkmxdyid, sjbjc) {
        // 渲染表格
        $('#' + sjkmxdyid).datagrid({
            title: "数据表:" + sjbjc,
            nowrap: false,
            fit: true,
            rownumbers: true,
            singleSelect: true,
            fitColumns: false,
            remoteSort: false,
            data: data.rows,
            columns: data.columns,
            // pagination: true
        });
    }
});
