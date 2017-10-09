$(document).ready(function() {
    // 绑定增加/修改弹出框中的取消按钮
    $('#window_cancel').click(function(){
        $('#bean_window').window('close');
    });
    $('#dgCsaldylb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "get",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        pageSize:50,
        queryParams:{"ssid":ywgl_ssid, "sslb":ywgl_sslb, "lb":ywgl_lb},
        url: '/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/get_csaldylb_view',
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: 'ID', width: 12, hidden: true },
            { field: 'demoid', title: 'demoid', width: 12, hidden: true },
            { field: 'mc', title: '测试案例名称', width: 20 },
            { field: 'ms', title: '测试案例描述', width: 20 },
            { field: 'zjzxr', title: '最近执行人', width: 10 },
            { field: 'zjzxsj', title: '最近执行时间', width: 12, align:'center' },
            { field: 'operation', title: '操作', width: 10, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:updaterow(\'dgCsaldylb\','+rowIndex+');">查看</a> <a href="javascript:;" onclick="javascript:removerowcsal(\'' + rowData.id + '\');">删除</a>';
            } }
        ]],
        toolbar: '#divToolbar'
    });
});

// 测试案例的基本信息
function updaterow(id, index) {
    var event = event || window.event;
    event.stopPropagation();    
    if(ywgl_lb == '2' || ywgl_lb == '4'){
        ywgl_lb = 'zlc'
    }else if(ywgl_lb == '3'){
        ywgl_lb = 'jd'
    }else if(ywgl_lb == '1'){
        ywgl_lb = 'jy'
    }
    var row = $('#'+id).datagrid('getData').rows[index];
    // $("#ifmJbxx").attr('src',"/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/csal_jbxx_view?csalid="+row.id);
    $("#ifmJbxx").attr('src',"/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_view/index_view?lx="+ywgl_lb+"&csaldyid=" + encodeURI(row.id) + "&demoid=" + encodeURI(row.demoid));
    newWindow($("#divJbxx"),'测试案例查看',860,450);
}
/**
 * 弹出自动化测试窗口
 * @returns {boolean}
 */
function auto_test(){
    var row = $('#dgCsaldylb').datagrid('getSelections');
    if(row.length < 1){
        $.messager.alert('提示', '请选择需要测试的测试案例!', 'info');
        return false;
    }
    var csalids='';
    for(var i = 0,len=row.length; i< len; i++){
        csalids+= row[i].id+",";
    }
    
    $("#zdhcsal_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/index_view?csalids="+csalids);
    // 打开自动化测试的结果
    newWindow($("#bean_window"),'自动化测试',600,360);
}
function view_rz(csalid,pc,zxjg,jgsm,demoid,ssid,lb,event){
    if(event != undefined && event != 'undefined'){
        event.stopPropagation();
    }
    if(lb=='1'||lb==1){
        lb = 'lc'
    }else if(lb=='2'||lb==2){
        lb='zlc'
    }
    $("#ifmcsxx").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx="+lb+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm);//lx交易是：lc，子流程：zlc
    newWindow($("#csxx_window"),'交易日志查看',1230,500);
}
/**
 * 删除
 * @param id
 * @param index
 * @param dw
 */
function removerowcsal(id) {
    var event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('提示', '是否确认删除此测试案例信息吗？', function(r){
        if (r) {
            // 添加遮罩
            ajaxLoading();
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_view/data_del_csaldy_view",
                data: {"csaldyid": id},
                success: function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, "dgCsaldylb");
                },
                error: function() {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    })
}
