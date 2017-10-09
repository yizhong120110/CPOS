/**
* 交易监控日志查看
*/
// jsPlumb实例
var instance = null;
// 最后激活的node节点
var lastActiveNode = null;
$(document).ready(function() {
    
    // 流程图展示
    !function ( $, win ) {
        // 可拖拽的节点的css样式
        var nodeStyle = ".node1";
        // delete icon
        var delete_icon = 'i.icon-delete';
        // 拖出线和箭头的点
        var ep = '.ep';
        // 节点容器id【jsPlumb默认值Container使用-用作id=workflow】
        var nodeContainer = 'divWorkflow';
        // 节点容器jQuery对象
        var $nodeContainer = $( '#'+nodeContainer );
        // 容器内的后代【node】的样式选择器 如 【#workflow .node1】
        var nodeSelector = "#" + nodeContainer + " " + nodeStyle;
        function workflow( callback ) {
            return new Workflow( callback );
        }
        function Workflow( callback ) {
            // jsPlumb只有等到DOM初始化完成之后才能使用
            // 因此我们在以下代码中调用jsPlumb.ready方法
            var href = this;
            jsPlumb.ready(function () {
                // instances of jsPlumb
                // 获得jsPlumb实例
                workflow.instance = instance = jsPlumb.getInstance({
                    // 给jsPlumb设一些默认值【公共值】
                    // 【连接点】的默认形状
                    Endpoint: [ "Dot", {radius: 2} ],
                    // 【覆盖物】
                    ConnectionOverlays: [
                        [ "Arrow", { location: 1, id:"arrow", length: 14, foldback: 0.8} ],
                        [ "Label", { label: "连接线", id: "label", cssClass: "aLabel"} ]
                    ],
                    Container: nodeContainer
                });
                callback && callback.call( href );
            });
        };
        
        /**
         * 创建【工作流】
         * @param data
         * |- data.label 工作流名称
         * |- data.locations 工作流节点位置及属性
         * |- data.connector 工作流连接器
         */
        function createWorkflow ( data ) {
            // var
            var locations = data.locations;
            var connector = data.connector;
            var allNodesStrings = '';
            // check
            if ( !locations || !connector ) {
                return false;
            }
            // 遍历&&拼接所有节点
            $.each( locations, function(key, location) {
                allNodesStrings += '<div class="node1 '+ location['class'] +'" id="'+key+'" style="left:'+location['left']+'px; top:'+location['top']+'px;"' +
                    '><span>'+location["label"]+'</span></div>';
            });
            // 向容器追加节点
            $nodeContainer.append( allNodesStrings );
            // 初始化&&渲染工作流图
            jsPlumbInitAfter ( nodeSelector, connector , function () {
                $.each(connector, function (i, conns) {
                    instance.connect({
                        source:conns.source,
                        target:conns.target
                    });
                });
            });
        }
        /**
         * node节点初始化后 调用callback
         * @param selector
         * @param callback
         */
        function jsPlumbInitAfter ( selector, connector, callback ) {
            var selector = instance.getSelector( selector );
            // 绑定一个connector监听。注意传递的参数info不只包含connector（新连接）
            // 这个监听设置新连接的id做为标签的文本显示
            instance.bind('connection', function (info) {
                var index = instance.getAllConnections().length-1;
                var label = null;
                if (connector && connector.length) {
                    label = connector[index].label;
                    info.connection.getOverlay('label').setLabel(label || '');
                }
            });
            instance.doWhileSuspended(function () {
                // 使每一个.ep的div是一个source，我们用Continuous anchor和StateMachine connectors
                // 我们提供connector的paint style。注意在这个例子中strokeStyle是动态的，这会阻止我们去默认设置
                // jsPlumb.Defaults.PaintStyle拿默认值。
                // 我们使用了filter选项告诉jsPlumb，元素的一部分应该响应拖拽的起点
                instance.makeSource(selector, {
                    filter: ep,
                    anchor: "Continuous",
                    connector: [ "StateMachine", {curviness: 20 }],
                    connectorStyle: {
                        strokeStyle: "#5c96bc",
                        lineWidth:2,
                        outlineColor: "transparent",
                        outlineWidth: 4
                    },
                    maxConnections: 5,
                    onMaxConnections: function ( info , e ) {
                        alert("Maximum connector (" + info.maxConnections + ") reached");
                    }
                });
                // 初始化所有的 ".node1" 元素 是connector targets
                instance.makeTarget(selector, {
                    dropOptions: {
                        hoverClass: "dragHover"
                    },
                    anchor: "Continuous"
                });
                callback && callback( instance );
            });
        }
        workflow(function() {
            var jyid = $("#hidJyid").val();
            var jyrq = $("#hidJyrq").val();
            var lsh = $("#hidLsh").val();
            var jym = $("#hidJym").val();
            var lclx = $("#hidLclx").val();
            var lccj = $("#hidLccj").val();
            var jymc = $("#hidJymc").val();
            var sys_run_trace = $("#hidSys_run_trace").val();
            // ajax 得到数据后 渲染成图
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/workflow_view",
                data: {'jyid': jyid,'jyrq': jyrq,'lsh': lsh,'jym': jym,'lclx': lclx,'lccj': lccj,'jymc': jymc,'sys_run_trace': sys_run_trace},
                success: function(data){
                    for(var id in data[0]) {
                        var type = data[0][id]["type"];
                        if (type == 'start_zlc' || type == 'start_jy') {
                            data[0][id]["class"] = 'theme_start';
                        } else if(type == 'end_zlc' || type == 'end_jy') {
                            data[0][id]['class'] = 'theme_end';
                        } else if(type == "zlc") {
                            data[0][id]['class'] = 'theme_b';
                        } else {
                            data[0][id]['class'] = 'theme_a';
                        }
                    };
                    // 先设置一个flow_data包括 connector和locations
                    flow_data = {locations:data[0], connector:data[1]};
                    createWorkflow(flow_data);
                    // 重新设置流程图样式
                    update_wkflow_class( data[2] )
                    // 隐藏域流程走向详情
                    $("#hidConnector1").val( JSON.stringify( data[2] ) );
                    // 隐藏域流程走向
                    $("#hidLczx").val( JSON.stringify( data[3] ) );
                    // 隐藏域子流程字典
                    $("#hidZlcDic").val( JSON.stringify( data[4] ) );
                },
                error: function(){
                    errorAjax();
                }
            });
        });
        win.workflow = workflow;
    }(jQuery, window);
    // 流程图 查看日志
    $("#lbtnCkrz").click(function( e ) {
        // 剔除原有的右击事件
        e.preventDefault();
        // 查看日志
        select_rz();
    });
    // 节点编辑
    $("#divJdbj").click(function( e ) {
        // 剔除原有的右击事件
        e.preventDefault();
        // 节点编辑
        nodeEdit();
    });
    
    //选项卡间进行切换
    $("#tbsRzck").tabs({
        onSelect: function(title, index){
            if( index == 0 ){
                //流程图
            }else if( index == 1 ){
                // 列表
                // 传递参数:
                // 交易日期
                var jyrq = $("#hidJyrq").val();
                // 流水号
                var lsh = $("#hidLsh").val();
                // 隐藏域中的lczx结构
                var lczx = $("#hidLczx").val();
                // zlc_dic数据结构
                var zlc_dic = $("#hidZlcDic").val();
                // connector1执行走向
                var connector1 = $("#hidConnector1").val();
                // 流程类型
                var lclx = $("#hidLclx").val();
                // 流程层级
                var lccj = $("#hidLccj").val();
                // 参数字符串
                var cs_str = 'jyrq=' + jyrq + '&lsh=' + lsh + '&lczx=' + lczx + '&zlc_dic=' + zlc_dic + '&connector1=' + connector1 + '&lclx=' + lclx + '&lccj=' + lccj;
                // 加载页面
                $('#tbsRzck iframe')[0].src='/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/lctlb_view?' + cs_str;
            }
        }
    });
    
    // 导出日志
    $("#lbtnDcrz").click(function( e ) {
        // 剔除原有的右击事件
        e.preventDefault();
        // 导出日志
        dcrz();
    });
});

