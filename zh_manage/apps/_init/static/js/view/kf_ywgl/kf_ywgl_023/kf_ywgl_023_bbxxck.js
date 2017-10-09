var bblx;
$(document).ready(function() {
    bblx = $('#txtLx').val();
    $('#datagrid_bbxxck').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        pagination : true,
        fitColumns : true,
        pageSize: 50,
        method: "get",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url:'/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_data_view',
        queryParams:{  
            lx:$('#txtLx').val(),
            id:$('#txtId').val(),
            tjrq:$("#seaTjrq").datebox("getValue"),
            tjms:$("#txtTjms").textbox("getValue"),
            bbh:$("#txtBbh").textbox("getValue")
        },
        frozenColumns: [
            [{
                field: 'ck',
                checkbox: true
            }]
        ],
        columns: [
            [{
                field: 'mkmc',
                title: '模块名称',
                width: 100
            }, {
                field: 'bbh',
                title: '版本号',
                width: 50,
                align:'right', 
                halign:'center', 
                formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;
                    }else{
                        return value;
                    }
                }
            }, {
                field: 'tjms',
                title: '提交描述',
                width: 120
            }, {
                field: 'tjr',
                title: '提交人',
                width: 60
            }, {
                field: 'tjsj',
                title: '提交时间',
                width: 60,
                align:'center'
            }, {
                field: 'cz',
                title: '操作',
                width: 60,
                formatter: function(value, rowData, rowIndex) {
                    return '<a href="javascript:;" onclick="javascript:viewjyxx(\'' + rowData.bbh + '\');">查看</a>';
                }
            }]
        ],
        toolbar: "#tb"
    });
    // 文本框底部汉字描述
    $('#txtBbh').textbox('textbox').attr('placeholder', 'bbh1,bbh2,bbh3...');
    // 主页面 form tab排序
    $("#fmSearch").tabSort();
});
/**
* 条件查询
* event：时间对象
*/
function doSearch(event){
    // 取消默认提交事件
    if( event != '' && event != 'undefined' ){
        event.preventDefault();
    }
    // 提交日期
    var seaTjrq = $("#seaTjrq").datebox("getValue");
    // 提交描述
    var txtTjms = $("#txtTjms").textbox("getValue");
    // 版本号
    var txtBbh = $("#txtBbh").textbox("getValue");
    var mode_m = /^[0-9]*$/;
    var mode_n = /^[,]+$/
    for (var i = 0; i < txtBbh.length; i++) {
        if( !mode_m.test(txtBbh[i]) && !mode_n.test(txtBbh[i]) ){
            $.messager.alert('提示','查询区域版本号输入信息有误，请重新输入！','info');
            return false;
        }
    };
    // 类型
    var bb_id = $('#txtId').val();
    // ID
    var bb_lx = $('#txtLx').val();
    // 根据条件查询管理对象
    $("#datagrid_bbxxck").datagrid('load',{
        lx:bb_lx,
        id:bb_id,
        tjrq: seaTjrq,
        tjms: txtTjms,
        bbh: txtBbh,
    });
}
/**
 *版本对比
 */
function bbdb() {
    var id = $('#txtId').val();
    var jdlx = $('#txtJdlx').val();
    var checkedItems = $('#datagrid_bbxxck').datagrid('getChecked');
    if (checkedItems.length == 2) {
        var bbh1 = checkedItems[0].bbh;
        var bbh2 = checkedItems[1].bbh;
        var data = '?lx='+bblx+'&id='+id+'&bbh1='+bbh1+'&bbh2='+bbh2+"&jdlx="+jdlx;
        var url = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbdb_data_view';
        if (bblx == 'jy') {
            newTab(checkedItems[0].mkmc + '_版本对比', url+data);
        } else if (bblx == 'zlc') {
            newTab(checkedItems[0].mkmc + '_版本对比', url+data);
        } else if (bblx == 'gghs') {
            newTab(checkedItems[0].mkmc + '_版本对比', url+data);
        } else if (bblx == 'jd') {
            newTab(checkedItems[0].mkmc + '_版本对比', url+data);
        } else if (bblx == 'sjk') {
            newTab(checkedItems[0].mkmc + '_版本对比', url+data);
        }
    } else {
        $.messager.alert('警告', '需要选择两个版本进行对比', 'warning');
    }
}

/**
 *当前版本对比
 */
function dqbbdb() {
    var id = $('#txtId').val();
    var jdlx = $('#txtJdlx').val();
    var checkedItems = $('#datagrid_bbxxck').datagrid('getChecked');
    if (checkedItems.length == 1) {
        var bbh1 = checkedItems[0].bbh;
        var data = '?lx='+bblx+'&id='+id+'&bbh1='+bbh1+'&type=bd'+'&jdlx='+jdlx;
        var url = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbdb_data_view';
        if (bblx == 'jy') {
            newTab(checkedItems[0].mkmc + '_本地版本对比', url+data);
        } else if (bblx == 'zlc') {
            newTab(checkedItems[0].mkmc + '_本地版本对比', url+data);
        } else if (bblx == 'gghs') {
            newTab(checkedItems[0].mkmc + '_本地版本对比', url+data);
        } else if (bblx == 'jd') {
            newTab(checkedItems[0].mkmc + '_本地版本对比', url+data);
        } else if (bblx == 'sjk') {
            newTab(checkedItems[0].mkmc + '_本地版本对比', url+data);
        }
    } else {
        $.messager.alert('警告', '需要选择一个版本进行对比', 'warning');
    }
}

function viewjyxx(bbh) {
    var event = event || window.event;
    event.stopPropagation();    
    var id = $('#txtId').val();
    var jdlx = $('#txtJdlx').val();
    var data = '?lx='+bblx+'&id='+id+'&bbh='+bbh+'&jdlx='+jdlx;
    var ifm = $('#bean_window_bbck').children('iframe').get(0);
    var url = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxx_data_view';
    if (bblx == 'jy') {
        url = url + data;
    } else if (bblx == 'zlc') {
        url = url + data;
    } else if (bblx == 'gghs') {
        url = url + data;
    } else if (bblx == 'jd') {
        url = url + data;
    } else if (bblx == 'sjk') {
        url = url + data;
    }
    ifm.src = url;
    newWindow($('#bean_window_bbck'), '版本查看', 900, 480);
}
