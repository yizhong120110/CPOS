$(function() {
    var bbh1 = ($('#bbh1').val() + '').replace(/None/gm, "''");
    var bbh2 = ($('#bbh2').val() + '').replace(/None/gm, "''");
    bbh1Obj = eval('(' + bbh1 + ')');
    bbh2Obj = eval('(' + bbh2 + ')');
    console.log(bbh1Obj.bbxx);
    //判断是否是本地比对，如果是，右左侧的为“本地版本”
    if (bbh1Obj.bbh === '本地版本') {
        $('#isbd').text(bbh1Obj.bbh);
    }
    //需要标注成黄色的栏目
    var bzArray = bbh1Obj.bz.split(',');
    $('#bbnr_db_code').mergely({
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
        $('#bbnr_db_code').mergely('options', {
            autoupdate: false,
            change_timeout: 3600000
        });
    }, 1000);

    var left_data =
        $('#datagrid_bbxx_left').datagrid({
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
                    field: 'sxmc',
                    title: '属性名称',
                    width: 120
                }, {
                    field: 'sxnr',
                    title: '属性内容',
                    width: 280,
                    styler: function(value, row, index) {
                        for (var i = 0; i < bzArray.length; i++) {
                            if (row.id == bzArray[i]) {
                                return 'background-color:#ffee00;color:red;';
                            }
                        }

                    }
                }]
            ],
            data: bbh1Obj.bbxx,
            onClickRow: function(rowIndex, rowData) {
                var datagrid_bbxx_right = $('#datagrid_bbxx_right');
                var index = datagrid_bbxx_right.datagrid('getRowIndex', datagrid_bbxx_right.datagrid("getSelected"))
                if (index || index != rowIndex) {
                    datagrid_bbxx_right.datagrid("selectRow", rowIndex);
                }
            }
        });

    var right_data =
        $('#datagrid_bbxx_right').datagrid({
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
                    field: 'sxmc',
                    title: '属性名称',
                    width: 120
                }, {
                    field: 'sxnr',
                    title: '属性内容',
                    width: 280,
                    styler: function(value, row, index) {
                        for (var i = 0; i < bzArray.length; i++) {
                            if (row.id == bzArray[i]) {
                                return 'background-color:#ffee00;color:red;';
                            }
                        }
                    }
                }]
            ],
            data: bbh2Obj.bbxx,
            onClickRow: function(rowIndex, rowData) {
                var datagrid_bbxx_left = $('#datagrid_bbxx_left');
                var index = datagrid_bbxx_left.datagrid('getRowIndex', datagrid_bbxx_left.datagrid("getSelected"))
                if (index || index != rowIndex) {
                    datagrid_bbxx_left.datagrid("selectRow", rowIndex);
                }
            }
        });

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

    function regionSH(title) {
        if (title == '版本信息') {
            $('#bbnr_db').hide().data('show', '2');
            $('#bbxx_db').show();
        } else if (title == '版本内容') {
            $('#bbnr_db').show().data('show', '1');
            $('#bbxx_db').hide();
        }
    }

    // 监听左侧grid body滚动
    $('#datagrid_bbxx_left').datagrid('getBody').scroll(function(e){
        $("#datagrid_bbxx_right")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });

    // 监听右侧grid body滚动
    $('#datagrid_bbxx_right').datagrid('getBody').scroll(function(e){
        $("#datagrid_bbxx_left")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });

});
