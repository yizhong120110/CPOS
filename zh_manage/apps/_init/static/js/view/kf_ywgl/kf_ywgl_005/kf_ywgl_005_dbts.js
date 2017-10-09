$(document).ready(function() {
    //初始化节点名称
    var nodeid = $('#nodeid').val();
    var type = $('#type').val();
    var bjid = parent.$('#workflow div[id][data-nodeid="' + nodeid + '"]').attr('id');
    var lcmc = parent.$('#mc').val();
    var jdmc = parent.$('#' + bjid).text();
    $('#txtDqjd').textbox('setValue', jdmc);
    $('#bzmc').textbox('setValue', (lcmc+'_'+jdmc+'_'));
    $('#bzms').next().children().attr("maxlength", "500");

    /*
     * 重新加载其他测试案例要素列表
     * lx: 1输入 2输出
     */
    function reloadQtcsalys(lx) {
        var id = (lx == '1' ? 'fzqtaldsrys' : 'fzqtaldscys');
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbts_bz_data_view",
            data: {
                "nodeid": $('#nodeid').val(),
                "lx": lx
            },
            success: function(data) {
                data.bz.unshift({
                    bzid: "0",
                    bzmc: "不复制"
                });
                //$("#"+id).combobox('loadData', data.bz);
                $("#" + id).combobox({
                    data: data.bz,
                    valueField: 'bzid',
                    textField: 'bzmc',
                    editable: false,
                    onLoadSuccess: function(data) {
                        $(this).combobox('setValue', 0);
                    },
                    onSelect: function(record) {
                        var yslx = (lx == '1' ? 'sr' : 'sc');
                        var ys = data.ys[record.bzid];
                        $('input[data-jdysbm]').val('');
                        for (var i in ys) {
                            $('input[data-yslx="' + yslx + '"][data-jdysbm="' + ys[i].ysdm + '"]').val(ys[i].ysz).prev().text(ys[i].ysz)
                        }
                    }
                });
            },
            error: function() {
                errorAjax();
            }
        });
    }

    reloadQtcsalys('1');
    reloadQtcsalys('2');

    // 输入要素
    $('#datagrid_srys').datagrid({
        nowrap: false,
        fit: false,
        height: '150px',
        border: true,
        rownumbers: true,
        singleSelect: true,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbts_ys_data_view",
        queryParams: {
            lcid: parent.$('#id').val(),
            nodeid: nodeid,
            type: type,
            lb: '1'
        },
        columns: [
            [{
                field: 'jdysbm',
                title: '输入要素',
                width: 35
            }, {
                field: 'value',
                title: '值',
                width: 65,
                formatter: function(value, rowData, rowIndex) {
                    return '<input type="text" autocomplete="off" name="nr" data-yslx="sr" data-jdysbm="' + rowData.jdysbm + '" style="width:141px" />' + 
                    '<input type="hidden" data-yslx="hidden_sr" data-jdysbm="' + rowData.jdysbm + '" />';
                }
            }]
        ],
        onLoadSuccess: function(data) {
            for (var ys in qjscsrys) {
                $('input[data-yslx="sr"][data-jdysbm="' + ys + '"]').val(qjscsrys[ys]);
            }
        }
    });

    // 上次执行的输出要素、值
    var qjscsrys = {};

    // 输出要素
    $('#datagrid_scys').datagrid({
        nowrap: false,
        fit: false,
        height: '150px',
        border: true,
        rownumbers: true,
        singleSelect: true,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbts_ys_data_view",
        queryParams: {
            lcid: parent.$('#id').val(),
            nodeid: nodeid,
            type: type,
            lb: '2'
        },
        columns: [
            [{
                field: 'jdysbm',
                title: '输出要素',
                width: 35
            }, {
                field: 'value',
                title: '值',
                width: 65,
                formatter: function(value, rowData, rowIndex) {
                    return '<pre class="scys-pre" style="margin:0;padding:0">' + value + '</pre><input type="text" name="nr" class="scys-input" data-yslx="sc" data-jdysbm="' + rowData.jdysbm + '" style="width:140px;display: none;" />';
                },
                styler: function(value, row, index) {
                    return 'word-break:break-word;';
                }
            }]
        ],
        onLoadSuccess: function(data) {
            $('#datagrid_scys').datagrid('resize');

            function scys_input_blur(e) {
                // 失去焦点 隐藏 并使pre获得其值并显示
                if ($("#tg").prop("checked")) {
                    var $this = $(this);
                    var value = $this.val();
                    $this.hide().prev().text(value).css('word-break', 'break-word').show();
                }
            }

            function scys_input_focus(e) {
                if ($("#tg").prop("checked")) {
                    $(this).closest('td').css('word-break', 'normal');
                }
            }

            $(".scys-input").off('blur', scys_input_blur);
            $(".scys-input").on('blur', scys_input_blur);

            $(".scys-input").off('focus', scys_input_focus);
            $(".scys-input").on('focus', scys_input_focus);

        },
        onSelect: function(rowIndex, rowData) {
            if ($("#tg").prop("checked")) {
                $("#datagrid_scys")
                    .datagrid('getBody')
                    .find("tr")
                    .find('.scys-input').hide().end()
                    .find('.scys-pre').show().end()
                    .eq(rowIndex)
                    .find('.scys-input').show().focus()
                    .end()
                    .find('.scys-pre').hide()
            }
        }
    });

    // 返回值
    $('#datagrid_fhz').datagrid({
        nowrap: false,
        fit: false,
        height: '150px',
        border: true,
        rownumbers: true,
        singleSelect: true,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbts_ys_data_view",
        queryParams: {
            lcid: parent.$('#id').val(),
            nodeid: nodeid,
            type: type,
            lb: '3'
        },
        columns: [
            [{
                field: 'jdysbm',
                title: '返回值',
                width: 28
            }, {
                field: 'ysmc',
                title: '名称',
                width: 72,
                formatter: function(value, rowData, rowIndex) {
                    return '<input class="fhz_radio" disabled type="radio" name="value" value="' + rowData.jdysbm + '" /> ' + (value || '');
                }
            }]
        ],
        onSelect: function(rowIndex, rowData) {
            if ($("#tg").prop("checked")) {
                $('#datagrid_fhz')
                    .datagrid("getPanel")
                    .find("[name=value]")
                    .eq(rowIndex)
                    .prop("checked", true);
            }
        },
        onUnselect: function(rowIndex, rowData) {
            if ($("#tg").prop("checked")) {
                $('#datagrid_fhz')
                    .datagrid("getPanel")
                    .find("[name=value]")
                    .eq(rowIndex)
                    .prop("checked", false);
            }
        }
    });

    // 【跳过】复选框
    $("#tg").click(function() {
        var chked = this.checked;
        var tab = $("#srscys_tab").tabs('getSelected');
        var index = $('#srscys_tab').tabs('getTabIndex', tab);
        var node = parent.$('#workflow div[data-nodeid="' + $('#nodeid').val() + '"]');
        if (chked) {
            // 禁用【输入要素】tab选项卡并且在index是0时选择【输出要素】选项卡
            $("#srscys_tab")
                .tabs('disableTab', "输入要素")
                .tabs(index ? 'resize' : 'select', "输出要素");

            // 【输出要素】显示可复制下拉框
            $("#fzqtaldscys_table").show();

            // 【输出要素】显示input框，隐藏span
            $("#datagrid_scys").datagrid('getPanel')
                .find('.scys-input').hide()
                .end()
                .find('.scys-pre').show();

            // 【返回值】的radio启用
            $('#datagrid_fhz').datagrid('getPanel')
                .find('.fhz_radio').prop('disabled', false);
            
            // 启用“下一步”按钮
            if (node.data('type') != 'end_jy') {
                $('#btnNext').linkbutton('enable');
            }

            // 禁用执行按钮
            $('#btnExecute').linkbutton('disable');

            // 禁用日志按钮
            $('#btnViewlog').linkbutton('disable');
        } else {
            // 启用【输入要素】tab选项卡
            $("#srscys_tab")
                .tabs('enableTab', "输入要素");

            // 【输出要素】隐藏可复制下拉框
            $("#fzqtaldscys_table").hide();

            // 【输出要素】隐藏input框，显示span
            $("#datagrid_scys").datagrid('getPanel')
                .find('.scys-pre').show()
                .end()
                .find('.scys-input').hide();

            // 【返回值】的radio禁用
            $('#datagrid_fhz').datagrid('getPanel')
                .find('.fhz_radio').prop('disabled', true);

            if (node.data('type') == 'end_zlc') {
                // 禁用“执行”按钮
                $('#btnExecute').linkbutton('disable');
            } else {
                // 启用“执行”按钮
                $('#btnExecute').linkbutton('enable');
            }
            // 启用日志按钮
            if ($('#log_lsh').val() != '') {
                $('#btnViewlog').linkbutton('enable');
            }
            if ($('#fhz').val() == '') {
                $('#btnNext').linkbutton('disable');
            }
        }
    })

    function addIcon() {
        $('#txtDemomcSelected').textbox({
            icons: [{
                iconCls: 'icon-delete',
                handler: function(e) {
                    $(e.data.target).textbox('clear');
                    $('#txtDemojbxxidSelected').val('');
                    $('#txtDemomcSelected').textbox({
                        icons: null
                    });
                }
            }]
        });
    }

    $("#btnSelectDemo,#btnSelectDemoPL").click(function(e) {
        e.preventDefault();
        var havaYwsjb = false;
        var demoSelBtnID = this.id;
        $.ajax({
            async: false, // 使用同步方式
            type: 'GET',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/get_ywsjb_view",
            data: {
                "ywid": $('#ywid').val()
            },
            success: function(data) {
                parent.window.tbsYwsjbData = data;
                if (data.length > 0) {
                    havaYwsjb = true;
                }
                if (demoSelBtnID == "btnSelectDemo"){
                    // 隐藏批量写demo的布局
                    parent.$("#divYwsj").hide();
                    parent.$("#tbsYwsjb").show();
                    var tabLength = parent.$('#tbsYwsjb').tabs('tabs').length;
                    for (var i=tabLength-1; i>=0; i--) {
                        parent.$('#tbsYwsjb').tabs('close', i);
                    }
                    $(data).each(function(i){
                        parent.$('#tbsYwsjb').tabs('add', {
                            title: this['sjbmc'] || this['sjbjc'],
                            selected: i==0
                        });
                        parent.$('#tbsYwsjb').tabs('getTab', i).html('<iframe data-src="/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/index_view?sjkmxdy_id='+this['sjkmxdyid']+'&lx=demo" scrolling="no" frameborder="0" style="width:100%;height:100%;display:block"></iframe>');
                    });
                }
                var pCount = 0;
                if (demoSelBtnID == "btnSelectDemoPL"){
                    // 隐藏控件
                    parent.$("#divYwsj").show();
                    parent.$("#tbsYwsjb").hide();
                    parent.$('#comboYwsjb').combobox({
                        data:data,
                        valueField:'sjkmxdyid',
                        textField:'sjbmc',
                        onLoadSuccess : function(data){
                            pCount = data.length;
                        },
                        onShowPanel : function() {
                            if(pCount <= 10){
                                // 动态调整高度 
                                parent.$('#comboYwsjb').combobox('panel').height(pCount * 20);
                            }else{
                                parent.$('#comboYwsjb').combobox('panel').height(200);
                            }
                        }
                    });
                }
                
            }
        });
        if (!havaYwsjb) {
            $.messager.alert('错误', '没有相关的业务表，无法进行Demo录入', 'error');
            return false;
        }
        var bean_window_demo = parent.$("#bean_window_demo");
        parent.newWindow(bean_window_demo, '选择DEMO数据',  686, 420);
        parent.$("#dgSearch").tabSort();
        parent.$('#dgDemo').datagrid({
            fit: false,
            height: '343px',
            width: '675px',
            rownumbers: true,
            pagination: true,
            fitColumns: true,
            method: "get",
            singleSelect: true,
            remoteSort: false,
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_jbxx_data_view?ywid=" + $('#ywid').val(),
            frozenColumns: [
                [{
                    field: 'ck',
                    formatter: function(value, rowData, rowIndex) {
                        return '<input type="radio" name="demo_radio" />';
                    }
                }]
            ],
            columns: [
                [{
                    field: 'id',
                    hidden: true
                }, {
                    field: 'mc',
                    title: '名称',
                    width: 40
                }, {
                    field: 'sjms',
                    title: '描述',
                    width: 45
                }, {
                    field: 'operation',
                    title: '操作',
                    width: 15,
                    formatter: function(value, rowData, rowIndex) {
                        return '<a href="javascript:;" onclick="updaterow_demo(\'dgDemo\',' + rowIndex + ',\'' + demoSelBtnID + '\');return false;">编辑</a> <a href="javascript:delete_demo(\'' + rowData.id + '\');">删除</a>';
                    }
                }]
            ],
            toolbar: [{
                iconCls: 'icon-add',
                text: '新增',
                handler: function() {
                    add_demo();
                }
            }, {
                iconCls: 'icon-ok',
                disabled: true,
                text: '确定',
                handler: function() {
                    var rowData = parent.$('#dgDemo').datagrid('getSelected');
                    $('#txtDemojbxxidSelected').val(rowData.id);
                    $('#txtDemomcSelected').textbox('setValue', rowData.mc);
                    parent.$("#bean_window_demo").window('close');
                    addIcon();
                },
                id: 'datagrid_demo_ok'
            }],
            onDblClickRow: function(rowIndex, rowData) {
                $('#txtDemojbxxidSelected').val(rowData.id);
                $('#txtDemomcSelected').textbox('setValue', rowData.mc);
                parent.$("#bean_window_demo").window('close');
                addIcon();
            },
            onSelect: function(rowIndex, rowData) {
                var panel = parent.$('#dgDemo')
                    .datagrid("getPanel");
                panel
                    .find("[name=demo_radio]")
                    .eq(rowIndex)
                    .prop("checked", true);
                panel
                    .find("#datagrid_demo_ok")
                    .linkbutton('enable');
            },
            onUnselect: function(rowIndex, rowData) {
                parent.$('#dgDemo')
                    .datagrid("getPanel")
                    .find("[name=demo_radio]")
                    .eq(rowIndex)
                    .prop("checked", false);
            },
            onLoadSuccess: function(data) {
                $(data.rows).each(function(index, element) {
                    if (this.id == $('#txtDemojbxxidSelected').val()) {
                        var panel = parent.$('#dgDemo')
                            .datagrid("getPanel");
                        panel
                            .find("[name=demo_radio]")
                            .eq(index)
                            .prop("checked", true);
                        panel
                            .find("#datagrid_demo_ok")
                            .linkbutton('enable');
                        parent.$('#dgDemo')
                            .datagrid("selectRow", index);
                        return false;
                    }
                });
            }
        });
        
        // 每次新打开窗口，重新加载
        parent.$('#dgDemo').datagrid('load',{
            mc: '',
            ms: ''
        });
    });

    /**
     * 新增DEMO数据
     */
    function add_demo() {
        parent.newWindow(parent.$("#bean_window_add_demo"), 'DEMO数据录入', 600, 410);
        parent.$("#tbsDemo").tabs('select', 0);
        parent.$("#tbsDemo").tabs('disableTab', 1);
    }


    // 当前布局ID
    var bjid = parent.$('#workflow div[data-nodeid="' + $('#nodeid').val() + '"]').attr('id');
    // 步骤布局ID列表，保存步骤的执行顺序
    var bz_bjids = [bjid];
    // 布局ID对应步骤ID
    var bjid_bzid_map = {};
    // 选择的DemoID列表
    var demoids = [];

    function getTypeByNodeid(nodeid) {
        var type = parent.$('#workflow div[data-nodeid="' + nodeid + '"]').data('type');
        return (type == undefined || type == '') ? 'jd' : type;
    }

    function getBjidByNodeid(nodeid) {
        return parent.$('#workflow div[data-nodeid="' + nodeid + '"]').attr('id');
    }

    function refreshWin(nodeid) {
        var lcid = parent.$('#id').val();
        var type = getTypeByNodeid(nodeid);
        // qjscsrys = {}; 下面需要先输出后输入，输入覆盖原有的输入
        // 输入要素、值
        $($('#datagrid_srys').datagrid('getRows')).each(function() {
            qjscsrys[this.jdysbm] = $('input[data-yslx="sr"][data-jdysbm="' + this.jdysbm + '"]').val();
        });
        // 上次执行的输出要素、值
        $($('#datagrid_scys').datagrid('getRows')).each(function() {
            qjscsrys[this.jdysbm] = $('input[data-yslx="sc"][data-jdysbm="' + this.jdysbm + '"]').val();
        });
        // 更新窗体数据
        $('#datagrid_srys').datagrid('reload', {
            lcid: lcid,
            nodeid: nodeid,
            type: type,
            lb: '1'
        });
        $('#datagrid_scys').datagrid('reload', {
            lcid: lcid,
            nodeid: nodeid,
            type: type,
            lb: '2'
        });
        $('#datagrid_fhz').datagrid('reload', {
            lcid: lcid,
            nodeid: nodeid,
            type: type,
            lb: '3'
        });
        // 步骤名称、步骤描述
        var jdmc = parent.$('#workflow div[data-nodeid="' + nodeid + '"]').text();
        $('#bzmc').textbox('setValue', lcmc + '_' + jdmc + '_');
        $('#txtDqjd').textbox('setValue', jdmc);
        $('#bzms').textbox('setValue', '');
    }

    function jump_node(bjid_target) {
        // 当前布局ID
        var bjid_source = getBjidByNodeid($('#nodeid').val());
        // 目标节点ID
        var nodeid_target = parent.$('#' + bjid_target).data('nodeid');
        // 更新窗体数据
        refreshWin(nodeid_target);

        // 流程图中转至目标一节点
        parent.$('#' + bjid_source).removeClass('active');
        parent.$('#' + bjid_target).addClass('active');
        $("#nodeid").val(nodeid_target);
        var type = parent.$('#' + bjid_target).data('type');
        type = (type == undefined || type == '') ? 'jd' : type;
        $("#type").val(type);
        
        // 去掉“跳过”勾选
        if ($('#tg').get(0).checked) {
            // 使用此方式，触发点击事件，使启用/禁用输入要素Tab等
            $("#tg").trigger('click');
        }
        // 禁用“下一步”按钮
        $('#btnNext').linkbutton('disable');
        // 禁用“日志”按钮
        $('#btnViewlog').linkbutton('disable');
        if (type == 'end_zlc') {
            // 禁用“执行”按钮
            $('#btnExecute').linkbutton('disable');
        } else {
            $('#btnExecute').linkbutton('enable');
        }
        
        // 取消Demo数据选择
        $('#txtDemomcSelected').textbox('clear');
        $('#txtDemojbxxidSelected').val('');
        $('#txtDemomcSelected').textbox({
            icons: null
        });
        $("#srscys_tab").tabs('select', 0);
    }

    $('#btnBack').linkbutton({
        onClick: function() {
            // 当前布局ID
            var bjid_source = parent.$('#workflow div[data-nodeid="' + $('#nodeid').val() + '"]').attr('id');
            var idx = bz_bjids.indexOf(bjid_source);
            if (idx < 1) {
                parent.$.messager.alert('错误', '无法转到上一步', 'error');
                return false;
            }

            // 删除保存的步骤
            if (!demo_del_step([bjid_bzid_map[bz_bjids[idx]], bjid_bzid_map[bz_bjids[idx-1]]])) {
                parent.$.messager.alert('错误', '步骤删除失败，无法转到上一步', 'error');
                return false;
            }
            // 转到上一步
            jump_node(bz_bjids[idx - 1]);
            bz_bjids = bz_bjids.slice(0, idx);
            bjid_bzid_map[bz_bjids[idx-1]] = null;
            $('#log_lsh').val('');
            if (idx == 1) {
                // 禁用“上一步”按钮
                $('#btnBack').linkbutton('disable');
                // 禁用“查看单步调试记录”按钮
                $('#btnDbtsjl').linkbutton('disable');
            }
            // 重新加载其他测试案例要素列表
            reloadQtcsalys('1');
            reloadQtcsalys('2');
        }
    });

    $('#btnNext').linkbutton({
        onClick: function() {
            if ($('#bzmc').textbox('getValue') == '') {
                parent.$.messager.alert('错误', '步骤名称不可为空，请输入', 'error', function(){
                    $("#bzmc").next().children().focus();
                });
                return false;
            } else if ($('#bzmc').textbox('getValue').length > 50) {
                parent.$.messager.alert('错误', '步骤名称过长，最长可输入50位，请重新输入', 'error', function(){
                    $("#bzmc").next().children().focus();
                });
                return false;
            }
            var node = parent.$('#workflow div[data-nodeid="' + $('#nodeid').val() + '"]');
            var type = node.data('type');
            var fhz = null;
            // 如果勾选了跳过
            if ($('#tg').get(0).checked) {
                var all_null = true;
                $('input[data-yslx="sc"]').each(function() {
                    if ($(this).val() != '') {
                        all_null = false;
                        return false;
                    }
                });
                if (all_null) {
                    parent.$.messager.alert('错误', '请录入输出要素', 'error', function() {
                        $(".scys-input:first").show().focus().prev().hide();
                    });
                    return false;
                }
                fhz = $('input.fhz_radio:checked').val();
                if ((fhz == undefined || fhz == '') && type != 'start_jy') {
                    parent.$.messager.alert('错误', '请选择返回值', 'error', function() {
                        $("#srscys_tab").tabs('select', "返回值");
                    });
                    return false;
                }
                // 跳过，默认为成功
                executeState = true;
            } else {
                fhz = $('#fhz').val();
            }

            // 保存当前步骤
            if (!demo_save_step(fhz)) {
                parent.$.messager.alert('错误', '当前步骤保存失败，无法转到下一步', 'error');
                return false;
            }

            // 转到下一步骤
            var bjid = node.attr('id');
            var targetId = '';
            $.each(parent.instance.getAllConnections(), function() {
                if (this.sourceId == bjid && (this.getOverlay('label').getLabel() == fhz || type == 'start_jy')) {
                    targetId = this.targetId;
                    return false;
                }
            });
            // 如果执行失败（SYS_XYM != '000000'），跳到结束节点
            if (!executeState) {
                targetId = parent.$('#workflow div[data-type="end_jy"]').attr('id') || parent.$('#workflow div[data-type="end_zlc"]').attr('id');
            }
            if (!targetId) {
                parent.$.messager.alert('错误', '返回值为' + fhz + '，无法转到下一步', 'error');
                return false;
            }
            // 启用“查看单步调试记录”按钮
            $('#btnDbtsjl').linkbutton('enable');
            // 启用“上一步”按钮
            $('#btnBack').linkbutton('enable');

            // 流程图中移至下一节点
            jump_node(targetId);
            
            $('#fhz').val('');
            $('#log_lsh').val('');
            bz_bjids.push(targetId);
            // 重新加载其他测试案例要素列表
            reloadQtcsalys('1');
            reloadQtcsalys('2');
        }
    });

    function demo_save_step(fhz) {
        // 新的步骤ID
        var bzid = new UUID().toString();
        // 节点ID
        var nodeid = $('#nodeid').val();
        // 输入要素
        var srys = {};
        $('input[data-yslx=hidden_sr]').each(function() {
            srys[$(this).data('jdysbm')] = $(this).val();
        });
        // 输出要素
        var scys = {};
        $('input[data-yslx=sc]').each(function() {
            scys[$(this).data('jdysbm')] = $(this).val();
        });
        // 当前布局ID
        var bjid = parent.$('#workflow div[data-nodeid="' + nodeid + '"]').attr('id');
        var saved = false;
        $.ajax({
            async: false, // 使用同步方式
            type: "POST",
            dataType: "json",
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_save_step_view",
            data: {
                "bzid": bzid,
                "bzid_old": bjid_bzid_map[bjid],
                'srys': JSON.stringify(srys),
                'scys': JSON.stringify(scys),
                'lx': $('#type').val(),
                'nodeid': nodeid,
                'fhz': fhz,
                'mc': $('#bzmc').textbox('getValue'),
                'ms': $('#bzms').textbox('getValue'),
                'sftg': $('#tg').get(0).checked * 1 + '',
                'demoid': $('#txtDemojbxxidSelected').val(),
                'log_lsh': $('#log_lsh').val()
            },
            success: function(data) {
                if (!data.state) {
                    //parent.$.messager.alert('错误', data.msg, 'error');
                } else {
                    bjid_bzid_map[bjid] = bzid;
                }
                saved = data.state;
            }
        });
        return saved;
    }

    function demo_del_step(bzids_old) {
        var state = false;
        $.ajax({
            async: false, // 使用同步方式
            type: "POST",
            dataType: "json",
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_del_step_view",
            data: {
                "bzids_old": JSON.stringify(bzids_old)  // 已执行过的步骤IDs
            },
            success: function(data) {
                if (!data.state) {
                    //parent.$.messager.alert('错误', data.msg, 'error');
                }
                state = data.state;
            }
        });
        return state;
    }
    
    var executeState = false;
    $("#btnExecute").linkbutton({
        onClick: function() {
            // 添加遮罩
            ajaxLoading();
            if ($('#bzmc').textbox('getValue').length > 50) {
                parent.$.messager.alert('错误', '步骤名称过长，最长可输入50位，请重新输入', 'error', function(){
                    $("#bzmc").next().children().focus();
                });
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            // 默认输入要素（以上各个节点的输入、输出）
            var srys = qjscsrys;
            // 删除系统流水号
            //delete srys['SYS_XTLSH']; ( zcl 2015-09-01 屏蔽， 保证一次单步调试只产生一条交易流水 )
            $('input[data-yslx=sr]').each(function() {
                var $this = $(this);
                srys[$this.data('jdysbm')] = $this.val()
                                    .replace(/\\n/g, "\n")
                                    .replace(/\\r/g, "\r")
                                    .replace(/\\t/g, "\t");
                $('input[data-yslx="hidden_sr"][data-jdysbm="' + $this.data('jdysbm') + '"]').val($this.val());
            });
            
            // 选择的Demo
            var demojbxxid = $('#txtDemojbxxidSelected').val();
            var data = {
                "ywid": parent.$('#ywid').val(),
                "demojbxxid": demojbxxid,
                "nodeid": $('#nodeid').val(),
                "lcid": parent.$('#id').val(),
                "type": $('#type').val(), // 节点类型 jd/zlc
                "lx": parent.$('#lx').val(), // 流程类型 lc/zlc
                'srys': JSON.stringify(srys)
            };
            
            $.ajax({
                type: "POST",
                dataType: "json",
                url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_execute_view",
                data: data,
                success: function(data) {
                    executeState = data.state;
                    if (data.state) {
                        // 执行成功 SYS_XYM == '000000'
                        var SYS_JYJDZXJG = data.trans_dict.SYS_JYJDZXJG;
                        $('#fhz').val(SYS_JYJDZXJG == null ? 'None' : SYS_JYJDZXJG);
                        var fhz_radio = $('input.fhz_radio[value="' + SYS_JYJDZXJG + '"]').get(0);
                        if (fhz_radio) {
                            fhz_radio.checked = true;
                        }
                        var node = parent.$('#workflow div[data-nodeid="' + $('#nodeid').val() + '"]');
                        // 启用“下一步”按钮
                        if (node.data('type') != 'end_jy') {
                            $('#btnNext').linkbutton('enable');
                        }
                        // 启用“查看单步调试记录”按钮
                        $('#btnDbtsjl').linkbutton('enable');
                        //parent.$.messager.alert('提示', data.msg, 'info');
                    } else {
                        // 执行失败 SYS_XYM != '000000'
                        //parent.$.messager.alert('错误', data.msg, 'error');
                    }
                    // 提示信息
                    afterAjax(data, '', '', parentType = true);
                    
                    var bm_arr = [];
                    for (var bm in data.trans_dict) {
                        bm_arr.push(bm);
                    }
                    
                    var scys_arr = [];
                    for (var i in data.scys) {
                        scys_arr.push(data.scys[i]['bm']);
                    }
                    // 排序（节点输出要素排最前，然后是响应码、响应内容、交易跟踪节点、其他）
                    bm_arr.sort(function(x, y) {
                        // 如果x是节点输出要素，y不是
                        if ($.inArray(x, scys_arr) >= 0 && $.inArray(y, scys_arr) == -1)
                            return -1;
                        // 如果x不是节点输出要素，y是
                        if ($.inArray(x, scys_arr) == -1 && $.inArray(y, scys_arr) >= 0)
                            return 1;
                        // 如果x是响应码、相应内容，y不是
                        if ($.inArray(x, ['SYS_RspCode','SYS_RspInfo']) >= 0 && $.inArray(y, ['SYS_RspCode','SYS_RspInfo']) == -1)
                            return -1;
                        // 如果x不是响应码、相应内容，y是
                        if ($.inArray(x, ['SYS_RspCode','SYS_RspInfo']) == -1 && $.inArray(y, ['SYS_RspCode','SYS_RspInfo']) >= 0)
                            return 1;
                        // 如果x是交易跟踪节点，y不是
                        if (x == 'SYS_JYJDGZ' && y != 'SYS_JYJDGZ')
                            return -1;
                        // 如果x不是交易跟踪节点，y是
                        if (x != 'SYS_JYJDGZ' && y == 'SYS_JYJDGZ')
                            return 1;
                        // 其他
                        if (x < y)
                            return -1;
                        if (x > y)
                            return 1;
                    });
                    
                    var dgData = [];
                    var bm = null;
                    var value = null;
                    for (var i in bm_arr) {
                        bm = bm_arr[i];
                        // 去掉'SYS_CLBZ', 'SYS_DZXJDDM', 'SYS_ISDEV', 'SYS_ZLCDEV', 'SYS_JYLX', 'msgxh'
                        if ($.inArray(bm, ['SYS_CLBZ', 'SYS_DZXJDDM', 'SYS_ISDEV', 'SYS_ZLCDEV', 'SYS_JYLX', 'msgxh']) == -1) {
                            value = data.trans_dict[bm] === null ? 'None' : data.trans_dict[bm];
                            dgData.push({jdysbm: bm, value: value});
                        }
                    }
                    // 加载到输出要素列表中
                    $('#datagrid_scys').datagrid('loadData', dgData);
                    
                    var val = null;
                    for (var i in bm_arr) {
                        bm = bm_arr[i];
                        if ($.type(data.trans_dict[bm]) == 'string') {
                            val = data.trans_dict[bm]
                                        .replace(/\n/g, "\\n")
                                        .replace(/\r/g, "\\r")
                                        .replace(/\t/g, "\\t");
                        }
                        $('input[data-yslx="sc"][data-jdysbm="' + bm + '"]').val(data.trans_dict[bm]);
                        $('input[data-yslx="sc"][data-jdysbm="' + bm + '"]').prev().text(val);
                    }
                    
                    $('#log_lsh').val(data.trans_dict.SYS_XTLSH || '');
                    // 启用“日志”按钮
                    $('#btnViewlog').linkbutton('enable');
                    // 当demoid有值时才往demoids放，要不然很多垃圾的空字符串
                    if (demojbxxid != "" && demojbxxid != null){
                        demoids.push(demojbxxid);
                    }
                }
            });
        }
    });
    
    parent.$("#winDbts").window({
        onClose: function() {
            if (bz_bjids.length == 0 && demoids.length == 0) {
                return false;
            }
            var bzids = [];
            for (var i in bz_bjids) {
                bzids.push(bjid_bzid_map[bz_bjids[i]]);
            }
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/del_dbts_view",
                data: {
                    "bzids": JSON.stringify(bzids),
                    "demoids": JSON.stringify(demoids)
                },
                success: function(data) {

                }
            });
        }
    });

    $('#btnViewlog').linkbutton({
        onClick: function() {
            $.ajax({
                type: "GET",
                dataType: "json",
                url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_log_view",
                data: {
                    "log_lsh": $('#log_lsh').val()
                },
                success: function(data) {
                    if (data.state) {
                        parent.$("#divLog").find('pre').text(data.log);
                        parent.newWindow(parent.$("#divLog"), '日志', 860, 480);
                    } else {
                        //parent.$.messager.alert('错误', data.msg, 'error');
                        // 提示信息
                        afterAjax(data, '', '', parentType = true);
                    }
                }
            });
        }
    });

    $('#btnDbtsjl').linkbutton({
        onClick: function() {
            if ($('#bzmc').textbox('getValue') == '') {
                parent.$.messager.alert('错误', '步骤名称不可为空，请输入', 'error', function(){
                    $("#bzmc").next().children().focus();
                });
                return false;
            }
            var fhz = $('#fhz').val();
            // 保存当前步骤
            if (fhz != '' && !demo_save_step(fhz)) {
                parent.$.messager.alert('错误', '当前步骤保存失败，无法查看单步调试记录', 'error');
                return false;
            } else if ($('#bzmc').textbox('getValue').length > 50) {
                parent.$.messager.alert('错误', '步骤名称过长，最长可输入50位，请重新输入', 'error', function(){
                    $("#bzmc").next().children().focus();
                });
                return false;
            }
            var bzids = [];
            for (var i in bz_bjids) {
                bzids.push(bjid_bzid_map[bz_bjids[i]]);
            }
            parent.newWindow(parent.$('#winDbtsjl'), "单步调试节点记录", 960, 500);
            parent.$('#winDbtsjl iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbtsjl_view?lcid=" + parent.$('#id').val() + "&lx=" + parent.$('#lx').val() + "&bz_bjids=" + bz_bjids.join(',') + "&bzids=" + bzids.join(',');
        }
    });

});
