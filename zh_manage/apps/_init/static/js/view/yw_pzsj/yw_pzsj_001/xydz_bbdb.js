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
                    bzArray = leftXydzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftXydzRs.leftJkdx
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
                    bzArray = rightXydzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightXydzRs.rightJkdx
    });
    //规则代码
    $('#divGzdm').mergely({
        width: 'auto',
        height: 'auto',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftGzdmNr);
        },
        rhs: function(setValue) {
            setValue(rightGzdmNr);
        }
    });
    //传入参数
    $('#dgCrcsLeft').datagrid({
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
        data: leftCrcsRs
    });
    //传入参数
    $('#dgCrcsRight').datagrid({
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
        data: rightCrcsRs
    });
     // 延迟1s解决拖动不显示
    setTimeout(function() {
        $('#divGzdm').mergely('options', {
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
    $('#dgCrcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgCrcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgCrcsRight').datagrid('getBody').scroll(function(e){
        $("#dgCrcsLeft")
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
        $('#divXml').hide();
        $('#divCrcs').hide();
    } else if (title == '规则代码') {
        $('#divJbxx').hide();
        $('#divXml').show();
        $('#divCrcs').hide();
    } else if (title == "传入参数" ){
        $('#divJbxx').hide();
        $('#divXml').hide();
        $('#divCrcs').show();
    }
}
