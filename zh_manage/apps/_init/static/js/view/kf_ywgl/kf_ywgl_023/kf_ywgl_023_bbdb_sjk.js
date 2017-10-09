$(function() {
    var bbh1 = ($('#bbh1').val() + '').replace(/None/gm, "''");
    var bbh2 = ($('#bbh2').val() + '').replace(/None/gm, "''");
    bbh1Obj = eval('(' + bbh1 + ')');
    bbh2Obj = eval('(' + bbh2 + ')');
    if (bbh1Obj.bbh === '本地版本') {
        $('#isbd').text(bbh1Obj.bbh);
    }
    $("#tab_right").tabs({
        onSelect: function(title, index) {
            $("#tab_left").tabs('select', index);
        }
    });

    $("#tab_left").tabs({
        onSelect: function(title, index) {
            $("#tab_right").tabs('select', index);
        }
    });
    // 字段管理  右侧
    $('#zdgl_right').datagrid({
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
                width: 120,
                styler: function(value, row, index) {
                    return zdgl_bz('zdmc', row, bbh2Obj);
                }
            }, {
                field: 'zdms',
                title: '字段描述',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdms', row, bbh2Obj);
                }
            }, {
                field: 'zdlx',
                title: '字段类型',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdlx', row, bbh2Obj);
                }
            }, {
                field: 'zdcd',
                title: '字段长度',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdcd', row, bbh2Obj);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('sfkk', row, bbh2Obj);
                }
            }, {
                field: 'iskey',
                title: '是否主键',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('iskey', row, bbh2Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('mrz', row, bbh2Obj);
                }
            }]
        ],
        data: bbh2Obj.gl_sjkzdb,
        onClickRow: function(rowIndex, rowData) {
            $('#zdgl_left').datagrid("selectRow", rowIndex);
        }
    });
    // 字段管理  左侧
    $('#zdgl_left').datagrid({
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
                width: 120,
                styler: function(value, row, index) {
                    return zdgl_bz('zdmc', row, bbh1Obj);
                }
            }, {
                field: 'zdms',
                title: '字段描述',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdms', row, bbh1Obj);
                }
            }, {
                field: 'zdlx',
                title: '字段类型',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdlx', row, bbh1Obj);
                }
            }, {
                field: 'zdcd',
                title: '字段长度',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('zdcd', row, bbh1Obj);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('sfkk', row, bbh1Obj);
                }
            }, {
                field: 'iskey',
                title: '是否主键',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('iskey', row, bbh1Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return zdgl_bz('mrz', row, bbh1Obj);
                }
            }]
        ],
        data: bbh1Obj.gl_sjkzdb,
        onClickRow: function(rowIndex, rowData) {
            $('#zdgl_right').datagrid("selectRow", rowIndex);
        }
    });

    // 索引管理  左侧
    $('#sygl_left').datagrid({
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
                field: 'symc',
                title: '索引名称',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('symc', row, bbh1Obj);
                }
            }, {
                field: 'syzd',
                title: '索引字段',
                width: 120,
                styler: function(value, row, index) {
                    return sygl_sy('syzd', row, bbh1Obj) + 'word-break: break-word;';
                }
            }, {
                field: 'sylx',
                title: '索引类型',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('sylx', row, bbh1Obj);
                }
            }, {
                field: 'sfwysy',
                title: '是否唯一索引',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('sfwysy', row, bbh1Obj);
                }
            }]
        ],
        data: bbh1Obj.gl_sjksy,
        onClickRow: function(rowIndex, rowData) {
            $('#sygl_right').datagrid("selectRow", rowIndex);
        }
    });

    // 索引管理  右侧
    $('#sygl_right').datagrid({
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
                field: 'symc',
                title: '索引名称',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('symc', row, bbh2Obj);
                }
            }, {
                field: 'syzd',
                title: '索引字段',
                width: 120,
                styler: function(value, row, index) {
                    return sygl_sy('syzd', row, bbh2Obj) + 'word-break: break-word;';
                }
            }, {
                field: 'sylx',
                title: '索引类型',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('sylx', row, bbh2Obj);
                }
            }, {
                field: 'sfwysy',
                title: '是否唯一索引',
                width: 50,
                styler: function(value, row, index) {
                    return sygl_sy('sfwysy', row, bbh2Obj);
                }
            }]
        ],
        data: bbh2Obj.gl_sjksy,
        onClickRow: function(rowIndex, rowData) {
            $('#sygl_left').datagrid("selectRow", rowIndex);
        }
    });
    // 约束管理  左侧
    $('#ysgl_left').datagrid({
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
                width: 120,
                styler: function(value, row, index) {
                    return sygl_ys('ysmc', row, bbh1Obj);
                }
            }, {
                field: 'yszd',
                title: '约束字段',
                width: 280,
                styler: function(value, row, index) {
                    return sygl_ys('yszd', row, bbh1Obj) + 'word-break: break-word;';
                }
            }]
        ],
        data: bbh1Obj.gl_sjkys,
        onClickRow: function(rowIndex, rowData) {
            $('#ysgl_right').datagrid("selectRow", rowIndex);
        }
    });
    // 约束管理  左侧
    $('#ysgl_right').datagrid({
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
                width: 120,
                styler: function(value, row, index) {
                    return sygl_ys('ysmc', row, bbh2Obj);
                }
            }, {
                field: 'yszd',
                title: '约束字段',
                width: 280,
                styler: function(value, row, index) {
                    return sygl_ys('yszd', row, bbh2Obj) + 'word-break: break-word;';
                }
            }]
        ],
        data: bbh2Obj.gl_sjkys,
        onClickRow: function(rowIndex, rowData) {
            $('#ysgl_left').datagrid("selectRow", rowIndex);
        }
    });

    // 判断字段管理中需要高亮的内容
    function zdgl_bz(bzzd, row, obj) {
        if (obj.bz.bz_sjkzdb == '' || obj.bz.bz_sjkzdb.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_sjkzdb.length; i++) {
            var sjkzdb = obj.bz.bz_sjkzdb[i];
            id = sjkzdb.id
            bz_nr = sjkzdb.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }
    }

    // 判断索引管理中需要高亮的内容
    function sygl_sy(bzzd, row, obj) {
        if (bbh1Obj.bz.bz_sjksy == '' || bbh1Obj.bz.bz_sjksy.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_sjksy.length; i++) {
            var sjksy = obj.bz.bz_sjksy[i];
            id = sjksy.id
            bz_nr = sjksy.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }

    }

    // 判断约束管理中需要高亮的内容
    function sygl_ys(bzzd, row, obj) {
        if (bbh1Obj.bz.bz_sjkys == '' || bbh1Obj.bz.bz_sjkys.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_sjkys.length; i++) {
            var sjkys = obj.bz.bz_sjkys[i];
            id = sjkys.id
            bz_nr = sjkys.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }

    }


    // 监听grid 滚动
    datagridCompare($('#zdgl_right'), $('#zdgl_left'));
    datagridCompare($('#sygl_right'), $('#sygl_left'));
    datagridCompare($('#ysgl_right'), $('#ysgl_left'));


});
