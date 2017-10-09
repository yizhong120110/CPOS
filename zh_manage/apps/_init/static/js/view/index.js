$(document).ready(function() {
    $("#window_cancel").click(function(){
        $("#add_server_window").window("close");
    });
});

function view_server(name, err, war) {
    newTab(name+"-主机详细信息", "/html/qfwjk/server/server.html?err="+err+"&war="+war);
}

function add_server() {
    newWindow($("#add_server_window"), "添加监控服务器", 720, 460);
}

function newTab(title, href) {
    var parentMain = window.parent.parent.document.getElementById("pnlMain");
    var $main = top.$(parentMain);
    if ($main.tabs('exists', title)) {
        $main.tabs('select', title);
    } else {
        var content = '<iframe scrolling="auto" frameborder="0" src="'+href+'" style="width:100%;height:100%;"></iframe>';
        $main.tabs('add',{
            title:title,
            content:content,
            closable:true
        });
    }
}

/* 创建新的窗体
 * @param beanWindow 窗体对象
 * @param title 窗体的标题
 * @param width 窗体的宽度
 * @param height 窗体的高度
 */
function newWindow(beanWindow,title,width,height) {
    // 清空window中的值
    clearWindow(beanWindow);
    // 创建window
    var top = ($(window).height()-height)*0.35;
    var left = ($(window).width()-width)*0.5;
    beanWindow.window({
        title : title,
        width : width,
        height : height,
        top: top < 0 ? 0 : top,
        left: left < 0 ? 0 : left,
        closed : false,
        cache : false,
        modal : true
    });
}

/**
 * 清空window中input中的数据
 * @param beanWindow 要清理的window对象
 */
function clearWindow(beanWindow){
    // 清空输入框中的值
    beanWindow.form('clear');
}