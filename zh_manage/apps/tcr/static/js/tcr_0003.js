/**
 * 页面ready方法
 */
$(function() {

    // 终端一览
    $("#dgZdxx").datagrid({
        nowrap : true,
        fit: true,
        rownumbers : true,
        pagination : true,
        pageSize : 50,
        fitColumns : true,
        method: "POST",
        url: "/tcr/oa/tcr_0003/tcr_0003_view/data_view",
        singleSelect: true,
        selectOnCheck: true, 
        checkOnSelect: true,
        remoteSort: false,
        frozenColumns: [
            [{field: 'select_box', checkbox: true}]
        ],
        columns: [[
            {field: 'tcrid', title: '终端号', width: 15, align: 'center' },
            {field: 'tcrname', title: '终端名称', width: 20 },
            {field: 'updtime', title: '更新时间', width: 18, align: 'center',
                formatter: function(value, rowData, rowIndex) {
                    var updtime = '';
                    if(value != '' && value != null) {
                        updtime = value.substring(0, 4) + '/';
                        updtime += value.substring(4, 6) + '/';
                        updtime += value.substring(6, 8) + ' ';
                        updtime += value.substring(8, 10) + ':';
                        updtime += value.substring(10, 12) + ' ';
                        updtime += value.substring(12, 14);
                    }
                    return updtime;
                }
            },
            {field: 'tcrstate', title: '终端状态',width: 10,
                formatter: function(value, rowData, rowIndex){
                    if(value == '1') {
                        return '<span class="colorGreen">正常</span>';
                    } else if(value == '2') {
                        return '<span class="colorRed">异常</span>';
                    } else {
                        return '未监控';
                    }
                }
            },
            {field: 'tcrstate_value', title: '终端状态值',hidden: true},
            {field: 'des',title: '终端状态描述',width: 50},
            {field: 'cz',title: '操作',width: 12, align: 'center', 
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if(rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:kcjk(' + rowIndex + ');">库存监控</a>';
                    }
                    return czStr;
                }
            }
        ]]
    });

    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
});

/**
* 表格查询
**/
function doSearch() {

    // 终端名称
    var tcrmc = $("#txtSearch_tcrname").textbox('getValue').trim();

    // 根据条件查询终端一览
    $("#dgZdxx").datagrid('load',{
        tcrmc: tcrmc
    });
}

//交易信息查看
function kcjk(rowIndex) {

    // 取消行选中
    event.stopPropagation();
    // 选中行数据
    var row = $('#dgZdxx').datagrid('getData').rows[rowIndex];
    var title = '库存监控_' + row.tcrname;
    
    // 终端状态
    if(row.tcrstate_value != '1' && row.tcrstate_value != '2') {
        $.messager.alert('提示','该终端未监控!','info');
        return;
    }

    var url = "/tcr/oa/tcr_0004/tcr_0004_view/index_view?tcrid="+row.tcrid;
    newTab(title, url);
}