/*
* 函数说明：根据流程执行过程，更新流程走向
* 实现规则：
* JS将connector1结构中的布局ID与locations中的布局ID相匹配：
*   1.对于“节点返回值”为负值的节点节点高亮显示（圈红）；
*   2.将connector1结构中的布局ID、返回值，与connector中的前置布局ID、返回值相匹配，进行连接线高亮显示；
*   3.并将connector1中的节点ID、编码和zlc_run_trace赋到对应控件属性中
*/
function update_wkflow_class( connector1 ){
    // 流程类型
    var lclx = $("#hidLclx").val();
    // 遍历所有执行流程
    $.each( connector1, function(i, jdxx) {
        // 出现异常的节点，边框为红色
        if( jdxx['jdfhz'] == '-1' ){
            $("#" + jdxx['bjid']).addClass('red');
        }
        // 流程走向连接线为橙色
        if( jdxx['jdfhz'] != '' ){
            setLineColor(jdxx['bjid'], jdxx['jdfhz'], '#FF8C00');
        }
        // 右击事件( 节点编辑：子流程节点、子流程开始节点、子流程结束节点 无右击事件 )
        if( ( lclx != 'zlc' && jdxx['jdlx'] != 'zlc') || ( lclx == 'zlc' && jdxx['jdbm'] != 'zlcstart' && jdxx['jdbm'] != 'end' && jdxx['jdlx'] != 'zlc') ){
            $("#" + jdxx['bjid']).on('contextmenu', function(e) {
                //剔除原有的右击事件
                e.preventDefault();
                // 选中
                lastActiveNode = $(this);
                //显示快捷菜单
                $('#mm').menu('show', {
                    left: e.pageX,
                    top: e.pageY
                }).data("fireElement", e.currentTarget);
            });
        }else{
            $("#" + jdxx['bjid']).on('contextmenu', function(e) {
                //剔除原有的右击事件
                e.preventDefault();
            });
        }
        // 单击事件( 若节点类型为开始、结束节点，且流程类型为子流程，则不做任何处理 )
        if( ( lclx != 'zlc') || ( lclx == 'zlc' && jdxx['jdbm'] != 'zlcstart' && jdxx['jdbm'] != 'end') ){
            $("#" + jdxx['bjid']).click(function(e) {
                //剔除原有的右击事件
                e.preventDefault();
                // 选中
                lastActiveNode = $(this);
                sel_jdxx();
            });
        }
        // 给节点添加属性
        // 节点id
        $("#" + jdxx['bjid']).attr( "data-nodeid", jdxx['jdid'] );
        // 节点编码
        $("#" + jdxx['bjid']).attr( "data-jdbm", jdxx['jdbm'] );
        // 子流程日志信息
        $("#" + jdxx['bjid']).attr( "data-sys_run_trace", jdxx['zlc_run_trace'] );
        // 节点类型
        $("#" + jdxx['bjid']).attr( "data-jdlx", jdxx['jdlx'] );
        // 节点名称
        $("#" + jdxx['bjid']).attr( "data-jdmc", jdxx['mc'] );
    });
}
/*
*根据布局id和返回值设置连接线样式
*/
function setLineColor(bjid, fhz, color) {
    $.each(instance.getAllConnections(), function() {
        if (this.sourceId == bjid && this.getOverlay('label').getLabel() == fhz) {
            this.setPaintStyle({
                strokeStyle: color,
                lineWidth: 2
            });
        }
    });
}
/*
* 查看流程全部日志
*/
function select_rz(){
    // 请求信息：流水号、交易日期、流程类型、交易或子流程名称、流程层级
    var jyrq = $("#hidJyrq").val();
    var lsh = $("#hidLsh").val();
    var lclx = $("#hidLclx").val();
    var lccj = $("#hidLccj").val();
    var jymc = $("#hidJymc").val();
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/lcrzck_view",
        data: {'jyrq': jyrq, 'lsh': lsh, 'lclx': lclx, 'lccj': lccj},
        success: function(data){
            var title = "交易[" + jymc +"]日志查看";
            if( lclx == 'zlc' ){
                title = "子流程[" + jymc + "]日志查看";
            }
            // 打开窗口
            newWindow($("#winRznr"),title, 800, 400);
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 获取数据成功
            if( data.state == true ){
                $("#preLcrznr").html( $('<div/>').text(data.rznr).html() );
            }else{
                afterAjax(data, "", "");
            }
        },
        error : function(){
            errorAjax();
        }
    });
}
/**
*节点编辑
*/
function nodeEdit() {
    // 节点id
    var nodeid = lastActiveNode.attr('data-nodeid') || '';
    // 先判断是否是系统节点
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/check_jdlx_view",
        data: {'jdid': nodeid},
        success: function(data){
            // 反馈信息初始化页面
            data = $.parseJSON(data);
            // 验证成功，可以修改
            if( data.state == true ){
                // 节点类（ 用来判断是否是开始、结束节点 ）
                var jd_class = lastActiveNode.attr('class') || '';
                // 布局id（ 如果节点名称发生变化时，更新流程节点名称 ）
                var bjid = lastActiveNode.attr('id') || '';
                // 编辑开始、结束节点是页面title不一致
                var title = '节点编辑';
                if( jd_class.indexOf( 'theme_start' ) > -1 ){
                    title = '编辑流程解包';
                    bjid = '';
                }else if( jd_class.indexOf( 'theme_end' ) > -1 ){
                    title = '编辑流程打包';
                    bjid = '';
                }
                //newWindow($("#winNodeEdit"), title, 900, 480);
                newWindow2($("#winNodeEdit"), title, '85', 480);
                $('#winNodeEdit iframe')[0].src = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/node_edit_view?nodeid=" + nodeid + "&bjid=" + bjid;
            }else{
                afterAjax(data, "", "");
            }
        },
        error : function(){
            errorAjax();
        }
    });
}

