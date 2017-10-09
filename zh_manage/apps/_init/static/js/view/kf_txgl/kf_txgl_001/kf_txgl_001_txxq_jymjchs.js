var edtor = undefined;
$(document).ready(function() {
    
    // 初始化代码编辑器
    // CodeMirror对象
    edtor = CodeMirror.fromTextArea(document.getElementById("txtHsnr"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true
    });
    
    //将tab换为4个空格
    edtor.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    //初始化内容
    var nr = $("#txtHsnr").val();
    edtor.setValue(nr);
    
    // 保存
    $('#lbtnAddOrUpd').click(window_update_add_func);
    // 测试
    $('#lbtnTest').click(hs_test);
    // 执行
    $('#lbtnWindowZx').click(hz_zx);
    // 取消
    $('#lbtnWindowCancel').click(windowCancelFun);
    
});

/**
* 公共函数更新提交
*/
function window_update_add_func(e){
    e.preventDefault();
    // 添加遮罩
    ajaxLoading();
    var url = '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jymjchs_sub_view';
    var txid = $('#txid').val();
    $('#formJcjymhs').form('submit', {
        url:url,
        queryParams: {'txid':txid},
        dataType : 'json',
        onSubmit: function(){
            var ret = sub_check();
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
            // 执行请求后的方法
            afterAjax(data, '','');
            // 赋值
            if(typeof data == 'string'){
                data = $.parseJSON(data);
            }
            if( data.state == true ){
                // 赋值
                $("#jcjymhsid").val( data.jcjymhsid );
            }
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}

/**
* 提交前校验
*/
function sub_check(){
    //函数内容
    var hsnr = edtor.getValue();
    if (hsnr=="" || hsnr==null) {
        $.messager.alert('错误','函数内容不可为空，请输入','error', function(){
            $("#txtHsnr").next().children().focus();
        });
        return false;
    }
    return true;
}

/**
* 测试打开
*/
function hs_test(e){
    e.preventDefault();
    // 判断是否打开测试页面
    var jcjymhsid = $("#jcjymhsid").val();
    var hsnr = edtor.getValue();
    var ret = checkNull( hsnr, '函数内容', 'txtHsnr' );
    if( ret == false ){
        return ret
    }else if( jcjymhsid == '' ){
        $.messager.alert('错误','不允许测试，函数内容未保存，请先点击[保存]按钮保存函数内容，再点击[测试]按钮进行测试。','error')
        return false;
    }else{
        // 增加窗体
        newWindow($("#bean_window"),'交易码解出函数-测试执行',400,300);
        $('#bean_window').find('form').tabSort();
    }
}

/**
* 取消测试，关闭测试页面
*/
function windowCancelFun(e) {
    e.preventDefault();
    $('#bean_window').window('close');
};

/**
* 执行测试 todo( 核心执行测试方法还未写好 )
*/
function hz_zx(e){
    e.preventDefault();
    // 添加遮罩
    ajaxLoading();
    var url = '/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jymjchs_testzx_view';
    var txid = $("#txid").val();
    var jcjymhsid = $("#jcjymhsid").val();
    $('#bean_window').find('form').form('submit', {
        url:url,
        queryParams: {'txid':txid, 'jcjymhsid':jcjymhsid},
        dataType : 'json',
        onSubmit: function(){
            //校验报文是否为空
            var bw = $("#txtBw").textbox('getValue');
            var ret = checkNull( bw, '要发送的报文', 'txtBw' );
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
            //执行请求后的方法
            afterAjax(data, '','bean_window');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            errorAjax();
        }
    });
}
