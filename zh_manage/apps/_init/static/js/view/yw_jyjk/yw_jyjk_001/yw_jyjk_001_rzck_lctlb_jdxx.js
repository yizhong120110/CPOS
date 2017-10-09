$(document).ready(function() {
    //输入要素列表
    var sryslb = ($('#hidSrys').val() + '').replace(/'None'/gm, "''").replace(/None/gm, "''");
    //输出要素列表
    var scyslb = ($('#hidScys').val() + '').replace(/'None'/gm, "''").replace(/None/gm, "''");
    //获取输入要素值
    sryslb = eval('(' + sryslb + ')');
    //获取输出要素值
    scyslb = eval('(' + scyslb + ')');
    //初始化输入要素
    $('#dgSrys').datagrid({
        nowrap : false,
        fit : false,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: sryslb,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'bm', title: '输入要素', width: 28 },
            { field: 'ysz', title: '值', width: 67, editor:{type:'text'}, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            }}
        ]]
    });
    //初始化输出要素
    $('#dgScys').datagrid({
        nowrap : false,
        fit : false,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: scyslb,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'bm', title: '输入要素', width: 28 },
            { field: 'ysz', title: '值', width: 67, editor:{type:'text'}, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            }}
        ]]
    });
});