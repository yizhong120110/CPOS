/**
 * 页面初始化加载
*/
$(document).ready(function() {

    // 渲染表格，页面初始化信息加载
    treeGrid = $('#dgBmgl').treegrid({
        method: "post",
        singleSelect: true,
        selectOnCheck: true,
        checkOnSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/data_view",
        idField:'id',
        treeField:'text',
        columns: [
            [
                {field: 'id', title: '部门ID', width: 40, hidden:'true' },
                {field: 'text', title: '部门名称', width: 100},
                {field: 'bm', title: '部门代码', width: 80},
                {field: 'flmc', title: '部门分类', width: 60},
                {field: 'pxh', title: '排序', width: 40, halign:'center',align:'right'},
                {field: 'zfzr', title: '主负责人', width: 60},
                {field: 'dh', title: '电话', width: 40},
                {field: 'cz', title: '传真', width: 40}
            ]
        ],
        toolbar: [{
            id:'add',
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                 // 增加
                //show_addOreditWindow('add');
                cdgl_add2upd('新增部门','', 'add');
            }
        }, {
            id:'edit',
            iconCls: 'icon-edit',
            text: '编辑',
            handler: function() {
                 var rows = treeGrid.treegrid('getSelections');
                 if(rows == '' || rows.length > 1 ){
                     $.messager.alert('警告', '必须且只能选择一项', 'warning');
                     return false;
                 }
                 // 增加
                //show_addOreditWindow('update',rows);
                cdgl_add2upd('编辑部门',rows[0].id, 'update');
            }
        },
        {
            id:'del',
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                 var rows = treeGrid.treegrid('getSelections');
                 if(rows == '' || rows.length > 1 ){
                     $.messager.alert('警告', '必须且只能选择一项', 'warning');
                     return false;
                 }
                // 调用删除方法
                removechecked(rows);
        }
        }],
        onBeforeLoad : function(param){
                //加载前清空选择
		    	$(this).treegrid('clearSelections').treegrid('unselectAll');
		    },
        onClickRow:function(row){
            //折叠设置
            treeGrid.treegrid('toggle', row.id);
        },
        onLoadSuccess: function(row,data) {
             //数据记录总数和刷新按钮
            var pagination = $('#dgBmgl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
            //设置按钮显示与隐藏
            get_anqxLst_gn('bmgl','','bm');
         }
    });

     // 新增/编辑的取消按钮
    $('#lbtnBmglCancel').click(function(e){
        e.preventDefault();
        windowCancelFun();
    });

    // 最大值限制
    $("#txtBmdm").next().children().attr("maxlength","100");
    $("#txtBmmc").next().children().attr("maxlength","30");
    $("#txtZfzr").next().children().attr("maxlength","10");
    $("#txtDh").next().children().attr("maxlength","50");
    $("#txtCz").next().children().attr("maxlength","15");
    $("#txtDz").next().children().attr("maxlength","100");
    $("#txtBz").next().children().attr("maxlength","100");

    // 绑定更新按钮的事件
    $('#lbtnBmglSubmit').click(function(e){
        e.preventDefault();
          // 添加遮罩
        ajaxLoading();
        // 出错提示
        if ($("#hidBmid").val()=="") {
            // 新增
            url = "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/add_bm_view";
        } else {
            // 修改
            url = "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/edit_bm_view";
        }
        // 提交表单
        $('#divBmglWindow').find('form').form('submit', {
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
                //重新加载数据
                treeGrid.treegrid('reload');
                //成功提示信息
                afterAjax(data, "dgBmgl", "divBmglWindow");
                // 取消遮罩
                ajaxLoadEnd();
            },
            error: function () {
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
    $('#divBmglWindow').window('close');
};


/**
* 函数名称：新增或编辑页面初始化
* 函数参数：
    wintit: 打开窗口标题
    id:选择的datagrid数据ID
    handle：操作类型：add，update
*/
function cdgl_add2upd(wintit,id, handle ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    var bmid = '';
    if (handle=='update'){
        bmid = id
    }
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/lst_view",
        data : {
            'bmid':bmid
        },
        success: function(data){
            // 打开窗口
            newWindow($("#divBmglWindow"),wintit,620,350);
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                show_addOreditWindow(handle,data);
            }else{
                // 失败，将错误信息展示给用户
                afterAjax(data, '', '');
            }
        },
        error: function(){
            // 请求异常，给用户提示
            errorAjax();
        }
    });
}

//新增或者编辑页面初始化
function show_addOreditWindow(handle,dataR) {
     //初始化下拉框
     $('#txtSjbm').combotree({
         editable:false,
         data:dataR.sjbm_lst,
         valueField:'value',
         textField:'text',
         onClick: function(node){
            // 在用户点击的时候提示
            if(node.id){
                $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/check_qx_view",
                data: {'bmid': node.id},
                success: function(data){
                    data = $.parseJSON(data);
                    if(data.state==false){
                        afterAjax(data, '', '');
                        $("#txtSjbm").combotree('setValue','');
                    }
                },
                error : function(){
                    errorAjax();
                }
            });
            }
        }
	});
    // 部门分类
    $('#selBmfl').combobox({
         editable:false,
         data:dataR.bmfl_lst,
         valueField:'value',
         textField:'text'
    });
    //窗口初始化
    if(handle == 'update'){
        get_edit(dataR);
    }else if (handle == 'add'){
        newWindow($("#divBmglWindow"),'新增部门',600,350);
        //部门分类-请选择
        $("#selBmfl").combobox('select', '-1');
        $("#selBmfl").combobox('enable');
        //部门代码-可用
        $("#txtBmdm").textbox('enable');
        //部门名称
        $("#txtBmmc").textbox('enable');
        //主负责人
        $("#txtZfzr").textbox('enable');
        //电话
        $("#txtDh").textbox('enable');
        //传真
        $("#txtCz").textbox('enable');
        //地址
        $("#txtDz").textbox('enable');
        //所属部门
        $("#txtSjbm").combotree('setValue',dataR['bmid_login']);
        $("#txtSjbm").combotree('enable');
        //备注
        $("#txtBz").textbox('enable');
        //排序号
        $("#txtPxh").numberbox('enable');
        $('#lbtnBmglSubmit').show();
        $('#lbtnBmglCancel').show();

         // 清空参数ID
        $("#hidBmid").val('');
        $("#hidXxlb").val('');
        $("#hidBmdm").val('');
    }
    // form tab排序
    $("#divBmglWindow").children('form').tabSort();
}

