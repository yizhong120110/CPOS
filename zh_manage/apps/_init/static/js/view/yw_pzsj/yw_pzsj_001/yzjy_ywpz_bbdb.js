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
                    bzArray = leftYzjycspzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftYzjycspzRs.leftJkdx
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
                    bzArray = rightYzjycspzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightYzjycspzRs.rightJkdx
    });
    
    $('#divKkmx_u').mergely({
        width: 'auto',
        height: '200',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.kkmxsqlid ? leftYzjyRs.kkmxsqlid : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.kkmxsqlid ? rightYzjyRs.kkmxsqlid : '');
        }
    });
    // 扣款明细
    $('#divKkmx_d').mergely({
        width: 'auto',
        height: '200',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.kkmxcxsqlid ? leftYzjyRs.kkmxcxsqlid : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.kkmxcxsqlid ? rightYzjyRs.kkmxcxsqlid : '');
        }
    });
    // 扩展模块
    $('#divKzmk_u').mergely({
        width: 'auto',
        height: '300',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.kzjyid ? leftYzjyRs.kzjyid : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.kzjyid ? rightYzjyRs.kzjyid : '');
        }
    });
    // 扩展模块
    $('#dgKzjyfsLeft').datagrid({
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
                    if(leftYzjyRs.kzjyfs != rightYzjyRs.kzjyfs){
                        return 'background-color:#ffee00;color:red;';
                    }
                }
            }]
        ],
        data: [{'id':'1','sxmc':'扩展校验方式','sxnr':leftYzjyRs.kzjyfs}]
    });
    // 扩展模块
    $('#dgKzjyfsRight').datagrid({
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
                    if(leftYzjyRs.kzjyfs != rightYzjyRs.kzjyfs){
                        return 'background-color:#ffee00;color:red;';
                    }
                }
            }]
        ],
        data: [{'id':'2','sxmc':'扩展校验方式','sxnr':rightYzjyRs.kzjyfs}]
    });
    
    
    // 导入流水
    $('#divDrls_u').mergely({
        width: 'auto',
        height: '300',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.lsdrid ? leftYzjyRs.lsdrid : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.lsdrid ? rightYzjyRs.lsdrid : '');
        }
    });
    // 导入流水
    $('#dgDrlsLeft').datagrid({
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
                    if(leftYzjyRs.lsdrfs != rightYzjyRs.lsdrfs){
                        return 'background-color:#ffee00;color:red;';
                    }
                }
            }]
        ],
        data: [{'id':'1','sxmc':'导入流水方式','sxnr':leftYzjyRs.lsdrfs}]
    });
    // 导入流水
    $('#dgDrlsRight').datagrid({
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
                    if(leftYzjyRs.lsdrfs != rightYzjyRs.lsdrfs){
                        return 'background-color:#ffee00;color:red;';
                    }
                }
            }]
        ],
        data: [{'id':'2','sxmc':'导入流水方式','sxnr':rightYzjyRs.lsdrfs}]
    });
    
    // 异常更新
    $('#divYcqbcx_u').mergely({
        width: 'auto',
        height: '120',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.YC_ALLCANCEL_SQLID ? leftYzjyRs.YC_ALLCANCEL_SQLID : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.YC_ALLCANCEL_SQLID ? rightYzjyRs.YC_ALLCANCEL_SQLID : '');
        }
    });
    
    // 异常更新
    $('#divYcdbzt_d').mergely({
        width: 'auto',
        height: '120',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.YC_SINGLE_SQLID ? leftYzjyRs.YC_SINGLE_SQLID : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.YC_SINGLE_SQLID ? rightYzjyRs.YC_SINGLE_SQLID : '');
        }
    });
    
    // 异常更新
    $('#divYcqbtg_d').mergely({
        width: 'auto',
        height: '120',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(leftYzjyRs.YC_ALLPASS_SQLID ? leftYzjyRs.YC_ALLPASS_SQLID : '');
        },
        rhs: function(setValue) {
            setValue(rightYzjyRs.YC_ALLPASS_SQLID ? rightYzjyRs.YC_ALLPASS_SQLID : '');
        }
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
});

/*
*动态展示、隐藏内容
*/
function regionSH(title) {
    if (title == '基本信息') {
        $('#divJbxx').show();
        $('#divKkmx').hide();
        $('#divKzmk').hide();
        $('#divDrls').hide();
        $('#divYcgx').hide();
    } else if (title == '扣款明细') {
        $('#divJbxx').hide();
        $('#divKkmx').show();
        $('#divKzmk').hide();
        $('#divDrls').hide();
        $('#divYcgx').hide();
    } else if (title == "扩展模块" ){
        $('#divJbxx').hide();
        $('#divKkmx').hide();
        $('#divKzmk').show();
        $('#divDrls').hide();
        $('#divYcgx').hide();
    } else if (title == "导入流水" ){
        $('#divJbxx').hide();
        $('#divKkmx').hide();
        $('#divKzmk').hide();
        $('#divDrls').show();
        $('#divYcgx').hide();
    } else if (title == "异常更新" ){
        $('#divJbxx').hide();
        $('#divKkmx').hide();
        $('#divKzmk').hide();
        $('#divDrls').hide();
        $('#divYcgx').show();
    }
}
