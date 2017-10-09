/**
* 通讯详情选项卡切换
* 第一个选项卡客户端、服务端都是基本信息
* 第二个选项卡：
* 客户端为：C端通讯管理
* 服务端为：交易码解出函数
*/
$(document).ready(function() {
    var txid = $("#txid").val();
    $('#tbsTxxq iframe')[0].src='/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jbxx_view?txid=' + txid + "&nocache=" +Math.random();
    $("#tbsTxxq").tabs({
         onSelect: function(title, index){
            if( index == 0 ){
                $("#tbsTxxq iframe")[0].src='/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jbxx_view?txid=' + txid + "&nocache=" +Math.random();
            }
            if( index == 1 ){
                var fwfx = $("#fwfx").val();
                //服务方向 1（客户端） 2（服务端）
                if( fwfx == '2' ){
                    // 交易码解出函数
                    $('#tbsTxxq iframe')[1].src='/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_jymjchs_view?txid=' + txid + "&nocache=" +Math.random();
                }else{
                    $('#tbsTxxq iframe')[1].src='/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/txxq_cdtx_view?txid=' + txid + "&nocache=" +Math.random();
                }
            }
         }
    });
    
});