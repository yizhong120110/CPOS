$(document).ready(function() {
    $('#win_tj').find('form').tabSort();
    // 绑定按钮事件
    $('#btnCommit_ok').click(winOkFuc);
    $('#btnCommit_cancel').click(winCalcelFuc);
    
    // 最大值限制
    $("#txtTjms").next().children().attr("maxlength","66");
});

// 版本提交按钮的方法
function winOkFuc(e){
    e.preventDefault();
    // 添加遮罩
    ajaxLoading();
    // 版本提交
    $('#bbform').form('submit', {
        url:'/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbtj_view',
        onSubmit: function(){
            var ret = validate();
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            var data = eval('(' + data + ')');
            if (data.state == true || data.state == 'true') {
                window.parent.$('#bbtj_window').window('close');
                window.parent.$.messager.alert('提示',data.msg,'info',function(){
                    if($('#txtGridid').val() == null || $('#txtGridid').val() == ''){
                        window.parent.location.reload();
                    }else if($('#txtGridid').val() == 'lcbjtj'){
                        // 如果是流程编辑的版本提交，获取新的唯一码
                        window.parent.refreshWym();
                    }else if($('#txtGridid').val() == 'jdbjtj'){
                        // 如果是节点的版本提交，获取新的唯一码
                        window.parent.refreshJdWym();
                    }else{
                        window.parent.$('#'+$('#txtGridid').val()).datagrid('reload');
                    }
                });
            } else {
                $.messager.alert('错误',data.msg,'error');
            }
        }
    });
}

// 取消按钮的方法
function winCalcelFuc(e){
    e.preventDefault();
    window.parent.$('#bbtj_window').window('close');
}

// 提交版本前验证版本内容
function validate(){
    var bzxx = $("#txtTjms").textbox("getValue");
    
    // 当前版本提交描述
    if (bzxx=="" || bzxx==null) {
        $.messager.alert('错误','当前版本提交描述不可为空，请输入','error', function(){
            $("#txtTjms").next().children().focus();
        });
        return false;
    }
    return true;
}