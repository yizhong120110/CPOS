$(document).ready(function() {
    $('#tbsJdxx').tabs({
        fit: false,
        border: false,
        tabPosition: 'left',
        headerWidth: 175,
        onSelect: function(title, index) {
            var s = $("#tbsJdxx iframe")[index].src;
            if (s == undefined || s == '') {
                csalid = $('#hidCsalids').val();
                pc = $('#hidPc').val();
                lx = $('#hidLx').val();
                lxdm = $('#hidLxdm').val();
                //alert($("#tbsJdxx iframe")[index]).data("sftg"));
                var data = $("#tbsJdxx iframe")[index].id + "&demoid=" + $($("#tbsJdxx iframe")[index]).data("demoid")+ "&sftg=" + $($("#tbsJdxx iframe")[index]).data("sftg") + "&pc="+pc + "&jdcsalid="+csalid + "&lx="+lx + "&lxdm="+lxdm;
                $("#tbsJdxx iframe")[index].src = "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/csal_jdxx_jbxx_view?jdcsalzxbzid=" + data;
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
    
    // 禁用第一个开始节点和最后一个结束节点
    if($('#hidLx').val() == 'zlc'){
        $('#tbsJdxx').tabs('disableTab', 0); 
        $('#tbsJdxx').tabs('disableTab', $('#tbsJdxx').tabs('tabs').length-1); 
        $('#tbsJdxx').tabs('select', 1);
    }else{
        $("#tbsJdxx").tabs('unselect', 0);
        $("#tbsJdxx").tabs('select', 0);
    }
});
