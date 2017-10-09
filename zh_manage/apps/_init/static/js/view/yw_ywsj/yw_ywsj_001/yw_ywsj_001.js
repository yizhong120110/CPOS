$(document).ready(function() {
    
    // 渲染表格
    // 准备数据
    var url = "/oa/yw_ywsj/yw_ywsj_001/yw_ywsj_001_view/data_view";
    // field长度
    var width_arr = [ '15%', '10%', '15%', '15%', '10%' ];
    // 导入导出标志
    dr_dc = 'dr';
    // 通讯，业务标志
    lx = 'tx';
    //初始化
    $('#dgDrls').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : false,
        singleSelect: true,
        method: "get",
        remoteSort: false,
        url: url,
        columns: [[
            { field: 'id', title: 'ID',  hidden:true },
            { field: 'jy_txmc', title: '交易/通讯名称',  width: '15%' },
            { field: 'czms', title: '导入描述', width: width_arr[0] },
            { field: 'wjm', title: '文件名' , width: '17%'},
            { field: 'czr', title: '导入人', width: width_arr[1] },
            { field: 'czsj', title: '导入时间', width: width_arr[2], align: 'center' },
            { field: 'bz', title: '备注', width: width_arr[3] },
            { field: 'sfht', title: '操作', width: width_arr[4], formatter: function(value,row,index){
                //可以回退
                var ret_str = '<a href="javascript:;" onclick="javascript:drlsUpd(\''+row.id+'\')">编辑</a>';
                if( value == 'TRUE'){
                    ret_str += ' <a href="javascript:;" onclick="javascript:drlsHt(\''+row.id+'\',\''+row.nrlx+'\')">回退</a>';
                }
                return ret_str
            } }
        ]]
        ,
        toolbar : [{
                iconCls : 'icon-up',
                text : '通讯导出',
                handler : function() {
                    dr_dc_tab('dc','tx','通讯管理导出');
                }
            },{
                iconCls : 'icon-down',
                text : '通讯导入',
                handler : function() {
                    dr_dc_tab('dr','tx','通讯管理导入');
                }
            },{
                iconCls : 'icon-up',
                text : '业务导出',
                handler : function() {
                    //导出
                    dr_dc_tab('dc','yw','业务管理导出');
                }
            },{
                iconCls : 'icon-down',
                text : '业务导入',
                handler : function() {
                    dr_dc_tab('dr','yw','通讯管理导入');
                }
            }
       ]
    });
    
    var fields =  $('#dgDrls').datagrid('getColumnFields');
    var muit="";
    for(var i=2; i<fields.length-1; i++){
        var opts = $('#dgDrls').datagrid('getColumnOption', fields[i]);
        if(i == 1){
            muit += "<div selected='selected' data-options=\" name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }else{
            muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }
        
    };
    $('#mm').html($('#mm').html()+muit);
    $('#search_box').searchbox({
        menu:'#mm'
    });   
    
    // 最大值限制（编辑）
    $("#txtCzms").next().children().attr("maxlength","50");
    $("#txtBz").next().children().attr("maxlength","150");
    // 初始化按钮点击事件(编辑)
    $("#lbtnDrlsSubmit").click(function(e){
        e.preventDefault();
        // 编辑提交
        drlsUpdSub();
    });
    // 取消按钮(编辑)
    $("#lbtnDrlsCancel").click(function (e){
        e.preventDefault();
        $("#divDrlsWindow").window('close');
    });
    
    // 最大值限制（回退）
    $("#txtHtms").next().children().attr("maxlength","50");
    $("#txtHtBz").next().children().attr("maxlength","150");
    $("#txtFhrmm").next().children().attr("maxlength","20");
    // 初始化按钮点击事件( 回退 )
    $("#lbtnHtDrlsSubmit").click(function(e){
        e.preventDefault();
        // 回退提交
        drlsHtSub();
    });
    // 取消按钮( 回退 )
    $("#lbtnHtDrlsCancel").click(function (e){
        e.preventDefault();
        $("#divHtDrlsWindow").window('close');
    });
    
    // 通讯导入导出
    $("#lbtnTxdrCancel").click(function (e){
        e.preventDefault();
        e.stopImmediatePropagation();
        $("#divTxdrWindow").window('close');
    });
    $("#lbtnTxdrSubmit").click(function (e){
        e.preventDefault();
        //通讯ID
        var txid = $('#selTxdr').combogrid('getValues');
        if(txid==''){
            $.messager.alert('错误','导入通讯不可为空,请选择','error', function(){
                $("#selTxdc").next().children().focus();
            });
            return false;
        }
        var url = '';
        var title = '';
        if(lx == 'tx' && dr_dc == 'dr'){
            title = '通讯导入';
            url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?txid="+txid+'&drlx='+lx;
        }
        if(lx == 'tx' && dr_dc == 'dc'){
            title = '通讯导出';
            url = "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/index_view?txid="+txid+'&dclx='+lx;
        }
        if(lx == 'yw' && dr_dc == 'dr'){
            title = '业务导入';
            url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?ywid="+txid+'&drlx='+lx;
        }
        if(lx == 'yw' && dr_dc == 'dc'){
            title = '业务导出';
            url = "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/index_view?ywid="+txid+'&dclx='+lx;
        }
        newTab(title, url);
        $("#divTxdrWindow").window('close');
    });
    $('#selTxdr').combogrid({
        panelWidth:280,
        editable:true,
        idField:'id',
        textField:'mc',
        method: "get",
        multiple:true,
        pagination : false,
        onChange:onChange,
        rowStyler: function(index,row) {
            style_str = '';
            if (row.id == '-1') {
                style_str = "color:blue;"
            } 
            return style_str
        },
        url:'/oa/yw_ywsj/yw_ywsj_001/yw_ywsj_001_view/get_yw_tx_view',
        columns:[[   
            {field:'id', title:'id', width:60, hidden:true},
            {field: 'mc', title: '名称', width: 250},
        ]]
    });
    
});

