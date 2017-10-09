
/**
* 条件查询
* event：事件对象
*/
function doSearch(event){
    event.preventDefault();
    // 发起日期
    var rq = $("#dateSearchRq").textbox('getValue');
    // 名称
    var mc = $("#txtSearchMc").textbox('getValue');
    // 任务类型
    var rwlx = $("#combSearchRwlx").combobox('getValue');
    // 状态
    var zt = $("#selSearchZt").combobox('getValue');
    // 流水号
    var lsh = $("#txtSearchLsh").textbox('getValue');
    // 校验发起日期不可为空
    ret = checkNull( rq, '发起日期', 'dateSearchRq' );
    
    // 根据条件查询当日执行计划列表信息
    $("#dgDrzxjh").datagrid('load',{
        rq: rq,
        rwlx: rwlx,
        zt: zt,
        lsh: lsh,
        mc: mc
    });
}

/**
* 初始化页面元素
* 表格
*/
$(document).ready(function() {
    var jyrq = $("#dateSearchRq").datebox("getValue");
    // 渲染表格
    $('#dgDrzxjh').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/data_view",
        queryParams: {
            rq: jyrq
        },
        remoteSort: false,
        columns: [[
            // 列表展示信息：流水号、名称、任务类型、动作类型、crontab配置、计划发起时间、实际发起时间、状态、操作
            { field: 'drzxjhid', title: '当日执行计划id', hidden:true },
            { field: 'bcflsh', title: '被触发流水号', hidden:true },
            { field: 'lsh', title: '流水号', width: 35, formatter: function(value,row,index){
                 if (row.rwlxbm == 'fx' && row.ztbm !='0'){
                    // 为分析时可查看此分析执行的响应动作列表
                    return '<a href="javascript:;" onclick = "showXydzlb(\''+ row.lsh +'\', \''+ row.mc +'\',\'divXydzckWindow\',\'动作执行计划管理\');" >'+row.lsh+'</a> ';
                }else{
                    return row.lsh;
                }
            } },
            { field: 'mc', title: '名称', width: 40 },
            { field: 'rwlx', title: '任务类型', width: 20 },
            // { field: 'dzlx', title: '动作类型', width: 20 },
            { field: 'zdfqpz', title: 'crontab配置', width: 40 },
            { field: 'jhfqsj', title: '计划发起时间', width: 30, align: 'center' },
            { field: 'sjfqsj', title: '实际发起时间', width: 30, align: 'center' },
            { field: 'zt', title: '状态', width: 20 },
            { field: 'cz', title: '操作', width: 40, formatter: function(value,row,index){
                url = ''
                if ( row.ztbm == '1' || row.ztbm == '2'){
                    // 状态为“发起成功”或“发起失败”时，操作列显示“查看日志”
                    url += '<a href="javascript:;" onclick = "log_view(\''+ row.rzlsh +'\',\''+row.rq+'\');" >查看日志</a> ';
                }
                if (row.ztbm != '9' && row.jhrwid != null){
                    // 状态不为“已加入任务队列”时，操作列显示“执行”
                    url += '<a href="javascript:;" onclick = "sqCheck(\''+ row.drzxjhid +'\',\'dgDrzxjh\');" >执行</a> ';
                }
                if (row.ztbm != '9' && row.ztbm != '0'){
                    // 状态不为“已加入任务队列”、“未发起”时，操作列显示“手工执行记录”
                    url += '<a href="javascript:;" onclick = "showSgzxjl(\''+ row.lsh +'\', \''+ row.mc +'\',\''+row.rwlxbm+'\',\'divSgzxckWindow\',\'手工执行计划查看\');" >手工执行记录</a> ';
                }
                return url
            } },
        ]]
    });
    $("#fmSearch").tabSort();
    // 流水号限制输入长度
    $("#txtSearchLsh").next().children().attr("maxlength","20");
    // 发起日期限制输入长度
    $("#dateSearchRq").next().children().attr("maxlength","10");
});

/**
*授权处理
* drzxjhid：当日执行计划id
**/
function sqCheck(drzxjhid,dgid){
    event = event || window.event
    event.stopPropagation();
    var cs_url = "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/sgzx?drzxjhid="+drzxjhid;
    url = "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/ty_sq?url="+cs_url + '&dgid=' + dgid;
    $('#sqFrame').attr('src', url );
    newWindow( $( "#divSqWindow" ),'授权',386,186 );
}
/**
* 手工执行处理
* drzxjhid：当日执行计划id
*/
function sgzx( drzxjhid ){
    // 点击链接时，不选中行
    event = event || window.event
    event.stopPropagation();
    // 向后台请求信息
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/sgzxcl",
        data: { 'drzxjhid': drzxjhid },
        success: function(data){
            // 打开窗口
            //newWindow( $( "#" + winid ),wintit,900,470 );
            // 反馈信息
            data = $.parseJSON( data );
            $('#txtTbpzmc').textbox( 'setValue',data.pzmc)
            // 初始化页面元素
            pageInit( pzid )
        },
        error: function(){
            errorAjax();
        }
    });
}


