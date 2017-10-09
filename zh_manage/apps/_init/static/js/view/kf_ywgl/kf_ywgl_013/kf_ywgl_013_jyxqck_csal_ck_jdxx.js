$(document).ready(function() {
    $('#lb_busnessTab').tabs({
        fit: true,
        border: false,
        tabPosition: 'left',
        headerWidth: 175,
        onSelect: function(title,index){
            var s = $("#lb_busnessTab iframe")[index].src;
            if (s==undefined || s=='') {
                // 判断类型
                if (lx == "jd") {
                    // 节点
                    $("#dqxzjd").val(jdcsalzxbzid);
                    $("#lb_busnessTab iframe")[index].src = "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx_jbxx_view/index_view?jdcsalzxbzid=" + jdcsalzxbzid + "&demoid="+demoid;
                } else {
                   // 其他
                   $("#dqxzjd").val($("#lb_busnessTab iframe")[index].id);
                   $("#lb_busnessTab iframe")[index].src = "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx_jbxx_view/index_view?jdcsalzxbzid=" + $("#lb_busnessTab iframe")[index].id + "&demoid="+$("#lb_busnessTab iframe")[index].name;
                }
            }
        }
    }).find(".tabs-header ul.tabs>li").each(function(i, li) {
        // 气泡
        $(li).ttip({
            ttipEvent: 'h',
            msg: $(li).find("a>span").first().text()
        });
        $(li).find("a>span").eq(0).css({
            "padding": 0,
            // add by bianl 2015-04-08
            // 截断字符
            "text-overflow": "ellipsis",
            "display": "block",
            "width": "138px",
            "overflow": "hidden"
        }).end().eq(1).css({
            "right": "20px",
            "left": "initial"
        });
    });
});