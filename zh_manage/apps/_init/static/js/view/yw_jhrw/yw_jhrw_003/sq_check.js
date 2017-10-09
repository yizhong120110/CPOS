$(document).ready(function() {
    
    // 获取要执行的url
    var hidurl = $('#hidurl').val();
    // 密码限制输入长度
    $("#txtFhrmm").next().children().attr("maxlength","20");
    // 提交按钮
    $("#lbtnCheckSubmit").click(function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 获取复核人
        var fhr = $("#selFhr").textbox("getValue");
        $('#sqForm').form('submit', {
            url: '/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/sq_check',
            onSubmit: function(){
                // 校验复核人
                ret = checkNull( fhr, '授权人', 'selFhr' );
                if( ret == false ){
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false
                } else {
                    // 校验复核人密码
                    var fhrmm = $("#txtFhrmm").textbox("getValue");
                    ret = checkNull( fhrmm, '授权人密码', 'txtFhrmm' );
                }
                if( ret == false ){
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false
                }
                return ret;
            },
            // 授权成功后，进行业务处理
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                data = $.parseJSON( data );
                if (data.state == true){
                    // 组织业务数据对象
                    var g_data = getRequest(hidurl.substr(hidurl.indexOf('?'), hidurl.length));
                    var url = hidurl.substr(0, hidurl.indexOf('?'));
                    g_data['fhr'] = fhr;
                    ywcl(url,g_data);
                    // 将授权页面关闭
                    parent.$("#divSqWindow").window('close');
                }else{
                    //afterAjax(data, "", "");
                    $("#error_msg").html(data.msg);
                }
            }
        });
    });
    // 取消按钮
    $('#lbtnCheckCancel').click( function(e){
        e.preventDefault();
        // 将授权页面关闭
        parent.$("#divSqWindow").window('close');
    });
    // tab顺
    $("#sqForm").tabSort();
    $('#selFhr').combobox({    
        data : hyxx_lst,
        valueField:'hydm',    
        textField:'xm',
        panelMaxHeight:80,
        onLoadSuccess : function(data){
            pCount = data.length;
        },
        onShowPanel : function() {
            if(pCount <= 4){
                // 动态调整高度 
                $(this).combobox('panel').height(pCount * 20);
            }else{
                $(this).combobox('panel').height(80);
            }
        }
    });
    // 默认选择第一个
    $("#selFhr").combobox('select', $("#selFhr").combobox("getData")[0].hydm);
});

function ywcl(url,g_data){
    // 处理业务之前先调用父页面的方法
    if( typeof parent.ywcl_start === 'function' ){
        // 执行成功后会调用父页面的方法，里面可以加一些自己需要的操作
        parent.ywcl_start(url,g_data);
    }
    // 向后台请求信息
    $.ajax({
        type: 'POST',
        dataType: 'text',
        url: url,
        data: g_data,
        success: function(data){
            // 处理业务之前先调用父页面的方法
            if( typeof parent.ywcl_end === 'function' ){
                // 执行成功后会调用父页面的方法，里面可以加一些自己需要的操作
                parent.ywcl_end(url,g_data);
            }
            // 反馈信息
            afterAjax(data, '', '', true);
            
            // 要刷新数据表格id
            var dgid = $("#hidDgid").val();
            if( dgid != '' ){
                parent.$("#" + dgid).datagrid('reload');
            }
            if( typeof parent.succ_func === 'function' ){
                // 执行成功后会调用父页面的方法，里面可以加一些自己需要的操作
                parent.succ_func(data);
            }
        },
        error: function(){
            errorAjax();
            if( typeof parent.error_func === 'function' ){
                // 执行失败后会调用父页面的方法，里面可以加一些自己需要的操作
                parent.error_func();
            }
        }
    });
}

function getRequest(url) { 
    var theRequest = new Object(); 
    if (url.indexOf("?") != -1) { 
        var str = url.substr(1); 
        strs = str.split("*"); 
        for(var i = 0; i < strs.length; i ++) { 
            theRequest[strs[i].split("=")[0]]=unescape(strs[i].split("=")[1]); 
        } 
    } 
    return theRequest; 
} 