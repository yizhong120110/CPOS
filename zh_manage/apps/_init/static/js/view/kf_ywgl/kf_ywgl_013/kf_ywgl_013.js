$(document).ready(function() {
    
    $("#tableCsal").datagrid({
        "title": "自动化测试列表",
        "toolbar" : "#tb",
        "url":""
    });
    // 渲染树形结构
    $('#treeCsal').tree({
        method: "get",
        lines: true,
        url: '/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_view/data_view?ywid=' + $("#txtYwid").val(),
        checkbox: true,
        animate: true,
        onCheck: treeOnCheck,
        onClick: treeOnClick,
        loadFilter : function(data){
          if (data){
            return data[0];
          }
        }
    });

    // 渲染表格
    $('#tableCsal').datagrid({
        title: "业务自动化测试信息",
        nowrap : true,
        fit : true,
        singleSelect: true,
        method: "get",
        idField:'ID',
        url: '/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_view/data_view?ywid=' + $("#txtYwid").val(),
        columns: [[
            { field: 'id', title: 'ID', width: '1%', hidden: true },
            { field: 'pid', title: 'pid', width: '1%', hidden: true },
            { field: 'lx', title: '类型', width: '25%' },
            { field: 'text', title: '名称', width: '30%', formatter: function(value,rowData,rowIndex) {
                return '<a href="javascript:;" onclick="javascript:jdcsal(\''+rowData.id+'\',\''+value+'\',\'' + rowData.lx +'\',\'' + rowData.text +'\');">'+value+'</a>';
            } },
            { field: 'alsl', title: '测试案例数量', align: "right", width: '25%' },
            { field: 'dycs', title: '引用次数', align: "right", width: '20%', formatter: function(value,rowData,rowIndex) {
                if (value > 0) {
                    return '<a href="javascript:;" onclick="javascript:yycs(\'' + rowData.id + '\');">'+value+'</a>';
                } else {
                    return value;
                }
            } }
        ]],
        loadFilter : function(data){
          if (data){
            return data[1];
          }
        }
    });
    
    // 绑定增加/修改弹出框中的取消按钮
    $('#window_cancel').click(function(e){
        e.preventDefault();
        $('#bean_window').window('close');
    });
    
    // 关联的按钮的点击事件
    $('#gljy').click(function(){
        var check = $('#gljy')[0].checked;
        $.each($('#treeCsal').tree('getChecked'),function(index,node){
            treeOnCheck(node, check);
        })
    })
});


/* 创建新的窗体
 * @param beanWindow 窗体对象
 * @param title 窗体的标题
 * @param width 窗体的宽度
 * @param height 窗体的高度
 */
function newWindow(beanWindow, title, width, height) {
    // 清空window中的值
    clearWindow(beanWindow);
    // 创建window
    var top = ($(window).height()-height)*0.3;
    var left = ($(window).width()-width)*0.4;
    beanWindow.window({
        title : title,
        width : width,
        height : height,
        top: top < 0 ? 0 : top,
        left: left < 0 ? 0 : left,
        closed : false,
        cache : false,
        modal : true
    });
};

/**
 * 创建新的Tab
 * @param title
 * @param href
 */
function newTab(title, href) {
    var parentMain = window.parent.parent.document.getElementById("pnlMain");
    var $main = top.$(parentMain);
    if ($main.tabs('exists', title)) {
        $main.tabs('select', title);
    } else {
        var content = '<iframe scrolling="auto" frameborder="0" src="'+href+'" style="width:100%;height:100%;"></iframe>';
        $main.tabs('add',{
            title:title,
            content:content,
            closable:true
        });
    }
}

/**
 * 清空window中input中的数据
 * @param beanWindow 要清理的window对象
 */
function clearWindow(beanWindow){
    // 清空输入框中的值
    beanWindow.form('clear');
    
};

/**
 * Tab控制
 * @param index
 * @param value
 * @param lx
 */
function jdcsal(id, value, lx, text) {
    var event = event || window.event;
    event.stopPropagation();    
    if( lx == '交易' ){
        newTab(value+"_测试案例查看", "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/index_view?lx=" + encodeURI('jy') + "&csaldyssid=" + encodeURI(id) + "&text=" + encodeURI(text) + "&lxmc=" + encodeURI("交易"));
    }
    if( lx == "子流程" ){
        newTab(value+"_测试案例查看", "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/index_view?lx=" + encodeURI('zlc') + "&csaldyssid=" + encodeURI(id) + "&text=" + encodeURI(text) + "&lxmc=" + encodeURI("子流程"));
    }
    if( lx == "节点" ){
        newTab(value+"_测试案例查看", "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/index_view?lx=" + encodeURI('jd') + "&csaldyssid=" + encodeURI(id) + "&text=" + encodeURI(text) + "&lxmc=" + encodeURI("节点"));
    }
}

