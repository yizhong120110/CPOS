
$(document).ready(function() {
    var url = "/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/data_view?ywid=" + $("#ywid").val();
    
    $('#dgjylb').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        pageSize : 50,
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url: url,
        frozenColumns: [[
            { field: 'ck', checkbox: true },
        ]],
        columns: [[
            { field: 'id', title: 'id', width: 40 ,hidden:true},
            { field: 'jym', title: '交易码', width: 50 },
            { field: 'jymc', title: '交易名称', width: 100, formatter: function(value,row,index){
                return '<a href="javascript:;" onclick="javascript:jyxxck_tab(\''+value+'\',\''+row.id+'\');">'+value+'</a>';
            } },
            { field: 'zt', title: '交易状态', width: 60 },
            { field: 'bbh', title: '版本号', width: 40, formatter: function(value,rowData,rowIndex) {
                
                if (rowData.bbsftj=='0' || rowData.bbsftj==0) {
                    return '<span class="modified">'+value+'</span>';
                } else {
                    return '<span class="clean">'+value+'</span>';
                }
            } },
            { field: 'jyms', title: '交易描述', width: 100 },
            { field: 'cz', title: '操作', width: 100, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:bbtj(\''+'jy'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgjylb'+'\');">版本提交</a> '+
                '<a href="javascript:;" onclick="javascript:bbxxck('+rowIndex+',\''+rowData.jymc+'\');">版本信息查看</a> '+
                '<a href="javascript:;" onclick="javascript:bbhy(\''+'jy'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgjylb'+'\',\''+rowData.bbh+'\');">版本还原</a>';
            } }
           
        ]],
        
        toolbar : [ {
            iconCls : 'icon-add',
            text : '新增',
            handler : function() {
                // 增加
                showHide('add');
            }
        }, {
            iconCls : 'icon-remove',
            text : '删除',
            handler : function() {
                // 调用删除方法
                removechecked();
            }
        },  {
                iconCls : 'icon-down',
                text : '导入',
                handler : function() {
                    dr_tab();
                }
            },{
                iconCls : 'icon-up',
                text : '导出',
                handler : function() {
                    //导出
                    dc_tab();
                }
            },{
                iconCls : 'icon-history-look',
                text : '历史',
                handler : function() {
                    //查看
                    open_bqxxck( );
                }
            },{
                iconCls : 'icon-up',
                text : '导出交易代码',
                handler : function() {
                    //导出交易代码
                    var ywid = $("#ywid").val()
                    var to_path = 'window.location.href="/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/index_view?ywid=' + ywid + '"'
                    dm_down( 'dgjylb', 'jy', ywid, to_path );
                }
            }, {
                iconCls : 'icon-ok',
                text : '交易启用',
                handler : function() {
                    // 批量启用交易
                    jyczzt( '0' );
                }
            }, {
                iconCls : 'icon-cancel',
                text : '交易禁用',
                handler : function() {
                    // 批量禁用交易
                    jyczzt( '1' );
                }
            }
       ]
    });
 
    var fields =  $('#dgjylb').datagrid('getColumnFields');
    var muit="";
    for(var i=1; i<fields.length-1; i++){
        var opts = $('#dgjylb').datagrid('getColumnOption', fields[i]);
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
    
    // 最大值限制
    $("#txtJymc").next().children().attr("maxlength","30");
    $("#txtJym").next().children().attr("maxlength","20");
    $("#txtJyms").next().children().attr("maxlength","120");
    
    // 绑定增加/修改弹出框中的添加按钮---暂时是关闭，没有任何事件发生
    $('#lbtn_window_ok_add').click(windowOkFun);
    
    // 绑定增加/修改弹出框中的取消按钮
    $('#lbtn_window_cancel').click(windowCancelFun);
    /**
     * 关闭bean_window中的关闭按钮
     */
    function windowCancelFun(e) {
        e.preventDefault();
        $('#bean_window').window('close');
    };
    
    function showHide(handle) {
        // 增加窗体
        if(handle=='add'){
            $("#window_ok_update").hide();
            $("#lbtn_window_ok_add").show();
            // 增加窗体
            $('#jyzt').get(0).checked = true;
            newWindow($("#bean_window"),'新增交易',450,300);
            $('#bean_window').find('form').tabSort();
            $("#txtSsywid").combobox('setValue', $("#ywid").val());
            $("#txtSsywid").combobox('disable');
            $('#ywmc').textbox('setValue',$('#ywmch').val());
            $('#focusInput').val('txtJym');
            $("#txtJymc").next().children().focus();
        }
        $('#ssywid').val($("#ywid").val())
    };
    
    //新增交易
    function windowOkFun(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 添加交易
        $('#bean_window').find('form').form('submit', {
            url:'/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/add_view',
            onSubmit: function(){
                var ret = validate();
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
                //执行请求后的方法
                afterAjax(data, 'dgjylb','bean_window');
            },
            error: function () {
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
        
    };
    
    $("#commit_cancel").click(function(){
        $("#commit_window").window('close');
    });
    
});

//交易信息查看
function jyxxck_tab(jymc,jyid) {
    var event = event || window.event;
    event.stopPropagation();
    newTab(jymc+'_交易详情', '/oa/kf_ywgl/kf_ywgl_jyxq?jyid='+encodeURI(encodeURI(jyid)));
}

/**
*批量删除
*/
function removechecked(){
    checkSelected('dgjylb');
    var checkedItems = $('#dgjylb').datagrid('getChecked');
    var length = checkedItems.length;
    if(length) {
        $.messager.confirm("确认", "所选交易及其下的所有信息都将被删除且不可恢复，您确定要删除吗？", function(flag) {
            if (flag){
                // 添加遮罩
                ajaxLoading();
                var rows = $('#dgjylb').datagrid('getSelections');
                var idArray = new Array();//创建存放id的数组
                $.each(rows,function(n,row){
                    idArray[n] = row.id;
                });
                
                $.ajax({
                    url:'/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/del_view',
                    type : 'post',
                    dataType : 'text',
                    data : {
                        'ids' : idArray.join(",")
                    },
                    success:function(data){
                        // 取消遮罩
                        ajaxLoadEnd();
                        //执行请求后的方法
                        afterAjax(data, 'dgjylb','');
                    },
                    error: function () {
                        // 取消遮罩
                        ajaxLoadEnd();
                        errorAjax();
                    }
                });
                
            }
            
        });
    }
}

// 提交之前的验证
function validate(){
    var jymc = $("#txtJymc").textbox("getValue");
    var jym = $("#txtJym").textbox("getValue");
    var jyms = $("#txtJyms").textbox("getValue");
    // 交易名称
    if (jymc=="" || jymc==null) {
        $.messager.alert('错误','交易名称不可为空，请输入','error', function(){
            $("#txtJymc").next().children().focus();
        });
        return false;
    }
    // 校验名称
    if(checkMc(jymc,'交易名称','txtJymc') == false){
        return false;
    }
    if (jymc.length > 30) {
        $.messager.alert('错误','交易名称不能超过30个字符，请输入','error', function(){
            $("#txtJymc").next().children().focus();
        });
        return false;
    }
    
    // 交易码
    if (jym=="" || jym==null) {
        $.messager.alert('错误','交易码不可为空，请输入','error', function(){
            $("#txtJym").next().children().focus();
        });
        return false;
    }
    // 校验交易码
    if(checkBm(jym,'交易码','txtJym') == false){
        return false;
    }
    if (jym.length > 20) {
        $.messager.alert('错误','交易码不能超过20个字符，请输入','error', function(){
            $("#txtJym").next().children().focus();
        });
        return false;
    }
    
    // 交易描述
    if (jyms.length > 120) {
        $.messager.alert('错误','交易描述不能超过120个字符，请输入','error', function(){
            $("#txtJyms").next().children().focus();
        });
        return false;
    }
    
}

function bbxxck(index, Jymc) {
    var event = event || window.event;
    event.stopPropagation();
    var rows = $('#dgjylb').datagrid('getRows');
    var data = rows[index];
    newTab(Jymc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=jy&id=' + data.id);
}

/*
* 查询.
*/
function doSearch(value,name){
    //重新定义url
    var tj_str = 'ywid=' + $("#ywid").val() +'&search_name=' + name + '&search_value=' + value;
    $('#dgjylb').datagrid( {url:'/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/data_view?' + tj_str });
    $('#dgjylb').datagrid('reload');
}
/*
*交易导入
*/
function dr_tab(){
    var ywid = $('#ywid').val();
    title = '交易导入';
    var url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?ywid="+ywid+'&drlx='+'jy';
    newTab(title, url);
}
/*
*交易导出
*/
function dc_tab(){
    //校验是否可执行导出
    if( $('#dgjylb').datagrid('getData').rows.length == 0 ){
        $.messager.alert('提示','没有可导出交易','info')
        return false
    }
    var ywid = $('#ywid').val();
    title = '交易导出';
    var url = "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/index_view?ywid="+ywid+'&dclx='+'jy';
    newTab(title, url);
}
/*
*历史版本信息查看
*/
function open_bqxxck(){
    var title = '导入历史';
    var ywmc = $("#ywmch").val();
    var ywid = $("#ywid").val();
    if (ywmc != '')
        title = ywmc + '_交易导入历史';
    var url = "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/index_view?ss_idlb="+ywid+'&nrlx='+'jy';
    newTab(title, url);
}
/**
* 批量操作交易状态
* cztype: qy:0， jy:1
*/
function jyczzt( cztype ){
    checkSelected('dgjylb');
    var checkedItems = $('#dgjylb').datagrid('getChecked');
    var length = checkedItems.length;
    if(length) {
        // 获取此次操作交易原有状态
        var rows = $('#dgjylb').datagrid('getSelections');
        //创建存放id的数组
        var idArray = new Array();
        //存放状态数字
        var ztArray = new Array();
        $.each(rows,function(n,row){
            idArray[n] = row.id;
            ztArray[n] = row.zt;
        });
        //判断状态是否正确
        var find_index = -1;
        var msg = '';
        var msg2 = '';
        // 如果为启用
        if( cztype == '0' ){
            find_index = ztArray.indexOf('启用');
            msg = '启用交易列表中存在已经为启用的交易';
            msg2 = '您确定要批量启用状态交易吗？'
        }else{
            // 如果为禁用
            find_index = ztArray.indexOf('禁用');
            msg = '禁用交易列表中存在已经为禁用的交易';
            msg2 = '您确定要批量禁用状态交易吗？'
        }
        // 存在相应状态
        if( find_index > -1 ){
            $.messager.alert('提示',msg,'error')
            return false
        }
        $.messager.confirm("确认", msg2, function(flag) {
            if (flag){
                // 添加遮罩
                ajaxLoading();
                $.ajax({
                    url:'/oa/kf_ywgl/kf_ywgl_024/kf_ywgl_024_view/jyzt_upd_view',
                    type : 'post',
                    dataType : 'text',
                    data : {
                        'ids' : idArray.join(","),
                        'cztype': cztype
                    },
                    success:function(data){
                        // 取消遮罩
                        ajaxLoadEnd();
                        //执行请求后的方法
                        afterAjax(data, 'dgjylb','');
                    },
                    error: function () {
                        // 取消遮罩
                        ajaxLoadEnd();
                        errorAjax();
                    }
                });
            }
        });
    }
}