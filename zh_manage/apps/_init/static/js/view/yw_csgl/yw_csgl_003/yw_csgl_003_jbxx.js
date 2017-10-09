// 页面初始化
$(document).ready(function() {
    // 给保存按钮初始化方法
    $("#lbtnJbxxUpdate").click(function(e){
        e.preventDefault();
        jyxx_update();
    });
    // 翻译 引用的kf_ywgl_003已经存在
})

/**
* 函数说明：交易基本信息修改提交
* id：编辑交易id
* jym：用于后台删除缓存中此交易的信息，此处传递给后台后，后台就无需进行查询
*/
function jyxx_update(){
    // 添加遮罩
    ajaxLoading();
    // 交易id
    var id = $("#hidJyid").val();
    // 交易码
    var jym = $("#hidJym").val();
    // 更新前的基本信息
    var updQ = $("#hidUpdQ").val();
    // 交易状态
    var zt = $("#nfsJyzt").get(0).checked ? '1' : '0';
    // form表单提交
    $('#divJbxx').find('form').form('submit', {
        url: '/oa/yw_csgl/yw_csgl_003/yw_csgl_003_view/jbxx_edit_view',
        queryParams: { 'id': id, 'jym': jym, 'updQ': updQ, 'zt': zt }, 
        onSubmit: function(){
            // 交易超时时间
            var timeout = $("#txtTimeout").numberbox("getValue");
            // 交易超时时间判空
            var ret = checkNull(timeout, '交易超时时间', 'txtTimeout') 
            // 交易超时时间只能输入数字
            if( ret == true ){
                ret = checkInt(timeout, '交易超时时间', 'txtTimeout')
            }
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
            // 处理成功后，弹出后台反馈信息，无需重新加载数据表格， 无需关闭窗口，
            afterAjax(data, "", "");
            // 自动发起配置说明
            data = $.parseJSON( data );
            $("#txtZdfqpzsm").textbox('setValue', data.zdfqpzsm);
            // 更新成功，更新隐藏域值
            if( data.state == true ){
                $("#hidYzt").val( zt );
                var zdfqpz = $("#txtZdfqpz").textbox("getValue");
                $("#hidYzdfqpz").val( zdfqpz );
            }
        },
        error: function(data) {
            // 取消遮罩
            ajaxLoadEnd();
            // 异常提示
            errorAjax();
        }
    });
}