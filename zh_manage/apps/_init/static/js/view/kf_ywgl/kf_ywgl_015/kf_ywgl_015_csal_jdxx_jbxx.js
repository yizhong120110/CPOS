$(document).ready(function() {
    // 标记当前是否是通讯
    var tx = false;
    //输入要素列表
    var sryslb = ($('#hidSrys').val() + '');
    //输出要素列表
    var scyslb = ($('#hidScys').val() + '');
    sryslb = eval('(' + sryslb + ')');
    scyslb = eval('(' + scyslb + ')');
    // 如果是通讯的子流程测试案例   就显示输出要素。
    if ($('#hidLxdm').val() == '4'){
        $('#hideQw').val('1');
        tx = true;
    }
    $("#jsxx-jbxx-tabs").find("iframe").attr("src", url);

    // 输入要素表格渲染
    $('#dgSrys').datagrid({
        nowrap: false,
        fit: true,
        height: '78px',
        rownumbers: true,
        singleSelect: true,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        data: sryslb,
        columns: [
            [{
                field: 'ysdm',
                title: '输入要素',
                width: 21
            }, {
                field: 'qwscz',
                title: '值',
                width: 79,
                styler: function(value,row,index) {
                    return 'word-break:break-word;';
                },formatter:function(node){
                    return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
                }
            }]
        ]
    });

    // 输出要素表格渲染
    $('#dgScys').datagrid({
        nowrap: false,
        fit: true,
        height: '78px',
        rownumbers: true,
        singleSelect: true,
        fitColumns: true,
        method: "get",
        remoteSort: false,
        data: scyslb,
        columns: [
            [{
                field: 'ysdm',
                title: $('#hideQw').val() == '1' ? '输出要素' : '期望输出要素',
                width: $('#hideQw').val() == '1' ? 21 : 17
            }, {
                field: 'qwscz',
                title: '值',
                width: 79,
                styler: function(value,row,index) {
                    return 'word-break:break-word;';
                },formatter:function(value, rowData, rowIndex){
                    if(tx){
                        value = rowData.sjscz;
                    }
                    return $('<div/>').text(value).html().replace(/&lt;\/br&gt;/g,'</br>');
                }
            }, {
                field: 'sjscz',
                title: '实际返回',
                width: 79,
                styler: function(value,row,index) {
                    return 'word-break:break-word;';
                },formatter:function(node){
                    return $('<div/>').text(node).html().replace(/&lt;\/br&gt;/g,'</br>');
                },
                hidden: $('#hideQw').val() == '1'
            }]
        ]
    });

    $("#jsxx-jbxx-tabs").tabs({
        fit: true,
        border: true,
        showOption: true,
        enableNewTabMenu: true,
        tabPosition: 'top',
        headerWidth: 100
    })
    data = {"jdcsalzxbzid": $('#hidJdcsalzxbzid').text(),"csalid": $('#hidJdcsalid').text(),"pc": $('#hidPc').text()}
    if ($('#hidJdcsalzxbzid').text() != '' && $('#hidJdcsalzxbzid').text() != null) {
        data['mark'] = ''
    } else {
        data['mark'] = 'all'
    }
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_015/kf_ywgl_015_view/get_rz_view",
        data: data,
        success: function(data) {
            console.log(data.log);
            $("#rznr").text(data.log);
        },
        error: function() {
            errorAjax();
        }
    })
});
