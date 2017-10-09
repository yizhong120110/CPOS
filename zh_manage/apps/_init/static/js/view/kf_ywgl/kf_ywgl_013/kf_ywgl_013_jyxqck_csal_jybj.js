$(document).ready(function() {
    $("#srscys_tab").tabs({
         onSelect: function(title, index){
            if( index == 1){
                $("#srscys_tab iframe")[0].src = "/oa/kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx_view/index_view?csaldyid=" + csaldyid + "&lx=" + lx+"&demoid="+demoid;
            }
         }
    });
    if(rows_data.length){
        $('#csalms').textbox('setValue',rows_data[0]['ms']);
    }
});