/**
*查询节点详情
*/
function sel_jdxx(){
    // 节点id
    var nodeid = lastActiveNode.attr('data-nodeid') || '';
    // 节点编码
    var jdbm = lastActiveNode.attr('data-jdbm') || '';
    // 子流程日志信息
    var sys_run_trace = lastActiveNode.attr('data-sys_run_trace') || '';
    // 节点类型
    var jdlx = lastActiveNode.attr('data-jdlx') || '';
    var jdmc = lastActiveNode.attr('data-jdmc') || '';
    var jyrq = $("#hidJyrq").val();
    var lsh = $("#hidLsh").val();
    // 如果查看子流程详细信息
    if( jdlx == 'zlc' ){
        var lclx = 'zlc';
        var lccj = $("#hidLccj").val() + '.' + jdbm;
        // 定义url
        // 交易日期、流水号、交易码、流程类型（交易）、流程层级（交易码）、交易名称
        cs_str = 'jyid=' + nodeid + '&jyrq=' + jyrq + '&lsh=' + lsh + '&jym=' + jdbm + "&lclx=" + lclx + "&lccj=" + lccj + "&jymc=" + jdmc + '&sys_run_trace=' + sys_run_trace;
        // 最终sql
        url = '/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/rzck_view?' + cs_str;
        // 追加窗口
        var obj_win = '<div id="divRzckWindow'+ nodeid +'" class="easyui-window" style="display:none" data-options="closed:true,collapsible:false,minimizable:false,maximizable:false"> <iframe id="rzckFrame' + nodeid +'" name="rzckFrame" scrolling="auto"  frameborder="0"  src="##" style="width:100%;height:99.9%;"></iframe></div>'
        parent.$('body').append(obj_win);
        
        // 本流程图对应的交易id
        var old_jyid = $("#hidJyid").val();
        // 从父类里打开新窗口
        parent.$('#rzckFrame' + old_jyid).attr('src', url );
        var top = parent.$("#divRzckWindow").offset().top - parent.$("#divRzckWindow").offset().top * 0.35;
        var left = parent.$("#divRzckWindow").offset().left;
        newWindow(parent.$("#divRzckWindow"+ old_jyid),'子流程[' + jdmc + ']日志查看',1030,520,left,top);
        // 窗口显示
        parent.$("#divRzckWindow"+ old_jyid).css('display', 'block');
    }else{
        // 打开节点详细信息页面
        // 节点类（ 用来判断是否是开始、结束节点 ）
        var jd_class = lastActiveNode.attr('class') || '';
        // 节点是否是开始节点，默认不是
        var jdlx_start = '0';
        // 是开始节点样式，则是开始节点
        if( jd_class.indexOf( 'theme_start' ) > -1 ){
            jdlx_start = '1';
        }
        // 隐藏域中的lczx结构
        var lczx = $("#hidLczx").val();
        // zlc_dic数据结构
        var zlc_dic = $("#hidZlcDic").val();
        // 流程类型
        var lclx = $("#hidLclx").val();
        // 流程层级
        var lccj = $("#hidLccj").val();
        // 请求信息传入：节点的ID、编码、节点类型和lczx结构、zlc_dic数据结构、流程类型和流程层级
        $.ajax({
            type: 'POST',
            dataType: 'text',
            url: "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/jdrzck_view",
            data: {'jyrq':jyrq, 'lsh':lsh, 'jdid': nodeid, 'jdbm': jdbm, 'jdlx_start': jdlx_start, 'lczx': lczx, 'zlc_dic': zlc_dic, 'lclx': lclx, 'lccj': lccj},
            success: function(data){
                var title = '['+ jdmc +']节点查看'
                // 打开窗口
                newWindow($( "#winJdxx" ),title,770,400);
                // 窗口每次打开时，都是选中第一个标签
                $("#lb_busnessTab").tabs('select',0);
                // 反馈信息
                data = $.parseJSON( data );
                if( data.state == true ){
                    // 初始化页面元素
                    pageInitJd( data )
                }else{
                    afterAjax(data, '', '');
                }
            },
            error : function(){
                errorAjax();
            }
        });
    }
}