/*
* 获取编辑前数据
* id:编辑记录的id
* url： 后台关联url
* */
function get_edit(data){
     if(data['flag']=='0'){
        //隐藏域部门id
        $("#hidBmid").val(data['bmxx'].id);
        //部门代码
        $("#txtBmdm").textbox('setValue', data['bmxx'].bm);
        //编辑时禁止修改
        $("#txtBmdm").textbox('disable');
        //部门代码-隐藏
        $("#hidBmdm").val('setValue', data['bmxx'].bm);
        //部门名称
        $("#txtBmmc").textbox('setValue',data['bmxx'].bmmc);
        $("#txtBmmc").textbox('enable');
        //部门分类
        if(data['bmxx'].fl == '' || data['bmxx'].fl == null){
            $("#selBmfl").combobox('select', -1);
            $("#selBmfl").combobox('enable');
        }else{
            $("#selBmfl").combobox('select', data['bmxx'].fl);
            $("#selBmfl").combobox('enable');
        }
        //主负责人
        $("#txtZfzr").textbox('setValue', data['bmxx'].zfzr);
        $("#txtZfzr").textbox('enable');
        //电话
        $("#txtDh").textbox('setValue', data['bmxx'].dh);
        $("#txtDh").textbox('enable');
        //传真
        $("#txtCz").textbox('setValue', data['bmxx'].cz);
        $("#txtCz").textbox('enable');
        //地址
        $("#txtDz").textbox('setValue', data['bmxx'].dz);
        $("#txtDz").textbox('enable');

        //所属部门
        if(data['bmxx'].fjdid == '' || data['bmxx'].fjdid == null || data['bmxx'].fjdid == '0' ){
            $("#txtSjbm").combotree('setValue', '');
            $("#txtSjbm").combotree('enable');

        }else{
            $("#txtSjbm").combotree('setValue', data['bmxx'].fjdid);
            $("#txtSjbm").combotree('enable');

        }
        //备注
        $("#txtBz").textbox('setValue', data['bmxx'].bz);
        $("#txtBz").textbox('enable');

        //排序号
        $("#txtPxh").numberbox('setValue', data['bmxx'].pxh);
        $("#txtPxh").numberbox('enable');
        $('#lbtnBmglSubmit').show();
        $('#lbtnBmglCancel').show();
     }else if (data['flag']=='1'){
        //隐藏域部门id
        $("#hidBmid").val(data['bmxx'].id);
        //部门代码
        $("#txtBmdm").textbox('setValue', data['bmxx'].bm);
        //编辑时禁止修改
        $("#txtBmdm").textbox('disable');
        //部门代码-隐藏
        $("#hidBmdm").val('setValue', data['bmxx'].bm);
        //部门名称
        $("#txtBmmc").textbox('setValue',data['bmxx'].bmmc);
        $("#txtBmmc").textbox('disable');
        //部门分类
        if(data['bmxx'].fl == '' || data['bmxx'].fl == null){
            $("#selBmfl").combobox('select', -1);
            $("#selBmfl").combobox('disable');
        }else{
            $("#selBmfl").combobox('select', data['bmxx'].fl);
            $("#selBmfl").combobox('disable');
        }
        //主负责人
        $("#txtZfzr").textbox('setValue', data['bmxx'].zfzr);
        $("#txtZfzr").textbox('disable');
        //电话
        $("#txtDh").textbox('setValue', data['bmxx'].dh);
        $("#txtDh").textbox('disable');
        //传真
        $("#txtCz").textbox('setValue', data['bmxx'].cz);
        $("#txtCz").textbox('disable');
        //地址
        $("#txtDz").textbox('setValue', data['bmxx'].dz);
        $("#txtDz").textbox('disable');
        //所属部门
        if(data['bmxx'].fjdid == '' || data['bmxx'].fjdid == null || data['bmxx'].fjdid == '0' ){
            $("#txtSjbm").combotree('setValue', '');
            $("#txtSjbm").combotree('disable');
        }else{
            $("#txtSjbm").combotree('setValue', data['bmxx'].fjdid);
            $("#txtSjbm").combotree('disable');

        }
        //备注
        $("#txtBz").textbox('setValue', data['bmxx'].bz);
        $("#txtBz").textbox('disable');
        //排序号
        $("#txtPxh").numberbox('setValue', data['bmxx'].pxh);
        $("#txtPxh").numberbox('disable');
        $('#lbtnBmglSubmit').hide();
        $('#lbtnBmglCancel').hide();
    }

}

