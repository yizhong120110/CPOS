$(document).ready(function() {

    // 绑定按钮方法
    $("#lbtnRequest").on('click', function(e) {
        e.preventDefault();
        doSearch();
    });

    function doSearch() {

        // 添加遮罩
        ajaxLoading();
        // ajax请求
        $.ajax({
            url: '/tcr/oa/tcr_0001/tcr_0001_view/get_request',
            type: 'post',
            success: function(data) {
                // 添加遮罩
                ajaxLoadEnd();
                //执行请求后的方法
                if (data.state == true) {
                    // 如果查询成功
                    $.messager.alert('信息', data.msg, 'warning');
                } else {
                    // 如果查询失败
                    $.messager.alert('警告', data.msg, 'warning');
                }
            },
            error: function() {
                // 添加遮罩
                ajaxLoadEnd();
                // 失败后要执行的方法
                errorAjax();
            }
        });
    }
});