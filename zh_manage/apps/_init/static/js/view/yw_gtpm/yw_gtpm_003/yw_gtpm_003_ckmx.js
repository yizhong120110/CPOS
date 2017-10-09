/**
* 阈值校验流水明细查看
*/
/**
 * Created by 成德功 on 2015/4/27.
 */
$(document).ready(function() {
    // 渲染表格
    var datagrid = $('#dgYzxylsCkmx').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        pagination: true,
        fitColumns: true,
        method: "post",
        pageSize:50,
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        remoteSort: false,
        url: "/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/data_mxck_view",
        queryParams: {
            wjid: wjid
        },
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [
            [{
                field: 'id',
                title: '明细id',
                hidden: true 
            }, 
            {
                field: 'ywlsh',
                title: '业务流水号',
                width: 100
            }, {
                field: 'wjm',
                title: '文件名称',
                width: 120,
                formatter: function(value, rowData, rowIndex){
                    return wjm;
                }
            }, {
                field: 'ywlx',
                title: '业务类型',
                width: 100,
                formatter: function(value, rowData, rowIndex){
                    return ywmc;
                }
            }, {
                field: 'sfzh',
                title: '三方账号',
                width: 100
            }, {
                field: 'kkje',
                title: '扣款金额',
                width: 100,
                align: 'right'
            }, {
                field: 'khmc',
                title: '客户名称',
                width: 100
            }, {
                field: 'zt',
                title: '状态',
                width: 100,
                formatter: function(value, rowData, rowIndex){
                    // 若状态为55[单笔异常]，则展示：可置为失败和置为批扣
                    // 若状态为00[准备批扣]，则展示：可置为失败
                    // 若状态为97[失败不再扣款]和98[失败不再校验]，则展示：可置为批扣
                    if(rowData.zt == '55'){
                        return '单笔阈值异常 ';
                    }
                    else if(rowData.zt == '97') {
                        return '失败不再扣款 ';
                    }
                    else if(rowData.zt == '98') {
                        return '失败不再校验 ';
                    }
                    else if(rowData.zt == '00'){
                        return '待扣款 ';
                    }
                }
            }, {
                field: 'cz',
                title: '备注',
                width: 80,
                formatter: function(value, rowData, rowIndex){
                    // 若状态为55[单笔异常]，则展示：可置为失败和置为批扣
                    // 若状态为00[准备批扣]，则展示：可置为失败
                    // 若状态为97[失败不再扣款]和98[失败不再校验]，则展示：可置为批扣
                    if(rowData.zt == '55'){
                        return '可置为失败和置为批扣 ';
                    }
                    else if(rowData.zt == '97'||rowData.zt == '98') {
                        return '可置为批扣 ';
                    }
                    else if(rowData.zt == '00'){
                        return '可置为失败 ';
                    }
                }
            }]
        ],
        toolbar: [{
            iconCls:'icon-edit',
            text: '批量置为失败',
            handler:function(){
                edit('zwsb');
            }
        },{
            iconCls:'icon-edit',
            text: '批量置为批扣',
            handler:function(){
                edit('zwpk');
            }
        }]
    });
    $("#selZt").combobox({
        data: zt,
        valueField: 'value',
        textField: 'text'
    });
    // 绑定查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });
    $('#yzjylsckmxForm').tabSort();
});

/**
* 条件查询
* event：时间对象
*/
function doSearch(){
    // 业务类型
    var ywlx = ''//$("#txtYwlx").textbox("getValue")
    // 三方账号
    var sfzh = $("#txtSfzh").textbox("getValue")
    // 客户名称
    var khmc = $("#txtKhmc").textbox("getValue")
    // 流水状态
    var lszt = $("#selZt").textbox("getValue")
    // 根据条件查询管理对象
    $("#dgYzxylsCkmx").datagrid('load',{
        wjid:wjid,
        ywlx: ywlx,
        sfzh: sfzh,
        khmc: khmc,
        zt: lszt
    });
}
/**
 * 置为批扣/置为失败
 */
function edit(flag) {
    if(!checkSelected("dgYzxylsCkmx")) {
        return; 
    }
    var rows = $('#dgYzxylsCkmx').datagrid('getSelections');
    var idArray = new Array();//创建存放id的数组
    var bz = false
    $.each(rows,function(n,row){
        var mx = {'id':row.id, 'ywlx':row.ywlx, 'kkje':row.kkje, 'zt':row.zt}
        idArray[n] = mx;
        if(flag=='zwsb'){
            if(row.zt=='97' || row.zt=='98'){
                bz=true;
            }
        }else{
            if(row.zt=='00'){
                bz=true;
            }
        }
    });
    if(bz){
        $.messager.alert('错误', '选择的明细中有不符合条件的，请查看每条明细后面的备注，再进行选择', 'error');
    }else{
        var tsxx = ''
        if(flag=='zwsb'){
            var tsxx='执行该操作后，该明细还会重新置为待扣款状态，等待阈值校验发起，您确定要执行吗？'
        }else{
            var tsxx='执行该操作后，直接导入到GTP流水中，等待GTP扣款，您确定要通过吗？'
        }
        $.messager.confirm('确认',tsxx, function(r){
                if(r){
                    // 添加遮罩
                    ajaxLoading();
                    $.ajax({
                    url:'/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/edit_view',
                    type : 'post',
                    dataType : 'json',
                    data : {
                        'mx' : JSON.stringify(idArray),
                        'flag': flag,
                        'wjid':wjid
                    },
                    success:function(data){
                        //执行请求后的方法
                        afterAjax(data, 'dgYzxylsCkmx','');
                        // 取消遮罩
                        ajaxLoadEnd();
                    },
                    error: function () {
                        errorAjax();
                        // 取消遮罩
                        ajaxLoadEnd();
                    }
                    });
                }
            })
    }
}
