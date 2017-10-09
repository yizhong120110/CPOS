 $(document).ready(function() {
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
                type: 'GET',
                dataType: 'json',
                url: "/oa/kf_ywgl/kf_ywgl_004/kf_ywgl_004_view/data_view",
                data: {"lx":"zlc", "id":$("#zlcid").val()},
                success: function(data){
                    for(var id in data[0]) {
                        var type = data[0][id]["type"];
                        if (type == "start_zlc" || type == "end_jy") {
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
                    flow_data = {locations:data[0], connector:data[1]};
                    createWorkflow(flow_data);
                },
                error: function(){
                    errorAjax();
                }
            });
        });
        
        win.workflow = workflow;
    }(jQuery, window);
    
});