/**
 * 页面初始化加载
*/
$(document).ready(function() {

    // 渲染表格，页面初始化信息加载
    treeGrid = $('#dgCdgl').treegrid({
        method: "post",
        singleSelect: true,
        selectOnCheck: true,
        checkOnSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/data_view",
        idField:'id',
        treeField:'text',
        columns: [
            [
                {field: 'id', title: '菜单ID', width: 40, hidden:'true'},
                {field: 'text', title: '菜单名称', width: 100},
                {field: 'url', title: '请求地址', width: 100},
                {field: 'pxh', title: '排序', width: 20,halign:'center', align:'right'},
                {field: 'lxmc', title: '类型', width: 30 },
                {field: 'lymc', title: '来源', width: 40 },
                {field: 'bz', title: '备注', width: 100}
            ]
        ],
        toolbar: [{
            id:'add',
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
               // 增加
               cdgl_add2upd('新增菜单','', 'add','cd' );
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
                 // 编辑
                cdgl_add2upd('编辑菜单',rows[0].id, 'update','cd' );
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
                //参数：菜单iD 和 菜单名称
                var dataR = {
                    'id': rows[0].id,
                    'cdmc':rows[0].text,
                    'ly':rows[0].ly
                }
                //后台URL
                url = "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/del_cd_view"
                // 调用删除方法
                removechecked(dataR,url,treeGrid,'1');
        }
        }],
        onBeforeLoad : function(param){
                //加载前清空选择
		    	$(this).treegrid('clearSelections').treegrid('unselectAll');
		    },
        onClickRow:function(row){
            //单击事件-加载功能列表
            gnlb_get(row);
            treeGrid.treegrid('toggle', row.id);
        },
        onLoadSuccess: function(row,data) {

            //菜单按钮加载
            get_anqxLst_gn('cdgl','','cd');

            //保留数据总数和刷新按钮
            var pagination = $('#dgCdgl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
        }
    });

  // 功能列表初始化加载
    dataGrid =$('#dgCdGngl').datagrid({
        method: "post",
        nowrap : false,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/gnlb_view",
        idField:'id',
        columns: [
            [
                {field: 'id',  width: 40, checkbox:'true' },
                {field: 'gndm', title: '功能代码', width: 100},
                {field: 'gnmc', title: '功能名称', width: 80},
                {field: 'bz', title: '备注', width: 100}
            ]
        ],
        toolbar: [{
            id:'gn_add',
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 增加
                cdgl_add2upd('新增功能','', 'add','gn' );
            }
        }, {
            id:'gn_edit',
            iconCls: 'icon-edit',
            text: '编辑',
            handler: function() {
                 var rows = dataGrid.datagrid('getSelections');
                 if(rows == '' || rows.length > 1 ){
                     $.messager.alert('警告', '必须且只能选择一项', 'warning');
                     return false;
                 }
                 // 编辑
                cdgl_add2upd('编辑功能',rows[0].id, 'update','gn' );

            }
        },
        {
            id:'gn_del',
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 调用删除方法
                removePl();
        }
        }],
        onBeforeLoad : function(param){
                //数据加载前清空选择
		    	$(this).datagrid('clearSelections').datagrid('unselectAll');
		    },
        onLoadSuccess: function(data) {
            //菜单按钮加载
            get_anqxLst_gn('cdgl','','gn');

            //保留数据总数和刷新按钮
            var pagination = $('#dgCdGngl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
        }
    });

    // 菜单一览窗口新增/编辑的取消按钮
    $('#lbtnCdglCancel').click(function(e){
        e.preventDefault();
        windowCancelFun('divCdglWindow');
    });

    // 功能一览窗口新增/编辑的取消按钮
    $('#lbtnGnCancel').click(function(e){
        e.preventDefault();
        windowCancelFun('divGnWindow');
    });
    // 最大值限制
    //菜单新增编辑窗口元素
    $("#txtCdmc").next().children().attr("maxlength","30");
    $("#txtUrl").next().children().attr("maxlength","100");
    $("#nubPxh").next().children().attr("maxlength","2");
    $("#txtBz").next().children().attr("maxlength","100");
    //功能新增编辑窗口元素
    $("#txtGndm").next().children().attr("maxlength","20");
    $("#txtGnmc").next().children().attr("maxlength","30");
    $("#txtSm").next().children().attr("maxlength","100");

    // 绑定菜单一览新增或编辑窗口更新按钮的事件
    $('#lbtnCdglSubmit').click(function(e){
        e.preventDefault();
          // 添加遮罩
        ajaxLoading();
        // 出错提示
        if ($("#hidCdid").val()=="") {
            // 新增
            url = "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/add_cd_view";
        } else {
            // 修改
            url = "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/edit_cd_view";
        }
        // 提交表单
        addOrEditSubmit( "divCdglWindow",url, "dgCdgl",'1')
    });

    //绑定功能一览新增或编辑窗口更新按钮的事件
    $('#lbtnGnSubmit').click(function(e){
        e.preventDefault();
          // 添加遮罩
        ajaxLoading();

        // 出错提示
        if ($("#hidGnid").val()=="") {
            // 新增
            url = "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/add_gn_view";
        } else {
            // 修改
            url = "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/edit_gn_view";
        }
        // 提交表单
        addOrEditSubmit( "divGnWindow",url, "dgCdGngl",'2')
    });

});

 /**
   * treegrid行单击事件.
   * @param row 行数据
   */
 function gnlb_get(row) {
    // 加载画面数据
  	$('#dgCdGngl').datagrid('reload', {'cdid' : row.id});
 }

