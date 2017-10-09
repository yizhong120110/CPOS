$(document).ready(function () {
    var mainTabs = "#pnlMain", homePageTitle = "主页", homePageHref = null;
//    $('#mnuMain').tree({
//                method: "get",
//                lines: false,
//                url: "/static/_init/js/view/tree-data.json",
//                enableContextMenu: false,
//        onClick: function(node) {
//            // 打开tab页
//            var strPageName = node.text;
//            if ($('#pnlMain').tabs('exists',strPageName)) {
//                $('#pnlMain').tabs('select', strPageName);
//            } else {
//                // alert(node.url)
//                // iframe
//                var content = '<iframe scrolling="auto" frameborder="0" src="'+node.url+'" style="width:100%;height:600px;"></iframe>';
//                $('#pnlMain').tabs('add', {
//                    title: strPageName,
//                    content: content,
//                    closable: true
//                });
//            }
//        }
//    });
    jQuery.ajax({
        type:"GET",
        url: "/static/_init/js/view/tree-data1.json",
        dataType:"json",
        global:false,
        success: function( data ){
            var menuobj = jQuery( "#mnuMain" )
            var appendTab = function( n ){
                var strPageName = n.text;
                if ($('#pnlMain').tabs('exists',strPageName)) {
                    $('#pnlMain').tabs('select', strPageName);
                } else {
                    var content = '<iframe scrolling="auto" frameborder="0" src="'+n.url+'" style="width:100%;height:100%;"></iframe>';             
                    $('#pnlMain').tabs('add', {
                        title: strPageName,
                        content: content,
                        closable: true
                    });
                }
            }
            
            jQuery.each( data , function(i, n){
                var liobj = jQuery("<li><a href='javascript:void(0);'>"+n.text+"</a></li>")
                jQuery("a", liobj[0]).first().click( function(){
                      //打开tab页
                    if ( n.url != "")
                        appendTab( n );
                    else
                        ;
                 } )
                if ( n.children.length > 0 ) {
                     var ulobj = jQuery( "<ul></ul>")
                     jQuery.each( n.children, function(i, n){
                         var aobj = jQuery("<a href='javascript:void(0);'>"+n.text+"</a>");
                         aobj.click( function(){
                             appendTab( n )
                              //打开tab页
                         } )
                         ulobj.append(jQuery( "<li></li>" ).append( aobj ))
                     });
                     liobj.append(ulobj);
                     menuobj.append(liobj);
                } else
                    menuobj.append( liobj );
            });
        }
     });
    
    // 全屏切换
//        $(btnFullScreen).click(function () {
//                if ($.util.supportsFullScreen) {
//                    if ($.util.isFullScreen()) {
//                        $.util.cancelFullScreen();
//                    } else {
//                        $.util.requestFullScreen();
//                    }
//                } else {
//                    $.easyui.messager.show("当前浏览器不支持全屏 API，请更换至最新的 Chrome/Firefox/Safari 浏览器或通过 F11 快捷键进行操作。");
//                }
//            });
//
//            $(btnExit).click(function () {
//                $.easyui.messager.confirm("操作提醒", "您确定要退出当前程序并关闭该网页？", function (c) {
//                    if (c) {
//                        window.onbeforeunload = null;
//                        $.util.closeWindowNoConfirm();
//                    }
//                });
//            });
       
   // 工具栏按钮
   // 

   // 回到主页
    $("#mainTabs_jumpHome").click(function () { jumpHome(); });
    // 关闭当前页
    $("#mainTabs_closeTab").click(function () { closeCurrentTab(); });
    // 关闭其它页
    $("#mainTabs_closeOther").click(function () { closeOtherTabs(); });
    // 关闭所有页
    $("#mainTabs_closeAll").click(function () { closeAllTabs(); });
    $("#btnShowNorth").click(function () { topToggle();});

    // 隐藏头部
    // 
    function topToggle(){
        l.layout("toggle", "north");
    };
    // 

    /**
     * 回到主页.
     */
    function jumpHome () {
        var t = $(mainTabs), tabs = t.tabs("tabs"), panel = $.array.first(tabs, function (val) {
            var opts = val.panel("options");
            return opts.title == homePageTitle && opts.href == homePageHref;
        });
        if (panel && panel.length) {
            var index = t.tabs("getTabIndex", panel);
            t.tabs("select", index);
        }
    }
    jQuery("#rMainTab").click(
        jumpHome()
    );
    
    
    /**
     * 关闭当前Tab.
     */
    function closeCurrentTab () {
        var t = $(mainTabs), index = t.tabs("getSelectedIndex");
        return t.tabs("closeClosable", index);
    };

    /**
     * 除当前页外关闭其它Tab.
     * 
     * @param index Tab索引.
     */
    function closeOtherTabs (index) {
        var t = $(mainTabs);
        if (index == null || index == undefined) { index = t.tabs("getSelectedIndex"); }
        return t.tabs("closeOtherClosable", index);
    };
    
    /**
     * 关闭所有Tab.
     */
    function closeAllTabs () {
        return $(mainTabs).tabs("closeAllClosable");
    };

    // var busnessTab;
    
    var busnessTab = $("#orderDetail").tabs({
        tabPosition:'left',
        
        enableConextMenu: true,
        onSelect: function(title,index){
            if( index == 1 ){
                newWindow($("#bean_window"),'编辑交易',1100,500,0,0);
            }
        }
    });

    /* 创建新的窗体
     * @param beanWindow 窗体对象
     * @param title 窗体的标题
     * @param width 窗体的宽度
     * @param height 窗体的高度
     */
    function newWindow(beanWindow,title,width,height,top,left) {
        // 清空window中的值
        clearWindow(beanWindow);
        // 创建window
        beanWindow.window({
            title : title,
            width : width,
            height : height,
            top: top,
            left: left,
            closed : false,
            cache : false
            // modal : true
        });
    };

    /**
     * 清空window中input中的数据
     * @param beanWindow 要清理的window对象
     */
    function clearWindow(beanWindow){
        // 清空输入框中的值
        beanWindow.form('clear');
    };
    
    /**
      * 节点编辑tab关闭时提醒
      */
    $(mainTabs).tabs({
        onBeforeClose: function(title, index) {
            if(title.indexOf("-流程编辑")<0) {
                return true;
            }
            $($(mainTabs).tabs("getTab",index)).find("iframe")[0].contentWindow.close_confirm($(this), index);
            return false;
        }
    });
    
});
