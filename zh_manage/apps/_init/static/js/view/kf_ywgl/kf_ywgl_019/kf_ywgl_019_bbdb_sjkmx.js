$(document).ready(function() {
    var leftRs = ($('#hidLeftRs').val()+'').replace(/None/gm,"''");
    var rightRs = ($('#hidRightRs').val()+'').replace(/None/gm,"''");
    leftRsObj = eval('(' + leftRs + ')');
    rightRsObj = eval('(' + rightRs + ')');
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
    //数据表基本信息
    $('#dgSjbjbxxLeft').datagrid({
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
                    bzArray = leftRsObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftRsObj.leftSjbxx
    });

    $('#dgSjbjbxxRight').datagrid({
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
                    bzArray = rightRsObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightRsObj.rightSjbxx
    });
    //数据表字段
    $('#dgSjbzdLeft').datagrid({
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
                field: 'zdmc',
                title: '字段名称',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdmc',row);
                }
            }, {
                field: 'zdlx',
                title: '字段类型',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdlx',row);
                }
            }, {
                field: 'zdcd',
                title: '字段长度',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdcd',row);
                }
            }, {
                field: 'xscd',
                title: '小数长度',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('xscd',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sfkk',row);
                },formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }, {
                field: 'iskey',
                title: '是否主键',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('iskey',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('mrz',row);
                }
            },{
                field: 'zdms',
                title: '字段描述',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdms',row);
                }
            }]
        ],
        data: leftRsObj.leftSjbzd
    });
    $('#dgSjbzdRight').datagrid({
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
                field: 'zdmc',
                title: '字段名称',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdmc',row);
                }
            }, {
                field: 'zdlx',
                title: '字段类型',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdlx',row);
                }
            }, {
                field: 'zdcd',
                title: '字段长度',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdcd',row);
                }
            }, {
                field: 'xscd',
                title: '小数长度',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('xscd',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sfkk',row);
                },formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }, {
                field: 'iskey',
                title: '是否主键',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('iskey',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('mrz',row);
                }
            },{
                field: 'zdms',
                title: '字段描述',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('zdms',row);
                }
            }]
        ],
        data: rightRsObj.rightSjbzd
    });
    //数据表索引
    $('#dgSjbsyLeft').datagrid({
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
                field: 'symc',
                title: '索引名称',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('symc',row);
                }
            }, {
                field: 'syzd',
                title: '索引字段',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('syzd',row);
                }
            }, {
                field: 'sylx',
                title: '索引类型',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sylx',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return SYLX_DIC[value];
                    }else{
                        return value
                    }
                }
            }, {
                field: 'sfwysy',
                title: '是否唯一索引',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sfwysy',row);
                },
                formatter: function(value,row,index) {
                    if( value ){
                        return value == "UNIQUE" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: leftRsObj.leftSjbsy
    });
    $('#dgSjbsyRight').datagrid({
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
                field: 'symc',
                title: '索引名称',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('symc',row);
                }
            }, {
                field: 'syzd',
                title: '索引字段',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('syzd',row);
                }
            }, {
                field: 'sylx',
                title: '索引类型',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sylx',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return SYLX_DIC[value];
                    }else{
                        return value
                    }
                }
            }, {
                field: 'sfwysy',
                title: '是否唯一索引',
                width: 50,
                styler: function(value, row, index) {
                    return diff_field('sfwysy',row);
                },
                formatter: function(value,row,index) {
                    if( value ){
                        return value == "UNIQUE" ? "是" : "否";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: rightRsObj.rightSjbsy
    });
    //数据表约束
    $('#dgSjbysLeft').datagrid({
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
                field: 'ysmc',
                title: '约束名称',
                width: 120,
                styler: function(value, row, index) {
                    return diff_field('ysmc',row);
                }
            }, {
                field: 'yszd',
                title: '约束字段',
                width: 120,
                styler: function(value, row, index) {
                    return diff_field('yszd',row);
                }
            }]
        ],
        data: leftRsObj.leftSjbys
    });
    $('#dgSjbysRight').datagrid({
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
                field: 'ysmc',
                title: '约束名称',
                width: 120,
                styler: function(value, row, index) {
                    return diff_field('ysmc',row);
                }
            }, {
                field: 'yszd',
                title: '约束字段',
                width: 120,
                styler: function(value, row, index) {
                    return diff_field('yszd',row);
                }
            }]
        ],
        data: rightRsObj.rightSjbys
    });
    // 监听左侧grid body滚动
    $('#dgSjbjbxxLeft').datagrid('getBody').scroll(function(e){
        $("#dgSjbjbxxRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSjbjbxxRight').datagrid('getBody').scroll(function(e){
        $("#dgSjbjbxxLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgSjbzdLeft').datagrid('getBody').scroll(function(e){
        $("#dgSjbzdRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSjbzdRight').datagrid('getBody').scroll(function(e){
        $("#dgSjbzdLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgSjbsyLeft').datagrid('getBody').scroll(function(e){
        $("#dgSjbsyRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSjbsyRight').datagrid('getBody').scroll(function(e){
        $("#dgSjbsyLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgSjbysLeft').datagrid('getBody').scroll(function(e){
        $("#dgSjbysRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSjbysRight').datagrid('getBody').scroll(function(e){
        $("#dgSjbysLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});


/*
*判断业务参数是否一致
*/
function diff_field(field,row){
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
/*
*动态展示、隐藏内容
*/
function regionSH(title) {
    if (title == '数据表基本信息') {
        $('#divJbxx').show();
        $('#divSjbzd').hide();
        $('#divSjbsy').hide();
        $('#divSjbys').hide();
    }  else if (title == "数据表字段" ){
        $('#divJbxx').hide();
        $('#divSjbzd').show();
        $('#divSjbsy').hide();
        $('#divSjbys').hide();
    } else if (title == "数据表索引" ){
        $('#divJbxx').hide();
        $('#divSjbzd').hide();
        $('#divSjbsy').show();
        $('#divSjbys').hide();
    } else if (title == "数据表约束引" ){
        $('#divJbxx').hide();
        $('#divSjbzd').hide();
        $('#divSjbsy').hide();
        $('#divSjbys').show();
    }
}
