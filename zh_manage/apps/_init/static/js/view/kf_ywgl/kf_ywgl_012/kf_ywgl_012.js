$(document).ready(function() {
    $('#lbtDateCR').hide();
    // 平台
    var pt = $('#hidPt').val();
    var url = '';
    var queryParams = {};
    if ($('#lx').val() == 'demo') {
        $('#searchBox').hide();
        // 当用户选择了批量导入的按钮时，批量导入才会展示。
        if(parent.demoSelID == 'btnSelectDemoPL'){
            $('#lbtDateCR').show();
        }
        // Demo表数据
        url = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_sj_data_view?demojbxxid=' + $("#demojbxxid").val() + '&sjbmc=' + $('#sjbmc').val();
    } else {
        // 真实表数据
        url = '/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/data_view?sjbmc=' + $("#sjbmc").val() + '&zdmc_str=' + $("#zdmc_str_sel").val() + '&sjbzj_str=' + $("#sjbzj").val() + '&zdxx_str=' + $("#zdxx_str").val();
    }
    
    // 渲染表格
    $('#dgSjkbxxck').datagrid({
        title: "数据表：",
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : $('#lx').val() != 'demo',
        pageSize: 50,
        fitColumns : false,
        method: "get",
        url: url,
        queryParams: queryParams,
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        onLoadSuccess: function(data) {
            sjid_xssx = data.sjid_xssx;
            var datagrid = $(this).data().datagrid;
            var colums = datagrid.options.columns;
            var view2 = datagrid
                .panel
                .find('.datagrid-view2');
            var header = view2.children(".datagrid-header");
            var body = view2.children(".datagrid-body");
            var htable = header.find('.datagrid-htable');

            htable
                .find('.datagrid-header-row')
                .children()
                .each(function(i, tdElement) {
                    var col = colums[0][i];
                    var opts = {};
                    if (col && col.ttip) {
                        col.msg = col.ttipMsg;
                        $(tdElement).ttip(col);
                    }
                });

            if (!data.total) {
                body.append('<div style="width:'+htable.width()+'px;text-align:center;">&nbsp;</div>');
            }
        }
    });
    // 平台是开发时，有操作按钮
    if( pt == 'kf' ){
        $('#dgSjkbxxck').datagrid({
            frozenColumns: [[
                { field: 'ck', checkbox: true }
            ]],
            toolbar: "#dgSjkbxxckTb"
        })
    }
    
    // 初始化查询控件
    var fields =  $('#dgSjkbxxck').datagrid('getColumnFields');
    var muit="";
    // 可以用于查询的字段
    var zdmc_str = $("#zdmc_str_sel").val();
    var zdmc_arr = zdmc_str.split(',');
    for(var i=0; i<fields.length; i++){
        if( zdmc_arr.indexOf( fields[i] ) > -1 ){
            var opts = $('#dgSjkbxxck').datagrid('getColumnOption', fields[i]);
            muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }
    };
    $('#shbSjkmxdyDiv').html($('#shbSjkmxdyDiv').html()+muit);
    $('#sebSjkmxdy').searchbox({
        searcher:function(value,name){
            // 向后台发送条件查询请求函数
            do_search( name, value );
        },
        menu:'#shbSjkmxdyDiv',
        prompt:'请输入查询内容'
    });
    
    // 初始化各个按钮事件
    // 插入按钮
    $("#lbtDateOpen").click(function(){
        showHide('add');
    })
    // 批量删除按钮
    $("#lbtDateDel").click(function(){
        removechecked( 'dgSjkbxxck' );
    })
    
    // 批量插入demo数据的窗口
    $("#lbtDateCR").click(function(){
        // 打开插入界面
        newWindow($("#divCRWindow"),'插入表数据(insert sql语句,分号分隔)',500,305);
        $("#crform").tabSort();
    })
    // 批量插入demo数据的窗口保存按钮
    $("#lbtnCRSave").click(function(e){
        e.preventDefault();
        saveCRSub();
    })
    // 批量插入demo数据的窗口取消按钮
    $("#lbtnCRCancel").click(function(e){
        e.preventDefault();
        $('#divCRWindow').window('close');
    })
    // open页面保存按钮
    $("#lbtnSave").click(function(e){
        e.preventDefault();
        saveEditSub();
    })
    // open页面取消按钮
    $("#lbtnCancel").click(function(e){
        e.preventDefault();
        $('#divBsjWindow').window('close');
    })
});

