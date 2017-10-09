$(document).ready(function() {
    $("#tbsDbts iframe")[0].src = $($("#tbsDbts iframe")[0]).data('src');
    
    // 执行步骤Tabs
    $('#tbsDbts').tabs({
        fit: true,
        border: false,
        tabPosition: 'left',
        headerWidth: 180,
        tools: '#tab-tools',
        onSelect: function(title, index) {
            if (title != '查看全部日志' && $("#tbsDbts iframe")[index].src == '') {
                $("#tbsDbts iframe")[index].src = $($("#tbsDbts iframe")[index]).data('src');
            }
            // 只有节点才启用“保存为节点测试案例”按钮
            if (title != '查看全部日志' && zxbz[index]['lx'] == '1') {
                $('#btnSaveJdCsal').linkbutton('enable');
            } else {
                $('#btnSaveJdCsal').linkbutton('disable');
            }
            if (title != '查看全部日志') {
                parent.window.demoid = zxbz[index]['demoid'];
                parent.window.nodeid = zxbz[index]['nodeid'];
                parent.window.bzid = zxbz[index]['bzid'];
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
    
    // 保存为节点测试案例
    $('#btnSaveJdCsal').linkbutton({
        onClick: function() {
            parent.casl_lx = 'jd';
            parent.newWindow(parent.$("#divSaveCsal"), '保存为节点测试案例', 500, 270);
            parent.$("#txtCsalSsyw").textbox('setValue', parent.$("#ywmc").val());
            parent.$("#txtCsalSsjy").textbox('setValue', parent.$("#mc").val());
            // form tab排序
            parent.$("#divSaveCsal").children('form').tabSort();
        }
    });
    
    // 保存为测试案例
    $('#btnSaveCsal').linkbutton({
        onClick: function() {
            parent.casl_lx = 'lc';
            parent.newWindow(parent.$("#divSaveCsal"), '保存为测试案例', 500, 270);
            parent.$("#txtCsalSsyw").textbox('setValue', parent.$("#ywmc").val());
            parent.$("#txtCsalSsjy").textbox('setValue', parent.$("#mc").val());
            // form tab排序
            parent.$("#divSaveCsal").children('form').tabSort();
        }
    });
    
    // 日志流水号列表
    var rzkeys = [];
    parent.window.bzids = [];
    $(zxbz).each(function(){
        parent.window.bzids.push(this['bzid']);
        parent.window.demoids.push(this['demoid'] || '');
        rzkeys.push(this['rzlsh'] || '');
    });
    
    // 获取全部日志
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_005/kf_ywgl_005_view/demo_log_all_view",
        data: {
            "rzkeys": JSON.stringify(rzkeys)
        },
        success: function(data) {
            if (data.state) {
                $('#log_all').text(data.log);
            } else {
                afterAjax(data, '', '');
            }
        }
    });
    
});
