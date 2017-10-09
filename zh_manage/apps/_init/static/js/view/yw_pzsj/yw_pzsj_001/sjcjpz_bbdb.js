$(document).ready(function() {
    $("#tbsLeft").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tbsRight").tabs('select', index);
        }
    });

    $("#tbsRight").tabs({
        onSelect: function(title, index) {
            regionSH(title);
            $("#tbsLeft").tabs('select', index);
        }
    });
    //节点基本信息
    $('#dgJbxxLeft').datagrid({
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
                    bzArray = leftDxcjpzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: leftDxcjpzRs.leftJkdx
    });
    $('#dgJbxxRight').datagrid({
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
                    bzArray = rightDxcjpzRs.diff.split(',');
                    for(var i = 0; i < bzArray.length; i++){
                        if(row.id == bzArray[i]){
                            return 'background-color:#ffee00;color:red;';
                        }
                    }
                }
            }]
        ],
        data: rightDxcjpzRs.rightJkdx
    });
    //适用对象
    $('#dgSydxLeft').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [],
        data: leftSydxRs.rows
    });
    //适用对象
    $('#dgSydxRight').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [],
        data: rightSydxRs.rows
    });
    setField("dgSydxLeft",leftSydxRs);
    setField("dgSydxRight",rightSydxRs);
    
    // 传入参数
    $('#dgCrcsLeft').datagrid({
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
                width: 120,
                hidden:true
            }, {
                field: 'dxmc',
                title: '适用对象名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('dxmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }]
        ],
        data: leftCrcsRs
    });
    // 传入参数
    $('#dgCrcsRight').datagrid({
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
                width: 120,
                hidden:true
            }, {
                field: 'dxmc',
                title: '适用对象名称',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('dxmc',row);
                }
            }, {
                field: 'csdm',
                title: '参数代码',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csdm',row);
                }
            }, {
                field: 'cssm',
                title: '参数说明',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('cssm',row);
                }
            }, {
                field: 'csz',
                title: '参数值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('csz',row);
                }
            }, {
                field: 'sfkk',
                title: '是否可空',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('sfkk',row);
                }
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50,
                styler: function(value, row, index) {
                    return dif_field('mrz',row);
                }
            }]
        ],
        data: rightCrcsRs
    });
    
    // 监听左侧grid body滚动
    $('#dgJbxxLeft').datagrid('getBody').scroll(function(e){
        $("#dgJbxxRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgJbxxRight').datagrid('getBody').scroll(function(e){
        $("#dgJbxxLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgSydxLeft').datagrid('getBody').scroll(function(e){
        $("#dgSydxRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgSydxRight').datagrid('getBody').scroll(function(e){
        $("#dgSydxLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听左侧grid body滚动
    $('#dgCrcsLeft').datagrid('getBody').scroll(function(e){
        $("#dgCrcsRight")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    // 监听右侧grid body滚动
    $('#dgCrcsRight').datagrid('getBody').scroll(function(e){
        $("#dgCrcsLeft")
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
});

/*
*动态展示、隐藏内容
*/
function regionSH(title) {
    if (title == '基本信息') {
        $('#divJbxx').show();
        $('#divSydx').hide();
        $('#divCrcs').hide();
    } else if (title == '适用对象') {
        $('#divJbxx').hide();
        $('#divSydx').show();
        $('#divCrcs').hide();
    } else if (title == '传入参数') {
        $('#divJbxx').hide();
        $('#divSydx').hide();
        $('#divCrcs').show();
    }
}
/*
* 设置grid的field
*/
function setField(grid_id,data){
    var array =[];
    var columns = [];
    data = data.csz;
    $(data).each(function(){
        array.push({field:'',title:'',width:''});
    });
    columns.push(array);
    $(data).each(function(index,el){
        columns[0][index]['field']= el.csdm;
        columns[0][index]['title']= el.cssm;
        // 15个像素一个字，动态的判断field的宽度
        if (el.cssm.length > 10){
            columns[0][index]['width'] = 15 * el.cssm.length;
        }else{
            columns[0][index]['width'] = 150;
        }
        
        columns[0][index]['styler'] = 
        function(value, row, index) {
            return dif_field(el.csdm,row);
        }
    });
    $("#"+grid_id).datagrid({'columns':columns});
}
