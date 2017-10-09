$(document).ready(function() {
    var leftRs = ($('#hidLeftRs').val()+'').replace(/None/gm,"''");
    var rightRs = ($('#hidRightRs').val()+'').replace(/None/gm,"''");
    leftRsObj = eval('(' + leftRs + ')');
    rightRsObj = eval('(' + rightRs + ')');
    $('#dgTxcsLeft').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return txcs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('zt',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "启用" : "禁用";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: leftRsObj.leftTxcs
    });
    $('#dgTxcsRight').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return txcs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return txcs('zt',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "启用" : "禁用";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: rightRsObj.rightTxcs
    });
    // 监听左侧grid body滚动
    $('#dgTxcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgTxcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgTxcsRight').datagrid('getBody').scroll(function(e){
        $("#dgTxcsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*判断通讯参数是否一致
*/
function txcs(field,row){
    if(row.diff == ''){
        return;
    }
    // 获取改行的id对应的列有无版本内容不一致情况
    difArray = row.diff.split(',');
    for(var i = 0; i < difArray.length; i++){
        var diffField = difArray[i];
        if(field == diffField ){
            return 'background-color:#ffee00;color:red;';
        }
    }
}