/*
*根据查询结果初始化节点详细信息页面
*/
function pageInitJd( data ){
    //初始化输入要素
    $('#dgSrys').datagrid({
        nowrap : false,
        fit : false,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: data.srys_lst,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'bm', title: '输入要素', width: 28 },
            { field: 'ysz', title: '值', width: 67, editor:{type:'text'}, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            }}
        ]]
    });
    //初始化输出要素
    $('#dgScys').datagrid({
        nowrap : false,
        fit : false,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        scrollbarSize: 15,
        singleSelect : true,
        data: data.scys_lst,
        columns: [[
            { field: 'id', title: 'ID', hidden: true },
            { field: 'bm', title: '输入要素', width: 28 },
            { field: 'ysz', title: '值', width: 67, editor:{type:'text'}, styler: function() {
                return 'word-break:break-word;';
            },formatter:function(node){
                return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
            }}
        ]]
    });
    // 日志
    $("#preJdRz").html( data.rznr );
}

/*
* 导出日志
*/
function dcrz(){
    // 请求信息：流水号、交易日期、流程类型、交易或子流程名称、流程层级
    var jyrq = $("#hidJyrq").val();
    var lsh = $("#hidLsh").val();
    var lclx = $("#hidLclx").val();
    var lccj = $("#hidLccj").val();
    var jymc = $("#hidJymc").val();
    // 文档请求url
    downUrl = "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/lcrzck_down_view?jyrq=" + jyrq + "&lsh=" + lsh + "&lclx=" + lclx + "&lccj=" + lccj;
    // jquery down
    $.fileDownload(downUrl)
        .done(function () {
            console.log('File download a success!');
        })
        .fail(function () {
            $.messager.alert('错误', '导出失败', 'error');
            console.log('File download failed!');
        });
}
