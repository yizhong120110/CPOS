
/**
* 条件查询
* event：事件对象
*/
function doSearch(event){
    event.preventDefault();
    // 规则类别
    var gzlb = $("#combSearchGzlb").combobox('getValue');
    // 配置名称
    var pzmc = $("#txtSearchPzmc").textbox('getValue');
    // 分析规则或指标
    var gzzb = $("#txtSearchGzzb").textbox('getValue');
    // 状态
    var zt = $("#selSearchZt").combobox('getValue');
    
    // 根据条件查询监控配置列表信息
    $("#dgJkpzxx").datagrid('load',{
        gzlb: gzlb,
        pzmc: pzmc,
        gzzb: gzzb,
        zt: zt
    });
}

/**
* 初始化页面元素
* 表格
*/
$(document).ready(function() {
    // 渲染表格
    $('#dgJkpzxx').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jhrw/yw_jhrw_002/yw_jhrw_002_view/data_view",
        remoteSort: false,
        columns: [[
            // 列表展示信息：规则类别、配置名称、分析规则或指标、任务执行主机、crontab配置、是否可并发、状态、响应动作查看
            { field: 'jhrwid', title: '计划任务id', hidden:true },
            { field: 'gzlb', title: '规则类别', width: 20 },
            { field: 'pzmc', title: '配置名称', width: 40 },
            { field: 'fxgzzb', title: '分析规则或指标', width: 40 },
            { field: 'rwzxzj', title: '任务执行主机', width: 40, formatter: function(value,row,index){
                return value+'('+row.ip+')';
            } },
            { field: 'zdfqpz', title: 'crontab配置', width: 40 },
            { field: 'sfkbf', title: '是否可并发', width: 20 },
            { field: 'zt', title: '状态', width: 20 },
            { field: 'ck', title: '响应动作查看', width: 20, formatter: function(value,row,index){
                if (row.fxpzid != null && row.fxpzid != ''){
                    return '<a href="javascript:;" onclick = "showXydzlb(\''+ row.fxpzid +'\', \''+ row.pzmc +'\',\'divXydzckWindow\',\'响应动作列表查看\');" >查看</a>';
                }
            } },
        ]]
    });
    $("#fmSearch").tabSort();
    // 配置名称
    $("#txtSearchPzmc").next().children().attr("maxlength","20");
    // 分析规则或指标
    $("#txtSearchGzzb").next().children().attr("maxlength","30");
});
/**
* 响应动作列表
* pzid：分析配置id
* pzmc：配置名称
* winid：open窗口的win
* wintit：open窗口的title
*/
function showXydzlb( pzid, pzmc, winid, wintit ){
    event = event || window.event
    event.stopPropagation();
    // 打开窗口
    newWindow( $( "#" + winid ),wintit,900,470 );
    $('#txtTbpzmc').textbox( 'setValue',pzmc)
    // 初始化页面元素
    pageInit( pzid )
}

/**
*初始化响应动作列表
*/
function pageInit( pzid ){
    // 渲染表格
    $('#dgXydzlb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : false,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jhrw/yw_jhrw_002/yw_jhrw_002_view/xydzlb_sel_view",
        queryParams: {
            pzid: pzid
        },
        pageSize: 50,
        remoteSort: false,
        columns: [[
            // 列表展示信息：响应动作函数名称、中文名称、动作执行主机、分析结果触发、发起方式、动作计划执行时间
            { field: 'hsmc', title: '响应动作函数名称', width: 40 },
            { field: 'zwmc', title: '中文名称', width: 40 },
            { field: 'zjmc', title: '动作执行主机', width: 40 ,formatter: function(value,row,index){
                return value+'('+row.zjip+')';
            } },
            { field: 'fxjgcf', title: '分析结果触发', width: 20 },
            { field: 'fqfs', title: '发起方式', width: 20 },
            { field: 'jhsj', title: '动作计划执行时间', width: 30, align: 'center' }
        ]]
    });
    
}
