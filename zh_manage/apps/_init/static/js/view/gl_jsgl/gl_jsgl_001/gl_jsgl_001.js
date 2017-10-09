/**
 * 页面初始化加载
*/
$(document).ready(function() {
     //按钮列表-非toolbar
    buttonlst=['btnSearch'];
    //设置按钮显示与隐藏
    get_anqxLst_gn('jsgl',buttonlst,'jsgl');

     // 初始化页面-查询区域角色分类
    var jsfl_search = $("#selJsfl_search").combobox("getValue");
    if (jsfl_search == '-1' || jsfl_search =="" || jsfl_search == null){
        $("#selJsfl_search").combobox('setValue','-1');
    }
    // 渲染表格，页面初始化信息加载
    datagrid = $('#dgJsgl').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        pagination: true,
        pageSize: 50,
        pageList: [20,30,40,50],
        method: "post",
        singleSelect: false,
        selectOnCheck: true, 
        checkOnSelect: true,
        remoteSort: false,
        url: "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/data_view",
        frozenColumns: [
            [{field: 'select_box', checkbox: true}]
        ],
        columns: [
            [
                {field: 'id', title: '角色ID', hidden:true},
                {field: 'jsdm', title: '角色代码', width: 50},
                {field: 'jsmc', title: '角色名称', width: 120},
                {field: 'jsflmc', title: '角色分类', width: 50},
                {field: 'jsms', title: '角色描述', width: 150},
                {field: 'xm', title: '操作人', width: 50},
                {field: 'czsj', title: '操作时间', width: 60, align: 'center'},
                {field: 'cz', title: '操作', width: 50, formatter: function(value, rowData, rowIndex) {
                    return '<a href="javascript:;" onclick="javascript:show_addOreditWindow(\'update\',\'dgJsgl\',\''+rowIndex+'\',event);">编辑</a> ';
                }
            }]
        ],
        toolbar: [{
            id:'add',
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 增加
                show_addOreditWindow('add');
            }
        }, {
            id:'del',
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
                removechecked();
            }
        }]
    });
    // form tab排序
    $("#searchJsxx").children('form').tabSort();
    $('#btnSearch').click(function(e) {
        e.preventDefault();
        //查询事件
        doSearch();
    });

     // 新增/编辑的取消按钮
    $('#lbtnJsglCancel').click(function(e){
        e.preventDefault();
        windowCancelFun();
    });

    // 最大值限制
    $("#txtJsdm").next().children().attr("maxlength","10");
    $("#txtJsmc").next().children().attr("maxlength","30");
    $("#txtJsms").next().children().attr("maxlength","100");

    // 绑定更新按钮的事件
    $('#lbtnJsglSubmit').click(function(e){
        // 添加遮罩
        ajaxLoading();
        e.preventDefault();
        if ($("#hidJsid").val()=="") {
            // 新增
            url = "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/add_js_view";
        } else {
            // 修改
            url = "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/edit_js_view";
        }
        // 提交表单
        $('#divJsglWindow').find('form').form('submit', {
            url: url ,
            type:'post',
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
                //成功提交后的处理
                afterAjax(data, "dgJsgl", "divJsglWindow");
                // 取消遮罩
                ajaxLoadEnd();
            },
            error: function () {
                //异常提示
                errorAjax();
                // 取消遮罩
                ajaxLoadEnd();
            }
        });
    });
});

/**
 * bean_window中的关闭按钮
 */
function windowCancelFun() {
    //关闭时间
    $('#divJsglWindow').window('close');
};


//新增或者编辑页面初始化
function show_addOreditWindow(handle,id,index,event) {
    if(event){
        event.stopPropagation();
    }
    //窗口初始化
    if(handle == 'update'){
        //渲染窗口
        newWindow($("#divJsglWindow"),'编辑角色',400,280);
        //获取选择的数据对象
        var d = $('#' + id).datagrid('getData').rows[index];
        // 赋值id
        $("#hidJsid").val(d.id);
        // 获取角色信息
        url = "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/get_jsxx_view";
        get_edit(d.id,url);
    }else if (handle == 'add'){
        //渲染窗口
        newWindow($("#divJsglWindow"),'新增角色',400,280);
         //角色分类默认请选择
         $("#selJsfl").combobox('select', '-1');
         //角色代码可用设置
         $("#txtJsdm").textbox('enable');
         // 清空参数ID
        $("#hidJsid").val('');
        $("#hidXxlb").val('');
    }
    // form tab排序
    $("#divJsglWindow").children('form').tabSort();
}

