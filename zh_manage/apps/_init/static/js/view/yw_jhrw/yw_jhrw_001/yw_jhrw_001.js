/**
* 计划任务管理选项卡切换
* 第一个选项卡：自动发起交易列表
* 第二个选项卡：监控规则发起列表
* 第三个选项卡：当日执行计划列表
*/
$(document).ready(function() {
    // 平台
    var pt = $("#hidPt").val();
    if( pt == '' )
        pt = 'wh'
    //默认加载自动发起交易列表
    $('#tbsJhrwgl iframe')[0].src='/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/zdfqjylb_view?pt=' + pt;
    //选项卡间进行切换
    $("#tbsJhrwgl").tabs({
        onSelect: function(title, index){
            if( index == 0 ){
                //自动发起交易列表
                $("#tbsJhrwgl iframe")[0].src='/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/zdfqjylb_view?pt=' + pt;
            }else if( index == 1 ){
                //监控规则发起列表
                $('#tbsJhrwgl iframe')[1].src='/oa/yw_jhrw/yw_jhrw_002/yw_jhrw_002_view/index_view';
            }else if( index == 2 ){
                //当日执行计划列表
                $('#tbsJhrwgl iframe')[2].src='/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/index_view';
            }
        }
    });
});