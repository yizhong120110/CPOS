/**
 * 页面ready方法
 */
$(function() {

    // 每分钟调用一次
    function countSecond(){
        // 查询函数
        doSearch();
    　  setTimeout(countSecond, 60000);
    }

    // 初始化调用每分钟调用一次函数
    setTimeout(countSecond, 60000);

    doSearch();

    /**
    * 查询终端库存数据.
    */
    function doSearch() {

        // 添加遮罩
        ajaxLoading();
        // ajax请求
        $.ajax({
            url: '/tcr/oa/tcr_0004/tcr_0004_view/get_data',
            type: 'POST',
            dataType : 'json',
            data: {
                tcrid: tcrid
            },
            success: function(data) {
                // 取消遮罩
                ajaxLoadEnd();
                
                // 给页面赋值
                // 钞箱1
                $('#box1Per').progressbar({
                    value: (data.rows[0].box1/2700*100).toFixed(2)
                });
                $("#box1_able").html((100 - data.rows[0].box1/2700*100).toFixed(2) + "%");
                $("#box1").html(toThousands(data.rows[0].box1));

                // 钞箱2
                $('#box2Per').progressbar({
                    value: (data.rows[0].box2/2700*100).toFixed(2)
                });
                $("#box2_able").html((100 - data.rows[0].box2/2700*100).toFixed(2) + "%");
                $("#box2").html(toThousands(data.rows[0].box2));

                // 钞箱3
                $('#box3Per').progressbar({
                    value: (data.rows[0].box3/2700*100).toFixed(2)
                });
                $("#box3_able").html((100 - data.rows[0].box3/2700*100).toFixed(2) + "%");
                $("#box3").html(toThousands(data.rows[0].box3));

                // 钞箱4上
                $('#box4_1Per').progressbar({
                    value: (data.rows[0].box4_1/1050*100).toFixed(2)
                });
                $("#box4_1_able").html((100 - data.rows[0].box4_1/1050*100).toFixed(2) + "%");
                $("#box4_1").html(toThousands(data.rows[0].box4_1));

                // 钞箱4下
                $('#box4_2Per').progressbar({
                    value: (data.rows[0].box4_2/750*100).toFixed(2)
                });
                $("#box4_2_able").html((100 - data.rows[0].box4_2/750*100).toFixed(2) + "%");
                $("#box4_2").html(toThousands(data.rows[0].box4_2));

                // 回收箱
                $('#box5Per').progressbar({
                    value: (data.rows[0].box5/2700*100).toFixed(2)
                });
                $("#box5_able").html((100 - data.rows[0].box5/2700*100).toFixed(2) + "%");
                $("#box5").html(toThousands(data.rows[0].box5));
            },
            error: function() {
                // 取消遮罩
                ajaxLoadEnd();
                // 失败后要执行的方法
                errorAjax();
            }
        });
    }
});

function toThousands(num) {
    var num = (num || 0).toString(), re = /\d{3}$/, result = '';
    while ( re.test(num) ) {
        result = RegExp.lastMatch + result;
        if (num !== RegExp.lastMatch) {
            result = ',' + result;
            num = RegExp.leftContext;
        } else {
            num = '';
            break;
        }
    }

    if (num) {
        result = num + result;
    }
    return result;
}
