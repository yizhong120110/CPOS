$(document).ready(function() {
    
    $("#tbsZlcxq iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_008/kf_ywgl_008_view/index_view?zlcid=" + $("#zlcid").val();
    
    var busnessTab = $("#tbsZlcxq").tabs({
        tabPosition: 'left',
        enableConextMenu: true,
        onSelect: function(title, index){
            if( index == 1 ){
                $("#tbsZlcxq iframe")[1].src = "/oa/kf_ywgl/kf_ywgl_004/kf_ywgl_004_view/index_view?lx=zlc&id=" + $("#zlcid").val();
            }
            if( index == 2 ){
                 $("#tbsZlcxq iframe")[2].src =  "/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/index_view?lb=2&sslb=2&ssid=" + $("#zlcid").val();
            }
        }
    });
    
});
