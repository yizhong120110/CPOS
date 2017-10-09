var edtor = undefined;
// 用来判断当前是新增函数还是编辑函数
var aoe = 'add';
$(document).ready(function() {
    //tab顺
    $("#jbxxForm").tabSort()
    var url = "/oa/kf_ywgl/kf_ywgl_017/kf_ywgl_017_view/data_view?ywid=" + $("#txtYwid").val();
   
    $('#dgGghs').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        method: "get",
        pageSize:50,
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url: url,
        frozenColumns: [[
            { field: 'ck', checkbox: true },
        ]],
        columns: [[
            { field: 'id', title: 'id', hidden: true },
            { field: 'hsmc', title: '函数名称', width: 9 },
            { field: 'hsms', title: '函数描述', width: 10 },
            { field: 'bbh', title: '版本号', width: 4, formatter: function(value,rowData,rowIndex) {
                if (rowData.bbsftj==='1' || rowData.bbsftj===1) {
                    return '<span class="clean">'+value+'</span>';
                } else {
                    return '<span class="modified">'+value+'</span>';
                }
            } },
            { field: 'czr', title: '操作人', width: 5 },
            { field: 'czsj', title: '操作时间', width: 8, align: "center" },
            { field: 'operation', title: '操作', width: 13, formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:gghs_edit('+rowIndex+');">编辑</a> '+
                '<a href="javascript:;" onclick="javascript:bbtj(\''+'gghs'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgGghs'+'\');">版本提交</a> '+
                '<a href="javascript:;" onclick="javascript:bbxxck(\''+rowData.hsmc+'\',\''+rowData.id+'\');">版本信息查看</a> '+
                '<a href="javascript:;" onclick="javascript:bbhy(\''+'gghs'+'\',\''+rowData.bbsftj+'\',\''+rowData.id+'\',\''+'dgGghs'+'\',\''+rowData.bbh+'\');">版本还原</a>';
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
        },{
            iconCls : 'icon-up',
            text : '导出公共函数代码',
            handler : function() {
                //导出公共函数代码
                var ywid = $("#txtYwid").val()
                var to_path = 'window.location.href="/oa/kf_ywgl/kf_ywgl_017/kf_ywgl_017_view/index_view?ywid=' + ywid + '"'
                dm_down( 'dgGghs', 'gghs', ywid, to_path );
            }
        }
        ]
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });    
    
    // 最大值限制
    $("#txtHsmc").next().children().attr("maxlength","100");
    // 最大值限制
    $("#txtHsms").next().children().attr("maxlength","100");
    
    // 绑定增加/修改弹出框中的添加按钮---暂时是关闭，没有任何事件发生
    $('#lbtnWindowOkAddUpd').click(window_update_add_func);
    
    // 绑定增加/修改弹出框中的取消按钮
    $('#lbtnWindowCancel').click(windowCancelFun);
    
    // CodeMirror对象
    edtor = CodeMirror.fromTextArea(document.getElementById("txtHsnr"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true
    });
    
    //将tab换为4个空格
    edtor.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    
    $('#txtHsnr').next().css('border', '1px solid #abafb8');

});
// 信息查询
function doSearch() {
	
    // 函数名称
    var hsmc = $("#serchHsmc").textbox('getValue');
    // 通讯名称
    var hsms = $("#serchHsms").textbox('getValue');
    // 根据条件查询对象
    $("#dgGghs").datagrid('load',{
        hsmc:hsmc,
        hsms:hsms
    });
}

// 关闭bean_window中的关闭按钮

function windowCancelFun(e) {
    e.preventDefault();
    $('#bean_window').window('close');
};

