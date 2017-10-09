$(function() {
    
    $("#tbsYwxq iframe")[0].src = $($("#tbsYwxq iframe")[0]).attr('data-src');
    
    $("#tbsYwxq").tabs({
        tabPosition:'left',
        height:600,
        onSelect: function(title, index) {
            var src = $($("#tbsYwxq iframe")[index]).attr('data-src');
            if (index != 0 && $("#tbsYwxq iframe")[index].src == '') {
                $("#tbsYwxq iframe")[index].src = src;
            }
            // 自动化测试tab，每次点击时需要刷新页面。
            if (title == '自动化测试'){
                $("#tbsYwxq iframe")[index].src = src;
            }
        }
    });

});
