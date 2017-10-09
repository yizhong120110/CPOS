$(document).ready(function() {
    $("#tbsLeft").tabs({
        onSelect: function(title, index) {
            $("#tbsRight").tabs('select', index);
        }
    });

    $("#tbsRight").tabs({
        onSelect: function(title, index) {
            $("#tbsLeft").tabs('select', index);
        }
    });
    // 分析规则参数
    $('#dgYzjycsLeft').datagrid({
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
            }, {
                field: 'ywmc',
                title: '所属业务',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ywmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'kgl',
                title: '开关量',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('kgl',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'csz2',
                title: '参数值2',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz2',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csms',row);
                }
            }]
        ],
        data: leftYzjycspzRs
    });
    // 分析规则参数
    $('#dgYzjycsRight').datagrid({
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
            }, {
                field: 'ywmc',
                title: '所属业务',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ywmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'kgl',
                title: '开关量',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('kgl',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'csz2',
                title: '参数值2',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz2',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csms',row);
                }
            }]
        ],
        data: rightYzjycspzRs
    });
    // 监听左侧grid body滚动
    $('#dgYzjycsLeft').datagrid('getBody').scroll(function(e){
        $("#dgYzjycsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgYzjycsRight').datagrid('getBody').scroll(function(e){
        $("#dgYzjycsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});
