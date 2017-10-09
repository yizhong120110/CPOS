$(document).ready(function() {

    // 渲染表格
    $('#dgWdqdlb').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        pageSize: 50,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        frozenColumns: [
            [{
                field: 'ck',
                checkbox: true
            }]
        ],
        columns: [
            [{
                field: 'id',
                title: '编号',
                hidden: true
            }, {
                field: 'wdlb',
                title: '文档类别id',
                hidden: true
            }, {
                field: 'wdlbmc',
                title: '文档类别',
                width: '30%'
            }, {
                field: 'wdmc',
                title: '文档名称',
                width: '50%'
            }, {
                field: 'operator',
                title: '操作',
                width: '15%',
                formatter: function(value, row, index) {
                    return '<a href="javascript:void(0)" onclick="wdqd_down(\'dgWdqdlb\',\'2\','+ index +')">下载</a> ' +
                        '<a href="javascript:void(0)" onclick="wdqd_reload(\'update\',\'dgWdqdlb\',' + index + ')">上传</a> ' +
                        '<a href="javascript:void(0)" onclick="wdqd_remove(\'dgWdqdlb\',' + index + ');" >删除</a>';
                }
            }]
        ],
        toolbar: [{
            iconCls: 'icon-add',
            text: '添加文档',
            handler: function() {
                // 新增
                wdqd_reload('add');
            }
        }, {
            iconCls: 'icon-down',
            text: '一键下载',
            handler: function() {
                wdqd_down('dgWdqdlb', '1')
            }
        }]
    });

    // 初始化按钮点击事件
    $("#lbtnWdqdSubmit").click(function(e) {
        e.preventDefault();
        // 获取操作文档清单id（存在则为编辑，不存在则为新增）
        var wdqdid = $("#updid").val();
        // 遮罩
        ajaxLoading();
        // 判断是否添加了文件 true表示添加了文件，false表示没有添加文件
        if(fileup.isAddFile) {
            // 校验文件是否符合规则
            var fname = fileup.filename;
            var ret = checkFilename( fname );
            // 判断文件长度( 不得超过五十 )
            if( ret ){
                // 添加了文件，使用第三方插件上传文件及表单参数
                fileup.submit();
            }else{
                return false;
            }
        } else {
            if (wdqdid != '') {
                // 编辑
                // 没有添加文件 不调用上传控件，使用easyui的表单提交请求
                reload_sub();
            } else {
                // 取消遮罩
                ajaxLoadEnd();
                // 新增状态下，且没有添加文件，提示警告信息
                $.messager.alert('错误', '上传文档不可为空，请选择','error', function() {
                    $("#filScwd").next().children().focus();
                });
            }
        }
    });
    
    // 文档操作取消按钮
    $("#lbtnWdqdCancel").click(function(e) {
        e.preventDefault();
        $("#divWdqdWindow").window('close');
    });

});

/**
* 新增or编辑页面初始化
*/
var fileup = undefined;
function wdqd_reload(cztype, dgid, rowindex) {
    // 取消行选中
    var event = event || window.event;
    event.stopPropagation();
    // 根据操作类型不同做出不同操作
    if (cztype == 'add') {
        newWindow($("#divWdqdWindow"), '添加文档', 500, 220);
        // 文档列别默认选择第一个
        if( $("#selWdlb").combobox("getData").length > 0 ){
            $("#selWdlb").combobox('select', $("#selWdlb").combobox("getData")[0].value);
        }
        // 清空修改文档清单id
        $("#updid").val('');
        // 清空上传文档内容
        $("#filScwd").next().children('input.textbox-text').val('');
    } else if (cztype == 'update') {
        // 打开编辑界面
        newWindow($("#divWdqdWindow"), '上传文档', 500, 220);
        // 初始化页面数据
        var d = $('#' + dgid).datagrid('getData').rows[rowindex];
        // 默认文档类别
        if( $("#selWdlb").combobox("getData").length > 0 ){
            $("#selWdlb").combobox('select', d.wdlb);
        }
        // 赋值修改文档清单id
        $("#updid").val(d.id);
        // 赋值上传文档内容
        $("#filScwd").next().children('input.textbox-text').val(d.wdmc);
    }

    // 文件上传 - 在newWindow后
    fileup = fileUpload({
        id: 'filScwd',
        progressbar: 'scjd',
        url: '/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_add_view',
        submit: function(data) {
            // 提交前 额外的参数
            // 获取操作文档清单id（存在则为编辑，不存在则为新增）
            var wdqdid = $("#updid").val();
            var ywid = $("#ywid").val();
            var wdlb = $('#selWdlb').combobox('getValue');
            // 校验文档类别
            if( wdlb == '' ){
                ajaxLoadEnd();
                $.messager.alert('错误', '文档类别不可为空，请选择', 'error');
                return false;
            }
            if (wdqdid != '') {
                //编辑
                fileup.setUrl("/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_edit_view");
            } else {
                fileup.setUrl("/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_add_view");
            }
            // 组织上传携带的参数
            data.formData = {
                'ywid': ywid,
                'wdqdid': wdqdid,
                'wdlb': wdlb
            };
        },
        success: function(data) {
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data.result, "dgWdqdlb", "divWdqdWindow");
        },
        error: function(data) {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('警告', '文件上传失败，可能原因：<br />1.网络不稳定或太慢，请检查网络，稍后重试<br />2.文件上传异常，请与管理员联系', 'warning');
        }
    });
    // 重新初始化tabindex
    $('#wdqdform').tabSort();
}

