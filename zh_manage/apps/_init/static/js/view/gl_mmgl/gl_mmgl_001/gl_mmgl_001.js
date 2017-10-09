/**
 * 页面初始化加载
*/
$(document).ready(function() {
    
    // 最大值限制
    $("#oldPassword").next().children().attr("maxlength","20");
    $("#password").next().children().attr("maxlength","20");
    $("#affirmPassword").next().children().attr("maxlength","20");
    
     // 保存按钮
    $('#lbtnUpdate').click(function(e){
        e.preventDefault();
        // 密码修改提交
        update_submit();
    });
    
    // 重置按钮
    $('#lbtnReset').click(function(e){
        e.preventDefault();
        // 重置方法调用
        clearValue();
    });
});

// 密码修改提交
function update_submit(){
    // 对密码进行校验，失败返回false，成功则向后台提交
    if(!check_pass()){
        return false;
    }else{
        // 请求后台
        $.ajax({
            url:'/oa/gl_mmgl/gl_mmgl_001/gl_mmgl_001_view/update_view',
            type : 'POST',
            data:{
                password : $.md5($.trim($('#password').val())),
                oldPassword : $.md5($.trim($('#oldPassword').val()))
            },
            success:function(data) {
                if(data.state == true) {
                    // 页面文本清空
                    clearValue();
                    $.messager.alert('提示', data.msg.replace("\n", "<br/>") , 'info',function(){
                        window.open('/oa_core/logout','_parent');
                    });
                } else {
                    afterAjax(data, "", "");
                }
            },
            error : function() {
                $.messager.alert('错误', '修改失败,请与管理员联系!', 'error');
            },
        });
    }
}

// 密码校验
function check_pass(){
    
    // 获取页面中原密码，新密码，确认密码的值
    var ymm = $.trim($("#oldPassword").val())
    var xmm = $.trim($("#password").val())
    var zmm = $.trim($("#affirmPassword").val())
    
    // 对密码做前台校验判断
    if(xmm.length == 0){
        $.messager.alert('提示','新密码不可为空','info');
        return false;
    }
    if(xmm.length < 6 || xmm.length >20){
        $.messager.alert('提示','新密码长度有误，请输入6-20位密码','info');
        return false;
    }
    if(zmm.length == 0){
        $.messager.alert('提示','确认密码不可为空','info');
        return false;
    }
    if(xmm != zmm ){
        $.messager.alert('提示','两次输入的新密码不一致，请重新输入','info');
        return false;
    }
    // 当前信息通过验证的返回值
    return true;
}

// 当前页面文本进行清空数据
function clearValue(){
    // 重置为空
    $('#oldPassword').textbox('clear');
    $('#password').textbox('clear');
    $('#affirmPassword').textbox('clear');
}