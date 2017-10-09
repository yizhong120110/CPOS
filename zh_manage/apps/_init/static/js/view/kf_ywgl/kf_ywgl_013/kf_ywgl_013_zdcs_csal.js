$(document).ready(function() {
    
    var lx = $('#hidLx').val();
    var csaldyssid = $('#hidCsalids').val();
    var jdmc = $('#hidJdmc').val();
    var lxmc = $('#hidLxmc').val();
    
    var datagrid_url = '/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/data_view';
    $('#dgZdcs').datagrid({
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
        queryParams:{
            'csaldyssid':csaldyssid,
            'lx':lx,
            'dxmc':jdmc,
            'lxmc': lxmc,
            'gl':'',
            'jddyid':''
        },
        url: datagrid_url,
        pageSize:50,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: 'ID', width: 12, hidden: true },
            { field: 'lxdm', title: 'lxdm', width: 12, hidden: true },
            { field: 'ssid', title: 'ssid', width: 12, hidden: true },
            { field: 'demoid', title: 'demoid', width: 12, hidden: true },
            { field: 'dxmc', title: '测试对象名称', width: 20 },
            { field: 'lx', title: '类型', width: 10 },
            { field: 'mc', title: '测试案例名称', width: 20 },
            { field: 'ms', title: '测试案例描述', width: 30 },
            { field: 'operation', title: '操作', width: 15, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:updaterowcsal(\'' + rowData.lx + '\', \'' + rowData.id + '\', \'' + rowData.demoid + '\', \'' + rowData.lxdm + '\');">查看</a> <a href="javascript:;" onclick="javascript:removerowcsal(\'' + rowData.id + '\');">删除</a>';
            } }
        ]],
        toolbar: '#tb'
    });
    // 绑定增加/修改弹出框中的取消按钮
    $('#window_cancel').click(function(e){
        e.preventDefault();
        $('#bean_window').window('close');
    });
    // 如果是交易测试案例列表，则不显示补充关联测试
    if( lx == 'jy' ){
        $("#tdGljy").hide();
    }else{
        $("#tdGljy").show();
    }
    $('#gljy').click(function(){
        get_xgcsal(lx,csaldyssid,jdmc,lxmc);
    });

    $("#tb_form").tabSort();
});

/**
 * 查看
 * @param id
 */
function updaterowcsal(lx, id, demoid,lxdm) {
    var event = event || window.event;
    event.stopPropagation();    
    $("#codeEdit_ck iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_view/index_view?lx="+lxdm+"&csaldyid=" + encodeURI(id) + "&demoid=" + encodeURI(demoid);
    newWindow($("#codeEdit_ck"),'测试案例查看',900,400);
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
                    afterAjax(data, "dgZdcs");
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

/**
 * 弹出自动化测试执行窗口
 * @returns {boolean}
 */
function auto_test(){
    var row = $('#dgZdcs').datagrid('getSelections');
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

/**
 * 弹出自动化测试日志查看
 * @returns {boolean}
 */
function view_rz(csalid,pc,zxjg,jgsm,demoid,ssid,lb,event){
    if(event != undefined && event != 'undefined'){
        event.stopPropagation();
    }
    if(lb=='1'||lb==1){
        lb = 'lc'
        $("#rzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx="+lb+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm);//lx交易是：lc，子流程：zlc
        newWindow($("#rzck_window"),'交易日志查看',1230,500);
    }else if(lb=='2'||lb==2||lb=='4'||lb==4){
        lb='zlc'
        $("#rzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx="+lb+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm);//lx交易是：lc，子流程：zlc
        newWindow($("#rzck_window"),'交易日志查看',1230,500);
    }else if(lb=='3'||lb==3){
        lb='jd'
        $("#jdrzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/csalxx_view?jdcsalid="+csalid+"&pc="+pc+"&demoid="+demoid);
        // 打开自动化测试的结果
        newWindow($("#jdrzck_window"),'日志查看',1230,420);
        getZxjgms(csalid,pc);
    }
}

// 获取执行结果和结果描述
function getZxjgms(csalid,pc){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/zxjgms_view",
        data: {"jdcsalid": csalid,"pc":pc},
        success: function(data){
            if (data.zxjg == '0' || data.zxjg == 0){
                data.zxjg = "失败";
            }else{
                data.zxjg = "成功";
            }
            $('#zxjg').html(data.zxjg);
            $('#jgsm').html(data.jgsm);
        },
        error: function() {
            errorAjax();
        }
    });
}

function get_xgcsal(lx,csaldyssid,dxmc,lxmc){
    if($('#gljy')[0].checked) {
        var jddyid = '';
        var row = $('#dgZdcs').datagrid('getRows');
        // 获取节点id
        if(row.length > 0){
            jddyid = row[0].ssid;
        }
        $('#dgZdcs').datagrid('load',{
            csaldyssid: csaldyssid,
            lx: lx,
            dxmc: dxmc,
            lxmc: lxmc,
            gl:'True',
            jddyid:jddyid
        });
    }else{
        $('#dgZdcs').datagrid('load',{
            csaldyssid: csaldyssid,
            lx: lx,
            dxmc: dxmc,
            lxmc: lxmc,
            gl:'',
            jddyid:''
        });
    }
}
