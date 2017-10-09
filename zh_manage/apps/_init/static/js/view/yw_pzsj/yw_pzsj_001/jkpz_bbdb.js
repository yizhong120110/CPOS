$(document).ready(function() {
    $("#tbsLeft").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tbsRight").tabs('select', index);
        }
    });

    $("#tbsRight").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tbsLeft").tabs('select', index);
        }
    });
    //节点基本信息
    $('#dgJbxxLeft').datagrid({
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
                width: 50,
                hidden:true
            },{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = leftJcpzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftJcpzRs.leftJkdx
    });
    $('#dgJbxxRight').datagrid({
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
                width: 50,
                hidden:true
            },{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = rightJcpzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightJcpzRs.rightJkdx
    });
    // 分析规则参数
    $('#dgFxgzcsLeft').datagrid({
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
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }]
        ],
        data: leftFxgzcsRs
    });
    // 分析规则参数
    $('#dgFxgzcsRight').datagrid({
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
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }]
        ],
        data: rightFxgzcsRs
    });
    
    // 响应动作
    $('#dgJcpzXydzLeft').datagrid({
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
                field: 'fxjgcf',
                title: '分析结果触发',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('fxjgcf',row);
                }
            }, {
                field: 'hsmc',
                title: '动作函数名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('hsmc',row);
                }
            }, {
                field: 'zwmc',
                title: '动作名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zwmc',row);
                }
            }, {
                field: 'fqfs',
                title: '发起方式',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('fqfs',row);
                }
            }, {
                field: 'jhsj',
                title: '动作执行时间',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('jhsj',row);
                }
            }, {
                field: 'dzzxzj',
                title: '动作执行主机',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('dzzxzj',row);
                }
            }]
        ],
        data: leftJcpzXydzRs
    });
    // 响应动作
    $('#dgJcpzXydzRight').datagrid({
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
                field: 'fxjgcf',
                title: '分析结果触发',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('fxjgcf',row);
                }
            }, {
                field: 'hsmc',
                title: '动作函数名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('hsmc',row);
                }
            }, {
                field: 'zwmc',
                title: '动作名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zwmc',row);
                }
            }, {
                field: 'fqfs',
                title: '发起方式',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('fqfs',row);
                }
            }, {
                field: 'jhsj',
                title: '动作执行时间',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('jhsj',row);
                }
            }, {
                field: 'dzzxzj',
                title: '动作执行主机',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('dzzxzj',row);
                }
            }]
        ],
        data: rightJcpzXydzRs
    });
    
    // 响应动作参数
    $('#dgJcpzXydzcsLeft').datagrid({
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
                field: 'hsmc',
                title: '动作函数名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('hsmc',row);
                }
            }, {
                field: 'zwmc',
                title: '动作名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zwmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }]
        ],
        data: leftJkpzXydzcsRs
    });
    
    // 响应动作参数
    $('#dgJcpzXydzcsRight').datagrid({
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
                field: 'hsmc',
                title: '动作函数名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('hsmc',row);
                }
            }, {
                field: 'zwmc',
                title: '动作名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zwmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }]
        ],
        data: rightJkpzXydzcsRs
    });
    
    // 监听左侧grid body滚动
    $('#dgJbxxLeft').datagrid('getBody').scroll(function(e){
        $("#dgJbxxRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJbxxRight').datagrid('getBody').scroll(function(e){
        $("#dgJbxxLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    
    // 监听左侧grid body滚动
    $('#dgFxgzcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgFxgzcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgFxgzcsRight').datagrid('getBody').scroll(function(e){
        $("#dgFxgzcsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    
    // 监听左侧grid body滚动
    $('#dgJcpzXydzLeft').datagrid('getBody').scroll(function(e){
        $("#dgJcpzXydzRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJcpzXydzRight').datagrid('getBody').scroll(function(e){
        $("#dgJcpzXydzLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    
    // 监听左侧grid body滚动
    $('#dgJcpzXydzcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgJcpzXydzcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJcpzXydzcsRight').datagrid('getBody').scroll(function(e){
        $("#dgJcpzXydzcsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*动态展示、隐藏内容
*/
function regionSH(title) {
    if (title == '基本信息') {
        $('#divJbxx').show();
        $('#divFxgzcs').hide();
        $('#divJcpzXydz').hide();
        $('#divJcpzXydzcs').hide();
    } else if (title == '分析规则参数') {
        $('#divJbxx').hide();
        $('#divFxgzcs').show();
        $('#divJcpzXydz').hide();
        $('#divJcpzXydzcs').hide();
    } else if (title == "响应动作" ){
       $('#divJbxx').hide();
        $('#divFxgzcs').hide();
        $('#divJcpzXydz').show();
        $('#divJcpzXydzcs').hide();
    } else if (title == "响应动作参数" ){
        $('#divJbxx').hide();
        $('#divFxgzcs').hide();
        $('#divJcpzXydz').hide();
        $('#divJcpzXydzcs').show();
    }
}
