var sum = 1;
$(document).ready(function() {
    $('#lbtnExport').click(function(){
        export_pdf();
    });
    /**
    * 初始化页面元素
    * 表格：特色业务系统主机--巡检信息
    */
    // 渲染表格
    $('#dgZjxj').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : false,
        pagination : false,
        pageSize: 50,
        singleSelect:true,
        striped: true,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/data_zjxj_view",
        remoteSort: false,
        columns: [
            [
            { title: '主机检查', align:'center',colspan:3 }
            ],[
            { field: 'jknr', title: '监控内容', align:'left',halign:'center', width: 33 },
            { field: 'yj', title: '阈值', align:'left', halign:'center',width: 33},
            { field: 'jkqk', title: '监控情况', align:'left',halign:'center', width: 34}
        ]]
    });

    /**
    * 初始化页面元素
    * 表格：Oracle数据库表空间检查--巡检信息
    */
    // 渲染表格
    $('#dgSjkxj').datagrid({
        nowrap : false,
        fit : true,
        singleSelect:true,
        rownumbers : false,
        pagination : false,
        striped: true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/data_sjkxj_view",
        remoteSort: false,
        columns: [
            [
            { title: '表空间使用情况', align:'center',colspan:3 }
            ],[
            { field: 'bjkm', title: '表空间名', align:'left',halign:'center', width:33 },
            { field: 'yj', title: '阈值', align:'left', halign:'center',width:33},
            { field: 'bkjsybl', title: '表空间使用比例', align:'left',halign:'center', width:34}
        ]]
    });

    /**
    * 初始化页面元素
    * 表格：特色业务系统进程检查--巡检信息
    */
    // 渲染表格
    $('#dgJcxj').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : false,
        singleSelect:true,
        pagination : false,
        striped: true,
        pageSize: 50,
        fitColumns : true,
        method: "get",
        url: "/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/data_jcxj_view",
        remoteSort: false,
        columns: [
            [
            { title: '平台进程检查表', align:'center',colspan:4 }
            ],
            [
            { field: 'ptfujc', title: '平台服务进程', align:'left',halign:'center', width:30, },
            { field: 'jcsl', title: '进程个数', align:'left', halign:'center',width:25, formatter: function(value, rowData, rowIndex) {
                return "<input type='text' id='txtJcs"+ rowIndex +"' name='txtJcsValue"+ rowIndex +"' value ='' class='easyui-textbox' style='width:250px' />";
            }},
            { field: 'qdsj', title: '启动时间', align:'left',halign:'center', width:25, formatter: function(value, rowData, rowIndex) {
                return "<input type='text' id='txtQdsj"+ rowIndex +"' name='txtQdsjValue"+ rowIndex +"' value ='' class='easyui-textbox' style='width:250px' />";
            }},
            { field: 'qt', title: '其他(是否有错误)', align:'left',halign:'center', width:20, formatter: function(value, rowData, rowIndex) {
                return "<input type='text' id='txtQtcw"+ rowIndex +"' name='txtQtcwValue"+ rowIndex +"' value ='' class='easyui-textbox' style='width:200px' />";
            }}
        ]]
    });

    /**
    * 初始化页面元素
    * 表格：Tong中间件日志检查--巡检信息
    */
    // 渲染表格
    $('#dgTongxj').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : false,
        pagination : false,
        striped: true,
        pageSize: 50,
        fitColumns : true,
        singleSelect:true,
        method: "get",
        url: "/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/data_Tonglogxj_view",
        remoteSort: false,
        columns: [
            [
            { title: '主机检查', align:'center',colspan:3 }
            ],
            [
            { field: 'rzmc', title: '日志名称', align:'left',halign:'center', width:33},
            { field: 'rzdx', title: '日志大小', align:'left', halign:'center',width:33},
            { field: 'bug', title: '异常或错误', align:'left',halign:'center', width:34, formatter: function(value, rowData, rowIndex) {
                return "<input type='text' id='txtBug"+ rowIndex +"' name='txtBugValue"+ rowIndex +"' value ='' class='easyui-textbox' style='width:330px' />";
            }}
        ]]
    });
    
    $('#lbtnRefresh').linkbutton({
        onClick: function(){
            $('#dgZjxj').datagrid('reload');
            $('#dgSjkxj').datagrid('reload');
            $('#dgJcxj').datagrid('reload');
            $('#dgTongxj').datagrid('reload');
            // 赋值采集时间
            var now_date = get_nowdate();
            $("#spSjcjsj").text( now_date );
        }
    });
    
    
    // 渲染表格
    $('#dgTsjy').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : false,
        pagination : false,
        striped: true,
        fitColumns : true,
        singleSelect:true,
        columns: [
            [
            { field: 'id', title: 'id', hidden: true },
            { field: 'xh', title: '序号', align:'center',halign:'center', width:20},
            { field: 'ycms', title: '异常描述', align:'left', halign:'center',width:40},
            { field: 'ycyyjcs', title: '异常原因及措施', align:'left',halign:'center', width:40},
            { field: 'cz', title: '操作', align:'center', halign:'center',width:6, formatter: function(value, rowData, rowIndex) {
                    czStr = '<a href="javascript:;" onclick="javascript:xtjy_delete(' + rowData.id +');">删除</a> ';
                    return czStr;
            }},
        ]],
        // 在数据加载之前进行的预设定
        onBeforeLoad:function(){
            // 预先追加五行表格
            for (var i = 0; i < 3; i++) {
                $("#dgTsjy").datagrid("appendRow", {
                    id:i,
                    xh:i+1, 
                    ycms:"<input type='text' id='txtYcms"+(i+1)+"' name='txtYcmsValue' value ='' class='easyui-textbox' style='width:400px' />", 
                    ycyyjcs:"<input type='text' id='txtYcyyjcs"+(i+1)+"' name='txtYcyyjcsValue' value ='' class='easyui-textbox' style='width:400px' />"
                });
            };
        },
        // 在点击单元格的时候触发事件
        onClickCell:function(index,field,value){
            // 查询当前信息行数
            var rows = $("#dgTsjy").datagrid("getRows");
            var dqxx = $("#txtXh"+(index+1)).val();
            // 当下标为最后一行且单元格为序号时 新增一行数据表格
            if( index == rows.length-1 && field == "ycms" && value != "undefined" && value.length > 0){
                sum = sum+1
                $("#dgTsjy").datagrid("appendRow", {
                    id:sum,
                    xh:rows.length+1,
                    ycms:"<input type='text' id='txtYcms"+(rows.length+1)+"' name='txtYcmsValue' value ='' class='easyui-textbox' style='width:400px' />",
                    ycyyjcs:"<input type='text' id='txtYcyyjcs"+(rows.length+1)+"' name='txtYcyyjcsValue' value ='' class='easyui-textbox' style='width:400px' />"
                });
            }
        }
    });
    
    
    
});

