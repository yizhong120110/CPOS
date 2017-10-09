$(function () {
    // 数据列表
    $('#dgXtcs').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        pageSize: 50,
        fitColumns: true,
        method: "get",
        url: "/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/data_view",
        remoteSort: false,
        frozenColumns: [[
            {field: 'select_box', checkbox: true}
        ]],
        columns: [[
            {field: 'id', title: '参数ID', hidden: true},
            {field: 'csdm', title: '参数代码', width: '18%'},
            {field: 'value', title: '参数值', width: '28%'},
            {field: 'csms', title: '参数描述', width: '32%'},
            {field: 'ly', title: '来源', width: '6%', formatter: function (value, rowData, rowIndex) {
                return value == "1" ? "自定义" : "系统预置";
            }},
            {
                field: 'zt', title: '状态', width: '6%', formatter: function (value, rowData, rowIndex) {
                return value == "1" ? "启用" : "禁用";
            }
            },
            {
                field: 'cz', title: '操作', width: '6%', formatter: function (value, rowData, rowIndex) {
                return '<a href="javascript:;" onclick="emdit(\''+rowIndex+'\');">编辑</a> ';
            }
            }
        ]],
        toolbar: [
            {
                iconCls: 'icon-add',
                text: '新增',
                handler: function () {
                    // 增加
                    showHide('add');
                }
            }, {
                iconCls: 'icon-remove',
                text: '删除',
                handler: function () {
                    // 调用删除方法
                    removechecked();
                }
            }
        ],
        onLoadSuccess: function(data){ // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断来源为铺底的不允许选中
                for (var i = 0; i < data.rows.length; i++) {
                    if (data.rows[i].ly == '2') {
                        $("input[type='checkbox']")[i + 1].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgXtcs').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('.datagrid-cell-check input:enabled').length == $('#dgXtcs').datagrid('getChecked').length && $('#dgXtcs').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgXtcs').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('.datagrid-header-check input').get(0).checked = true;
        }
    });

    

    // 搜索框设置
    var fields =  $('#dgXtcs').datagrid('getColumnFields');
    var muit="";
    for(var i=0; i<fields.length-1; i++){
        var opts = $('#dgXtcs').datagrid('getColumnOption', fields[i]);
        if( fields[i] != 'id' ){
            muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }
    };
    $('#divSearch').html($('#divSearch').html()+muit);
    $('#search_box').searchbox({
        menu:'#divSearch',
        prompt:'请输入查询内容',
        searcher:doSearch
    });

    // 最大值限制
    $("#txtCsdm").next().children().attr("maxlength","32");
    $("#txtCsz").next().children().attr("maxlength","1000");
    $("#txtCsms").next().children().attr("maxlength","150");

    // 按钮【保存】的click事件监听
    $("#lbtnXtcsSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 参数状态
        var cszt = $("#nfsCszt").get(0).checked ? "1" : "0";
        // 平台
        var pt = $("#txtPt").val();
        var url = undefined;
        // 出错提示
        var msg = "新增失败，请稍后再试";
        if ($("#txtCsid").val()=="") {
            // 新增
            url = "/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/data_add_view";
        } else {
            // 修改
            url = "/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/data_edit_view",
                msg = "修改失败，请稍后再试";
        }
        // 提交表单
        $('#divXtcsWindow').find('form').form('submit', {
            url: url,
            queryParams: {'cszt': cszt, 'pt': pt},
            onSubmit: function(){
                var csid = $('#txtCsid').val();
                var csbm = $("#txtCsdm").textbox("getValue");
                var csz = $("#txtCsz").textbox("getValue");
                var csms = $("#txtCsms").textbox("getValue");
                if (csbm=="") {
                    $.messager.alert('错误','参数代码不可为空，请输入','error', function(){
                        $("#txtCsdm").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if(!checkBm(csbm,'参数代码','txtCsdm')){
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (csz=="") {
                    $.messager.alert('错误','参数值不可为空，请输入','error', function(){
                        $("#txtCsz").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (csbm == "YWZJ_IP") {
                    if(!checkBm3(csz,"参数值","txtCsz")) {
                        // 取消遮罩
                        ajaxLoadEnd();
                        return false;
                    }
                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "dgXtcs", "divXtcsWindow");
            },
            error: function () {
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });

    // 按钮【取消】的click事件监听
    $("#lbtnXtcsCancel").click(function(e){
        e.preventDefault();
        $('#divXtcsWindow').window('close');
    });

    /**
     *批量删除
     */
    function removechecked(){
        if(!checkSelected("dgXtcs")) {
            return;
        }
        $.messager.confirm('确认', '参数删除后数据将不可恢复，您确定要删除吗？', function(r){
            if (r) {
                // 添加遮罩
                ajaxLoading();
                // 当前选中的记录
                var checkedItems = $('#dgXtcs').datagrid('getChecked');
                var csids = new Array();
                $(checkedItems).each(function(index, item){
                    csids.push(item["id"]);
                });
                // 平台
                var pt = $("#txtPt").val();
                $.ajax({
                    type: 'POST',
                    dataType: 'text',
                    url: "/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/data_del_view",
                    data: {"csids": csids.join(","), "pt": pt},
                    success: function(data){
                        // 取消遮罩
                        ajaxLoadEnd();
                        afterAjax(data, "dgXtcs", "");
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

    // 执行搜索
    function doSearch(value,name){
        //重新定义url
        var tj_str = 'search_name=' + name + '&search_value=' + value;
        $('#dgXtcs').datagrid( {url:'/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/data_view?' + tj_str });
    }

    $("#txtCsdm").next().children().on('keydown', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if(keycode == 229) {
            $(that).blur();
            setTimeout(function() {
                $(that).focus()
            }, 10)
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

    $("#txtCsdm").next().children().on('keypress', function(e){
        var that = this;
        var value = this.value;
        // 按键的keycode
        var keycode = e.which;
        // shift键是否按住
        var isshift = e.shiftKey;
        if ((keycode >= 65 && keycode <= 90)
            || keycode == 8
            || keycode == 46
            // || keycode == 36
            || (keycode >= 48 && keycode <= 57)
            || (keycode == 95)) {
        } else {
            e.preventDefault();
            e.stopImmediatePropagation();
        }
    });

});

// 按钮【编辑】clcik事件监听
function emdit(rowIndex) {
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    //var rowIndex = $(e.currentTarget).data('rowIndex');
    
    showHide('update', 'dgXtcs', rowIndex);
};

/**
 *新增or编辑业务参数弹窗
 */
function showHide(handle,id,index) {
    if(handle=='add'){
        newWindow($("#divXtcsWindow"),'新增系统参数',450,320);
        // 新增时参数代码控件可编辑
        $("#txtCsdm").textbox('enable');
        // 打开窗口时已清空表单，需要重新赋值为启用状态
        $("#nfsCszt").get(0).checked = true;
        // 清空参数ID
        $("#txtCsid").val('');
        $("#txtCsdm").next().children().select();
    }
    else if(handle=='update'){
        newWindow($("#divXtcsWindow"),'编辑系统参数',450,320);
        var d = $('#'+id).datagrid('getData').rows[index];
        $("#txtCsid").val(d.id);
        $("#txtCsdm").textbox('setValue', d.csdm);
        $("#txtCsdm").textbox('disable');
        $("#txtCsz").textbox('setValue', d.value);
        $("#txtCsms").textbox('setValue', d.csms);
        $("#nfsCszt").get(0).checked = (d.zt=="1");
    }

    // tab排序
    $("#divXtcsWindow").children('form').tabSort();
    $('#txtCsdm').textbox('textbox').attr('placeholder', '仅能输入大写字母数字下划线');
}
