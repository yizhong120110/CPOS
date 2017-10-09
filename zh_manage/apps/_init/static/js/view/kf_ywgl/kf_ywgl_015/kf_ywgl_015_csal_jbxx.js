$(document).ready(function() {
     $("#tbsJbxx").tabs({
         onSelect: function(title, index){
            if( index == 1 ){
                $("#tbsJbxx iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_009/kf_ywgl_009_view/csal_jdxx_view?csalid="+jbxx_csalid+"&lx="+lx;
            }
         }
    });
});
