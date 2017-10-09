/**
 * Created by Bianl on 2014/4/20.
 * 即时执行函数
 * 主div：id=main
 * 容器：id=workflow class=workflow
 * html如下：
    <!-- 工作流程图 -->
    <div id="main">
        <h2 id="name">流程图名称</h2>
        <div class="workflow" id="workflow"></div>
    </div>
 *
 * 动态节点的html标签表示：
    <div class="node">
        <span>节点名称</span>
        <div class="ep"></div>
    </div>
 *
 * 创建工作流
 *
 */

// jsPlumb实例
var instance = null;
// 最后激活的node节点
var lastActiveNode = null;
//当前选择demo按钮的id,用来标识选择的是单个插入demo还是批量插入
var demoSelID = '';
$(function() {

    $('<form id="form11" data-index="10"><div id="searchbox" style="position:absolute;top:3px;right:13px;width:180px;">' +
            '<select id="cb_yw" style="width:68px;height:29px;"></select> ' +
            '<input id="sb_yw" style="margin-left:10px;width:80px;height:27px;"/>' +
            '</div></form>')
        .appendTo(
            $("div.layout-panel-west > .panel-header > .panel-title")[0]
        );
    var yws = [{
        value: '全部',
        text: '全部'
    },{
        value: '基础库',
        text: '基础库'
    },{
        value: 'BEAI通讯',
        text: 'BEAI通讯'
    }];
    for (var i in ywmc_arr) {
        yws.push({
            value: ywmc_arr[i],
            text: ywmc_arr[i]
        });
    }
    $('#cb_yw').combobox({
        data: yws,
        editable: false,
        // panelHeight: 'auto',
        onChange: onChangeYW,
        multiple: true,
        width: 50,
        height: 29,
        onLoadSuccess: function() {
            $('#cb_yw').combobox('setValues', ['基础库', 'BEAI通讯', $("#ywmc").val()]);
        }
    }).combobox('panel').css({
        'height': 'auto',
        'max-height': '200px'
    });

    $('#sb_yw').searchbox({
        searcher: doSearch,
        prompt: '输入关键词'
    });

    var filterflag = false;


    // value 值
    function onChangeYW(value) {
        filterflag = true;
        var sel_val = $.trim(value);
        var search_value = $.trim($("#sb_yw").val());
        searchFilter(sel_val, search_value);
        filterflag = false;
    }

    function doSearch(value) {
        filterflag = true;
        var sel_val = $.trim($("#cb_yw").combobox('getValues'));
        var search_value = $.trim(value);
        searchFilter(sel_val, search_value);
        filterflag = false;
    }

    /**
     * @param arr type:[] 原数组
     * @param indexs type:[] 由arr数组的索引组成的数组
     * @returns type:{}
     */
    function getObjByIndex(arr, indexs) {
        var new_obj = {};
        $.each(indexs, function(i, index) {
            new_obj[index] = arr[index];
        });
        return new_obj;
    }

    /**
     * 过滤函数
     * @param index
     * @param panel
     */
    function handleFilter(index, panel, search_value) {
        var nodes = panel.children('.node');
        // var j_indexs = [];
        // if (!nodes.length) {
        //     panel.closest('.panel').hide();
        //     return;
        // }
        // 打开所有的库
        // 打开再过滤
        // console.log(search_value)
        if (search_value) {
            $("#menu").accordion("select", parseInt(index));
        }
        // 遍历panel下的所有节点，不符合的隐藏，符合的显示
        $.each(nodes, function(j, node) {
            var node_text = $.trim(node.innerText);
            if(node_text.indexOf(search_value) == -1) {
                $(node).hide();
            } else {
                $(node).show();
                // j_indexs.push(j);
            }
        });
        // if (!j_indexs.length) {
        //     // 隐藏过滤后隐藏所有子节点的库
        //     panel.closest('.panel').hide();
        // }
    }

    function whenEnd(search_value, indexs) {
        var $menu = $("#menu");
        var panels = $menu.accordion("panels");
        if(!search_value) {
            $.each(indexs=='all' ? panels : getObjByIndex(panels, indexs), function(i, panel) {
                0 == i ?
                    $menu.accordion("select", parseInt(i)) :
                    $menu.accordion("unselect", parseInt(i));
            });
        }
    }

    function searchFilter(sel_val, search_value) {
        // set jQuery对象
        var $menu = $("#menu");
        // 得到所有的panels
        var panels = $menu.accordion("panels");
        // 节点库多选 类型数组
        var node_arr = null;
        // 业务id
        var ywid = $("#ywid").val();
        // 记录显示的索引
        var indexs = [];
        // 转化sel_val为数组
        if (!sel_val) {
            node_arr = [];
        } else {
            node_arr = sel_val.split(',');
        }
        // console.log(node_arr)
        // 包含全部?
        var is_all = sel_val.indexOf("全部") !== -1;
        // 第一步,所有的都库都隐藏
        $menu.children('.panel').hide();
        // 第二步,根据不同的条件进行显示
        // -----------------------------
        // 当node_arr==[]
        // 即初始化 - 基础库、BEAI通讯、本业务通讯库、本业务业务库
        if(node_arr.length===0) {
            // 索引第0,1显示
            panels[0].closest('.panel').show();
            indexs.push(0);
            panels[1].closest('.panel').show();
            indexs.push(1);
            // 通过遍历,找到本业务通讯库和本业务业务库
            for(var i=2, len=panels.length; i<len; i++) {
                if (ywid === panels[i].data('ywid')) {
                    panels[i].closest('.panel').show();
                    indexs.push(i);
                }
            }
            // 处理search_value
            $.each(getObjByIndex(panels, indexs), function(i, panel) {
                handleFilter(i, panel, search_value);
            });
            whenEnd(search_value, indexs);
        }
        // 当node_arr数组非空
        if(node_arr.length) {
            if(is_all) {
                // 有all,展示全部
                $.each(panels, function(i, panel) {
                    panel.closest('.panel').show();
                    handleFilter(i, panel, search_value);
                });
                whenEnd(search_value, 'all');
            } else {
                // 非all
                // console.log('非all')
                $.each(node_arr, function(i, node_name) {
                    if ("基础库" == node_name) {
                        panels[0].closest('.panel').show();
                        indexs.push(0);
                    } else if ("BEAI通讯" == node_name) {
                        panels[1].closest('.panel').show();
                        indexs.push(1);
                    } else if($("#ywmc").val() == node_name) {
                        for(var n=2, len=panels.length; n<len; n++) {
                            if (ywid === panels[n].data('ywid')) {
                                panels[n].closest('.panel').show();
                                indexs.push(n);
                            }
                        }
                    } else {
                        $.each(panels, function(i, panel) {
                            var text = '';
                            if (i > 1) {
                                text = panels[i].prev().find(".panel-title").text();
                                if (text.indexOf(node_name) != -1) {
                                    panels[i].closest('.panel').show();
                                    indexs.push(i);
                                }
                            }
                        });
                    }
                });
                // 处理search_value
                $.each(getObjByIndex(panels, indexs), function(i, panel) {
                    handleFilter(i, panel, search_value);
                });
                whenEnd(search_value, indexs);
            }
        }
    }

    var win = window;
    // 可拖拽的节点的css样式
    var nodeStyle = ".node";
    var nodeStyle1 = ".node1";
    // delete icon
    var delete_icon = 'i.icon-delete';
    // 拖出线和箭头的点
    var ep = '.ep';

    // 节点容器id【jsPlumb默认值Container使用-用作id=workflow】
    var nodeContainer = 'workflow';
    // 节点容器jQuery对象
    var $nodeContainer = $('#' + nodeContainer);
    // 容器内的后代【node】的样式选择器 如 【#workflow .node】
    var nodeSelector = "#" + nodeContainer + " " + nodeStyle1;

    // 可拖拽的节点id和jQuery对象
    var menu = 'menu';
    var acceptNodeSelector = '#' + menu + ' > .node';
    var $menu = $('#' + menu);
    var $node = $('>' + nodeStyle, $menu);

    $menu.accordion({
        // 节点库刷新
        onSelect: function(title, index) {
            var search_value = $.trim($("#sb_yw").val());
            if (title == '基础库') {
                if (!search_value) {
                    $("#menu").accordion("getPanel", 0).find('.node').show();
                }
                return false;
            }
            var panel = $menu.accordion('getPanel', index);
            var type = panel.data('type');
            var ywid = panel.data('ywid');
            $.ajax({
                type: 'GET',
                dataType: 'json',
                url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/repository_data_view",
                data: {
                    type: type,
                    ywid: ywid
                },
                success: function(data) {
                    var node_html = '';
                    $(data).each(function() {
                        if (this.type == 'zlc') {
                            node_html += '<div class="node" nodestyle="b" data-nodeid="' + this.id + '" data-type="zlc" data-saved="1" myhide="0"> ' +
                                '<i class="ico-mn-left-2"></i> ' +
                                '<span>' + this.mc + '</span> ' +
                                '</div>';
                        } else {
                            node_html += '<div class="node" nodestyle="a" data-nodeid="' + this.id + '" data-saved="1" data-wym="' + this.wym1 + '" data-wym_bbk="' + (this.wym2 || '') + '" myhide="0"> ' +
                                '<i class="ico-mn-left-1"></i> ' +
                                '<span>' + this.jdmc + '</span> ' +
                                '</div>';
                        }
                    });
                    panel.html(node_html);
                    initWorkflowMenu('menu');
                    // 添加过滤
                    var sel_val = $.trim($("#cb_yw").combobox('getValues'));
                    var search_value = $.trim($("#sb_yw").val());
                    if (filterflag || search_value) {
                        searchFilter(sel_val, search_value);
                    }
                }
            });
        }
    });

    // 节点
    var top = 0;
    var left = 0;

    function workflow(callback) {
        return new Workflow(callback);
    }

    function Workflow(callback) {
        // jsPlumb只有等到DOM初始化完成之后才能使用
        // 因此我们在以下代码中调用jsPlumb.ready方法
        var href = this;
        jsPlumb.ready(function() {
            // instances of jsPlumb
            // 获得jsPlumb实例
            workflow.instance = instance = jsPlumb.getInstance({
                // 给jsPlumb设一些默认值【公共值】
                // ---------------------
                // 【连接点】的默认形状
                Endpoint: ["Dot", {
                    radius: 2
                }],
                // 【覆盖物】
                ConnectionOverlays: [
                    ["Arrow", {
                        location: 1,
                        id: "arrow",
                        length: 14,
                        foldback: 0.8
                    }],
                    ["Label", {
                        label: "value",
                        id: "label",
                        cssClass: "aLabel"
                    }]
                ],
                //
                Container: nodeContainer
            });
            callback && callback.call(href);
        });
    };

    Workflow.fn = Workflow.prototype = {
        constructor: Workflow,
        name: 'xxxx',
        '网址': "xxxx",
        '版本': '0.1.0',
        '版权': 'xxxx',
        /**
         * 初始化菜单中的节点可以拖拽
         */
        'menu': function(menuId) {
            new initWorkflowMenu(menuId);
        }
    };

    /**
     * 从节点得到所有的线路（可能含有多个，需要看这个节点，连线的条数相对应）
     * @param node
     * @returns {Array}
     */
    win.getLineByNode = function(node) {
        var endPoints = [],
            lines = null;
        endPoints = instance.getEndpoints(node);
        if (endPoints && endPoints.length) {
            lines = [];
            $.each(endPoints, function(index, endPoint) {
                if (endPoint.connections && endPoint.connections.length) {
                    lines.push(endPoint.connections[0]);
                }
            });
        }
        return lines;
    };

    /**
     * 通过EndPoint找到从这个点出去的线
     * @param line
     * @returns {*}
     */
    win.setLineColor = function(line, colers) {
        if (line) {
            //#e5db3d 浅黄
            if (colers == undefined)
                colers = "#f00"
            line.setPaintStyle({
                strokeStyle: colers,
                lineWidth: 2
            });
        }
        return line;
    };

    /**
     * 恢复线的颜色
     * @param line
     */
    win.resetLineColor = function(line) {
        if (line) {
            line.setPaintStyle({
                strokeStyle: "#5c96bc",
                lineWidth: 2
            });
        }
        return line;
    };

    function initWorkflowMenu(menuId) {
        // 可拖拽的节点id和jQuery对象
        var menu = menuId;
        var acceptNodeSelector = '#' + menu + ' .node';
        var $menu = $('#' + menu);
        var $node = $(nodeStyle, $menu);

        // 菜单节点变成【可拖元素】
        $node.draggable({
            // proxy: 'clone',
            proxy: function(source) {
                var $source = $(source);
                var $div = $source.clone(false);
                // console.log($div);
                $div.appendTo('body');
                return $div;
            },
            revert: true,
            onDrag: function(e) {
                var data = e.data;
                left = data.left;
                top = data.top;
            }
        });

        // 拖拽出节点【创造节点】
        // 当拖出来一个div时 怎么让这个div能拖动并能拖出connector，该节点的双击还能定义属性
        // ================================================================================
        // 创建一个节点（创建操作：拖拽）
        // 容器支持节点拖拽到此处
        $nodeContainer.droppable({
            // 仅接受选择器【#node】的拖拽功能
            accept: acceptNodeSelector,
            onDrop: function(event, source) {
                var sd = $nodeContainer.offset();
                var helper = $(source);
                var nodestyle = helper.attr("nodestyle") ? helper.attr("nodestyle") : helper.parent().attr("nodestyle");
                var dragDiv = helper.clone(false);
                // 拖拽的位置还有的小的出入
                dragDiv.html("<i class='icon-delete workflow-delete workflow-hidden'></i><span>" + dragDiv.find('span').text() + "</span><div class='ep'></div>")
                    .css({
                        top: top - sd.top,
                        left: left - sd.left,
                        width: "auto" //这里把宽度设置成auto
                    })
                    .attr("id", new UUID().toString())
                    // 这里要删除这两个类 否则调用instance.draggable( selector );会报错...
                    .removeClass("ui-draggable ui-draggable-dragging").addClass("node1 theme_" + nodestyle).removeClass("node");
                $(this).append(dragDiv);
                jsPlumbInitAfter(dragDiv[0]);
                refreshNodeConnColor(dragDiv.data('nodeid'));
            }
        });
    };

    //单击
    $nodeContainer.on('click', nodeStyle1, function(e) {
        //双击也需要做的事情
        var $this = $(this),
            lines, line;
        //if ( lastActiveNode ) lastActiveNode.removeClass('active');
        //首先删除所有的属性
        $("div").removeClass("active");
        lastActiveNode = $this;
        $this.addClass('active');
        lines = getLineByNode(this);
    });

    // 监听所有节点的双击事件
    $nodeContainer.on('dblclick', nodeStyle1, jd_dblclick);

    function jd_dblclick() {
        var type = lastActiveNode.data('type') || 'jd';
        if (type == 'start_jy') {
            newWindow($('#divDajiebao'), '选择解包', 453, 225);
            $('#txtYwmc').textbox('setValue', $('#ywmc').val());
            $('#txtJymc').textbox('setValue', $('#mc').val());
            $('#divDajiebao span.djb').text('流程解包');
            $('#djblx').val('jb');
            refreshDjbjd('jb');
        } else if (type == 'end_jy') {
            newWindow($('#divDajiebao'), '选择打包', 453, 225);
            $('#txtYwmc').textbox('setValue', $('#ywmc').val());
            $('#txtJymc').textbox('setValue', $('#mc').val());
            $('#divDajiebao span.djb').text('流程打包');
            $('#djblx').val('db');
            refreshDjbjd('db');
        } else if (type == 'zlc') {
            zlc_ck();
        } else if (type == 'jd') {
            jd_upd();
        }
    }

    // 选择打包、选择解包 菜单
    $('#itemStartSelDb, #itemEndSelDb').click(function() {
        jd_dblclick();
    });

    $('#selLcdjb').combobox({
        onLoadSuccess: function() {
            $('#selAddDjbjd').css({
                'display': 'block'
            }).parent().css({
                'padding': '0',
                'line-height': '20px'
            });
        }
    });

    function refreshDjbjd(lx) {
        $('#selLcdjb').combobox('loadData', [{
            'id': '',
            'jdmc': '请选择'
        }]);
        var text = '新增流程打包';
        if ($('#djblx').val() == 'jb') {
            text = '新增流程解包';
        }
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/djbjd_data_view",
            data: {
                'lx': lx,
                'jyid': $('#id').val()
            },
            success: function(data) {
                data.unshift({
                    'id': '',
                    'jdmc': '请选择'
                });
                data.push({
                    'id': 'add_djbjd',
                    'jdmc': '<a href="javascript:;" id="selAddDjbjd" onclick="btnAddDjbjd(event)">' + text + '</a>'
                });
                $('#selLcdjb').combobox('loadData', data);
            },
            error: function() {
                errorAjax();
            }
        });
    }

    $('#lbtnDjbjdSubmit').click(function(e) {
        e.preventDefault();
        $("#divDajiebao").find('form').form('submit', {
            url: '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/set_djbjd_view',
            queryParams: {
                'lcid': $('#id').val(),
                'lcbm': $('#lcbm').val()
            },
            onSubmit: function(param) {
                var jdid = $("#selLcdjb").combobox("getValue");
                //非空判断
                if (jdid == "") {
                    $.messager.alert('错误', $('#divDajiebao span.djb').text() + '不可为空，请选择', 'error', function() {
                        $("#selLcdjb").next().children().focus();
                    });
                    return false;
                }
                //判断编辑的值在下拉框中是否存在
                if (jdid == null){
                     $.messager.alert('错误', $('#divDajiebao span.djb').text() + '选择有误，请重新选择', 'error', function() {
                        $("#selLcdjb").next().children().focus();
                    });
                    return false;
                }

                // 更新流程图中开始、结束节点的data-nodeid
                lastActiveNode.attr('data-nodeid', jdid);
                lastActiveNode.data('nodeid', jdid);
                return true;
            },
            success: function(data) {
                afterAjax(data, "", "divDajiebao");
            },
            error: function() {
                errorAjax();
            }
        });
    });

    $('#lbtnDjbjdCancel').click(function(e) {
        e.preventDefault();
        $("#divDajiebao").window('close');
    });

    $('#btnEditDjbjd').click(function() {
        var title = '编辑流程打包';
        var jdlx = '8';
        if ($('#djblx').val() == 'jb') {
            title = '编辑流程解包';
            jdlx = '9';
        }
        var nodeid = $('#selLcdjb').combobox('getValue');
        if (!nodeid) {
            $.messager.alert('错误', '请先选择节点再进行编辑', 'error');
            return false;
        }
        jd_new_edit(title, '', nodeid);
    });

    // 节点编辑window，关闭时刷新打解包列表
    $('#winNodeEdit').window({
        onClose: function() {
            refreshDjbjd($('#djblx').val());
        }
    });

    function jd_upd() {
        //newWindow($("#winNodeEdit"), '节点编辑', 900, 490);
        newWindow2($("#winNodeEdit"), '节点编辑', '85', 490);
        var nodeid = lastActiveNode.attr('data-nodeid') || '';
        $('#winNodeEdit iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?nodeid=" + nodeid + "&bjid=" + lastActiveNode.attr('id');
    }

    function zlc_ck() {
        newWindow($("#winCommon"), '子流程查看', 900, 490);
        $('#winCommon iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/zlc_index_view?zlcid=" + lastActiveNode.attr('data-nodeid');
    }

    // 鼠标进入节点
    $nodeContainer.on('mouseover', '>' + nodeStyle1, function(e) {
        $(this).find(delete_icon).removeClass('workflow-hidden');
    });

    // 鼠标离开节点
    $nodeContainer.on('mouseout', '>' + nodeStyle1, function(e) {
        $(this).find(delete_icon).addClass('workflow-hidden');
    });

    jdids_del = [];
    // 节点/子流程删除
    $nodeContainer.on('click', delete_icon, function(e) {
        var $target = $(this);
        var $node = $target.closest('.node1');
        removeNode($node.attr('id'));
    });
    
    // 节点/子流程删除
    $("#jd_del, #zlc_del").click(function() {
        removeNode(lastActiveNode.attr('id'));
    });
    
    function removeNode(id) {
        var $node = $('#' + id);
        if ($node.attr('data-nodeid') && $node.attr('data-type') != 'zlc') {
            jdids_del.push($node.attr('data-nodeid'));
        }
        win.workflow.instance.removeAllEndpoints(id);
        win.workflow.instance.remove(id);
    }
    
    $("#line_edit").on('click', function(e) {
        var component = $("#mm_line").data("component");
        // component.fire('dblclick');
        instance.fire("dblclick", component);
    });

    $("#line_del").on('click', function(e) {
        var component = $("#mm_line").data("component");
        instance.detach(component);
    });


    // 右击事件
    $nodeContainer.on('contextmenu', nodeStyle1, function(e) {
        // 剔除原有的右击事件
        e.preventDefault();
        // 选中
        $("div").removeClass("active");
        lastActiveNode = $(this);
        $(this).addClass('active');
        // 显示快捷菜单
        var type = $(this).data("type") || 'jd';
        if (type == "zlc") {
            $('#mm_zlc').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        } else if (type == "jd") {
            $('#mm_jd').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        } else if (type == "start_jy") {
            $('#mm_start').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        } else if (type == "end_jy") {
            $('#mm_end').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        }
        return false;
    });

    $nodeContainer.click(function(e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        var $labelInput = $('.connection-label', e.target);
        var value = null;
        var $target = null;
        var labelObject = null;
        if ($labelInput.length) {
            $target = $('#' + $labelInput.data('target'));
            labelObject = $target.data('labelObject');
            if (labelObject != null) {
                value = $labelInput.val();
                if (value === '') {
                    //labelObject.setLabel( $target.data('oldValue') );
                } else {
                    labelObject.setLabel(value);
                }
            }
            // 更新连线颜色
            updateItemConnColor($(labelObject.canvas).data('c'), value);
            $labelInput.remove();
        }
    });

    /**
     * 创建【工作流】
     * @param data
     * |- data.label 工作流名称
     * |- data.locations 工作流节点位置及属性
     * |- data.connector 工作流连接器
     */
    function createWorkflow(data) {
        // var
        var locations = data.locations;
        var connector = data.connector;
        var allNodesStrings = '';
        // check
        if (!locations || !connector) {
            return false;
        }
        // 遍历&&拼接所有节点
        $.each(locations, function(key, location) {
            var node_delete = (location["type"] != 'start_zlc' && location["type"] != 'start_jy' && location["type"] != 'end_zlc' && location["type"] != 'end_jy') ? '<i class="icon-delete workflow-delete workflow-hidden"></i>' : '';
            allNodesStrings += '<div class="node1 ' + location['class'] + '" id="' + key + '" data-nodeid="' + location['nodeid'] + '" data-type="' + location["type"] +
                '" data-saved="1" data-wym="' + location["wym"] + '" data-wym_bbk="' + (location["wym_bbk"] || '') + '" data-czpzid="' + (location["czpzid"] || '')
                + '" style="left:' + location['left'] + 'px; top:' + location['top'] + 'px;"' + '>' + node_delete + '<span>' + location["label"] +
                '</span><div class="ep"></div></div>';
        });
        // 向容器追加节点
        $nodeContainer.append(allNodesStrings);

        // 初始化&&渲染工作流图
        jsPlumbInitAfter(nodeSelector, connector, function() {
            $.each(connector, function(i, conns) {
                instance.bind('connection', instanceConnection);
                instance.connect({
                    source: conns.source,
                    target: conns.target
                });
                instance.unbind('connection', instanceConnection);
            });
        });

        // 监听connection线的连接
        function instanceConnection(info) {
            var index, label;
            if (connector && connector.length) {
                index = instance.getAllConnections().length - 1;
                label = connector[index].label;
                info.connection.getOverlay('label').setLabel(label || '');
            }
        }
        
        function instanceConnection2(info) {
            var type = $(info.source).data('type');
            if (type == 'start_jy' || type == 'start_zlc') {
                info.connection.getOverlay('label').setLabel('0');
            }
        }
        
        instance.bind('connection', instanceConnection2);
    }



    function instanceDblclick(c) {
        var labelObject = c.getOverlay('label');
        var labelElement = labelObject.canvas;
        var oldValue = labelObject.getLabel();
        labelObject.setLabel('');
        var $label = $(labelElement);
        $label.data('oldValue', oldValue);
        $label.data('labelObject', labelObject);
        $label.data('c', c);
        var $input = $('<input type="text" autocomplete="off" class="connection-label" maxlength="5" data-target="' + $label.attr('id') + '" ' +
            'value="' + oldValue + '" style="width: 50px;z-index:9999;">');
        $input.css({
            position: 'absolute',
            left: $label.css('left'),
            top: $label.css('top')
        });
        $label.after($input);
        $input.focus().select();
        $input.on('keypress keyup', function(e) {
            var valueNew = $(this).val();
            if (!valueNew) return;
            // 如果按键是回车
            if (e.which === 13) {
                labelObject.setLabel(valueNew);
                // 更新连线颜色
                updateItemConnColor(c, valueNew);
                valueNew = null;
                $input.remove();
            }
        });
    }

    function instanceContextmenu(component, originalEvent) {
        $('#mm_line')
            .data("component", component)
            .menu('show', {
                left: originalEvent.pageX,
                top: originalEvent.pageY
            });
        originalEvent.preventDefault();
    }

    /**
     * node节点初始化后 调用callback
     * @param selector
     * @param callback
     */
    function jsPlumbInitAfter(selector, connector, callback) {
        //
        var selector = instance.getSelector(selector);

        // 初始化 【元素】都可【拖动】...
        instance.draggable(selector);
        // 当connector被删除时，可以这么做： jsPlumb.bind('click', jsPlumb.detach)
        // 绑定一个dblclick事件到每一个connector；
        instance.unbind('dblclick', instanceDblclick);
        instance.bind('dblclick', instanceDblclick);

        instance.unbind("contextmenu", instanceContextmenu);
        instance.bind("contextmenu", instanceContextmenu);

        // add by bianl 2015-04-08 添加线拖拽到节点之前的事件
        // 返回true允许链接，返回false不允许链接
        // 为了解决，不允许链接自己的bug
        instance.bind("beforeDrop", function(params) {
            return params.sourceId != params.targetId;
        });

        // 绑定一个connector监听。注意传递的参数info不只包含connector（新连接）
        // 这个监听设置新连接的id做为标签的文本显示
        // instance.unbind('connection', instanceConnection);
        // instance.bind('connection', instanceConnection);
        // This function abstracts out the pattern of suspending drawing, doing something, and then re-enabling drawing
        instance.batch(function() {
            // 使每一个.ep的div是一个source，我们用Continuous anchor和StateMachine connectors
            // 我们提供connector的paint style。注意在这个例子中strokeStyle是动态的，这会阻止我们去默认设置
            // jsPlumb.Defaults.PaintStyle拿默认值。
            // 我们使用了filter选项告诉jsPlumb，元素的一部分应该响应拖拽的起点
            instance.makeSource(selector, {
                filter: ep,
                anchor: "Continuous",
                connector: ["StateMachine", {
                    curviness: 20
                }],
                connectorStyle: {
                    strokeStyle: "#5c96bc",
                    lineWidth: 2,
                    outlineColor: "transparent",
                    outlineWidth: 4
                },
                maxConnections: 5
                // ,
                // onMaxConnections: function(info, e) {
                //     alert("Maximum connector (" + info.maxConnections + ") reached");
                // }
            });
            // 初始化所有的 ".node" 元素 是connector targets
            instance.makeTarget(selector, {
                dropOptions: {
                    hoverClass: "dragHover"
                },
                anchor: "Continuous"
            });
            callback && callback(instance);
        });
        
        // 监听connection线的连接
        function instanceConnection(info) {
            console.log(info);
        }
    }

    /**
     * 获取流程图中的所有节点，包含坐标、节点类型(jd/zlc)等
     */
    function getAllNodes() {
        var blocks = []
        $("#workflow .node1").each(function(idx, elem) {
            var $elem = $(elem);
            blocks.push({
                bjid: $elem.attr('id'),
                nodeid: $elem.data('nodeid'),
                label: $elem.find('span').text(),
                x: parseInt($elem.css("left"), 10),
                y: parseInt($elem.css("top"), 10),
                type: $elem.data('type') || 'jd',
                saved: $elem.data('saved')
            });
        });
        return blocks;
    }

    /**
     * 获取流程图中的所有节点的走向关系
     */
    function getAllConns() {
        var conns = [];
        $.each(instance.getAllConnections(), function() {
            conns.push({
                target: this.targetId,
                source: this.sourceId,
                label: this.getOverlay('label').getLabel()
            });
        });
        return conns;
    }

    var nodes = null;
    var conns = null;
    workflow(function() {
        this.menu('menu');
        // ajax 得到数据后 渲染成图
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_004/kf_ywgl_004_view/data_view",
            data: {
                "lx": $("#lx").val(),
                "id": $("#id").val()
            },
            success: function(data) {
                for (var id in data[0]) {
                    var type = data[0][id]["type"];
                    if (type == "start_zlc" || type == "start_jy") {
                        data[0][id]["class"] = "theme_start";
                    } else if (type == "end_zlc" || type == "end_jy") {
                        data[0][id]["class"] = "theme_end";
                    } else if (type == "zlc") {
                        data[0][id]["class"] = "theme_b";
                    } else {
                        data[0][id]["class"] = "theme_a";
                    }
                };
                // 先设置一个flow_data包括 connector和locations
                flow_data = {
                    locations: data[0],
                    connector: data[1]
                };
                createWorkflow(flow_data);
                nodes = getAllNodes();
                conns = getAllConns();
                window.locations = data[0];
                // 遍历所有的连接线
                $.each(instance.getAllConnections(), function() {
                    // 前置节点的返回值列表
                    var fhz_arr = data[0][this.sourceId]['fhz'];
                    var type = data[0][this.sourceId]['type'];
                    // 如果不是开始节点，且返回值不在返回值列表中，则变为红线
                    if (type != 'start_jy' && type != 'start_zlc' && fhz_arr.indexOf(this.getOverlay('label').getLabel()) < 0) {
                        setLineColor(this);
                        $(this.canvas).ttip({
                            msg: '前置节点无此返回值',
                            ttipEvent: 'h'
                        })
                    }
                });
            },
            error: function() {
                errorAjax();
            }
        });
    });

    win.workflow = workflow;

    // 节点测试案例
    $("#start_csal, #end_csal, #jd_csal, #zlc_csal").click(function() {
        if (lastActiveNode.data('saved') != '1') {
            $.messager.alert('错误', '节点未保存，无法查看测试案例！', 'error');
            return false;
        }
        newWindow($("#winCommon"), $(this).text(), 1300, 490);
        var lx = lastActiveNode.data('type') == 'zlc' ? 'zlc' : 'jd';
        var lxmc = lx == 'jd' ? '节点' : '子流程';
        var nodeid = lastActiveNode.data('nodeid') || '';
        var text = lastActiveNode.text();
        $('#winCommon iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_zdcs_csal_view/index_view?lx=" + lx + "&csaldyssid=" + nodeid + "&text=" + text + "&lxmc=" + lxmc;
    });
    // 节点编辑
    $("#jd_upd").click(jd_upd);
    // 子流程查看
    $("#zlc_ck").click(zlc_ck);

    //单步调试
    $("#jd_dbgz, #zlc_dbgz, #btnJdDbts, #itemStartDbgz, #itemEndDbgz").click(function() {
        var nodes_now = getAllNodes();
        var nodes_old = $.extend(true, [], nodes);
        // 不比较位置坐标
        $.each(nodes_now, function() {
            this.x = null;
            this.y = null;
        });
        $.each(nodes_old, function() {
            this.x = null;
            this.y = null;
        });
        if (!compare(nodes_old, nodes_now) || !compare(conns, getAllConns())) {
            // 所做修改未保存
            $.messager.alert('错误', '请先保存流程，再进行单步调试！', 'error');
            return false;
        }
        if ($('#workflow div[data-type="start_jy"]').data('nodeid') == '' || $('#workflow div[data-type="end_jy"]').data('nodeid') == '') {
            // 是否设置打解包节点
            $.messager.alert('错误', '请先设置打解包节点，再进行单步调试！', 'error');
            return false;
        }
        if (!lastActiveNode || ['start_zlc', 'end_zlc'].indexOf(lastActiveNode.data('type')) >= 0 || $('#' + lastActiveNode.attr('id')).length == 0) {
            var bjid = $("div[data-type='start_jy']").attr('id');
            if (!bjid) {
                var start_bjid = $("div[data-type='start_zlc']").attr('id');
                $.each(getAllConns(), function() {
                    if (this.source == start_bjid) {
                        bjid = this.target;
                        return false;
                    }
                });
            }
            if (!bjid) {
                $.messager.alert('错误', '请先保存正确的流程，再进行单步调试！', 'error');
                return false;
            }
            setActiveNode(bjid);
        }
        newWindow($("#winDbts"), "单步调试", 300, 485, 0, null);
        var nodeid = lastActiveNode.data('nodeid');
        var type = lastActiveNode.data('type') || 'jd';
        var ywid = $('#ywid').val();
        $('#winDbts iframe')[0].src = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/dbts_index_view?nodeid=' + nodeid + '&type=' + type + '&ywid=' + ywid;
        
        // 将demoid清空
        window.demoids = [];
    });

    // 与当前版本进行比对
    $("#start_ydqbbdb, #end_ydqbbdb, #jd_ydqbbdb").click(function() {
        if (lastActiveNode.data('saved') != '1') {
            $.messager.alert('错误', '节点未保存，无法进行版本比对！', 'error');
            return false;
        }
        if ((lastActiveNode.data('wym_bbk') || '') == '') {
            $.messager.alert('错误', '当前节点未提交过版本，无法与当前版本进行比对！', 'error');
            return false;
        }
        newWindow($("#winCommon"), "与当前版本进行比对", 1000, 495);
        var nodeid = lastActiveNode.data('nodeid');
        var lx = lastActiveNode.data('type') == 'zlc' ? 'zlc' : 'jd';
        $('#winCommon iframe')[0].src = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbdb_data_view?type=bd&lx=' + lx + '&id=' + nodeid;
    });

    // 节点提交版本
    $("#start_tjbb, #end_tjbb, #jd_tjbb").click(function(e) {
        if (lastActiveNode.data('saved') != '1') {
            $.messager.alert('错误', '节点未保存，无法进行版本提交！', 'error');
            return false;
        }
        // 判断唯一码是否变更
        var wym = lastActiveNode.data('wym');
        var wym_bbk = lastActiveNode.data('wym_bbk');
        if (wym == wym_bbk) {
            $.messager.alert('错误', '本地内容未修改，无法提交。', 'error');
        } else {
            var lx = $(e.target).data('type') == 'zlc' ? 'zlc' : 'jd';
            bbtj(lx, '0', lastActiveNode.data('nodeid'), 'jdbjtj');
        }
    });

    // 节点版本信息查看
    $("#start_bbxxck, #end_bbxxck, #jd_bbxxck").click(function(e) {
        if (lastActiveNode.data('saved') != '1') {
            $.messager.alert('错误', '节点未保存，无法查看版本信息！', 'error');
            return false;
        }
        var lx = $(e.target).data('type') == 'zlc' ? 'zlc' : 'jd';
        var mc = lastActiveNode.text();
        newTab(mc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=' + lx + '&id=' + lastActiveNode.data('nodeid'));
    });

    // 交易版本信息查看
    $('#btnLcBbck').click(function() {
        var lx = $('#lx').val() == 'zlc' ? 'zlc' : 'jy';
        var mc = $('#mc').val();
        newTab(mc + '_版本信息查看', '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbxxck_index_view?lx=' + lx + '&id=' + $('#id').val());
    });

    // 交易测试案例查看
    $('#btnLcCsal').click(function() {
        var lb = $('#lx').val() == 'zlc' ? '2' : '1';
        newWindow($("#winCommon"), "测试案例列表", 1270, 490);
        $('#winCommon iframe')[0].src = '/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/index_view?lb=' + lb + '&sslb=' + lb + '&ssid=' + $('#id').val();
    });

    window.tbsYwsjbData = [];
    $('#tbsYwsjb').tabs({
        onSelect: function(title, index) {
            // 渲染数据
            var iframeLength = $('#tbsYwsjb iframe').length;
            if (index < iframeLength) {
                $('#tbsYwsjb iframe')[index].contentWindow.$("#dgSjkbxxck").datagrid('reload');
            }
        }
    });

    // 获取表结构的信息
    window.keys = [];

    $("#btnLcSubmit").click(lcSubmit);

    /**
     * 流程保存
    */
    function lcSubmit() {
        // 添加遮罩
        ajaxLoading();
        var lx = $("#lx").val();
        var id = $("#id").val();
        var nodes_tmp = getAllNodes();
        var conns_tmp = getAllConns();
        for (var i in nodes_tmp) {
            if (nodes_tmp[i]['saved'] != "1") {
                $.messager.alert('错误', '新增节点未保存', 'error');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
        }
        // 是否设置打解包节点
        var jbnodeid = $('#workflow div[data-type="start_jy"]').data('nodeid');
        var dbnodeid = $('#workflow div[data-type="end_jy"]').data('nodeid');
        if (jbnodeid == '' && dbnodeid != '') {
            // 未设置解包节点
            $.messager.alert('错误', '交易开始节点还未配置解包节点，请先配置再保存流程', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        } else if (jbnodeid != '' && dbnodeid == '') {
            // 未设置打包节点
            $.messager.alert('错误', '交易结束节点还未配置打包节点，请先配置再保存流程', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        } else if (jbnodeid == '' && dbnodeid == '') {
            // 未设置打解包节点
            $.messager.alert('错误', '交易开始和结束节点还未配置打解包节点，请先配置再保存流程', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        // 开始节点的流程线只能一个，且返回值只能是0
        var start_bjid = $('#workflow div[data-type="start_jy"]').attr('id') || $('#workflow div[data-type="start_zlc"]').attr('id');
        var jbnodeid_conn = 0;
        for (var i in conns_tmp) {
            if (conns_tmp[i]['source'] == start_bjid) {
                jbnodeid_conn += 1;
                if (conns_tmp[i]['label'] != '0') {
                    jbnodeid_conn += 1;
                }
            }
            if (jbnodeid_conn > 1) {
                $.messager.alert('错误', '开始节点的流程线只能一个，且返回值只能是0', 'error');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
        }
        // 校验流程图中是否有没有连接线的节点
        var source = false;
        var target = false;
        for (var i in nodes_tmp) {
            source = false;
            target = false;
            for (var j in conns_tmp) {
                if (nodes_tmp[i]['type'] == 'end_jy' || nodes_tmp[i]['type'] == 'end_zlc' || nodes_tmp[i]['bjid'] == conns_tmp[j]['source']) {
                    source = true;
                }
                if (nodes_tmp[i]['type'] == 'start_jy' || nodes_tmp[i]['type'] == 'start_zlc' || nodes_tmp[i]['bjid'] == conns_tmp[j]['target']) {
                    target = true;
                }
            }
            if (!source || !target) {
                break;
            }
        }
        if (!source || !target) {
            $.messager.alert('错误', '流程中包含没有连接线的节点，请修改后再保存流程', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        // 校验流程图中是否有相同的节点
        node_arr = {};
        for (var i in nodes_tmp) {
            if (node_arr[nodes_tmp[i]['nodeid']]) {
                node_arr[nodes_tmp[i]['nodeid']]['count'] += 1;
                $.messager.alert('错误', '流程中不可多次调用同一个节点或子流程', 'error');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            } else {
                node_arr[nodes_tmp[i]['nodeid']] = {
                    'jdmc': nodes_tmp[i]['label'],
                    'count': 1
                };
            }
        }
        // 同一个节点的分支，不允许线上值有相同的情况
        count_arr = {};
        node_arr = [];
        for (var i in conns_tmp) {
            if (count_arr[conns_tmp[i]['source']] != undefined && count_arr[conns_tmp[i]['source']]['label'] == conns_tmp[i]['label']) {
                count_arr[conns_tmp[i]['source']]['count'] += 1;
                var jdmc = $('#workflow #'+conns_tmp[i]['source']).text();
                if ($.inArray(jdmc, node_arr) == -1) {
                    node_arr.push(jdmc);
                }
            } else {
                count_arr[conns_tmp[i]['source']] = {
                    'label': conns_tmp[i]['label'],
                    'count': 1
                };
            }
        }
        if (node_arr.length > 0) {
            $.messager.alert('错误', '['+node_arr.join(',')+ ']节点的分支上存在赋值相同的情况，请修正后再保存流程！', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        // 校验流程中存在异常走向的线
        if (updateConnColor(window.locations) > 0) {
            $.messager.alert('错误', '流程中存在异常走向的线（红色线），请重新编辑后再保存！', 'error');
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        var saved = false;
        $.ajax({
            async: false, // 使用同步方式
            type: 'POST',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/lc_save_view",
            data: {
                "lx": lx,
                "id": id,
                "lcbm": $('#lcbm').val(),
                "nodes": JSON.stringify(nodes_tmp),
                "conns": JSON.stringify(conns_tmp)
            },
            success: function(data) {
                if (data.state) {
                    nodes = getAllNodes();
                    conns = getAllConns();
                    $('#wym').val(data.wym);
                    $('#wym_bbk').val(data.wym_bbk);
                    if (jdids_del.length > 0) {
                        // 节点在页面中删除后，请求后台在表中删除此节点
                        //（不需要提示是否已删除，因为有可能节点被其他流程引用，而不进行删除操作）
                        $.ajax({
                            type: 'POST',
                            dataType: 'json',
                            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/jd_del_view",
                            data: {
                                "jdids": JSON.stringify(jdids_del),
                                'lcid': id
                            },
                            success: function(data) {
                                jdids_del = [];
                            }
                        });
                    }
                    saved = true;
                    updateConnColor(window.locations);
                }
                afterAjax(data, "", "");
            },
            error: function() {
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
        return saved;
    }

    $('#txtCaslmc').next().children().attr("maxlength", "50");
    $('#txtCaslms').next().children().attr("maxlength", "100");
    // 执行步骤ID列表
    window.bzids = [];
    // DemoID列表
    window.demoids = [];
    // 当前要保存节点测试案例的节点定义ID
    window.nodeid = '';
    // 当前要保存节点测试案例的DemoID
    window.demoid = '';
    // 当前要保存节点测试案例的步骤ID
    window.bzid = '';
    // 保存测试案例类型（jd节点 lc流程）
    window.casl_lx = '';
    $("#btnSubmitSaveCsal").click(function(e) {
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        var queryParams = {};
        var url = '';
        if (casl_lx == 'jd') {
            url = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/save_jdcsal_view';
            // 节点类型
            var type = $('#workflow div[data-nodeid="' + nodeid + '"]').data('type');
            type = type == 'zlc' ? 'zlc' : 'jd';
            queryParams = {
                'nodeid': nodeid,
                'ywid': $('#ywid').val(),
                'lb': '3',
                'type': type,
                'lcid': $('#id').val(),
                'demoid': demoid,
                'bzid': bzid
            };
        } else {
            url = '/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/save_csal_view';
            queryParams = {
                'lcid': $('#id').val(),
                'lx': $('#lx').val(),
                'ywid': $('#ywid').val(),
                'demoids': JSON.stringify(demoids),
                'bzids': JSON.stringify(bzids)
            };
        }
        $("#divSaveCsal").find('form').form('submit', {
            url: url,
            queryParams: queryParams,
            onSubmit: function(param) {
                var mc = $("#txtCaslmc").textbox("getValue");
                if (mc == "") {
                    $.messager.alert('错误', '测试案例名称不可为空，请输入', 'error', function() {
                        $("#txtCaslmc").next().children().focus();
                    });
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                return true;
            },
            success: function(data) {
                // 取消遮罩，提示信息，关闭窗口
                afterAjax(data, '', 'divSaveCsal');
            },
            error: function() {
                errorAjax();
            }
        });
    });

    $("#btnCancelSaveCsal").click(function(e) {
        e.preventDefault();
        $('#divSaveCsal').window('close');
    });

    // 交易版本提交
    $('#btnLcCommit').click(function() {
        // 判断当前的流程图是否有修改未保存
        if (compare(nodes, getAllNodes()) && compare(conns, getAllConns())) {
            // 已经保存，然后判断唯一码是否变更
            if ($('#wym').val() == $('#wym_bbk').val()) {
                $.messager.alert('错误', '本地内容未修改，无法提交。', 'error');
            } else {
                var lx = $('#lx').val() == 'lc' ? 'jy' : 'zlc';
                bbtj(lx, '0', $('#id').val(), 'lcbjtj');
            }
        } else {
            // 所做修改未保存
            $.messager.alert('错误', '请先保存流程，再进行版本提交！', 'error');
        }
    });

    /**
     * 判断Object、Array、Function等引用类型对象是否相等
     */
    function compare(a, b) {
        var pt = /undefined|number|string|boolean/,
            fn = /^(function\s*)(\w*\b)/,
            cr = "constructor",
            cn = "childNodes",
            pn = "parentNode",
            ce = arguments.callee;
        if (pt.test(typeof a) || pt.test(typeof b) || a === null || b === null) {
            return a === b || (isNaN(a) && isNaN(b)); //为了方便，此处假定NaN == NaN 
        }
        if (a[cr] !== b[cr]) {
            return false;
        }
        switch (a[cr]) {
            case Date: {
                    return a.valueOf() === b.valueOf();
                };
            case Function: {
                    return a.toString().replace(fn, '$1') === b.toString().replace(fn, '$1'); //硬编码中声明函数的方式会影响到toString的结果，因此用正则进行格式化 
                };
            case Array: {
                    if (a.length !== b.length) {
                        return false;
                    }
                    for (var i = 0; i < a.length; i++) {
                        if (!ce(a[i], b[i])) {
                            return false;
                        }
                    }
                    break;
                };
            default: {
                    var alen = 0,
                        blen = 0,
                        d;
                    if (a === b) {
                        return true;
                    }
                    if (a[cn] || a[pn] || b[cn] || b[pn]) {
                        return a === b;
                    }
                    for (d in a) {
                        alen++;
                    }
                    for (d in b) {
                        blen++;
                    }
                    if (alen !== blen) {
                        return false;
                    }
                    for (d in a) {
                        if (!ce(a[d], b[d])) {
                            return false;
                        }
                    }
                    break;
                };
        }
        return true;
    }

    /**
     * 关闭流程编辑功能Tab时弹窗提示
     */
    function close_confirm(target, index) {
        var opts = target.tabs('options');
        var bc = opts.onBeforeClose;
        if (!compare(nodes, getAllNodes()) || !compare(conns, getAllConns())) {
            $.messager.confirm('提示', '保存更改吗？', function(r) {
                if (!r || (r && lcSubmit())) {
                    opts.onBeforeClose = function() {}; // 允许现在关闭
                    target.tabs('close', index);
                    opts.onBeforeClose = bc; // 还原事件函数
                }
            });
        } else {
            opts.onBeforeClose = function() {}; // 允许现在关闭
            target.tabs('close', index);
            opts.onBeforeClose = bc; // 还原事件函数
        }
    }
    window.close_confirm = close_confirm;

    $('#btnDemoJbxxSubmit').click(function(e) {
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        var mc = $('#txtDemomc').val();
        var ms = $('#txtDemoms').val();
        if (!checkNull(mc, '名称', 'txtDemomc')) {
            // 取消遮罩
            ajaxLoadEnd();
            return false;
        }
        $.ajax({
            type: "POST",
            dataType: "json",
            url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_jbxx_data_add_view",
            data: {
                "id": $('#txtDemoid').val(),
                "mc": $('#txtDemomc').textbox('getValue'),
                "ms": $('#txtDemoms').textbox('getValue'),
                "ywid": $('#ywid').val()
            },
            success: function(data) {
                if (data.state) {
                    $('#txtDemoid').val(data.demo_id);
                    $("#tbsDemo").tabs('enableTab', 1);
                    $('#dgDemo').datagrid('reload');
                    // 初始化表信息
                    $('#comboYwsjb').combobox({
                        onSelect: function(record){
                            $('#iframeYwsjb')[0].src = '/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/index_view?sjkmxdy_id='+record['sjkmxdyid']+'&lx=demo'+'&demojbxxid='+data.demo_id;
                        },
                        onLoadSuccess: function(record){
                            // 默认选中第一个
                            $('#comboYwsjb').combobox('select',$('#comboYwsjb').combobox('getData')[0].sjkmxdyid);
                        }
                    });
//                    // 数据表Tab刷新数据
//                    $('#tbsYwsjb iframe').each(function(){
//                        var $this = $(this);
//                        $this.attr('src', $this.data('src')+'&demojbxxid='+data.demo_id);
//                    });
                }
                afterAjax(data, '', '');
            }
        });
    });

    $('#btnDemoJbxxCancel').click(function(e) {
        e.preventDefault();
        $('#bean_window_add_demo').window('close');
    });
    
    // 最大值限制
    $("#txtDemomc").next().children().attr("maxlength", "50");
    $("#txtDemoms").next().children().attr("maxlength", "500");
    
    $('#btnSearch').click(function(e) {
        e.preventDefault();
        //查询事件
        doSearchBtn();
    });
    
    /**
     * 查询demo
     **/
    function doSearchBtn(){
        // demo名称
        var mc = $("#txtSearchMc").textbox('getValue');
        // demo描述
        var ms = $("#txtSearchMs").textbox('getValue');
        
        // 根据条件查询对象
        $("#dgDemo").datagrid('load',{
            mc: mc,
            ms: ms
        });
    }
    
    // 冲正配置
    // 选择冲正节点、子流程
    $('#cz_czpz').click(function() {
        var czpzid = lastActiveNode.data('czpzid');
        cz_czpz( czpzid );
    });
    
    $('#lbtnCzpzSubmit').click(function(e) {
        e.preventDefault();
        // 提交
        
        var nodes_now = getAllNodes();
        var nodes_old = $.extend(true, [], nodes);
        if (!compare(nodes_old, nodes_now)) {
            // 所做修改未保存
            $.messager.alert('错误', '请先保存流程，再进行单步调试！', 'error');
            return false;
        }
        // 节点或子流程id
        var nodeid = lastActiveNode.data('nodeid');
        // 步骤id
        var bzid = lastActiveNode.attr('id');
        // 节点类型
        var type = lastActiveNode.data('type') || 'jd';
        
        cz_czpz_sub( nodeid, bzid, type, lastActiveNode );
    });
    // 冲正配置取消按钮，关闭窗口
    $('#lbtnCzpzCancel').click(function(e) {
        e.preventDefault();
        $("#divPzcz").window('close');
    });
    
});

/**
 * 获取流程唯一码
 * 版本提交后调用
 */
function refreshWym() {
    var lx = $('#lx').val() == 'lc' ? 'jy' : 'zlc';
    var id = $('#id').val();
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/get_wym_view",
        data: {id: id, lx: lx},
        success: function(data) {
            if (data.state) {
                $('#wym').val(data.wym);
                $('#wym_bbk').val(data.wym_bbk);
            }
        }
    });
}

/**
 * 获取节点唯一码
 * 版本提交后调用
 */
function refreshJdWym() {
    var nodeid = lastActiveNode.data('nodeid');
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/get_wym_view",
        data: {id: nodeid, lx: 'jd'},
        success: function(data) {
            if (data.state) {
                var node = $('#workflow div[id][data-nodeid="' + nodeid + '"]');
                node.data('wym', data.wym);
                node.data('wym_bbk', data.wym_bbk);
            }
        }
    });
}

/**
 * 更新连接线颜色
 */
function refreshNodeConnColor(nodeid) {
    var $node = $('#workflow div[data-nodeid="' + nodeid + '"]');
    var type = $node.data('type') || 'jd';
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/get_node_fhz_view",
        data: {
            "nodeid": nodeid,
            "type": type
        },
        success: function(data) {
            var bjid = $node.attr('id');
            if (window.locations[bjid] == undefined) {
                window.locations[bjid] = {fhz: data['fhz'], type: type};
            } else {
                window.locations[bjid]['fhz'] = data['fhz'];
            }
            updateConnColor(window.locations);
        }
    });
}

function updateConnColor(data) {
    var i = 0;
    // 遍历所有的连接线
    $.each(instance.getAllConnections(), function() {
        // 前置节点的返回值列表
        var fhz_arr = (data[this.sourceId] || {fhz:[]})['fhz'];
        var type = (data[this.sourceId] || {type:''})['type'];
        // 如果不是开始节点，且返回值不在返回值列表中，则变为红线
        if (type != 'start_jy' && type != 'start_zlc' && fhz_arr.indexOf(this.getOverlay('label').getLabel()) < 0) {
            setLineColor(this);
            $(this.canvas).ttip({
                msg: '前置节点无此返回值',
                ttipEvent: 'h'
            });
            i++;
        } else {
            resetLineColor(this);
        }
    });
    return i;
}

function updateItemConnColor(conn, valueNew) {
    // 前置节点的返回值列表
    var fhz_arr = (window.locations[conn.sourceId] || {fhz:[]})['fhz'];
    var type = (window.locations[conn.sourceId] || {type:''})['type'];
    // 如果不是开始节点，且返回值不在返回值列表中，则变为红线
    if (type != 'start_jy' && type != 'start_zlc' && fhz_arr.indexOf(valueNew) < 0) {
        setLineColor(conn);
        $(this.canvas).ttip({
            msg: '前置节点无此返回值',
            ttipEvent: 'h'
        });
    } else {
        resetLineColor(conn);
    }
}

/**
 * 新增打解包节点
 */
function btnAddDjbjd(event) {
    event.stopPropagation();
    $('#selLcdjb').combobox('hidePanel');
    var jdlx = '8';
    if ($('#djblx').val() == 'jb') {
        jdlx = '9';
    }
    jd_new_edit($(event.target).text(), jdlx, '');
}

/**
 * 弹出节点新增/编辑窗口
 * title: 窗口标题
 * jdlx: 节点定义表中的lx
 * nodeid: 节点ID（为空时是新增）
 */
function jd_new_edit(title, jdlx, nodeid) {
    //newWindow($("#winNodeEdit"), title, 900, 490);
    newWindow2($("#winNodeEdit"), title, '85', 490);
    $('#winNodeEdit iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?jdlx=" + jdlx + "&nodeid=" + nodeid;
}

/**
 * 设置被选中的节点，会使流程图中节点的样式为选中状态
 * bjid: 布局ID
 */
function setActiveNode(bjid) {
    lastActiveNode = $('#' + bjid);
    $('#workflow div.node1').removeClass('active');
    $('#' + bjid).addClass('active');
}

/**
 * 编辑DEMO数据
 */
function updaterow_demo(id, index,demoSelBtnID) {
    // 记录用户点击的ann 
    demoSelID = demoSelBtnID;
    newWindow($("#bean_window_add_demo"), 'DEMO数据编辑', 600, 410);
    $("#tbsDemo").tabs('enableTab', 1);
    $("#tbsDemo").tabs('select', 0);
    var d = $('#' + id).datagrid('getData').rows[index];
    $("#txtDemoid").val(d.id);
    $("#txtDemomc").textbox('setValue', d.mc);
    $("#txtDemoms").textbox('setValue', d.sjms);
    // 单个demo录入
    if (demoSelBtnID == "btnSelectDemo"){
        // 选第一个数据表的Tab
        $('#tbsYwsjb').tabs('select', 0);
        
        $('#tbsYwsjb iframe').each(function(){
            var $this = $(this);
            $this.attr('src', $this.data('src')+'&demojbxxid='+d.id);
        });
    }
    // 批量demo录入
    if (demoSelBtnID == "btnSelectDemoPL"){
        $('#comboYwsjb').combobox({
            onSelect: function(record){
                $('#iframeYwsjb')[0].src = '/oa/kf_ywgl/kf_ywgl_012/kf_ywgl_012_view/index_view?sjkmxdy_id='+record['sjkmxdyid']+'&lx=demo'+'&demojbxxid='+d.id;
            },
            onLoadSuccess: function(record){
                // 默认选中第一个
                $('#comboYwsjb').combobox('select',$('#comboYwsjb').combobox('getData')[0].sjkmxdyid);
            }
        });
    }
    
}

/**
 * 删除DEMO数据
 * id: Demo基本信息ID
 */
function delete_demo(id) {
    $.messager.confirm("确认", '您确定要删除此Demo数据吗？', function(r) {
        if (r) {
            $.ajax({
                type: "POST",
                dataType: "json",
                url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_jbxx_data_del_view",
                data: {
                    "id": id
                },
                success: function(data) {
                    $("#datagrid_demo_ok").linkbutton('disable');
                    $('#txtDemojbxxidSelected').val('');
                    afterAjax(data, 'dgDemo', '');
                }
            });
        }
    });
}

/**
* 冲正配置页面初始化
*/
function cz_czpz( czpzid ){
    // 查询冲正配置：子流程信息
    $.ajax({
        type: 'post',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/get_czpz_view",
        data: {czpzlx: 'zlc'},
        success: function(data){
            if (data.state){
                // 打开选择页面
                newWindow($('#divPzcz'), '冲正配置', 453, 175);
                // 初始化冲正配置
                $('#selCzpzid').combobox({
                    editable:true,
                    data:data.czpz_lst,
                    valueField:'czpzid',
                    textField:'text',
                    onLoadSuccess: function(record){
                        // 默认选中第一个
                        $('#selCzpzid').combobox( 'select',czpzid );
                    }
                })
                
                // 冲正配置
                $("#hidCzpzid").val( czpzid );
                
                // tab顺
                $('#formPzcz').tabSort();
            }else{
                afterAjax( data, '', '' );
            }
        },
        error: function() {
            errorAjax();
        }
    });
}

/**
* 冲正配置提交
*/
function cz_czpz_sub( nodeid, bzid, type ){
    // 添加遮罩
    ajaxLoading();
    // 业务id
    var ywid = $('#ywid').val();
    var lx = $('#lx').val();
    // 交易子流程id
    var jy2zlcid = $("#id").val();
    // 请求url
    var url = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/czpz_sub_view";
    // 冲正配置
    var czpzid = $("#selCzpzid").combobox("getValue");
    // 参数
    queryParams = {
        'nodeid': nodeid,
        'bzid': bzid,
        'type': type,
        'ywid': ywid,
        'lx': lx,
        'jy2zlcid': jy2zlcid
    };
    // form 提交
    $("#formPzcz").form('submit', {
        url: url,
        queryParams: queryParams,
        onSubmit: function(param) {
//            var czpzid = $("#selCzpzid").combobox("getValue");
//            var ret = checkNull2( czpzid, '冲正配置', 'selCzpzid' );
//            if( ret == false ){
//                // 取消遮罩
//                ajaxLoadEnd();
//            }
            var ret = true;
            return ret;
        },
        success: function(data) {
            // 取消遮罩，提示信息，关闭窗口
            afterAjax( data, '', 'divPzcz' );
            // 保存成功
            data = $.parseJSON(data);
            if(data.state) {
                lastActiveNode.attr('data-czpzid', czpzid);
                lastActiveNode.data('czpzid', czpzid);
            }
            
        },
        error: function() {
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
    
}