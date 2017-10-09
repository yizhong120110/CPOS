$(document).ready(function() {
    $('#zlcxx').find('form').tabSort();
    // 最大值限制
    $("#txtMc").next().children().attr("maxlength","50");
    $("#txtMs").next().children().attr("maxlength","150");
    
    $("#lbtn_savelbt").click(savecnet)
    // 保存基本信息
    function savecnet(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 修改基本信息
        $('#zlcxx').find('form').form('submit', {
            url:'/oa/kf_ywgl/kf_ywgl_008/kf_ywgl_008_view/update_view',
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
                afterAjax(data, "", "");
                // 更新tab名称
                var parentDocument = window.parent.parent.document;
                top.$(parentDocument).find("#pnlMain ul.tabs .tabs-selected span.tabs-title").text($("#txtMc").textbox("getValue") + '_子流程详情查看');
            },
            error: function(){
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    }

    // 保存基本信息验证
    function validate(){
        var mc = $("#txtMc").textbox("getValue");
        var ms = $("#txtMs").textbox("getValue");
        
        // 子流程名称
        if (mc=="" || mc==null) {
            $.messager.alert('错误','子流程名称不可为空，请输入','error', function(){
                $("#txtMc").next().children().focus();
            });
            return false;
        }
        
        // 校验子流程名称
        if(checkMc(mc,'子流程名称','txtMc') == false){
            return false;
        }
    }
})