// 删除序号的方法
function xtjy_delete(id) {

    // 获取当前数据表格所有信息
    var rows = $("#dgTsjy").datagrid("getData").rows;
    var length = rows.length;
    // 当信息条数大于三条时才可进行删除
    if(length > 3){
        // 根据ID来进行删除当前条信息
        for (var i = 0; i < length; i++) {  
            if (rows[i]['id'] == id) {  
                $('#dgTsjy').datagrid('deleteRow',i);
                break;
            }
        }
        // 获取异常描述和异常原因及措施的值的列表
        var ycms_list = $("input[id^='txtYcms']");
        var ycyyjcs_list = $("input[id^='txtYcyyjcs']");
        // 使用循环赋值
        for (var i = 0; i < length-1; i++) {
            $('#dgTsjy').datagrid('updateRow',{
                index: i,
                row: {
                    id: i,
                    xh: i+1,
                    ycms:"<input type='text' id='txtYcms"+(rows.length+1)+"' name='txtYcmsValue' value ='"+ycms_list[i].value+"' class='easyui-textbox' style='width:400px' />",
                    ycyyjcs:"<input type='text' id='txtYcyyjcs"+(rows.length+1)+"' name='txtYcyyjcsValue' value ='"+ycyyjcs_list[i].value+"' class='easyui-textbox' style='width:400px' />"
                }
            });
        }
    }
}

