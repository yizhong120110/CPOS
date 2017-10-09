$(function() {
    var bbh1 = ($('#bbh1').val() + '').replace(/None/gm, "''");
    var bbh2 = ($('#bbh2').val() + '').replace(/None/gm, "''");
    bbh1Obj = eval('(' + bbh1 + ')');
    bbh2Obj = eval('(' + bbh2 + ')');
    jdlx = $('#jdlx').val();
    hid = true;
    if (jdlx == '5' || jdlx == 5) {
        hid = false;
    }
    if (bbh1Obj.bbh === '本地版本') {
        $('#isbd').text(bbh1Obj.bbh);
    }
    $('#bbnr_db').mergely({
        width: 'auto',
        height: 'auto',
        cmsettings: {
            readOnly: true,
            lineNumbers: true
        },
        lhs: function(setValue) {
            setValue(eval('(' + $('#bbh1_data').val() + ')'));
        },
        rhs: function(setValue) {
            setValue(eval('(' + $('#bbh2_data').val() + ')'));
        },
        resized: function() {
            if ($('#bbnr_db').data('show') == '2') {
                $('#bbnr_db').hide()
            }
        }
    });

    // 延迟1s解决拖动不显示
    setTimeout(function() {
        $('#bbnr_db').mergely('options', {
            autoupdate: false,
            change_timeout: 3600000
        });
    }, 1000);

    $("#tab_right").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tab_left").tabs('select', index);
        }
    });

    $("#tab_left").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tab_right").tabs('select', index);
        }
    });

    $('#bbxx_left').datagrid({
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
                hidden: true
            }, {
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = bbh1Obj.bz.bz_jddy.split(',');
                    for (var i = 0; i < bzArray.length; i++) {
                        if (row.id == bzArray[i]) {
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: bbh1Obj.gl_jddy
    });

    $('#bbxx_right').datagrid({
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
                hidden: true
            }, {
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = bbh1Obj.bz.bz_jddy.split(',');
                    for (var i = 0; i < bzArray.length; i++) {
                        if (row.id == bzArray[i]) {
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: bbh2Obj.gl_jddy
    });

    $('#srys_left').datagrid({
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
                width: 1,
                hidden: true
            }, {
                field: 'bm',
                title: '要素编码',
                width: 90,
                styler: function(value, row, index) {
                    return srys_bz('bm', row, bbh1Obj);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 110,
                styler: function(value, row, index) {
                    return srys_bz('ysmc', row, bbh1Obj);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('gslb', row, bbh1Obj);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('ly', row, bbh1Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('mrz', row, bbh1Obj);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                styler: function(value, row, index) {
                    return srys_bz('jkjy', row, bbh1Obj);
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                styler: function(value, row, index) {
                    return srys_bz('ssgzmc', row, bbh1Obj);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('zjcs', row, bbh1Obj);
                },
                hidden: hid
            }]
        ],
        data: bbh1Obj.gl_srys
    });
    $('#srys_right').datagrid({
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
                width: 1,
                hidden: true
            }, {
                field: 'bm',
                title: '要素编码',
                width: 90,
                styler: function(value, row, index) {
                    return srys_bz('bm', row, bbh2Obj);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 110,
                styler: function(value, row, index) {
                    return srys_bz('ysmc', row, bbh2Obj);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('gslb', row, bbh2Obj);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('ly', row, bbh2Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('mrz', row, bbh2Obj);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                styler: function(value, row, index) {
                    return srys_bz('jkjy', row, bbh2Obj);
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                styler: function(value, row, index) {
                    return srys_bz('ssgzmc', row, bbh2Obj);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return srys_bz('zjcs', row, bbh2Obj);
                },
                hidden: hid
            }]
        ],
        data: bbh2Obj.gl_srys
    });
    $('#scys_left').datagrid({
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
                width: 1,
                hidden: true
            }, {
                field: 'bm',
                title: '要素编码',
                width: 90,
                styler: function(value, row, index) {
                    return scys_bz('bm', row, bbh1Obj);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 110,
                styler: function(value, row, index) {
                    return scys_bz('ysmc', row, bbh1Obj);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('gslb', row, bbh1Obj);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('ly', row, bbh1Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('mrz', row, bbh1Obj);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                styler: function(value, row, index) {
                    return scys_bz('jkjy', row, bbh1Obj);
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                styler: function(value, row, index) {
                    return scys_bz('ssgzmc', row, bbh1Obj);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('zjcs', row, bbh1Obj);
                },
                hidden: hid
            }]
        ],
        data: bbh1Obj.gl_scys
    });
    $('#scys_right').datagrid({
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
                width: 1,
                hidden: true
            }, {
                field: 'bm',
                title: '要素编码',
                width: 90,
                styler: function(value, row, index) {
                    return scys_bz('bm', row, bbh1Obj);
                }
            }, {
                field: 'ysmc',
                title: '要素名称',
                width: 110,
                styler: function(value, row, index) {
                    return scys_bz('ysmc', row, bbh2Obj);
                }
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('gslb', row, bbh2Obj);
                }
            }, {
                field: 'ly',
                title: '来源',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('ly', row, bbh2Obj);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('mrz', row, bbh2Obj);
                }
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                styler: function(value, row, index) {
                    return scys_bz('jkjy', row, bbh2Obj);
                },
                hidden: hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                styler: function(value, row, index) {
                    return scys_bz('ssgzmc', row, bbh2Obj);
                },
                hidden: hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                styler: function(value, row, index) {
                    return scys_bz('zjcs', row, bbh2Obj);
                },
                hidden: hid
            }]
        ],
        data: bbh2Obj.gl_scys
    });
    $('#fhz_left').datagrid({
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
                hidden: true
            }, {
                field: 'bm',
                title: '返回值',
                width: 120,
                styler: function(value, row, index) {
                    return fhz_bz('bm', row, bbh1Obj);
                }
            }, {
                field: 'ysmc',
                title: '备注',
                width: 280,
                styler: function(value, row, index) {
                    return fhz_bz('jddyid', row, bbh1Obj);
                }
            }]
        ],
        data: bbh1Obj.gl_fhz
    });
    $('#fhz_right').datagrid({
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
                hidden: true
            }, {
                field: 'bm',
                title: '返回值',
                width: 120,
                styler: function(value, row, index) {
                    return fhz_bz('bm', row, bbh2Obj);
                }
            }, {
                field: 'ysmc',
                title: '备注',
                width: 280,
                styler: function(value, row, index) {
                    return fhz_bz('jddyid', row, bbh2Obj);
                }
            }]
        ],
        data: bbh2Obj.gl_fhz
    });

    function regionSH(title) {
        switch (title) {
            case '版本内容':
                $('#bbnr_db').show().data('show', '1');
                $('#bbxx_db').hide();
                $('#srys_db').hide();
                $('#scys_db').hide();
                $('#fhz_db').hide();
                break;
            case '版本信息':
                $('#bbnr_db').hide().data('show', '2');
                $('#bbxx_db').show();
                $('#srys_db').hide();
                $('#scys_db').hide();
                $('#fhz_db').hide();
                break;
            case '输入要素':
                $('#bbnr_db').hide().data('show', '2');
                $('#bbxx_db').hide();
                $('#srys_db').show();
                $('#scys_db').hide();
                $('#fhz_db').hide();
                break;
            case '输出要素':
                $('#bbnr_db').hide().data('show', '2');
                $('#bbxx_db').hide();
                $('#srys_db').hide();
                $('#scys_db').show();
                $('#fhz_db').hide();
                break;
            case '返回值':
                $('#bbnr_db').hide().data('show', '2');
                $('#bbxx_db').hide();
                $('#srys_db').hide();
                $('#scys_db').hide();
                $('#fhz_db').show();
                break;
        }
    }

    // 判断输入要素信息中需要高亮的内容
    function srys_bz(bzzd, row, obj) {

        if (bbh1Obj.bz.bz_srys == '' || bbh1Obj.bz.bz_srys.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_srys.length; i++) {
            var srys = obj.bz.bz_srys[i];
            id = srys.id
            bz_nr = srys.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }
    }

    // 判断输出要素中需要高亮的内容
    function scys_bz(bzzd, row, obj) {
        if (bbh1Obj.bz.bz_scys == '' || bbh1Obj.bz.bz_scys.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_scys.length; i++) {
            var scys = obj.bz.bz_scys[i];
            id = scys.id
            bz_nr = scys.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }
    }

    // 判断返回值中需要高亮的内容
    function fhz_bz(bzzd, row, obj) {
        if (bbh1Obj.bz.bz_fhz == '' || bbh1Obj.bz.bz_fhz.length == 0) {
            return;
        }
        // 获取改行的id对应的列有无版本内容不一致情况
        for (var i = 0; i < obj.bz.bz_fhz.length; i++) {
            var fhz = obj.bz.bz_fhz[i];
            id = fhz.id
            bz_nr = fhz.bznr
            for (var j = 0; j < bz_nr.length; j++) {
                if (bzzd == bz_nr[j] && id == row.id) {
                    return 'background-color:#ffee00;color:red;';
                }
            }
        }
    }

    // 监听grid 滚动
    datagridCompare($('#bbxx_left'), $('#bbxx_right'));
    datagridCompare($('#srys_left'), $('#srys_right'));
    datagridCompare($('#scys_left'), $('#scys_right'));
    datagridCompare($('#fhz_left'), $('#fhz_right'));

});
