$(document).ready(function() {
    // 绑定日志窗口关闭的事件
    $('#rzck_window').window({
        modal:true,
        closed:true,
        maximizable:false,
        minimizable:false,
        resizable:false,
        collapsible:false,
        title: '日志查看',
        onClose:function(){ 
            $('#rznr').html('');
        }
    });
    // 流程图返回的数据
    work_flow_data = [];
    !function ( $, win ) {
        // 可拖拽的节点的css样式
        var nodeStyle = ".node1";
        // delete icon
        var delete_icon = 'i.icon-delete';
        // 拖出线和箭头的点
        var ep = '.ep';
        
        // 节点容器id【jsPlumb默认值Container使用-用作id=workflow】
        var nodeContainer = 'workflow';
        // 节点容器jQuery对象
        var $nodeContainer = $( '#'+nodeContainer );
        // 容器内的后代【node】的样式选择器 如 【#workflow .node1】
        var nodeSelector = "#" + nodeContainer + " " + nodeStyle;
        
        // jsPlumb实例
        var instance = null;
        
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
                    // ---------------------
                    // 【连接点】的默认形状
                    Endpoint: [ "Dot", {radius: 2} ],
                    // 【连接线】【鼠标悬浮时的样式】
                    // HoverPaintStyle: {
                    //     strokeStyle: "#1e8151", // 颜色
                    //     lineWidth: 2 // 宽度
                    // },
                    // 【覆盖物】
                    ConnectionOverlays: [
                        [ "Arrow", { location: 1, id:"arrow", length: 14, foldback: 0.8} ],
                        [ "Label", { label: "连接线", id: "label", cssClass: "aLabel"} ]
                    ],
                    //
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
                allNodesStrings += '<div class="node1 '+ location['class'] +'" id="'+key+'" data-nodeid="'+location["nodeid"]+'" data-type="'+location["type"]+'" style="left:'+location['left']+'px; top:'+location['top']+'px;"' +
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
            // 当执行失败时才标注异常节点
            if($("#hidZxjg").val() == '失败'){
                // 遍历所有需要标红的节点
                for(i=0;i<data.jdgl.length;i++){
                    $("[data-nodeid="+data.jdgl[i]+"]").css('border', '1px solid red');
                }
            }
            // 节点点击，打开日志子窗口
            $('.node1').click(function(e) {
                //获取点击节点的id
                jdid = e.currentTarget.id;
                // 点击的节点的id
                jdid_c = $('#'+jdid).data('nodeid');
                if(work_flow_data[2][jdid_c]['rzlsh'] == '' || work_flow_data[2][jdid_c]['rzlsh'] == null){
                    $.messager.alert('提示', '该节点未执行，没有日志。', 'info');
                    return;
                }
                //判断该节点是否跳过
                // 如果该节点不是跳过节点，那么通过流水号获取日志
                if (work_flow_data[2][jdid_c]['sftg'] == '1'){
                    $('#rznr').text(work_flow_data[2][jdid_c]['rzlsh']);
                }else{
                    $.ajax({
                        type: 'POST',
                        dataType: 'json',
                        url: "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/get_jdrz_view",
                        data: {"rzlsh":work_flow_data[2][jdid_c]['rzlsh']},
                        success: function(data){
                            $('#rznr').text(data.log);
                        },
                        error: function(){
                            errorAjax();
                        }
                    });
                }
                
                newWindow($("#rzck_window"), '日志查看', 650, 410);
            });
            // 查看所有的日志，后台循环日志列表中的每一项，进行日志获取
            $('#view_log_btn_error').click(function(e) {
                $.ajax({
                    type: 'POST',
                    dataType: 'json',
                    url: "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/get_rz_view",
                    data: {"id":$("#hidId").val(), "pc":$("#hidPc").val(),"csalid":$("#hidCsalid").val(),"mark":"all"},
                    success: function(data){
                        $('#rznr').text(data.log);
                    },
                    error: function(){
                        errorAjax();
                    }
                });
                newWindow($("#rzck_window"), '日志查看', 650, 410);
            })            
        }
        
        /**
         * node节点初始化后 调用callback
         * @param selector
         * @param callback
         */
        function jsPlumbInitAfter ( selector, connector, callback ) {
            //
            var selector = instance.getSelector( selector );
            
            // 绑定一个connector监听。注意传递的参数info不只包含connector（新连接）
            // 这个监听设置新连接的id做为标签的文本显示
            instance.bind('connection', function (info) {
                var index = instance.getAllConnections().length-1;
                var label = null;
                if (connector && connector.length) {
                    label = connector[index].label;
                    info.connection.getOverlay('label').setLabel(label || '');
                    if(connector[index].hl) {
                        setLineColor(info.connection,'#FF0000');
                    }
                    if(connector[index].hl_y) {
                        setLineColor(info.connection,'#FF8C00');
                    }
                }
            });
            
            // This function abstracts out the pattern of suspending drawing, doing something, and then re-enabling drawing
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
            // ajax 得到数据后 渲染成图
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/workflow_view",
                data: {"lx":$("#hidLx").val(), "id":$("#hidId").val(), "pc":$("#hidPc").val(), "csalid":$("#hidCsalid").val()},
                success: function(data){
                    work_flow_data = data;
                    for(var id in data[0]) {
                        var type = data[0][id]["type"];
                        if (type == "start_zlc" || type == "start_jy") {
                            data[0][id]["class"] = "theme_start";
                        } else if(type == "end_zlc" || type == "end_jy") {
                            data[0][id]["class"] = "theme_end";
                        } else if(type == "zlc") {
                            data[0][id]["class"] = "theme_b";
                        } else {
                            data[0][id]["class"] = "theme_a";
                        }
                    };
                    // 先设置一个flow_data包括 connector和locations
                    flow_data = {locations:data[0], connector:data[1],jdgl:data[3]};
                    createWorkflow(flow_data);
                },
                error: function(){
                    errorAjax();
                }
            });
        });
        
        win.workflow = workflow;
    }(jQuery, window);
    
    var xmlEditor = null;
    $("#tbsJylc").tabs({
        onSelect: function(title,index){
            $("#jdlb")[0].src = "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/csal_jdxx_view?csalid="+$("#hidCsalid").val()+"&zxjg="+$("#hidZxjg").val()+"&jgsm="+$("#hidJgsm").val()+"&lx="+$("#hidLx").val()+"&pc="+$("#hidPc").val()+"&lxdm="+$("#hidLxdm").val();
        }
    });
    
    $('#lbtnLcbj').click(function(){
        var mc = $("#mc").val();
        var title = mc+"_流程编辑";
        var href = "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/index_view?lx="+$("#hidLx").val()+"&id="+$("#hidId").val()+"&mc="+mc;
        newTab(title, href);
    });
});

function setLineColor(line, colers) {
    if (line) {
        //#e5db3d 浅黄
        if (colers == undefined)
            colers = "#e5db3d"
        line.setPaintStyle({
            strokeStyle: colers,
            lineWidth: 2
        });
    }
    return line;
};
