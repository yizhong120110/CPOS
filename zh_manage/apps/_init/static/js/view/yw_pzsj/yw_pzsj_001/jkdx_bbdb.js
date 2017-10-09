$(document).ready(function() {
    $("#tbsLeft").tabs({
        onSelect: function(title, index) {
            //regionSH(title);
            $("#tbsRight").tabs('select', index);
        }
    });

    $("#tbsRight").tabs({
        onSelect: function(title, index) {
            //regionSH(title);
            $("#tbsLeft").tabs('select', index);
        }
    });
    //节点基本信息
    $('#dgJkdxLeft').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 50,
                hidden:true
            },{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = leftJkdxRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftJkdxRs.leftJkdx
    });
    $('#dgJkdxRight').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 50,
                hidden:true
            },{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280,
                styler: function(value, row, index) {
                    bzArray = rightJkdxRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightJkdxRs.rightJkdx
    });
     // 延迟1s解决拖动不显示
    setTimeout(function() {
        $('#divLjdm').mergely('options', {
            autoupdate: false,
            change_timeout: 3600000
        });
    }, 1000);
    // 监听左侧grid body滚动
    $('#dgJkdxLeft').datagrid('getBody').scroll(function(e){
        $("#dgJkdxRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJkdxRight').datagrid('getBody').scroll(function(e){
        $("#dgJkdxLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*动态展示、隐藏内容
*/
function regionSH(title) {
    if (title == '监控对象') {
        $('#divJkdx').show();
    }
}