//导入历史编辑初始化页面
function drlsUpd( drlsid ){
    var event = event || window.event;
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/data_edit_sel_view",
        data: { "drlsid": drlsid },
        success: function(data){
            if( data.state == true ){
                newWindow($("#divDrlsWindow"),'编辑导入历史',500,220);
                $("#hidDrlsid").val( drlsid );
                $("#txtCzms").textbox('setValue',data.czms);
                $('#txtBz').textbox('setValue',data.bz);
                // 重新初始化tabindex
                $('#updForm').tabSort();
            }else{
                //$.messager.alert('提示', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error : function(){
            $.messager.alert('提示', '请求异常，请刷新页面后重试！', 'error');
        }
    });
}

//导入历史编辑提交
function drlsUpdSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    $('#divDrlsWindow').find('form').form('submit', {
        url: '/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/data_edit_view',
        onSubmit: function(){
            // 校验导入描述
            var czms = $("#txtCzms").textbox("getValue");
            var ret = checkNull( czms, '导入描述', 'txtCzms' );
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDrls", "divDrlsWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('提示','编辑导入历史请求出现异常，请稍后重试','error');
        }
    });
}

//回退页面初始化
function drlsHt( drlsid ,nrlx){
    var event = event || window.event;
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/drht_sel_view",
        success: function(data){
            data = $.parseJSON(data);
            if( data.state == true ){
                newWindow($("#divHtDrlsWindow"),'回退确认',500,260);
                $("#txtNrlx").val(nrlx);
                $("#hidHtDrlsid").val( drlsid );
                // 复核人
                $('#selFhr').combobox({
                    editable:false,
                    data:data.fhr_lst,
                    valueField:'hydm',
                    textField:'xm'
                });
                //默认选择第一个
                if( data.fhr_lst.length > 0 ){
                    $("#selFhr").combobox('select', $("#selFhr").combobox("getData")[0].hydm);
                }
                // 重新初始化tabindex
                $('#htForm').tabSort();
            }else{
                //$.messager.alert('提示', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error : function(){
            $.messager.alert('提示', '请求异常，请刷新页面后重试！', 'error');
        }
    });

}

