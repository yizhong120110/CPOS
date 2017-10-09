/**
* 参数管理选项卡切换
* 第一个选项卡：系统参数管理
* 第二个选项卡：业务参数管理
* 第三个选项卡：交易参数
*/
$(document).ready(function() {
    /**
    * 默认加载系统参数管理
    */
    $('#tbsCsgl iframe')[0].src='/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/index_view?pt=wh';
    /**
    * 选项卡间进行切换
    */
    $("#tbsCsgl").tabs({
        onSelect: function(title, index){
            if( index == 0 ){
                /**
                * 系统参数管理
                */
                $("#tbsCsgl iframe")[0].src='/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/index_view?pt=wh';
            }else if( index == 1 ){
                /**
                * 业务参数管理
                */
                $('#tbsCsgl iframe')[1].src='/oa/yw_csgl/yw_csgl_002/yw_csgl_002_view/ywcsgl_indx_view?pt=wh';
            }else if( index == 2 ){
                /**
                * 交易参数管理
                */
                $('#tbsCsgl iframe')[2].src='/oa/yw_csgl/yw_csgl_003/yw_csgl_003_view/jycsgl_indx_view?pt=wh';
            }
        }
    });
});