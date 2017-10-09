/**
 * 页面初始化
 */
$(function() {
    // 当前页面选项加载
    $("#yzjyTab").tabs({
        fit: true,
        border: false,
        showOption: true,
        enableNewTabMenu: true,
        tabPosition: 'left',
        headerWidth: 120,
        onSelect: function(title,index) {
            var tab = $("#yzjyTab").tabs('getTab', index);
            if (title == "参数配置") {
                tab.children("iframe").attr("src", "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/cspz_view")
            } else if (title == "业务配置") {
                tab.children("iframe").attr("src", "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/index_view")
            }
        }
    })
});