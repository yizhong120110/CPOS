$(document).ready(function() {
    
    // 渲染表格
    $('#dgYwlb').datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "get",
        url: "/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/data_view",
        remoteSort: false,
        frozenColumns: [[
            { field: 'ck', checkbox: true }
        ]],
        columns: [[
            { field: 'id', title: '编号', hidden:true },
            { field: 'ywbm', title: '业务简称', width: 10 },
            { field: 'ywmc', title: '业务名称', width: 20, formatter: function(value,row,index){
                if (row.ywbm.toUpperCase() == 'BEAITX') {
                    return value
                } else {
                    return '<a href="javascript:;" onclick="ywxx_ck(event,\''+ value +'\', \''+ row.id +'\');" >'+value+'</a>';
                }
            } },
            { field: 'cjr', title: '创建人', width: 4 },
            { field: 'cjsj', title: '创建时间', width: 12, align:'center' },
            { field: 'drcs', title: '导入次数', width: 6, halign: 'center', align:'right', formatter: function(value,row,index){
                return accounting.formatNumber(value);
            } },
            { field: 'jysl', title: '交易数量', width: 6, halign: 'center', align:'right', formatter: function(value,row,index){
                return accounting.formatNumber(value);
            } },
            { field: 'operator', title: '操作', width: 8, formatter: function(value,row,index){
                if (row.ywbm.toUpperCase() == 'BEAITX') {
                    return ''
                } else {
                    return '<a href="javascript:;" onclick="dc_tab(event,\''+row.ywmc+'\',\''+row.id+'\')">导出</a> '+
                        '<a href="javascript:;" onclick="dr_tab(event,\''+row.ywmc+'\',\''+row.id+'\')">导入</a> ' +
                        '<a href="javascript:;" onclick="open_bqxxck(event,\''+row.ywmc+'\',\''+row.id+'\');" >历史</a>'+
                        '<a href="javascript:;" onclick="yw_dm_dc(event,\''+row.ywmc+'\',\''+row.id+'\');" > 代码导出</a>';
                }
            } }
        ]],
        toolbar : [ {
            iconCls : 'icon-add',
            text : '新增',
            handler : function() {
                // 新增
                add_yw();
            }
        }, {
            iconCls : 'icon-remove',
            text : '删除',
            handler : function() {
                if(!checkSelected("dgYwlb")) {
                    return;
                }
                $.messager.confirm("确认", '所选业务及其下的所有信息都将被删除且不可恢复，您确定要删除吗？', function (r) {
                    if (r) {
                        // 调用删除方法
                        removechecked();
                    }
                });
            }
        },{
            iconCls : 'icon-down',
            text : '导入新业务',
            handler : function() {
                // 新增
                dr_tab(event,'','-1');
            }
        }],
        onLoadSuccess: function(data){ // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断业务编码为BEAITX的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据业务编码让某些行不可选
                    if (data.rows[i].ywbm.toUpperCase() == 'BEAITX') {
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
                    $('#dgYwlb').datagrid('unselectRow', index - 1);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('.datagrid-cell-check input:enabled').length == $('#dgYwlb').datagrid('getChecked').length && $('#dgYwlb').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgYwlb').datagrid('unselectRow', index - 1);
                }
            });
            // 全选复选框置为勾选状态
            $('.datagrid-header-check input').get(0).checked = true;
        }
    });
    
    // 最大值限制
    $("#txtYwbm").next().children().attr("maxlength","10");
    $("#txtYwmc").next().children().attr("maxlength","50");
    $("#txtYwms").next().children().attr("maxlength","150");
    
    $("#lbtnYwSubmit").click(function(e){
        e.preventDefault();
        e.stopImmediatePropagation();
        // 添加遮罩
        ajaxLoading();
        $("#divYwWindow").find('form').form('submit', {
            url: '/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/data_add_view',
            onSubmit: function(param){
                var ywbm = $("#txtYwbm").textbox("getValue");
                var ywmc = $("#txtYwmc").textbox("getValue");
                var ywms = $("#txtYwms").textbox("getValue");
                if (ywbm=="") {
                    $.messager.alert('错误','业务简称不可为空，请输入','error', function(){
                        $("#txtYwbm").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (ywbm.trim().toUpperCase() == 'BEAITX') {
                    $.messager.alert('错误','业务简称不可为BEAITX，请重新输入','error', function(){
                        $("#txtYwbm").next().children().select();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkBm(ywbm, '业务简称', 'txtYwbm')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (ywmc=="") {
                    $.messager.alert('错误','业务名称不可为空，请输入','error', function(){
                        $("#txtYwmc").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if (!checkMc(ywmc, '业务名称', 'txtYwmc')) {
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                return true;
            },
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "dgYwlb", "divYwWindow");
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
    
    $("#lbtnYwCancel").click(function (e){
        e.preventDefault();
        e.stopImmediatePropagation();
        $("#divYwWindow").window('close');
    });
});

//交易信息查看
function ywxx_ck(event,value, id) {
    // 取消行选中
    event.stopPropagation();
    var title = '业务详情查看';
    if ( value != '' )
        title = value + '_业务详情';
    var url = "/oa/kf_ywgl/index?ywid="+id;
    newTab(title, url);
}

function add_yw(){
    // 增加窗体
    newWindow($("#divYwWindow"),'新增业务',450,255);

    // form tab排序
    $("#divYwWindow").children('form').tabSort();
};

/**
*批量删除
*/
function removechecked(){
    // 添加遮罩
    ajaxLoading();
    var checkedItems = $('#dgYwlb').datagrid('getChecked');
    var ywids = new Array();
    $(checkedItems).each(function(index, item){
        ywids.push(item["id"]);
    });
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/data_del_view",
        data: {"ywids":ywids.join(",")},
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            if (data.msg.indexOf("业务表") > 0 || data.msg.indexOf("引用") > 0) {
                $.messager.alert('提示', '<pre id="msgPre">'+data.msg+'</pre>', 'info');
                // 根据提示信息的长度来确定当前提示框的高度
                if ( data.msg.length >=0 && data.msg.length <= 20 ) {
                    $('#msgPre').css({'height': '15px'});
                } else if ( data.msg.length >=20 && data.msg.length <= 40 ){
                    $('#msgPre').css({'height': '30px'});
                } else if ( data.msg.length >=40 && data.msg.length <= 60 ){
                    $('#msgPre').css({'height': '45px'});
                } else if ( data.msg.length >=60 && data.msg.length <= 80 ){
                    $('#msgPre').css({'height': '60px'});
                } else {
                    $('#msgPre').css({'height': '75px'});
                };
                $('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '285px');
                var msgWin = $('#msgPre').parents('.messager-window');
                msgWin.css({'width': '350px', 'left': ($(window).width()-400)*0.5});
                msgWin.find('.window-header').css('width', '');
                msgWin.find('.messager-body').css('width', '');
                // 去掉因返回提示信息过长而出现的白块区域
                msgWin.siblings('.window-shadow').css({'height':'0px'});
                $('#dgYwlb').datagrid('reload');
            } else {
                afterAjax(data, "dgYwlb", "");
            }
        },
        error: function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/*
*业务导出
*/
function dc_tab(event, ywmc, ywid){
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/data_before_export_view",
        data: {"ywid": ywid},
        success: function(data){
            //说明可以导出左侧及右侧的数据
            if(data.state){
                var title = '业务导出';
                if (ywmc != '')
                    title = ywmc + '_业务导出';
                var url = "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/index_view?ywid="+ywid+'&dclx='+'yw';
                newTab(title, url);
            }else{
                afterAjax(data, "", "");
            }
        },
        error: function(){
            errorAjax();
        }
    });
}
/*
*业务导入
*/
function dr_tab(event,ywmc,ywid){
    event.stopPropagation();
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/data_before_export_view",
        data: {"ywid": ywid},
        success: function(data){
            //说明可以导出左侧及右侧的数据
            if(data.state){
                var title = '业务导入';
                if (ywmc != '')
                    title = ywmc + '_业务导入';
                var url = "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/index_view?ywid="+ywid+'&drlx='+'yw';
                newTab(title, url);
            }else{
                afterAjax(data, "", "");
            }
        },
        error: function(){
            errorAjax();
        }
    });
}
/*
*导入业务下拉框加载成功后，向表格中新增一条数据
*/
function onLoadSuccess(){
    $('#selYwdr').combogrid('grid').datagrid('insertRow',{
            index:0,
            row:{id:'-1',ywmc:'导入新业务'}
    });
    $('#selYwdr').combogrid('setValue','')
}
/*
*业务导入历史
*/
function open_bqxxck(event, ywmc, ywid){
    event.stopPropagation();
    var title = '导入历史';
    if (ywmc != '')
        title = ywmc + '_导入历史';
    var url = "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/index_view?ss_idlb="+ywid+'&nrlx='+'yw';
    newTab(title, url);
}

/*
*业务代码导出
*/
function yw_dm_dc(event, ywmc, ywid){
    event.stopPropagation();
    var to_path = 'window.location.href="/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/index_view?ywid=' + ywid + '"'
    dm_down( 'dgYwlb', 'yw', ywid, to_path );
}