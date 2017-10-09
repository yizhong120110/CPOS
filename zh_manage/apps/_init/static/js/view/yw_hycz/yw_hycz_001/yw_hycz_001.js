//查询
function doSearch() {
    // 操作时间
    var czsj = $("#searchCzsj").datebox('getValue');
    if (czsj) {
        if (!checkDate10(czsj,'操作时间','searchCzsj')) {
            return false;
        }
    }
    // 操作人员
    var xm = $("#searchCzry").textbox('getValue');
    // 操作平台
    var czpt = $("#combSearchCzpt").textbox('getValue');

    // 根据条件查询业务配置列表信息
    $("#dgHycz001").datagrid('load',{
        czsj: czsj,
        xm: xm,
        czpt: czpt
    });
}

$(function() {
    //初始化页面列表
    $('#dgHycz001').datagrid({
        fit: true,
        rownumbers: true,
        nowrap: false,
        singleSelect: true,
        fitColumns: true,
        pagination: true,
        remoteSort: false,
        pageSize : 10,
        url: "/oa/yw_hycz/yw_hycz_001/yw_hycz_001_view/data_view",
        method: "get",
        columns: [
            [{
                field: 'xm',
                title: '操作人员',
                width: 20
            }, {
                field: 'czpt',
                title: '操作平台',
                width: 15
            }, {
                field: 'czsj',
                title: '操作时间',
                width: 20,
                align:'center'
            }, {
                field: 'gnmc',
                title: '操作功能名称',
                width: 25
            }, {
                field: 'url',
                title: '功能url',
                width: 25,
                hidden: true
            }, {
                field: 'szcz',
                title: '所做操作',
                width: 80
            }]
        ]
    });
    //操作人员限制长度最大20位
    $("#searchCzry").next().children().attr("maxlength","20");
    
    // form tab排序
    $('form').tabSort();
    
    $('#btnSearch').click(function(e) {
        e.preventDefault();
        doSearch();
    });

});