//回退提交后台
function drlsHtSub(){
    // 添加遮罩
    ajaxLoading();
    // 提交表单
    var nrlx = $("#nrlx").val();
    $('#divHtDrlsWindow').find('form').form('submit', {
        url: '/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/drht_view',
        onSubmit: function(){
            // 校验回退描述
            var czms = $("#txtHtms").textbox("getValue");
            var ret = checkNull( czms, '导入描述', 'txtHtms' );
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
                // 校验复核人
                var fhr = $("#selFhr").textbox("getValue");
                ret = checkNull( fhr, '复核人', 'selFhr' );
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
               // 校验复核人密码
                var fhrmm = $("#txtFhrmm").textbox("getValue");
                ret = checkNull( fhrmm, '复核人密码', 'txtFhrmm' ); 
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgDrls", "divHtDrlsWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('提示','编辑导入历史请求出现异常，请稍后重试','error');
        }
    });
}

/*
* 查询.
*/
function doSearch(value,name){
    //var table = 'a';
    if(name == 'czr'){
        //table = 'b';
        name = 'xm';
    }
    //重新定义url
    //var tj_str = 'search_name='+table+'.' + name + '&search_value=' + value;
    var tj_str = 'search_name=' + name + '&search_value=' + value;
    $('#dgDrls').datagrid( {url:"/oa/yw_ywsj/yw_ywsj_001/yw_ywsj_001_view/data_view?" + tj_str });
    $('#dgDrls').datagrid('reload');
}


/**
*选择导入通讯时触发
*/
function onChange(newValue,oldValue){
    //选择导入新通讯，在选择其他通讯
    if(oldValue[0]!='' &&oldValue[0]!=undefined){
        if(oldValue.length!=0 && oldValue.length==1 &&oldValue[0] == '-1'&&newValue!=''){
            $('#selTxdr').combogrid('hidePanel');   
            $.messager.alert('提示','导入新通讯时,不可再导入其他通讯,请重新选择','info');
            $('#selTxdr').combogrid('reset');  
        }
    }
    if(newValue.lenth!=0&&oldValue[0]!='' &&oldValue[0]!=undefined&&oldValue[0]!='-1'){
        //若选择了其他通讯，在选择导入新通讯
        if(newValue[newValue.length-1] == '-1'){
            $('#selTxdr').combogrid('hidePanel');   
            $.messager.alert('提示','导入已存在通讯时,不可再导入新通讯,请重新选择','info');
            $('#selTxdr').combogrid('reset');  
        }
    }
}

/**
* 打开导入导出的tab
*/
function dr_dc_tab(dr_dc_,lx_,title){
    if(lx_ == 'yw'){
        $('#selTxdr').combogrid('grid').datagrid({'singleSelect':true});
    }else{
        $('#selTxdr').combogrid('grid').datagrid({'singleSelect':false});
    }
    dr_dc = dr_dc_;
    lx = lx_;
    $('#selTxdr').combogrid('grid').datagrid('reload',{'lx':lx,'dr':dr_dc});  
    //导出
    newWindow($("#divTxdrWindow"),title,400,200);
    if(dr_dc_ == 'dr' && lx_ == 'tx'){
        $("#spanDd").html("请选择需导入的通讯");
    }
    if(dr_dc_ == 'dc' && lx_ == 'tx'){
        $("#spanDd").html("请选择需导出的通讯");
    }
    if(dr_dc_ == 'dr' && lx_ == 'yw'){
        $("#spanDd").html("请选择需导入的业务");
    }
    if(dr_dc_ == 'dc' && lx_ == 'yw'){
        $("#spanDd").html("请选择需导出的业务");
    }
}
