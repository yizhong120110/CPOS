// 页面数据初始化
$(document).ready(function() {
    // 数据列表
    datagrid = $('#dgWzxx').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: false,
        pagination: true,
        fitColumns: true,
        pageSize: 50,
        showHeader: false,
        method: "post",
        url: "/oa/yw_kbmn/yw_kbmn_001/yw_kbmn_001_view/data_wzxx_view",
        remoteSort: true,
        columns: [[{
            field: 'id', title: '文章', width: '100%', formatter: function (value, rowData, rowIndex) {
                if( rowData.nr == undefined ){
                    nr = '';
                }
                return '<div class="wenzhang-list">'+
                            '<div class="easyui-panel">'+
                                '<a class="wenzhang-title" href="javascript:void(0);" onclick="title_press(\''+rowData.id+'\');">'+rowData.bt+'</a>'+
                                '<div class="wenzhang-content-summary">'+
                                    '<p>'+nr+'</p>'+
                                '</div>'+
                                '<div class="wenzhang-info">'+
                                    '<a class="wenzhang-author" href="javascript:void(0);" onclick="author_press(\''+rowData.cjhydm+'\',\''+rowData.xm+'\');" title="作者">'+rowData.xm+'</a> 发布于'+
                                    '<span class="wenzhang-launch-time">'+rowData.cjsj+'</span> 评论('+
                                    '<a href="javascript:void(0);" onclick="ping_press(\''+rowData.id+'\');">'+rowData.plts+'</a>) 阅读('+
                                    '<a href="javascript:void(0);" onclick="read_press(\''+rowData.id+'\');">'+rowData.fwl+'</a>)'+
                                '</div>'+
                            '</div>'+
                        '</div>';
            }
        }]]
    });
    // 最大值限制
    $("#txtName").next().children().attr("maxlength","1024");
    // 默认显示信息
    $('#txtName').textbox('textbox').attr('placeholder', '请输入文章名称或文章内容或文章标签等关键词');
    // 查询按钮的事件
    $("#lbtnSearch").click(function(e){
        e.preventDefault();
        // 查询事件调用的方法
        search();
    });
});

// 我的知识库
function my_zsk(){
    // 打来我的知识库新窗口
    newTab("我的知识库","/oa/yw_kbmn/yw_kbmn_003/yw_kbmn_003_view/index_view")
}

// XX的知识库
function tj_zsk( name,id ){
    
    alert("当前用户的行员代码是："+id);
    // newTab(name+"的知识库","/oa/yw_kbmn/yw_kbmn_004/yw_kbmn_004_view/index_view")

}

// 我的知识库
function fl_zsk(id,mc){
    // 打开窗口的名称和地址
    var title = "找找看-"+mc+"知识库";
    var url = "/oa/yw_kbmn/yw_kbmn_002/yw_kbmn_002_view/index_view?fl="+id;
    // 打开新的窗口
    newTab(title, url);
}

// 查询事件调用的方法
function search(){
    // 获取查询条件的内容
    var xx = $("#txtName").val();
    // 打开窗口的名称和地址
    var title = '找找看-知识库';
    var url = "/oa/yw_kbmn/yw_kbmn_002/yw_kbmn_002_view/index_view?nr="+xx;
    // 页面跳转时清空当前页面的查询信息
    $('#txtName').textbox('clear');
    // 打开新的窗口
    newTab(title, url);
}
// 点击文章标题的事件
function title_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("标题："+id);
}
// 点击作者姓名的事件
function author_press( id,name ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("作者ID："+id+"，姓名："+name);
}
// 点击评论的事件
function ping_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("评论信息："+id);
}
// 点击阅读的事件
function read_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("阅读数量："+id);
}
