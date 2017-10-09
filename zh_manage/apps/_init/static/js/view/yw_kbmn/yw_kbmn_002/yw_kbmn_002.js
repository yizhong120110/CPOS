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
        url: "/oa/yw_kbmn/yw_kbmn_002/yw_kbmn_002_view/data_wzxx_view",
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
        search_all();
    });
    
    // 判断分类信息是否存在，若存在则直接进行查询
    var flxx = $("#hidWzfl").val();
    if( flxx.length > 0 ){
        search_fl( flxx );
    }
    
    // 判断查询条件是否存在，若存在则直接进行查询
    var wbxx = $("#txtName").val();
    if( wbxx.length > 0 ){
        search_wb( wbxx );
    }

});

// 我的知识库
function my_zsk(){
    
    newTab("我的知识库","123")

}

// 默认执行分类查询事件调用的方法
function search_fl( flxx ){
    // 页面重新加载
    $("#dgWzxx").datagrid('load',{
        flxx: flxx
    });
}

// 默认执行条件查询事件调用的方法
function search_wb( wbxx ){
    // 页面重新加载
    $("#dgWzxx").datagrid('load',{
        name: wbxx
    });
}

// 当前页面执行查询
function search_all(){
    // 获取查询文本信息，文章分类
    var wbxx = $("#txtName").val();
    var flxx = $("#hidWzfl").val();
    // 页面重新加载
    $("#dgWzxx").datagrid('load',{
        name: wbxx,
        flxx:flxx
    });
}

// 点击文章标题的事件
function title_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("标题："+id);
    newTab("知识库主页","123")
}
// 点击作者姓名的事件
function author_press( id,name ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("作者："+id+"，姓名："+name);
    newTab(name+"的知识库","123")
}
// 点击评论的事件
function ping_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("评论信息："+id);
    newTab("知识库主页","123")
}
// 点击阅读的事件
function read_press( id ){
    event = event || window.event
    event.stopPropagation();
    event.preventDefault();
    alert("阅读数量："+id);
    newTab("知识库主页","123")
}
