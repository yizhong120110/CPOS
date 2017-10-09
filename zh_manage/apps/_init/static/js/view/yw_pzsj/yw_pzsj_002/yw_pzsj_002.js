$(document).ready(function() {
    // 先隐藏提示信息和导出按钮
    $("#div_warning").hide();
    $("#div_dc").hide();
    // 输入框长度限制
    $("#txtDcms").next().children().attr("maxlength","50");
    $("#txtBzxx").next().children().attr("maxlength","150");
    // 校验是否有需要导出的内容、如果有的话就导出
    check_sj();
});

/**
 * 校验是否有需要导出的内容
 **/
function check_sj(){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/yw_pzsj/yw_pzsj_002/yw_pzsj_002_view/data_view",
        data: {},
        success: function(data){
            //判断是否有要导出的数据
            if( data.have ){
                // 加载要导出的数据
                loadDcsj(data.return_data);
                $("#div_warning").hide();
                $("#div_dc").show();
            }else{
                $("#div_warning").show();
                $("#div_dc").hide();
                $.messager.alert('提示', data.msg, 'info');
            }
        },
        error: function () {
            errorAjax();
        }
    });
    //导出按钮
    $('#lbtnYwdcSubmit').click(function(){
        newWindow($("#dicExportMsgWindow"),'导出',450,260);
    });
    //导出时的取消按钮
    $('#lbtnExportCancel').click( function(e){
        e.preventDefault();
        $("#dicExportMsgWindow").window('close');
    });
    //导出时的导出按钮
    $('#lbtnExportSubmit').click( function(e){
        e.preventDefault();
        // 导出
        $('#dicExportMsgWindow').find('form').form('submit', {
            url: "/oa/yw_pzsj/yw_pzsj_002/yw_pzsj_002_view/dc_view",
            onSubmit:function (){
                //导出描述
                var dcms = $('#txtDcms').textbox('getValue');
                if (dcms=="") {
                        $.messager.alert('错误','导出描述不可为空，请输入','error', function(){
                        $("#txtDcms").next().children().focus();
                    });
                    return false;
                }
                // 遮罩
                ajaxLoading();
                return true;
            } ,
            success: function(data){
                // 取消遮罩
                ajaxLoadEnd();
                afterAjax(data, "", "dicExportMsgWindow");
            },
            error: function () {
                // 取消遮罩
                ajaxLoadEnd();
                errorAjax();
            }
        });
    });
}

/**
  * 加载待导出内容
  **/
function loadDcsj(return_data){
    // 导出内容的treegrid
    $('#treYwdc').treegrid({
        nowrap: true,
        fit: true,
        title: '待导出内容',
        data:return_data,
        idField: 'id',
        treeField: 'name',
        onLoadSuccess:loadSuccess,
        onDblClickRow:onDblClickRow,
        rowStyler: function(row) {
            style_str = 'height:22px;';
            if (row.name == undefined) {
                style_str = "hidden";
            }
            return style_str
        },
        columns: [[
            {field: 'name',title: '文件名',width: '50%',formatter: function(value, rowData, rowIndex) {
                    return rowData.name;
                }
            }, 
            {field: 'czr',title: '修改人',width: '15%'}, 
            {field: 'czsj',title: '修改时间',width: '25%',align:'center'}
        ]]
    });
}

/**
 * 导出的treegrid加载成功后调用的方法
 **/
function loadSuccess( ) {
    //页面加载后节点为折叠状态
    $('#treYwdc').treegrid('expandAll');
}
/**
 * 导出的treegrid的双击事件
 **/
function onDblClickRow(row){
    $('#treYwdc').treegrid('toggle', row.id);
}