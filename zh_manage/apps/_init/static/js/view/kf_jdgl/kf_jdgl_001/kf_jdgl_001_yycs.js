$(document).ready(function() {
    
    $('#datagrid_jdyycs').datagrid({
        nowrap : false,
        fit : true,
        border: false,
        rownumbers : true,
        singleSelect: true,
        pagination : false,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/yycs_data_view?jdid=" + $("#jdid").val(),
        remoteSort: false,
        columns: [[
            { field: 'ywmc', title: '业务名称', width: 35 },
            { field: 'mc', title: '交易/子流程名称', width: 35 },
            { field: 'jdlx', title: '类别', width: 15 },
            { field: 'yycs', title: '引用次数', width: 15, halign: 'center', align:'right', formatter: function(value,rowData,rowIndex) {
                return accounting.formatNumber(value);
            } }
        ]]
    });

});
