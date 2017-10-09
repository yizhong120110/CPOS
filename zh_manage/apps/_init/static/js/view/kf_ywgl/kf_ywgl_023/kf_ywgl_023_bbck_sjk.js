$(function() {
    var nro = ($('#txtBbxx').val() + '').replace(/None/gm, "''");
    nr = eval('(' + nro + ')');
    // 字段管理 
    $('#zdglt').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 50,
                hidden: true
            }, {
                field: 'zdmc',
                title: '字段名称',
                width: 120
            }, {
                field: 'zdms',
                title: '字段描述',
                width: 50
            }, {
                field: 'zdlx',
                title: '字段类型',
                width: 50
            }, {
                field: 'zdcd',
                title: '字段长度',
                width: 50
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50
            }, {
                field: 'iskey',
                title: '是否主键',
                width: 50
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50
            }]
        ],
        data: nr.gl_sjkzdb
    });
    // 索引管理  
    $('#syglt').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden: true
            }, {
                field: 'symc',
                title: '索引名称',
                width: 50
            }, {
                field: 'syzd',
                title: '索引字段',
                width: 50,
                styler: function(value, row, index) {
                    return 'word-break: break-word;';
                }
            }, {
                field: 'sylx',
                title: '索引类型',
                width: 50
            }, {
                field: 'sfwysy',
                title: '是否唯一索引',
                width: 50
            }]
        ],
        data: nr.gl_sjksy
    });
    // 约束管理 
    $('#ysglt').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 50,
                hidden: true
            }, {
                field: 'ysmc',
                title: '约束名称',
                width: 120
            }, {
                field: 'yszd',
                title: '约束字段',
                width: 280,
                styler: function(value, row, index) {
                    return 'word-break: break-word;';
                }
            }]
        ],
        data: nr.gl_sjkys
    });
});