/**
 *删除
 */
function removechecked(rows) {

    if (rows.length) {
        $.messager.confirm('提示', '数据删除后将不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/del_bm_view",
                    data: {
                        'id': rows[0].id,
                        'bmmc':rows[0].text
                    },
                    success: function(data){
                        //json串
                        data = $.parseJSON(data);
                        if(data.state == true){
                            //重新加载
                            treeGrid.treegrid('reload');
                            afterAjax(data, '', '');
                        }else{
                            afterAjax(data, '', '');
                        }
                    },
                    error : function(){
                        errorAjax();
                    }
                });
            }
        })
    } else {
        $.messager.alert('提示', '至少选择一项', 'info');
    }
}

// 输入框校验
function validate(){
    // 部门代码
    var bmgl_bmdm = $("#txtBmdm").textbox('getValue');
    // 部门名称
    var bmgl_bmmc = $("#txtBmmc").textbox('getValue');
    // 所属部门
    var bmgl_ssbm =$("#txtSjbm").combotree('getValue');
    // 电话
    var bmgl_dh = $("#txtDh").textbox('getValue');
    //排序号
    var bmgl_pxh = $("#txtPxh").numberbox('getValue');

     // 部门代码不可空
    if (!checkNull(bmgl_bmdm, '部门代码', 'txtBmdm') ) {
        return false;
    }
    //部门代码只能输入数字、字母、下划线
    if( !checkBm2(bmgl_bmdm,'部门代码','txtBmdm')){
         return false;
    }
     // 部门名称
    if (!checkNull(bmgl_bmmc, '部门名称', 'txtBmmc')) {
        return false;
    }
    if(bmgl_ssbm=='' || bmgl_ssbm ==null){
         $.messager.alert('错误', '所属部门不可为空，请选择', 'error', function() {
            $("#txtSjbm").next().children().focus();
        });
        return false;
    }
    //校验电话号码格式
    //手机号码正则
    var mobile_mode = /^(13|15|18|17)\d{9}$/;
    //电话号码正则
    var dh_mode = /^((\(\d{2,3}\))|(\d{3}\-))?(\(0\d{2,3}\)|0\d{2,3}-)?[1-9]\d{6,7}(\-\d{1,4})?$/;
    if(bmgl_dh !="" && bmgl_dh != null){
      if (mobile_mode.test(bmgl_dh) == false && dh_mode.test(bmgl_dh) == false) {
            $.messager.alert('错误', '电话格式错误，请重新输入', 'error', function() {
                $("#txtDh").next().children().select();
            });
        return false;
        }
    }
    //排序号不可空
    if (!checkNull(bmgl_pxh, '排序号', 'txtPxh') ){
        return false;
    }
}