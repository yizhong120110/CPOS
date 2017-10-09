$(document).ready(function() {
    var leftRs = ($('#hidLeftRs').val()+'').replace(/None/gm,"''");
    var rightRs = ($('#hidRightRs').val()+'').replace(/None/gm,"''");
    leftRsObj = eval('(' + leftRs + ')');
    rightRsObj = eval('(' + rightRs + ')');
    jdlx = $('#hidJdlx').val();
    hid = true;
    if (jdlx == '5' || jdlx == 5) {
        hid = false;
    }
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
                    bzArray = leftRsObj.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftRsObj.leftJdxx
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
            }]
        ],
        data: rightRsObj.rightJdxx
    });
    // 输入要素
    $('#dgSyysLeft').datagrid({
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
                field: 'bm',
                title: '编码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('gslb',row);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ly',row);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('jkjy',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '所属规则名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ssgzmc',row);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zjcs',row);
                },
                hidden: hid
            }]
        ],
        data: leftRsObj.leftSyys
    });
    $('#dgSyysRight').datagrid({
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
                field: 'bm',
                title: '编码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('gslb',row);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ly',row);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('jkjy',row);
                },
                formatter: function(value,row,index) {
                    if(value){
                        return value=="1" ? "是" : "否";
                    }else{
                        return value;
                    }
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '所属规则名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ssgzmc',row);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('zjcs',row);
                },
                hidden: hid
            }]
        ],
        data: rightRsObj.rightSyys
    });
    //节点逻辑代码
    $('#divLjdm').mergely({
        width: 'auto',
        height: 'auto',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(eval('(' + $('#hidLeftLjdm').val() + ')'));
        },
        rhs: function(setValue) {
            setValue(eval('(' + $('#hidRightLjdm').val() + ')'));
        }
    });
    //节点输出要素
    $('#dgScysLeft').datagrid({
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
                field: 'bm',
                title: '编码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('gslb',row);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ly',row);
                }
            }]
        ],
        data: leftRsObj.leftScys
    });
    $('#dgScysRight').datagrid({
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
                field: 'bm',
                title: '编码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('gslb',row);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('ly',row);
                }
            }]
        ],
        data: rightRsObj.rightScys
    });
    //返回值
    $('#dgFhzLeft').datagrid({
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
                field: 'bm',
                title: '返回值',
                width: 120,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '备注',
                width: 280,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }]
        ],
        data: leftRsObj.leftFhz
    });
    $('#dgFhzRight').datagrid({
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
                field: 'bm',
                title: '返回值',
                width: 120,
                styler: function(value, row, index) {
                    return dif_field('bm',row);
                }
            }, {
                field: 'ysmc',
                title: '备注',
                width: 280,
                styler: function(value, row, index) {
                    return dif_field('ysmc',row);
                }
            }]
        ],
        data: rightRsObj.rightFhz
    });
     // 延迟1s解决拖动不显示
    setTimeout(function() {
        $('#divLjdm').mergely('options', {
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
    $('#dgSyysLeft').datagrid('getBody').scroll(function(e){
        $("#dgSyysRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSyysRight').datagrid('getBody').scroll(function(e){
        $("#dgSyysLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgScysLeft').datagrid('getBody').scroll(function(e){
        $("#dgScysRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgScysRight').datagrid('getBody').scroll(function(e){
        $("#dgScysLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgFhzLeft').datagrid('getBody').scroll(function(e){
        $("#dgFhzRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgFhzRight').datagrid('getBody').scroll(function(e){
        $("#dgFhzLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*判断不一致属性
*/
function dif_field(field,row){
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
        $('#divXml').hide();
        $('#divSyys').hide();
        $('#divScys').hide();
        $('#divFhz').hide();
    } else if (title == '逻辑代码') {
        $('#divJbxx').hide();
        $('#divXml').show();
        $('#divSyys').hide();
        $('#divScys').hide();
        $('#divFhz').hide();
    } else if (title == "输入要素" ){
        $('#divJbxx').hide();
        $('#divXml').hide();
        $('#divSyys').show();
        $('#divScys').hide();
        $('#divFhz').hide();
    } else if (title == "输出要素" ){
        $('#divJbxx').hide();
        $('#divXml').hide();
        $('#divSyys').hide();
        $('#divScys').show();
        $('#divFhz').hide();
    } else if (title == "返回值" ){
        $('#divJbxx').hide();
        $('#divXml').hide();
        $('#divSyys').hide();
        $('#divScys').hide();
        $('#divFhz').show();
    }
}
