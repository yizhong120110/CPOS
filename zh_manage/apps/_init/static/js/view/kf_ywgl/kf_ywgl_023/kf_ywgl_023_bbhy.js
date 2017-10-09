$(document).ready(function() {
    // 绑定按钮事件
    $('#btnCommit_ok').click(winOkFuc);
    $('#btnCommit_cancel').click(winCalcelFuc);
    
});

// 版本提交按钮的方法
function winOkFuc(e){
    e.preventDefault();
    // 版本提交
    $('#bbform').form('submit', {
        url:'/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbhy_add_view',
        success: function(data){
            var data = eval('(' + data + ')');
            if (data && data.state) {
                window.parent.$('#bbhy_window').window('close');
                window.parent.$.messager.alert('提示',data.msg,'info',function(){
                    if($('#txtGridid').val() == null || $('#txtGridid').val() == ''){
                        window.parent.location.reload();
                    }else{
                        window.parent.$('#'+$('#txtGridid').val()).datagrid('reload');
                    }
                });
            } else {
                afterAjax(data, "", "");
            }
        },error: function () {
            errorAjax();
        }
    });
}

// 取消按钮的方法
function winCalcelFuc(e){
    e.preventDefault();
    window.parent.$('#bbhy_window').window('close');
}