var sjid_xssx = null;

/**
* 条件查询
*/
function do_search( name, value ){
    // 日期类型字段集合
    var date_zd_str = $("#date_zd_str").val();
    var name_sel = name;
    if( date_zd_str.indexOf(name) > -1 ){
        //TO_CHAR(dt, 'YYYY-MM-DD')
        name_sel = "TO_CHAR(" + name + ", 'YYYY-MM-DD')";
    }
    // 数据表名称
    var sjbmc = $("#sjbmc").val();
    // 数据表字段集合
    var zdmc_str = $("#zdmc_str_sel").val();
    // 主键
    var sjbzj = $("#sjbzj").val();
    // 字段信息
    var zdxx_str = $("#zdxx_str").val();
    // 重新定义url
    var tj_str = 'sjbmc='+ $("#sjbmc").val() +'&zdmc_str=' + zdmc_str + '&sjbzj_str=' + sjbzj + '&search_name=' + name+ '&search_name_sel=' + name_sel + '&search_value=' + value + '&zdxx_str=' + zdxx_str;
    // 数据表格重新请求数据
    $('#dgSjkbxxck').datagrid( {url:'/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/data_view?' + tj_str } );
}

/**
* 批量删除
*/
function removechecked( dgid ){
    // 获取主键
    var sjbzj = $("#sjbzj").val();
    if( sjbzj == '' ){
        $.messager.alert('错误','数据表没有主键，不允许操作表数据','error' );
        return false;
    }
    if(!checkSelected(dgid)) {
        return;
    }
    if ($('#lx').val() == 'demo') {
        $.messager.confirm('确认', '您确定要删除所选数据吗？', function(r){
            if (r) {
                // 遮罩
                ajaxLoading();
                var checkedItems = $('#dgSjkbxxck').datagrid('getChecked');
                // [[sjid, xssx], [sjid, xssx], ...]
                var data = [];
                $(checkedItems).each(function(index, item) {
                    var rowIndex = $('#dgSjkbxxck').datagrid('getRowIndex', item);
                    data.push(sjid_xssx[rowIndex]);
                });
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_sj_data_del_view?demojbxxid=" + $("#demojbxxid").val() + '&sjbjc=' + $("#sjbmc").val(),
                    data: {
                        "data": JSON.stringify(data)
                    },
                    success: function(data) {
                        // 取消遮罩
                        ajaxLoadEnd();
                        afterAjax(data, "dgSjkbxxck", "");
                    },
                    error: function() {
                        // 取消遮罩
                        ajaxLoadEnd();
                        errorAjax();
                    }
                });
            }
        })
    } else {
        $.messager.confirm('确认', '表数据删除后将无法恢复，您确认要删除吗？', function(r){
            if (r) {
                // 遮罩
                ajaxLoading();
                // 数据表
                var sjbmc = $("#sjbmc").val();
                // 获取主键集(zjzd,zjzd)
                var sjbzj = $("#sjbzj").val();
                var sjbzj_arr = sjbzj.split(',');
                var sjbzjtype = $("#sjbzjtype").val();
                var sjbzjtype_arr = sjbzjtype.split(',');
                // 当前选中的记录
                var checkedItems = $('#' + dgid).datagrid('getChecked');
                var ids = new Array();
                $(checkedItems).each(function(index, item){
                    var line = new Array();
                    for( i=0; i< sjbzj_arr.length; i++ ){
                        line.push( sjbzj_arr[i] + '|' +item[ sjbzj_arr[i] ] + '|' + sjbzjtype_arr[i] );
                    }
                    ids.push( line.join('~') );
                });
                
                // 发送删除请求
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/data_del_view",
                    data: {'sjbmc': sjbmc, "ids": ids.join(",")},
                    success: function(data){
                        // 取消遮罩
                        ajaxLoadEnd();
                        afterAjax(data, dgid, "");
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

var editIndex = 0;
/**
* 新增or编辑表数据页面初始化
* handle:操作类型 add：插入，1：编辑( 因为前台页面多级字符串嵌套，所有就使用数字1代替了update )
*/
function showHide(handle,index) {
    // 取消行选中
    var event = event || window.event;
    event.stopPropagation();
    editIndex = index;
    // 新增or编辑数据表id
    var id = 'dgSjkbxxck';
    // 获取主键集合
    var sjbzj = $("#sjbzj").val();
    var sjbzj_arr = sjbzj.split(',');
    // 根据字段多少自适应高度
    // 数据表字段集合
    var zdmc_str = $("#zdmc_str_sel").val();
    var zd_len = zdmc_str.split(',').length;
    // 编辑页面起始高度为100，每个字段增加高度35，最高600
    var win_height = 105 + 35*zd_len
    var max_height = $('#lx').val() == 'demo' ? 280 : 423;
    if( win_height > max_height )
        win_height = max_height
    
    // 根据操作类型不同做出不同操作
    if(handle=='add'){
        // 打开插入界面
        newWindow($("#divBsjWindow"),'插入表数据',550,win_height);
        // 启用主键
        if( sjbzj != "" ){
            for( i=0; i< sjbzj_arr.length; i++ ){
                $("#txt" + sjbzj_arr[i]).textbox('enable');
            }
        }
        // 操作类型为新增
        $("#cztype").val('add');
        // 默认值赋值
        var mrz_str = $("#mrz_str").val();
        if( mrz_str != '' ){
            var mrz_arr = mrz_str.split(",");
            for( i=0; i< mrz_arr.length; i++ ){
                var zdmc_mrz_arr = mrz_arr[i].split(':');
                $("#txt" + zdmc_mrz_arr[0]).textbox('setValue', zdmc_mrz_arr[1].replace(/\'/g, '') );
            }
        }
        
    }
    else if(handle==1){
        // 打开编辑界面
        newWindow($("#divBsjWindow"),'编辑表数据',550,win_height);
        // 初始化页面数据
        var d = $('#'+id).datagrid('getData').rows[index];
        for(var zdmc in d){
            // 对存在的对象赋值
            if( $("#txt" + zdmc) != undefined ){
                $("#txt" + zdmc).textbox('setValue', number_xsws( zdmc, eval( 'd.'+zdmc ) ));
            }
        }
        // 主键操作
        if( sjbzj != "" ){
            // 禁用页面元素
            var zjxx_arr = new Array();
            for( i=0; i< sjbzj_arr.length; i++ ){
                $("#txt" + sjbzj_arr[i]).textbox('disable');
                zjxx_arr.push( sjbzj_arr[i] + '|' + $("#txt" + sjbzj_arr[i]).val() );
            }
            // 修改信息主键信息赋值
            $("#updid").val( zjxx_arr.join('~') );
        }else{
            $("#updid").val('');
        }
        // 操作类型为编辑
        $("#cztype").val('update');
    }
    // 重新初始化tabindex
    $('#bsjform').tabSort();
}

/**
* 新增或编辑数据提交
*/
function saveEditSub(){
    // 操作类型
    var cztype = $("#cztype").val();
    // 数据表
    var sjbmc = $("#sjbmc").val();
    // 获取主键
    var sjbzj = $("#sjbzj").val();
    if( sjbzj == '' ){
        $.messager.alert('错误','数据表没有主键，不允许操作表数据','error' );
        return false;
    }
    var sjbzjtype = $("#sjbzjtype").val();
    var sjbzjvalue = '';
    // 数据表字段集合
    var zdmc_str = $("#zdmc_str_sel").val();
    // 数据表字段信息集合
    var zdxx_str = $("#zdxx_str").val();
    // 新增
    // 出错提示( 默认插入 )
    var msg = "插入失败，请稍后再试";
    var url = "/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/data_add_view";
    if( cztype == 'update' ){
        // 编辑
        msg = "编辑失败，请稍后再试";
        url = "/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/data_edit_view";
        // 修改信息的主键信息
        sjbzjvalue = $("#updid").val();
    }
    
    // start
    if ($('#lx').val() == 'demo') {
        var url = '';
        if (cztype == 'update') {
            // 编辑
            url = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_sj_data_edit_view?demojbxxid=' + $('#demojbxxid').val() + '&sjbjc=' + $('#sjbmc').val() + '&sjbms=' + $('#sjbms').val() + '&sjid=' + sjid_xssx[editIndex][0] + '&xssx=' + sjid_xssx[editIndex][1];
        } else {
            // 新增
            url = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_sj_data_add_view?demojbxxid=' + $('#demojbxxid').val() + '&sjbjc=' + $('#sjbmc').val() + '&sjbms=' + $('#sjbms').val();
        }
        // 提交数据
        submitSj(url, {});
    } else {
        var queryParams = {'czsjbmc': sjbmc, 'sjbzj': sjbzj, 'sjbzjtype': sjbzjtype, 'sjbzjvalue': sjbzjvalue, 'zdmc_str': zdmc_str, 'zdxx_str': zdxx_str};
        // 提交数据
        submitSj(url, queryParams);
    }
    // end
}

/**
* 表单数据提交
*/
function submitSj(url, queryParams) {
    // 遮罩
    ajaxLoading();
    $('#divBsjWindow').find('form').form('submit', {
        url: url,
        queryParams: queryParams,
        onSubmit: function(){
            // 字段详细信息集合
            var zdxx_attr = $("#zdxx_str").val().split('|');
            // 需要校验非空
            for( var i= 0; i < zdxx_attr.length; i++ ){
                // 字段名称
                var zdmc = zdxx_attr[i].split(',')[0];
                // 字段描述
                var zdms = zdxx_attr[i].split(',')[1];
                if( zdms == 'None' || zdms == '' )
                    zdms = zdmc.toUpperCase()
                // 字段长度
                var zdcd = zdxx_attr[i].split(',')[2];
                // 是否可控 N(不可空)，Y(可空)
                var sfkk = zdxx_attr[i].split(',')[3];
                if( $('#span'+ zdmc).length > 0 ){
                    var zd_value = $("#txt" + zdmc).textbox("getValue");
                    if (zd_value=="") {
                        $.messager.alert('错误',zdmc.toUpperCase() + '不可为空，请输入','error', function(){
                            $("#txt" + zdmc).next().children().focus();
                        });
                        // 取消遮罩
                        ajaxLoadEnd();
                        return false;
                    }
                }
            }
            return true;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgSjkbxxck", "divBsjWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
* 对于数值进行处理小数
*/
function number_xsws( zdmc, xx ){
    var zdmc_xsws_str = $("#zdmc_xsws_str").val();
    var zdmc_xsws_arr = zdmc_xsws_str.split(',')
    for( var i = 0; i < zdmc_xsws_arr.length; i++ ){
        var zdmc_2 = zdmc_xsws_arr[i].split(':')[0];
        var xsws = zdmc_xsws_arr[i].split(':')[1];
        if ( zdmc_2 == zdmc ){
            xx = accounting.formatNumber(xx,parseInt(xsws),"")
            break;
        }
    }
    return xx
}

/**
* 执行插入SQL
*/
function saveCRSub(){
    // 添加遮罩
    ajaxLoading();
    var sql = $('#txtCRNr').textbox("getValue");
    if (!checkNull(sql,'sql','txtCRNr')) {
        // 取消遮罩
        ajaxLoadEnd();
        return false;
    }
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_sj_data_pladd_view",
        data: {'demojbxxid': $('#demojbxxid').val(), "sjbjc": $('#sjbmc').val(), "sjbms":$('#sjbms').val(), "sql":sql},
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgSjkbxxck", "divCRWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