/*
* 获取编辑前数据
* id:编辑记录的id
* url： 后台关联url
* */
function get_edit(id,url){
    // ajax请求
    $.ajax({
        url:url,
        type : 'post',
        data : {
            'id':id
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                // 如果查询成功
                //角色id-隐藏
                $("#hidJsid").val(data['jsxx'].id);
                //角色代码
                $("#txtJsdm").textbox('setValue', data['jsxx'].jsdm);
                //角色信息-隐藏域
                $("#hidJsdm").val(data['jsxx'].jsdm);
                //角色代码-禁用
                $("#txtJsdm").textbox('disable');
                //角色名称
                $("#txtJsmc").textbox('setValue', data['jsxx'].jsmc);
                //角色分类
                if(data['jsxx'].jsfl == '' || data['jsxx'].jsfl == null){
                    $("#selJsfl").combobox('select', -1);
                }else{
                    $("#selJsfl").combobox('select', data['jsxx'].jsfl);
                }
                //角色描述
                $("#txtJsms").textbox('setValue', data['jsxx'].jsms);
            }else{
                // 如果查询失败
                afterAjax(data, "", "divJsglWindow");
            }
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 *批量删除
 */
function removechecked() {
    //获取删除对象
    var rows = $('#dgJsgl').datagrid('getSelections');
    //删除ids
    var jsids = new Array();
    $(rows).each(function(index, item){
        jsids.push(item["id"]);
    });
    if (rows.length) {
        $.messager.confirm('提示', '数据删除后将不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/del_js_view",
                    data: {'id': jsids.join(",")},
                    success: function(data){
                        //处理成功后，提示信息
                        afterAjax(data, "dgJsgl", "");
                    },
                    error : function(){
                        //异常提示信息
                        errorAjax();
                    }
                });
            }
        })
    } else {
        //至少选择一项
        checkSelected('dgJsgl');
    }
}
//查询事件
function doSearch(event){
    // 取消默认提交事件
    //event.preventDefault();
    // 角色分类
    var selJsfl = $("#selJsfl_search").combobox("getValue");
    // 角色名称
    var seaJsmc = $("#txtSearchJsmc").textbox("getValue");
    // 角色代码
    var seaJsdm = $("#txtSearchJsdm").textbox("getValue");
    // 根据条件查询对象
    $("#dgJsgl").datagrid('load',{
        jsmc: seaJsmc,
        jsfl: selJsfl,
        jsdm: seaJsdm
    });
}

// 输入框校验
function validate(){
    // 角色分类
    var jsgl_jsfl = $("#selJsfl").combobox('getValue');
    // 角色名称
    var jsgl_jsmc = $("#txtJsmc").textbox('getValue');
    // 角色代码
    var jsgl_jsdm = $("#txtJsdm").textbox('getValue');
     // 角色代码
    if (!checkNull(jsgl_jsdm, '角色代码', 'txtJsdm')) {
        return false;
    }
    //角色代码只能输入数字、字母、下划线
    if( !checkBm2(jsgl_jsdm,'角色代码','txtJsdm')){
         return false;
    }
     // 角色名称
    if (!checkNull(jsgl_jsmc, '角色名称', 'txtJsmc')) {
        return false;
    }
    // 角色分类
    if (jsgl_jsfl=="" || jsgl_jsfl==null || jsgl_jsfl=="请选择" || jsgl_jsfl=="-1") {
        $.messager.alert('错误','角色分类不可为空，请选择','error', function(){
            $("#selJsfl").next().children().focus();
        });
        return false;
    }
}
