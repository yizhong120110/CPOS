$(document).ready(function() {
    
    $("#tbsJyxq iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/index_view?jyid=" + $("#jyid").val();
    
    var busnessTab = $("#tbsJyxq").tabs({
        tabPosition: 'left',
        enableConextMenu: true,
        onSelect: function(title, index){
            if( index == 1 && $("#tbsJyxq iframe")[1].src==""){
                $("#tbsJyxq iframe")[1].src = "/oa/kf_ywgl/kf_ywgl_004/kf_ywgl_004_view/index_view?lx=lc&id=" + $("#jyid").val();
            }
            if( index == 2){
                $("#tbsJyxq iframe")[2].src = "/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/index_view?lb=1&sslb=1&ssid=" + $("#jyid").val();
            }
        }
    });
    
});