/**
* 响应动作列表
* lsh：流水号
* mc：监控配置名称
* winid：open窗口的win
* wintit：open窗口的title
*/
function showXydzlb( lsh, mc, winid, wintit ){
    event = event || window.event
    event.stopPropagation();
    
    // 打开窗口
    newWindow( $( "#" + winid ),wintit,1000,440 );
    $('#txtTbpzmc').textbox( 'setValue',mc)
    // 初始化页面元素
    pageInit( lsh )
}

/**
*初始化响应动作列表
*/
function pageInit( lsh ){
    // 渲染表格
    $('#dgDzzxjhgl').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/dzzxjhlb_sel_view",
        queryParams: {
            lsh: lsh
        },
        pageSize: 50,
        remoteSort: false,
        columns: [[
            // 列表展示信息：流水号、名称、动作类型、crontab配置、计划发起时间、实际发起时间、状态、操作
            { field: 'drjhid', title: '当日计划id', hidden:true },
            { field: 'rzlsh', title: '日志流水号', hidden:true },
            { field: 'lsh', title: '流水号', width: 35 },
            { field: 'mc', title: '名称', width: 30 },
            { field: 'dzlx', title: '动作类型', width: 15 },
            { field: 'jhfqsj', title: '计划发起时间', width: 30, align: 'center' },
            { field: 'sjfqsj', title: '实际发起时间', width: 30, align: 'center' },
            { field: 'zt', title: '状态', width: 25 },
            { field: 'cz', title: '操作', width: 40, formatter: function(value,row,index){
                url = ''
                if ( row.ztbm == '1' || row.ztbm == '2'){
                    // 状态为“发起成功”或“发起失败”时，操作列显示“查看日志”
                    url += '<a href="javascript:;" onclick = "log_view(\''+ row.rzlsh +'\',\''+row.rq+'\');" >查看日志</a> ';
                }
                if (row.ztbm != '9'){
                    // 状态不为“已加入任务队列”时，操作列显示“执行”
                    url += '<a href="javascript:;" onclick = "sqCheck(\''+ row.drjhid +'\',\'dgDzzxjhgl\');" >执行</a> ';
                }
                if (row.ztbm != '9' && row.ztbm != '0'){
                    // 状态不为“已加入任务队列”、“未发起”时，操作列显示“手工执行记录”
                    url += '<a href="javascript:;" onclick = "showSgzxjl(\''+ row.lsh +'\', \''+ row.mc +'\',\'dz\',\'divSgzxckWindow\',\'手工执行计划查看\');" >手工执行记录</a> ';
                }
                return url
            }  }
        ]]
    });
    
}

/**
* 手工执行计划列表
* lsh：流水号
* mc：名称
* rwlxbm：任务类型编码
* winid：open窗口的win
* wintit：open窗口的title
*/
function showSgzxjl( lsh, mc, rwlxbm, winid, wintit ){
    event = event || window.event
    event.stopPropagation();
    if (mc == null || mc == 'null'){
        mc = '';
    }
    // 打开窗口
    newWindow( $( "#" + winid ),wintit,1000,440 );
    $('#txtTbjhmc').textbox( 'setValue',mc)
    // 初始化页面元素
    pageInit2( lsh, rwlxbm )
}

/**
*初始化手工执行列表
*/
function pageInit2( lsh, rwlxbm ){
    // 渲染表格
    $('#dgSgzxck').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "post",
        url: "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/sgzxjh_sel_view",
        queryParams: {
            lsh: lsh,
            rwlx:rwlxbm
        },
        pageSize: 50,
        remoteSort: false,
        columns: [[
            // 列表展示信息：流水号、计划发起时间、实际发起时间、状态、操作
            { field: 'rzlsh', title: '日志流水号', hidden:true },
            { field: 'lsh', title: '流水号', width: 20 },
            { field: 'jhfqsj', title: '计划发起时间', width: 30, align: 'center' },
            { field: 'sjfqsj', title: '实际发起时间', width: 30, align: 'center' },
            { field: 'zt', title: '状态', width: 20 },
            { field: 'cz', title: '操作', width: 40, formatter: function(value,row,index){
                if ( row.ztbm == '1' || row.ztbm == '2'){
                    // 状态为“发起成功”或“发起失败”时，操作列显示“查看日志”
                    return '<a href="javascript:;" onclick = "log_view(\''+ row.rzlsh +'\',\''+row.rq+'\');">查看日志</a> ';
                }
            }  }
        ]]
    });
    
}

/**
*查看日志
*rzlsh：日志流水号
*rq：日期
*/
function log_view(rzlsh,rq){
    event = event || window.event
    event.stopPropagation();
    $.ajax({
        type: "POST",
        dataType: "json",
        url: "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/demo_log_view",
        data: {
            "log_lsh": rzlsh,
            "rq":rq
        },
        success: function(data) {
            if (data.state) {
                $("#preLcrznr").html( $('<div/>').text(data.log).html() );
                newWindow($("#divLog"), '日志', 860, 480);
            } else {
                afterAjax(data, "", "");
            }
        }
    });
}
