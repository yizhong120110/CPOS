$(document).ready(function() {

    var pnlMain = "#pnlMain",
        homePanel = "#homePanel",
        homePageTitle = "主页",
        homePageHref = null;

    $(pnlMain).tabs({
        fit: true,
        border: true,
        onBeforeClose: function(title, index) {
            // 标题不含"-流程编辑"
            if (title.indexOf("_流程编辑") == -1) {
                return true;
            }
            // 含"-流程编辑"页面 该逻辑建议修改
            try {
                $($(pnlMain).tabs("getTab", index)).children("iframe")[0].contentWindow.close_confirm($(this), index);
                return false;
            } catch(e) {
                return true
            }
        }
    });

    $("#rEditTab").click(function(){
        mmxg();
    });

    // 给主页的iframe赋值src
    // 主机监控$(homePanel).children('iframe').attr('src', '/oa/index');
    //if(dlxt == '开发系统'){
    //    // 业务管理
    //    var tab = $('#pnlMain').tabs('getSelected');  // 获取选择的面板
    //    $('#pnlMain').tabs('update', {
    //        tab: tab,
    //        options: {
    //            title: '业务管理'
    //        }
    //    });
    //    $(homePanel).children('iframe').attr('src', '/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/index_view');
    //
    //
    //
    //
    //}else if (dlxt == '管理系统'){
    //    // 业务管理
    //    var tab = $('#pnlMain').tabs('getSelected');  // 获取选择的面板
    //    $('#pnlMain').tabs('update', {
    //        tab: tab,
    //        options: {
    //            title: '角色管理'
    //        }
    //    });
    //    $(homePanel).children('iframe').attr('src', '/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/index_view');
    //}

    // 监听tabs标签双击 关闭tab标签页
    $(pnlMain).tabs('header').find('ul.tabs').on('dblclick', 'li', function(e) {
        var delegateTarget = $(e.delegateTarget);
        var allCurrentTargets = delegateTarget.children('li');
        var currentTarget = $(e.currentTarget);
        var index = allCurrentTargets.index(currentTarget);
        if ( index !== 0 ) {
            $(pnlMain).tabs('close', index);
        }
    });

    // 主menu-ajax
    jQuery.ajax({
        type: "GET",
        url: "/oa/tree-data",
        dataType: "json",
        global: false,
        data: {'hydm': hydm,
               'id':id,
                'dlxt':dlxt
        },
        success: function(data) {
            //debugger;
            //初始页面加载-加载第一条数据
            if(dlxt =='管理系统'){
                var tab = $('#pnlMain').tabs('getSelected');  // 获取选择的面板
                $('#pnlMain').tabs('update', {
                    tab: tab,
                    options: {
                        title: '主页'
                    }
                });
                $(homePanel)
                     .children('iframe')
                     .attr('src', '/oa/index');
            }else{
                 if (data.length> 0 ){
                     if(data[0].lx =='2' ){
                        zTitle = data[0].text
                        var tab = $('#pnlMain').tabs('getSelected');  // 获取选择的面板
                        $('#pnlMain').tabs('update', {
                            tab: tab,
                            options: {
                                title: zTitle
                            }
                        });
                        $(homePanel).children('iframe').attr('src', data[0].url);
                     }else{
                        getId(data);
                        var tab = $('#pnlMain').tabs('getSelected');  // 获取选择的面板
                        $('#pnlMain').tabs('update', {
                            tab: tab,
                            options: {
                                title: ztitle
                            }
                        });
                        $(homePanel).children('iframe').attr('src', url_href);
                     }
                }
            }

            //菜单加载
            var menuobj = jQuery("#mnuMain")
            var appendTab = function(n) {
                 newTab(n.text, n.url);
            }
            
            /**** 原代码， 未实现菜单的递归加载算法
            jQuery.each(data, function(i, n) {
                var liobj = jQuery("<li><a href='javascript:void(0);'>" + n.text + "</a></li>");
                jQuery("a", liobj[0]).first().click(function() {
                    //打开tab页
                    if (n.url != "" && n.lx =='2') {
                        appendTab(n);
                    }else{
                        //禁止点击
                        event.preventDefault();
                    }
                });
                
                if(n.children){
                    if (n.children.length > 0) {
                        var ulobj = jQuery("<ul></ul>");
                        jQuery.each(n.children, function(i, n) {
                            var aobj = jQuery("<a href='javascript:void(0);'>" + n.text + "</a>");
                            aobj.click(function() {
                                if (n.url != "" && n.lx =='2') {
                                    appendTab(n);
                                    console.info('3333333333333333',n);
                                }else{
                                    //禁止点击
                                    event.preventDefault();
                                }
                            });
                            ulobj.append(jQuery("<li></li>").append(aobj));
                        });
                        console.info('666666666',ulobj);
                        liobj.append(ulobj);
                    }
                }
                menuobj.append(liobj);
            });   ****/
            
            // 根据后台返回的json数据递归渲染菜单
            var loadLi = function( rows, jparent ) {
                $.each( rows,function( i, n ) {
                    var liobj = $("<li><a href='javascript:void(0);'>"+n.text+"</a></li>");
                    //如果存在孩子，添加箭头标识
                    //if(n.children.length > 0){
                    //	liobj = $("<li><a href='javascript:void(0);'>"+n.text+"&nbsp;▶</a></li>");
                    //}
                    //绑定点击事件
                    $( "a", liobj[0] ).first().click( function(){
                        // 通过点击打开相应的功能tab页
                        if ( n.url != "" && n.lx =='2' ) {
                            appendTab( n );
                        }else{
                            //禁止点击
                            event.preventDefault();
                        }
                    });
                    if(n.children ) {
                        if (n.children.length > 0) {
                            var ulobj = $("<ul></ul>");
                            $.each(n.children, function (ci, cn) {
                                var aobj = $("<a href='javascript:void(0);'>" + cn.text + "</a>");
                                //如果存在孩子，添加箭头标识
                                //if(cn.children.length > 0){
                                //    aobj = $("<a href='javascript:void(0);'>"+cn.text+"&nbsp;▶</a>");
                                //}
                                aobj.click(function () {
                                    if ( cn.url != "" && cn.lx =='2' ) {
                                        //打开tab页
                                        appendTab(cn);
                                    }else{
                                        //禁止点击
                                        event.preventDefault();
                                    }
                                });
                                var sonLiObj = $("<li></li>");
                                ulobj.append(sonLiObj.append(aobj));
                                //如果孙子节点的有多个孩子，进入迭代；
                                if (cn.children) {
                                    if (cn.children.length > 0) {
                                        sonLiObj.append(loadLi(cn.children, $("<ul></ul>")));
                                    }
                                } else {//没孩子，跳出
                                    return true;
                                }
                            });
                            liobj.append(ulobj);
                        }
                    }
                    jparent.append(liobj);
                });
                return jparent;
            }
            //调用加载
            loadLi(data,menuobj)
        }
    });

    //jQuery("#rMainTab").click(jumpHome);
    //返回到主页
    $("#rMainTab").click(function(e){
        $("#pnlMain").tabs( "select" , 0 );
    });

    /**
     * 回到主页.
     */
    function jumpHome() {
         var t = $(pnlMain),

            tabs = t.tabs("tabs"),
            panel = $.array.first(tabs, function(val) {
                var opts = val.panel("options");
                return opts.title == homePageTitle && opts.href == homePageHref;
            });
         if (panel && panel.length) {
            var index = t.tabs("getTabIndex", panel);
            t.tabs("select", index);
        }
    }

    /**
     * 关闭当前Tab.
     */
    function closeCurrentTab() {
        var t = $(pnlMain),
            index = t.tabs("getSelectedIndex");
        return t.tabs("closeClosable", index);
    };

    /**
     * 除当前页外关闭其它Tab.
     *
     * @param index Tab索引.
     */
    function closeOtherTabs(index) {
        var t = $(pnlMain);
        if (index == null || index == undefined) {
            index = t.tabs("getSelectedIndex");
        }
        return t.tabs("closeOtherClosable", index);
    };

    /**
     * 关闭所有Tab.
     */
    function closeAllTabs() {
        return $(pnlMain).tabs("closeAllClosable");
    };

});


function view_server(name) {
    newTab(name + "-主机详细信息", "/html/qfwjk/server/server.html");
}

function add_server() {
    newWindow($("#add_server_window"), "添加监控服务器", 560, 235);
}

var ztitle='';
var url_href='';
function getId(rowData){
     for (var menu in rowData){
         if (ztitle==''){
            if (rowData[menu].children) {
                if(rowData[menu].lx=='2'){
                    ztitle = rowData[menu].text;
                    url_href = rowData[menu].url;
                    break;
                }else{
                        getId(rowData[menu].children);
                }
            } else {
                 if(rowData[menu].lx=='2'){
                    ztitle = rowData[menu].text
                    url_href =rowData[menu].url;
                  break;
                }
            }
         }
    }
}
function mmxg(){
    var url = "/oa/gl_mmgl/gl_mmgl_001/gl_mmgl_001_view/index_view";
    newTab('修改密码', url);
};