// 动态显示增加或者编辑的公共函数窗口
function showHide(handle) {
    aoe=handle;
    // 增加窗体
    if(handle=='add'){
        $("#txtHsmc").textbox('enable');
        // 增加窗体
        newWindow($("#bean_window"),'新增公共函数',585,368);
        $('#bean_window').find('form').tabSort();
        edtor.setValue("");
        edtor.refresh();
        edtor.options.readOnly = false;
    } else if( handle=='update' ){
        //$("#txtHsmc").textbox('disable');
        // 增加窗体
        newWindow($("#bean_window"),'编辑公共函数',585,368);
        $('#bean_window').find('form').tabSort();
        edtor.setValue("");
        edtor.refresh()
        edtor.options.readOnly = false;
    }
    
    //设置ywid
    $("#txtYwidForm").val($("#txtYwid").val());
};

// 公共函数更新方法
function window_update_add_func(e){
    e.preventDefault();
    // 添加遮罩
    ajaxLoading();
    var url = '/oa/kf_ywgl/kf_ywgl_017/kf_ywgl_017_view/add_view'
    if( $('#txtId').val() ){
        url = '/oa/kf_ywgl/kf_ywgl_017/kf_ywgl_017_view/update_view'
    }
    $('#bean_window').find('form').form('submit', {
        url:url,
        dataType : 'json',
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
            afterAjax(data, 'dgGghs','bean_window');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

// 输入框校验
function validate(){
    var hsmc = $("#txtHsmc").textbox('getValue');
    var hsms = $("#txtHsms").textbox('getValue');
    var hsnr = edtor.getValue()
    
    // 函数名称
    if (hsmc=="" || hsmc==null) {
        $.messager.alert('错误','函数名称不可为空，请输入','error', function(){
            $("#txtHsmc").next().children().focus();
        });
        return false;
    }
    
    // 函数名称补充括号
    if( hsmc.indexOf(')') == -1 && hsmc.indexOf(')') == -1 ){
        $("#txtHsmc").textbox('setValue',hsmc + '()');
    }
    
    // 函数内容
    if (hsnr=="" || hsnr==null) {
        $.messager.alert('错误','函数内容不可为空，请输入','error', function(){
            $("#txtHsnr").next().children().focus();
        });
        return false;
    }
}

/**
*批量删除
*/
function removechecked(){
    if(!checkSelected('dgGghs')) {
        return;
    }
    $.messager.confirm("确认", "公共函数删除后数据将不可恢复,您确定要删除吗?", function(flag) {
        if (flag){
            // 添加遮罩
            ajaxLoading();
            var rows = $('#dgGghs').datagrid('getSelections');
            //创建存放id的数组
            var idArray = new Array();
            //创建存放内容id的数组
            var nrIdArray = new Array();
            $.each(rows,function(n,row){
                idArray[n] = row.id;
                nrIdArray[n] = row.nr_id
            });
            // 业务id
            var ywid = $("#txtYwid").val();
            
            $.ajax({
                url:'/oa/kf_ywgl/kf_ywgl_017/kf_ywgl_017_view/del_view',
                type : 'post',
                dataType : 'text',
                data : {
                    'ids' : idArray.join(","),
                    'nrids' : nrIdArray.join(","),
                    'ywid': ywid
                },
                success:function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    //执行请求后的方法
                    afterAjax(data, 'dgGghs','');
                },
                error : function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}

// 点击编辑时，将每行的值赋值给window
function gghs_edit(index) {
    var event = event || window.event;
    event.stopPropagation();    
    showHide('update');
    var rows = $('#dgGghs').datagrid('getRows');
    var row = rows[index];
    $("#txtHsmc").textbox('setValue', row['hsmc']);
    $("#hidHsmc").val( row['hsmc'] );
    $("#txtHsms").textbox('setValue', row['hsms']);
    $("#txtHsnr").val(row['nr']);
    
    $("#txtNr_id").val(row['nr_id']);
    $("#txtId").val(row['id']);
    edtor.setValue(row['nr']);
}
/*
版本信息查看
*/
function bbxxck(lc,gghsid) {
    var event = event || window.event;
    event.stopPropagation();    
    newTab(lc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=gghs&id=' + gghsid);
}