/**
* 获取当前时间
*/
function get_nowdate(){
    var myDate = new Date();
    var year_str = myDate.getFullYear();        //获取完整的年份(4位,1970-????)
    var month_str =  String( myDate.getMonth() + 1 );      //获取当前月份(0-11,0代表1月)
    var date_str =  String( myDate.getDate() );            //获取当前日(1-31)
    var hours_str =  String( myDate.getHours() );          //获取当前小时数(0-23)
    var min_str =  String( myDate.getMinutes() );          //获取当前分钟数(0-59)
    var sec_str =  String( myDate.getSeconds() );          //获取当前秒数(0-59)
    // 组织实践
    var now_date_ymd = year_str + '-' + change_str( month_str, 2, '0' ) + '-' + change_str( date_str, 2, '0' );
    var now_date_hms = change_str( hours_str, 2, '0' ) + ':' + change_str( min_str, 2, '0' ) + ':' + change_str( sec_str, 2, '0' )
    
    return now_date_ymd + ' ' + now_date_hms;
}

/**
* 给字符串左补零
*/
function change_str( str, len, char_str ){
    if( len - str.length > 0 )
        return (len - str.length)*char_str + str;
    else
        return str;
}

function export_pdf(){
    // 添加遮罩
    ajaxLoading();
    // 导出pdf
    $.ajax({
        url:'/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/export_pdf_view',
        type : 'post',
        dataType : 'json',
        data:{'export_data':JSON.stringify(get_input_data())},
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            if(data.state){
                var url = '/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/data_down_view?filepath='+data.real_path;
                // 下载pdf
                wdqd_down(url,data.real_path);
            }else{
                afterAjax(data, '','');
            }
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
* 文档下载
*/
function wdqd_down(downUrl,filepath) {
    // jquery down
    $.fileDownload(downUrl)
        .done(function () {
            ajaxLoadEnd();
            if(filepath != ''){
                // 删除生成的临时文件
                del_linshiFile(filepath);
                $.messager.alert('提示','导出成功','info');
            }
        })
        .fail(function () {
            ajaxLoadEnd();
            if(filepath != ''){
                // 删除生成的临时文件
                del_linshiFile(filepath);
                $.messager.alert('错误','导出失败','error');
            }
        });
}

/**
  * 删除文件
  **/
function del_linshiFile(filepath){
    $.ajax({
        url:"/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/delDC_view",
        type : 'post',
        dataType : 'json',
        data : {
            'filepath' : filepath
        },
        success:function(data){
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

function get_input_data(){
    // 平台进程检查表
    var jc_data = $("#dgJcxj").datagrid('getData').rows;
    var jcgs_json = $("input[id^='txtJcs']");
    var qdsj_json = $("input[id^='txtQdsj']");
    var qt_json = $("input[id^='txtQtcw']");
    $.each(jc_data,function(index,jc){
        // 进程个数
        jc['jcgs'] = jcgs_json[index].value;
        // 启动时间
        jc['qdsj'] = qdsj_json[index].value;
        // 其他
        jc['qt'] = qt_json[index].value;
    });
    
    // Tong中间件日志
    var tong_data = $("#dgTongxj").datagrid('getData').rows;
    var bug_json = $("input[id^='txtBug']");
    $.each(tong_data,function(index,tong){
        // 进程个数
        tong['bug'] = bug_json[index].value;
    });
    
    // 关键进程巡检结果描述
    var jcxjjg = $('#jcxjjg').val();
    
    // 分行特色业务平台系统交易情况
    jy_json = [{'title':'上一日交易总笔数:','value':$('#txtJzbs').val()},{'title':'异常（超时、冲正等）交易笔数:','value':$('#txtYcjyzbs').val()}];
    //分行特色业务平台系统交易异常情况
    var ycms_input_list = $('input[id^=txtYcms]');
    var ycyyjcs_input_list = $('input[id^=txtYcyyjcs]');
    jyyc_json = [];
    $.each(ycms_input_list,function(index,value){
        jyyc_json.push({'xh':index+1,'ycms':value.value,'ycyyjcs':ycyyjcs_input_list[index].value});
    });
    // 巡检小结
    var xjxj = $('#xjxj').val();
    return {'tong_data':tong_data,'jc_data':jc_data,'jcxjjg':[{'jcxjjg':jcxjjg}],'jy_data':jy_json,'jyyc_data':jyyc_json,'xjxj_data':[{'xjxj':xjxj}]}
}
