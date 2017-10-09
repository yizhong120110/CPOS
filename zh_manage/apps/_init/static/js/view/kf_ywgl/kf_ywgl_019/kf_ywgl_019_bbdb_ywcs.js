$(document).ready(function() {
    var leftYwxx = ($('#hidLeftYwxxRs').val()+'').replace(/None/gm,"''");
    var rightYwxx = ($('#hidRightYwxxRs').val()+'').replace(/None/gm,"''");
    var leftYwcs = ($('#hidLeftYwcs').val()+'').replace(/None/gm,"''");
    var rightYwcs = ($('#hidRightYwcs').val()+'').replace(/None/gm,"''");
    leftYwxxObj = eval('(' + leftYwxx + ')');
    rightYwxxObj = eval('(' + rightYwxx + ')');
    leftYwcsObj = eval('(' + leftYwcs + ')');
    rightYwcsObj = eval('(' + rightYwcs + ')');
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
                    bzArray = leftYwxxObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftYwxxObj.leftYwxx
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
                    bzArray = rightYwxxObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightYwxxObj.rightYwxx
    });
        
    $('#dgYwcsLeft').datagrid({
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
                    return ywcs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return ywcs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return ywcs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return ywcs('zt',row);
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
        data: leftYwcsObj
    });
    $('#dgYwcsRight').datagrid({
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
                    return ywcs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return ywcs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return ywcs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return ywcs('zt',row);
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
        data: rightYwcsObj
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
    $('#dgYwcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgYwcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgYwcsRight').datagrid('getBody').scroll(function(e){
        $("#dgYwcsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*判断业务参数是否一致
*/
function ywcs(field,row){
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
    if (title == '基本信息') {
        $('#divJbxx').show();
        $('#divYwcs').hide();
    }  else if (title == "业务参数" ){
        $('#divJbxx').hide();
        $('#divYwcs').show();
    }
}
