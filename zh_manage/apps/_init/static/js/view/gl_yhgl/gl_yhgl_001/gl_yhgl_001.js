/**
 * 页面初始化加载
*/
// 预定义当前页面显示信息
var datagrid;  //主页面列表初始化
var datagrid_js1;  //用户详细信息页面角色列表加载
var datagrid_qx;
var treeGrid_qx;//用户详细信息页面权限列表加载
var anqx_Lst=[];
$(document).ready(function() {

    //按钮列表-非toolbar
    buttonlst=['btnSearch'];
    //设置按钮显示与隐藏
    get_anqxLst_gn('yhgl',buttonlst,'yhgl');

    //新增编辑时限制所属部门只能是当前部门及子部门
    $("#txtSsbm").combotree({
        onClick: function(node){
            // 在用户点击的时候提示
            if(node.id){
                $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/check_qx_view",
                data: {'bmid': node.id},
                success: function(data){
                    data = $.parseJSON(data);
                    if(data.state==false){
                        afterAjax(data, "", "");
                        $("#txtSsbm").combotree('setValue','');
                    }
                },
                error : function(){
                    errorAjax();
                }
            });
            }
        }
    });

     // 初始化页面-查询区域性别
    var xb_search = $("#selXb_search").combobox("getValue");
    if (xb_search == '-1' || xb_search =="" || xb_search == null){
        $("#selXb_search").combobox('setValue','-1');
    }
    //查询区域部门初始化下拉框
    var bm_search = $("#selSearchBm").combobox("getValue");
    if (bm_search == '-1' || bm_search =="" || bm_search == null){
        $("#selSearchBm").combotree('setValue','');
    }
    // 渲染表格，页面初始化信息加载
    datagrid = $('#dgYhgl').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        pageSize: 50,
        pageList: [20, 30, 40, 50],
        method: "post",
        singleSelect: false,
        selectOnCheck: true, 
        checkOnSelect: true,
        remoteSort: false,
        url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/data_view",
        frozenColumns: [
            [{field: 'select_box', checkbox: true}]
        ],
        columns: [
            [
                {field: 'id', title: 'id', hidden:true},
                {field: 'dlzh', title: '行员代码', halign: 'center', width: 80},
                {field: 'xm', title: '姓名', halign: 'center', width: 60, formatter: function(value, rowData, rowIndex) {
                      if( value != "" && value != null ){
                        return '<a href="javascript:;" onclick="javascript:show_yhxxWindow(' + rowIndex + ',event);">'+ value +'</a>';
                    }
                }
                },
                {field: 'xb', title: '性别', halign: 'center', width: 30, align: 'center'},
                //{field: 'sj', title: '手机号', halign: 'center', width: 60},
                {field: 'dzyx', title: '电子邮箱', halign: 'center', width: 80},
                {field: 'ssbm', title: '所属部门', halign: 'center', width: 100},
                {field: 'dlcs', title: '登录次数', halign: 'center', width: 30, align:'right'},
                {field: 'zhdlsj', title: '最后登录时间', width: 80, halign: 'center', align: 'center'},
                //{field: 'bz', title: '备注', halign: 'center', width: 100},
                {field: 'js', title: '角色', halign: 'center', width: 100},
                {field: 'cz', title: '操作', halign: 'center',  width: 50, formatter: function(value, rowData, rowIndex) {
                    //return '<a href="javascript:show_addOreditWindow(\'update\',\'dgYhgl\',\''+rowIndex+'\');">编辑</a> ';
                    return '<a href="javascript:;" onclick="javascript:yhgl_add2upd(\'编辑用户\',\'update\',\'dgYhgl\',\''+rowIndex+'\',\'addoredit\',event);">编辑</a> ';
                }
            }]
        ],
        toolbar: [{
            id:'add',
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 增加
                //show_addOreditWindow('add');
                yhgl_add2upd('新增用户', 'add' ,'','','addoredit')
            }
        }, {
            id:'del',
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
               removechecked();
            }
        },{
            id:'MmRest',
            iconCls: 'icon-edit',
            text: '密码重置',
            handler: function() {
                // 调用密码重置方法
               mmResetFun();
            }
        }],
        onLoadSuccess: function(data) {
            //保留刷新按钮和数据总数
//            var pagination = $('#dgYhgl').parent().next();
//            var pi = pagination.find('.pagination-info');
//            if (pagination.find('table td').length == 13) {
//                pagination.find('table td:lt(12)').hide();
//            }
//            pi.text(pi.text().split(',')[1]);


         }
    });

    // 用户详细信息页面角色列表初始加载
    datagrid_js1 =$('#dgYhjs').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        method: "post",
        singleSelect: true,
        remoteSort: false,
        url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/data_js_view",
        columns: [
            [
                {field: 'id', title: 'id', hidden:true},
                {field: 'jsdm', title: '角色代码', halign: 'center', width: 80},
                {field: 'jsmc', title: '角色名称', halign: 'center', width: 80},
                {field: 'jsflmc', title: '角色分类', halign: 'center', width: 80},
                {field: 'jsms', title: '角色描述', halign: 'center',  width: 40}
            ]
        ],
        onLoadSuccess: function(data) {
            //保留刷新按钮和数据总数
            var pagination = $('#dgYhjs').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);;
        }
    });

    // 用户详细信息窗口权限列表初始加载
    treeGrid_qx = $('#dgYhqx').treegrid({
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/data_qx_view",
        idField:'id',
        treeField:'text',
        columns: [
            [
                {field: 'id', title: 'id', hidden:true},
                {field: 'text', title: '权限名称', halign: 'center',  width: 80},
                {field: 'qxflmc', title: '权限分类', halign: 'center', width: 80},
                {field: 'qxms', title: '权限描述', halign: 'center', width: 40}
            ]
        ],
        onBeforeLoad : function(param){
		    	$(this).treegrid('clearSelections').treegrid('unselectAll');
		    },
        onClickRow:function(row){
             treeGrid_qx.treegrid('toggle', row.id);
        },
        onLoadSuccess: function(row,data) {
            //显示记录数以及刷新按钮
            var pagination = $('#dgYhqx').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
        }
    });



    $('#js_id').combogrid({
        panelWidth:430,
        idField:'id',
        textField:'jsmc',
        rownumbers: true,
        fitColumns:true,
        multiple:true,
        url: '/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/data_jslst_view',
        columns:[[
            {field:'ckecked',checkbox:true },
            {field:'jsdm',title:'角色代码',width:80},
            {field:'jsmc',title:'角色名称',width:100}//,
        ]],
	    onLoadSuccess: function(data){
            //数据加载成功后的操作
	    	var ids = new Array();
	    	$.each(data.rows, function(n, d){
                if (d.checked) {
                    ids.push(d.id);
                }
	    	});
            //角色id赋值
	    	$('#js_id').combogrid('setValues', ids);
	    }
    });

      // 查询区域form tab排序
    $("#searchYhxx").children('form').tabSort();
    //查询按钮
    $('#btnSearch').click(function(e) {
        e.preventDefault();
        //查询事件
        doSearch();
    });

     // 新增/编辑的取消按钮
    $('#lbtnYhglCancel').click(function(e){
        e.preventDefault();
        windowCancelFun();
    });

    // 最大值限制
    $("#txtDlzh").next().children().attr("maxlength","30");
    $("#txtXm").next().children().attr("maxlength","20");
    $("#txtSj").next().children().attr("maxlength","50");
    $("#txtDh").next().children().attr("maxlength","50");
    $("#txtDzyx").next().children().attr("maxlength","50");
    $("#txtBz").next().children().attr("maxlength","100");

    //绑定新增编辑窗口更新按钮的事件
    $('#lbtnYhglSubmit').click(function(e){
        // 添加遮罩
        ajaxLoading();
        e.preventDefault();
        // 出错提示
        if ($("#hidYhid").val()=="") {
            // 新增
            url = "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/add_yh_view";
            //角色列表获取
            var g = $('#js_id').combogrid('grid');
            // 获取数据表格对象
            var rows = g.datagrid('getSelections');
            var jsids = new Array();
            $(rows).each(function(index, item){
                jsids.push(item["id"]);
            });
        } else {
                // 修改
                url = "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/edit_yh_view";
                //获取角色列表
                var g = $('#js_id').combogrid('grid');
                // 获取数据表格对象
                var rows = g.datagrid('getSelections');
                var jsids = new Array();
                $(rows).each(function(index, item){
                    jsids.push(item["id"]);
            });
        }
        // 提交表单
        $('#divYhglWindow').find('form').form('submit', {
            url: url ,
            type:'post',
            queryParams:{'jsid':jsids.join(",")},
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
                //提交成功后的处理
                afterAjax(data, "dgYhgl", "divYhglWindow");
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

//密码重置方法
function mmResetFun(){
    //获取选中的用户列表信息
    var rows = $('#dgYhgl').datagrid('getSelections');
    var yhids = new Array();
    $(rows).each(function(index, item){
        yhids.push(item["id"]);
    });
    if (rows.length) {
         $.messager.confirm('提示', '您确定要重置密码吗？', function(r) {
             if (r) {
                 $.ajax({
                     type: "post",
                     dataType: "json",
                     data: {'yhid': yhids.join(",")},
                     url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/resetMm_view",
                     success: function (data) {
                         //重置密码成功后
                         if (data.state == true) {
                            //密码重置成功后的提示信息
                            $.messager.alert('提示', data.msg.replace("\n", "<br/>"), 'info');
                         } else {
                            //重置失败提示信息
                            afterAjax(data, "", "");
                         }
                     },
                     erro: function () {
                         //异常处理信息
                         errorAjax();
                     }
                 });
             }
         });
    }else{
        //至少选择一项
        checkSelected('dgYhgl');
    }
}

/*
* 加载角色列表
* */

function editJsWindow(dataR){
    // 渲染角色列表表格，页面初始化信息加载
    $('#js_id').combogrid({
        url: '/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/data_jslst_view',
        queryParams:{id: dataR}
    });
}


/**
 * bean_window中的关闭按钮
 */
function windowCancelFun() {
    //关闭窗口
    $('#divYhglWindow').window('close');
};

/*
* 用户详细信息窗口渲染
* */
function show_yhxxWindow(rowIndex,event){
    //默认选中第一个tab页
    $('#tabsXxView').tabs('select',0);
     // 选择行信息 dgYhgl
    //var d = $('#dgYhgl').datagrid('getData').rows[rowIndex];
    //var yhid= d.id;
    // 获取用户详情信息
    yhgl_add2upd('','','dgYhgl', rowIndex ,'yhxq',event)
    // 用户角色和拥有权限页数据赋值
    //jsxx_setValue(yhid);
    //权限信息获取
    //qxxx_setValue(yhid);
}

/*
* 向后台请求获取用户角色数据
* */
function jsxx_setValue(dataR){
    // 渲染表格，页面初始化信息加载
    datagrid_js1.datagrid('reload', {
        id: dataR
    });
}

/*
*向后台请求获取用户权限数据
* */
function qxxx_setValue(dataR){
    // 渲染表格，页面初始化信息加载
    $('#dgYhqx').treegrid('reload', {
        yhid: dataR
    });
}

/**
* 函数名称：新增或编辑页面初始化
* 函数参数：
    wintit: 打开窗口标题
    id:选择的datagrid数据ID
    handle：操作类型：add，update
    type: yhxq,addoredit
*/
function yhgl_add2upd(wintit,handle ,id, index,type,event){
    if(event){
        event.stopPropagation();
    }
    var yhid=''
    if (handle=='update' || type=='yhxq'){
        var d = $('#' + id).datagrid('getData').rows[index];
        yhid= d.id;
    }

    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/get_yhxx_view",
        data : {
            'id': yhid
        },
        success: function(data){
            if (type=='yhxq'){
                newWindow($("#divYhxxxxWindow"),'用户详细信息',700,390);
            }else if(type =='addoredit'){
                 // 打开窗口
                newWindow($("#divYhglWindow"),wintit,650,350);
            }
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                if(type =='addoredit'){
                    if(handle=='update'){
                        // 初始化页面元素，编辑
                        show_addOreditWindow(handle, data , yhid);
                    }else{
                        // 初始化页面元素，新增
                        show_addOreditWindow(handle,data,'');
                    }
                }else if (type=='yhxq'){
                    //用户详情
                    get_edit(data,'2');
                }
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
    if(type=='yhxq'){
    // 用户角色和拥有权限页数据赋值
    jsxx_setValue(yhid);
    //权限信息获取
    qxxx_setValue(yhid);
    }
}

//新增或者编辑页面初始化
function show_addOreditWindow(handle,dataR,id) {
    // 所属部门
        $('#txtSsbm').combotree({
             mode:'remote',
             method:'get',
             editable:false,
             data:dataR.bm_lst,
             valueField:'value',
             textField:'text'
        });
    //性别
    $('#selXb').combobox({
             editable:false,
             data:dataR.xb_lst,
             valueField:'value',
             textField:'text'
        });
    //窗口初始化
    if(handle == 'update'){
        //加载编辑信息
        get_edit(dataR,'1');
        //加载角色列表
        editJsWindow(id);

    }else if (handle == 'add'){
        //设置下拉框初始化默认为请选择
        $("#selXb").combobox('select', '-1');
        $("#txtSsbm").combotree('setValue', '');
        $("#txtDlzh").textbox('enable');
         // 清空参数ID
        $("#hidYhid").val('');
        $("#hidXxlb").val('');
    }
    //新增或编辑窗口 form tab排序
   $("#divYhglWindow").children('form').tabSort();
}

/*
* 获取编辑前数据
* id:编辑记录的id
* url： 后台关联url
* type: 1-编辑页面信息 2-用户详情页面信息
* */
function get_edit(data,type){
                // 如果查询成功
                if (type == '1'){
                //编辑页面赋值
                $("#hidYhid").val(data['yhxx'].id);
                $("#hidHydm").val(data['yhxx'].dlzh);
                $("#txtDlzh").textbox('setValue', data['yhxx'].dlzh);
                $("#txtDlzh").textbox('disable');
                $("#selXb").combobox('select', data['yhxx'].xbbm);
                $("#txtXm").textbox('setValue', data['yhxx'].xm);
                $("#txtSj").textbox('setValue', data['yhxx'].sj);
                $("#txtCsrq").datebox('setValue', data['yhxx'].csrq);
                $("#txtDh").textbox('setValue', data['yhxx'].dh);
                $("#txtDzyx").textbox('setValue', data['yhxx'].dzyx);
                if(data['yhxx'].bmid =="" || data['yhxx'].bmid == null){
                    $("#txtSsbm").combotree('setValue', '');
                }else{
                    $("#txtSsbm").combotree('setValue', data['yhxx'].bmid);
                }
                $("#txtBz").textbox('setValue', data['yhxx'].bz);

                }else if (type == '2') {
                    //用户详情tab页数据赋值
                    $("#txtXxDlzh").textbox('setValue', data['yhxx'].dlzh);
                    $("#selXxXb").combobox('select', data['yhxx'].xbbm);
                    $("#selXxXb").combobox('disable');
                    $("#txtXxXm").textbox('setValue', data['yhxx'].xm);
                    $("#txtXxSj").textbox('setValue', data['yhxx'].sj);
                    $("#txtXxCsrq").datebox('setValue', data['yhxx'].csrq);
                    $("#txtXxCsrq").datebox('disable');
                    $("#txtXxDh").textbox('setValue', data['yhxx'].dh);
                    $("#txtXxDzyx").textbox('setValue', data['yhxx'].dzyx);
                    $("#txtXxSsbm").combobox('setValue', data['yhxx'].ssbm);
                    $("#txtXxSsbm").combobox('disable');
                    $("#txtXxBz").textbox('setValue', data['yhxx'].bz);
                    $("#txtDlcs").textbox('setValue', data['yhxx'].dlcs);
                    $("#txtZhdlrq").datebox('setValue', data['yhxx'].zhdlsj);
                    $("#txtZhdlrq").datebox('disable');
                }
}

/**
 *批量删除
 */
function removechecked() {
    var rows = $('#dgYhgl').datagrid('getSelections');
    var yhids = new Array();
    $(rows).each(function(index, item){
        yhids.push(item["id"]);
    });
    if (rows.length) {
        $.messager.confirm('提示', '数据删除后将不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/del_yh_view",
                    data: {'id': yhids.join(",")},
                    success: function(data){
                        afterAjax(data, "dgYhgl", "");
                    },
                    error : function(){
                        errorAjax();
                    }
                });
            }
        })
    } else {
        checkSelected('dgYhgl');
    }
}
//查询事件
function doSearch(event){
    // 取消默认提交事件
    //event.preventDefault();
    // 行员代码
    var selDlzh = $("#txtSearchDlzh").textbox("getValue");
    // 姓名
    var seaXm = $("#txtSearchXm").textbox("getValue");
    // 手机
    var seaSj = $("#txtSearchSj").textbox("getValue");
    // 所属部门
    var seaBm = $("#selSearchBm").combobox("getValue");
    // 性别
    var seaXb = $("#selXb_search").combobox("getValue");
    if (seaXb == '-1' || seaXb =="" || seaXb == null){
        $("#selXb_search").combobox('setValue','-1');
    }
    // 根据条件查询对象
    $("#dgYhgl").datagrid('load',{
        dlzh: selDlzh,
        xm: seaXm,
        sj: seaSj,
        bm: seaBm,
        xb: seaXb
    });
}

// 输入框校验
function validate(){
    // 性别
    var yhgl_xb = $("#selXb").combobox('getValue');
    // 行员代码
    var yhgl_dlzh = $("#txtDlzh").textbox('getValue');
    // 姓名
    var yhgl_xm = $("#txtXm").textbox('getValue');
    // 手机
    var yhgl_sj = $("#txtSj").textbox('getValue');
    // 电话
    var yhgl_dh = $("#txtDh").textbox('getValue');
    //电子邮箱
    var yhgl_dzyx = $("#txtDzyx").textbox('getValue');
    //出生日期
    var yhgl_csrq =$("#txtCsrq").datebox('getValue');
    //所属部门
    var yhgl_ssbm=$('#txtSsbm').combotree('getValue');

    //行员代码不可为空
    if(!checkNull(yhgl_dlzh, '行员代码', 'txtDlzh')){
        return false;
    }
    //行员代码只能输入半角字母、数字、下划线
    if(!checkBm2(yhgl_dlzh,'行员代码','txtDlzh')){
                    return false;
                }
    //姓名不可为空
    if(!checkNull(yhgl_xm, '姓名', 'txtXm')){
        return false;
    }
     //姓名只能输入半角字母、数字、下划线
    if(!checkMc(yhgl_xm,'姓名','txtXm')){
                    return false;
                }
    // 性别
    if (yhgl_xb=="" || yhgl_xb==null || yhgl_xb=="请选择" || yhgl_xb=="-1" ) {
        $.messager.alert('错误','性别不可为空，请选择','error', function(){
            $("#selXb").next().children().focus();
        });
        return false;
    }
    //手机不可为空
    if(yhgl_sj != null && yhgl_sj != ""){
        //校验手机号码格式是否错误
        if( !checkMobile(yhgl_sj,'手机号码','txtSj')){
            return false;
        }
    }
    
    var now = new Date();
    var myDate = now.getFullYear()+"-"+((now.getMonth()+1)<10?"0":"")+(now.getMonth()+1)+"-"+(now.getDate()<10?"0":"")+now.getDate();

    if( yhgl_csrq != "" && yhgl_csrq != null){
        if(yhgl_csrq >= myDate ){
            $.messager.alert('错误','出生日期不可大于当前日期，请输入','error', function(){
            $("#txtCsrq").next().children().focus();
        });
        return false;
        }

    }
    //校验电话号码格式
    if(yhgl_dh !="" && yhgl_dh != null){
        if( !checkPhone(yhgl_dh, '电话','txtDh')){
            return false;
        }
    }
       //校验电子邮箱格式
    if (yhgl_dzyx !="" && yhgl_dzyx != null){
        if( !checkEmail(yhgl_dzyx, '电子邮箱','txtDzyx')){
        return false;
    }
    }
    //所属部门不可为空
    if(!checkNull(yhgl_ssbm, '所属部门', 'txtSsbm')){
        return false;
    }
}
