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
                    bzArray = leftRsObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
                ,
                formatter: function(value,row,index) {
                    if(row.id=='zt'&&value){
                        return value=="1" ? "启用" : "禁用";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: leftRsObj.leftJyxx
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
                    bzArray = rightRsObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
                ,
                formatter: function(value,row,index) {
                    if(row.id=='zt'&&value){
                        return value=="1" ? "启用" : "禁用";
                    }else{
                        return value;
                    }
                }
            }]
        ],
        data: rightRsObj.rightJyxx
    });
        
    $('#dgJycsLeft').datagrid({
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
                    return jycs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return jycs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return jycs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return jycs('zt',row);
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
        data: leftRsObj.leftJycs
    });
    $('#dgJycsRight').datagrid({
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
                    return jycs('csdm',row);
                }
            }, {
                field: 'value',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return jycs('value',row);
                }
            }, {
                field: 'csms',
                title: '参数描述',
                width: 120,
                styler: function(value, row, index) {
                    return jycs('csms',row);
                }
            }, {
                field: 'zt',
                title: '状态',
                width: 50,
                styler: function(value, row, index) {
                    return jycs('zt',row);
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
        data: rightRsObj.rightJycs
    });
    $('#divJyxml').mergely({
        width: 'auto',
        height: 'auto',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(eval('(' + $('#hidLeftXml').val() + ')'));
        },
        rhs: function(setValue) {
            setValue(eval('(' + $('#hidRightXml').val() + ')'));
        }
    });
     // 延迟1s解决拖动不显示
    setTimeout(function() {
        $('#divJyxml').mergely('options', {
            autoupdate: false,
            change_timeout: 3600000
        });
    }, 1000);
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
    $('#dgJycsLeft').datagrid('getBody').scroll(function(e){
        $("#dgJycsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJycsRight').datagrid('getBody').scroll(function(e){
        $("#dgJycsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*判断业务参数是否一致
*/
function jycs(field,row){
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
    if (title == '交易信息') {
        $('#divJbxx').show();
        $('#divJycs').hide();
        $('#divXml').hide();
    } else if (title == '交易参数') {
        $('#divJbxx').hide();
        $('#divJycs').show();
        $('#divXml').hide();
    } else if (title == "流程XML" ){
        $('#divJbxx').hide();
        $('#divJycs').hide();
        $('#divXml').show();
    }
}