/**
 * bean_window中的关闭按钮
 * windowID:窗口ID
 */
function windowCancelFun(windowID) {
    $('#' + windowID).window('close');
};


/**
* 函数名称：新增或编辑页面初始化
* 函数参数：
    wintit: 打开窗口标题
    id:选择的datagrid数据ID
    handle：操作类型：add，update
    type:操作对象 cd,gn
*/
function cdgl_add2upd(wintit,id, handle,type ){
    // 设置操作行不被选中
    event = event || window.event;
    event.stopPropagation();
    var cdid = '';
    var gnid='';
    if (type=='cd' && handle=='update'){
        cdid = id
    }else if (type=='gn' && handle=='update'){
        gnid = id
    }
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/lst_view ",
        data : {
            'cdid':cdid,
            'gnid':gnid
        },
        success: function(data){
            //// 打开窗口
            if (type=='cd'){
                newWindow($("#divCdglWindow"),wintit,620,300);
            }else if(type=='gn'){
                 //新增功能窗口
                if ( handle=='add'){
                     //获取菜单id
                    var rows = $('#dgCdgl').treegrid('getSelected');
                    if (rows == null || rows ==""){
                        $.messager.alert('警告', "请先选择菜单，再添加对应的功能", 'warning');
                        return false;
                        }
                    newWindow($("#divGnWindow"),wintit,350,250);
                    $("#txtGndm").textbox('enable');
                    $("#hidCdid_gn").val(rows.id );
                    $("#hidCdmc_gn").val(rows.text);
                }else if ( handle=='update'){
                    newWindow($("#divGnWindow"),wintit,350,250);
                }

            }
            // 反馈信息
            data = $.parseJSON( data );
            // 获取数据成功
            if( data.state == true ){
                // 初始化页面元素
                show_addOreditWindow(handle,data,type);
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

/*
* 新增或者编辑页面初始化
* handle:操作类型： update：编辑 ，add:新增
* dataR:选择的列表数据
* flag: cd: 菜单 ，gn: 功能
*
* */
function show_addOreditWindow(handle,dataR,flag) {
    if(flag == 'cd'){
       //初始化下拉框
       // 菜单分类
       $('#selCdfl').combobox({
           editable:false,
           data:dataR.cdfl_lst,
           valueField:'value',
           textField:'text'
	    });
       //初始化下拉框
       // 登录系统下拉框
       $('#selSsxt').combobox({
           valueField:'value',
           textField:'text',
           editable:false,
           data:dataR.dlxt_lst
	    });
        //所属菜单树加载
        $('#selSjcd').combotree({
           mode:'remote',
           method:'get',
           editable:false,
           data:dataR.sjcd_lst
	    });

        //窗口初始化
        //编辑菜单窗口
        if(handle == 'update' ){
            get_edit(dataR,'cd');
        }else if (handle == 'add'){
            //新增菜单窗口
            $("#selCdfl").combobox('select', '-1');
             $("#selSsxt").combobox('select', '-1');
             // 清空参数ID
            $("#hidCdid").val('');
            $("#hidCdlb").val('');
            $("#hidCddm").val('');
            $("#txtCddm").textbox('enable');
        }
        // form tab排序
        $("#divCdglWindow").children('form').tabSort();
    }else if (flag =='gn'){
        //窗口初始化
        if(handle == 'update' ){
            get_edit(dataR,'gn');
        }else if (handle == 'add'){
             //新增功能窗口
             // 清空参数ID
            $("#hidGnlb").val('');
            $("#hidGnid").val('');
        }
        //tab顺设置
        $("#divGnWindow").children('form').tabSort();
    }
}

/*
* 获取编辑前数据
* id:编辑记录的id
* url： 后台关联url
* type: cd-菜单，gn-功能
* */
function get_edit(data, type){
    if (type == 'cd'){

        //菜单代码
        $("#txtCddm").textbox('disable');
        $("#hidCddm").val(data['cdxx'].cddm);
        $("#txtCddm").textbox('setValue',data['cdxx'].cddm);
        // 菜单名称
        $("#txtCdmc").textbox('setValue', data['cdxx'].cdmc);
        // 访问地址
        $("#txtUrl").textbox('setValue', data['cdxx'].url);
        //菜单分类
        if(data['cdxx'].lx == '' || data['cdxx'].lx == null){
            $("#selCdfl").combobox('select', -1);
        }else{
            $("#selCdfl").combobox('select', data['cdxx'].lx);
        }
        //所属菜单
        if(data['cdxx'].fjdid == '' || data['cdxx'].fjdid == null || data['cdxx'].fjdid == '0'){
            $("#selSjcd").combotree('setValue', '');
        }else{
            $("#selSjcd").combotree('setValue', data['cdxx'].fjdid);
        }
        //备注
        $("#txtBz").textbox('setValue', data['cdxx'].bz);
        //排序号
        $("#nubPxh").numberbox('setValue', data['cdxx'].pxh);
        //所属系统
        if(data['cdxx'].ssxt == '' || data['cdxx'].ssxt == null){
            $("#selSsxt").combobox('select', -1);
        }else{
            $("#selSsxt").combobox('select', data['cdxx'].ssxt);
        }
        //隐藏的菜单id
        $("#hidCdid").val(data['cdxx'].id);
    }else if (type == 'gn'){
            $("#hidGnid").val(data['gnxx'].id);
            $("#txtGnmc").textbox('setValue', data['gnxx'].gnmc);
            $("#txtGndm").textbox('disable');
            $("#hidGndm").val(data['gnxx'].gndm);
            $("#txtGndm").textbox('setValue',data['gnxx'].gndm);
            $("#txtSm").textbox('setValue', data['gnxx'].bz);
            $("#hidCdid_gn").val(data['gnxx'].sscdid );
    }
}

/*
* 新增或编辑提交表单操作
* windowID: 弹出的窗口的id
* url:后台操作连接的url
* gridID: 列表ID
* flag ： 标志 1-treeGrid,2-datagird
* */
function addOrEditSubmit( windowID,url, gridID,flag){
        // 提交表单
        $('#'+ windowID).find('form').form('submit', {
            url: url ,
            type:'post',
            onSubmit: function(){
                var ret = validate(flag);
                 // 反馈校验结果
                if( ret == false ){
                    // 取消遮罩
                    ajaxLoadEnd();
                }
                return ret;
            },
            success: function(data){
                if (flag =='1'){
                    //列表重新加载
                    treeGrid.treegrid('reload')
                    $('#dgCdGngl').datagrid('reload', {});
                }
                //提示信息
                afterAjax(data, gridID, windowID);
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
}

/**
 *删除
 * flag : 1-treegrid 2-datagrid
 * gridId:列表变量
 * url:后台执行url
 * dataR:后台执行的参数
 */
function removechecked(dataR,url,gridId,flag) {
        $.messager.confirm('提示', '数据删除后将不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url:url,
                    data:dataR,
                    success: function(data){
                        data = $.parseJSON(data);
                        if(data.state == true){
                            // 重新加载
                            if(flag == '1'){
                               gridId.treegrid('reload');
                               $('#dgCdGngl').datagrid('reload', {});
                            }else{
                                gridId.datagrid('reload');
                            }
                            //提示信息
                            afterAjax(data, '', '');
                        }else{
                            //提示信息
                            afterAjax(data, '', '');
                        }
                    },
                    error : function(){
                        errorAjax();
                    }
                });
            }
        })
}

/**
 *菜单功能：批量删除
 */
function removePl() {
    var rows = $('#dgCdGngl').datagrid('getSelections');
    var rows_cd = $('#dgCdgl').treegrid('getSelected');
    var gnids = new Array();
    $(rows).each(function(index, item){
        gnids.push(item["id"]);
    });
    if (rows.length) {
        $.messager.confirm('提示', '数据删除后将不可恢复，您确定要删除吗？', function(r) {
            if (r) {
                //发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/del_gn_view",
                    data: {'id': gnids.join(","),
                        'cdmc':rows_cd.text
                    },
                    success: function(data){
                        afterAjax(data, "dgCdGngl", "");
                    },
                    error : function(){
                        errorAjax();
                    }
                });
            }
        })
    } else {
        //至少选择一项
        checkSelected('dgCdGngl');
    }
}