/**
 * 弹出自动化测试窗口
 * @returns {boolean}
 */
function auto_test(){
    //校验是否有选择节点
    // 获取表格中的信息ID发送到后台
    var rowsData = $('#tableCsal').datagrid("getData").rows;
    if ( rowsData.length < 1 ){
        $.messager.alert('提示', '请选择需要测试的测试案例!', 'info');
        return false;
    }
    var csal='';
    for(var i = 0,len=rowsData.length; i< len; i++){
        csal+= rowsData[i].id+",";
    }
    $("#zdhcsal_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/index_view?csal="+csal);
    // 打开自动化测试的结果
    newWindow($("#bean_window"),'自动化测试',600,360);
}

/**
 * 加载自动化测试列表
 * @param node
 * @param checked
 */
function treeOnCheck(node, checked) {
    $("#tb_form").tabSort();
    $($('#treeCsal').tree('getChecked', ['checked','unchecked'])).each(function(index,item){

        if ($('#treeCsal').tree('isLeaf', item.target) && item.id != node.id && node.jd != undefined && node.jd.indexOf((item.id + ','))>=0) {
            if (checked && $('#gljy')[0].checked) {
                $('#treeCsal').tree('check', item.target);
            } else {
                $('#treeCsal').tree('uncheck', item.target);
            }
        }
    });
    
    var tableCsalItems = $('#tableCsal').datagrid('getData').rows;
    //倒序删除，防止index出错
    $($(tableCsalItems).get().reverse()).each(function(index, item){
        $('#tableCsal').datagrid('deleteRow', $('#tableCsal').datagrid('getRowIndex', item));
    });
    var checkedItems = $('#treeCsal').tree('getChecked');
    $.each(checkedItems, function(index, item){
        if (item.alsl > -1){
            if($('#treeCsal').tree('isLeaf',item.target)) {
                $('#tableCsal').datagrid('appendRow',{
                    id: item.id,
                    lx: item.lx,
                    text: item.text,
                    alsl: item.alsl,
                    dycs: item.dycs
                });
            }
        }
    });
}

/**
 * 树形结构点击事件
 * @param node
 */
function treeOnClick(node) {
    var checked = false;
    var checkedItems = $('#treeCsal').tree('getChecked');
    $.each(checkedItems, function(index, item){
        if (node.id == item.id) {
            checked = true;
        }
    });
    if (checked) {
        $('#treeCsal').tree('uncheck', node.target);
    } else {
        $('#treeCsal').tree('check', node.target);
    }
}

/**
 * 引用次数交易列表查看
 * @param ID
 * @param mc
 */
function yycs(jdid) {
    var event = event || window.event;
    event.stopPropagation();    
    newWindow($("#yycs_window"), "引用次数查看", 800, 420);
    $("#yycs_window iframe")[0].src = "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/yycs_index_view?jdid=" + jdid;
}

/**
 * 弹出自动化测试日志查看
 * @returns {boolean}
 */
function view_rz(csalid,pc,zxjg,jgsm,demoid,ssid,lb,event){
    if(event != undefined && event != 'undefined'){
        event.stopPropagation();
    }
    if(lb=='1'||lb==1){
        lb = 'lc'
        $("#rzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx="+lb+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm);//lx交易是：lc，子流程：zlc
        newWindow($("#rzck_window"),'交易日志查看',860,500);
    }else if(lb=='2'||lb==2){
        lb='zlc'
        $("#rzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/index_view?lx="+lb+"&id="+ssid+"&csalid="+csalid+"&pc="+pc+"&zxjg="+zxjg+"&jgsm="+jgsm);//lx交易是：lc，子流程：zlc
        newWindow($("#rzck_window"),'交易日志查看',860,500);
    }else if(lb=='3'||lb==3){
        lb='jd'
        $("#jdrzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/csalxx_view?jdcsalid="+csalid+"&pc="+pc+"&demoid="+demoid);
        // 打开自动化测试的结果
        newWindow($("#jdrzck_window"),'日志查看',700,420);
        getZxjgms(csalid,pc);
    }
}
// 获取执行结果和结果描述
function getZxjgms(csalid,pc){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/zxjgms_view",
        data: {"jdcsalid": csalid,"pc":pc},
        success: function(data){
            if (data.zxjg == '0' || data.zxjg == 0){
                data.zxjg = "失败";
            }else{
                data.zxjg = "成功";
            }
            $('#zxjg').html(data.zxjg);
            $('#jgsm').html(data.jgsm);
        },
        error: function() {
            errorAjax();
        }
    });
}
//function view_rz(csalid,pc,zxjg,jgsm,demoid,ssid,lb){
//    $("#rzck_iframe").attr("src","/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/csal_jbxx_view?csalid="+csalid+"&lx="+lb);
//    // 打开自动化测试的结果
//    newWindow($("#rzck_window"),'日志查看',700,420);
//}