/**
* 文档上传提交
*/
function reload_sub() {

    // 获取操作文档清单id（存在则为编辑，不存在则为新增）
    var wdqdid = $("#updid").val();
    var ywid = $("#ywid").val();

    var url = "/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_edit_view";
    var msg = "修改文档失败，请稍后再试";

    // 提交表单
    $('#divWdqdWindow').find('form').form('submit', {
        url: url,
        queryParams: {
            'ywid': ywid,
            'wdqdid': wdqdid
        },
        onSubmit: function() {
            var wdlb = $('#selWdlb').combobox('getValue');
            // 校验文档类别
            if( wdlb == '' ){
                ajaxLoadEnd();
                $.messager.alert('错误', '文档类别不可为空，请选择', 'error');
                return false;
            }
            return true;
        },
        success: function(data) {
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "dgWdqdlb", "divWdqdWindow");
        },
        error: function() {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
* 删除文档
*/
function wdqd_remove(dgid, rowindex) {
    // 取消行选择
    var event = event || window.event;
    event.stopPropagation();
    $.messager.confirm('确认', '文档删除后将不可恢复，您确定要删除吗？', function(r) {
        if (r) {
            ajaxLoading();
            var d = $('#' + dgid).datagrid('getData').rows[rowindex];
            //发送删除请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_del_view",
                data: {
                    'wdqdid': d.id,
                    'wdmc': d.wdmc
                },
                success: function(data) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    afterAjax(data, dgid, "");
                },
                error: function() {
                    // 取消遮罩
                    ajaxLoadEnd();
                    errorAjax();
                }
            });
        }
    });
}

/**
* 文档下载
*/
function wdqd_down(dgid, downtype, rowindex) {
    // 取消行选择
    var event = event || window.event;
    event.stopPropagation();
    // 下载类型:downtype（1：批量，2：单个）
    // 下载文档清档id集合
    var ids = new Array();
    var downUrl = undefined;
    //判断是否是批量下载
    if (downtype == '1') {
        if (!checkSelected(dgid)) {
            return;
        }
        // 当前选中的记录
        var checkedItems = $('#' + dgid).datagrid('getChecked');
        $(checkedItems).each(function(index, item) {
            ids.push(item['id']);
        });
    } else {
        var d = $('#' + dgid).datagrid('getData').rows[rowindex];
        ids.push(d.id);
    }
    //发送下载请求
    var ywid = $("#ywid").val();

    downUrl = "/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/data_down_view?wdqdidstr=" + ids.join(",") + "&ywid=" + ywid + "&downtype=" + downtype;
    ajaxLoading();

    // jquery down
    $.fileDownload(downUrl)
        .done(function () {
            console.log('File download a success!');
            ajaxLoadEnd();
        })
        .fail(function () {
            console.log('File download failed!');
            $.messager.alert('错误', '下载失败！', 'error');
            ajaxLoadEnd();
        });

    // window.location.href = "/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_data_down?wdqdidstr=" + ids.join(",") + "&ywid=" + ywid;

}

/**
* 校验提交信息
*/
function checkFilename( fname ){
    // 判断文件长度( 不得超过五十 )
    if( fname != '' && fname != undefined && fname.length > 50 ){
        // 取消遮罩
        ajaxLoadEnd();
        $.messager.alert('错误', '文档名称异常，长度不可超过50，请重新选择', 'error');
        return false;
    }
    // 校验文档扩展名
    var ext_arr = ['xls', 'xlsx', 'doc', 'docx', 'zip', 'rar'];
    if (fname != '' && fname != undefined) {
        var fname_arr = fname.split('.');
        if (fname_arr.length <= 1 || $.inArray(fname_arr[fname_arr.length - 1].toLowerCase(), ext_arr) == -1) {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('错误', '只允许上传['+ext_arr.join(',')+']类型文档，请重新选择', 'error');
            return false;
        }
    }
    return true;
}