// 输入框校验 flg: 1:菜单，2:功能
function validate(flag){
    if(flag=='1'){
        // 菜单代码
        var cdgl_cddm = $("#txtCddm").textbox('getValue');
         // 菜单名称
        var cdgl_cdmc = $("#txtCdmc").textbox('getValue');
        // 访问地址
        var cdgl_url = $("#txtUrl").textbox('getValue');
        // 菜单类型
        var cdgl_cdfl = $("#selCdfl").textbox('getValue');
         // 排序号
        var cdgl_pxh = $("#nubPxh").numberbox('getValue');
        // 所属系统
        var cdgl_ssxt = $("#selSsxt").textbox('getValue');

        // 菜单代码
        if(!checkNull(cdgl_cddm, '菜单代码', 'txtCddm')){
            return false;
        };
         // 菜单名称
        if(!checkNull(cdgl_cdmc, '菜单名称', 'txtCdmc')){
            return false;
        };

        //菜单名称输入格式校验--只能输入汉字、英文字母、半角下数字、英文下划线
        if( !checkMc(cdgl_cdmc,'菜单名称','txtCdmc')){
             return false;
        }

        //校验访问地址
        if(!checkNull(cdgl_url, '访问地址', 'txtUrl')){
             return false;
        };
        // 校验菜单类型
        if (cdgl_cdfl=="" || cdgl_cdfl==null || cdgl_cdfl=="请选择" || cdgl_cdfl=="-1" ) {
            $.messager.alert('错误','菜单类型不可为空，请选择','error', function(){
                $("#selCdfl").next().children().focus();
            });
            return false;
        }

        //排序号不可空
        if(!checkNull(cdgl_pxh, '排序号', 'nubPxh')){
            return false;
        };
         // 所属系统不可空
        if (cdgl_ssxt=="" || cdgl_ssxt==null || cdgl_ssxt=="请选择" || cdgl_ssxt=="-1" ) {
            $.messager.alert('错误','所属系统不可为空，请选择','error', function(){
                $("#selSsxt").next().children().focus();
            });
            return false;
        }
    }else if (flag == '2'){
        //功能代码
        var cdgl_gndm = $("#txtGndm").textbox('getValue');
        // 功能名称
        var cdgl_gnmc = $("#txtGnmc").textbox('getValue');

        // 功能代码
        if (!checkNull(cdgl_gndm, '功能代码', 'txtGndm')) {
            return false;
        }
        //功能名称输入格式校验--只能输入英文字母、半角下数字、英文下划线
        if( !checkBm2(cdgl_gndm,'功能代码','txtGndm')){
             return false;
        }
        // 功能名称
        if (!checkNull(cdgl_gnmc, '功能名称', 'txtGnmc')) {
            return false;
        }
    }
};
