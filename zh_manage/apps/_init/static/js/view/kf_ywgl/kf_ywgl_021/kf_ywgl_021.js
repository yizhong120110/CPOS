$(document).ready(function() {
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/data_export_jy_view",
        data: {"ywid":$('#hidYwid').val(),"dclx":$('#hidDclx').val(),"txid":$('#hidTxid').val()},
        success: function(data){
            if( data.state){
                //判断是否有未提交的数据
                //有未提交数据，需同时加载左右两侧的数据
                if( data.sfywtj ){
                    // 更新tab名称
                    $('#divExportWindow').hide();
                    $('#dicDctxWindow').show();
                    var xtlx = $('#hidXtlx').val();
                    // 编码环境
                    if (xtlx == 'kf') {
                        // 开发环境
                        $('#lbtnCommit').show();
                    } else if (xtlx == 'sc') {
                        // 生产环境
                        $('#lbtnCommit').hide();
                    }
                    loadWtjsj();
                }else{
                    //加载导出数据
                    $('#divExportWindow').show();
                    $('#dicDctxWindow').hide();    
                    loadDcsj();
                }
            }else{
                //$.messager.alert('错误', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error: function () {
            errorAjax();
        }
    });
    //左侧表格右键点击事件,选中右键点击行
    $('#treDctxLeft').treegrid({
        onContextMenu:function(e,row){
            $('#treDctxLeft').treegrid( 'select',row.id );
            $('#treDctxRight').treegrid( 'select',row.id );
        }
    });
    //提交按钮
    $('#lbtnCommit').click( function(e){
        obj = $('#treDctxLeft').treegrid( 'getSelected' );
        if( obj.diff == '1' || obj.diff == '2'){
            bbsftj = '2';
        }else{
            bbsftj = '1';
        }
        bbtj(obj.lx,bbsftj,obj.id,'');
    });
    //还原按钮
    $('#lbtnRollback').click( function(e){
        e.preventDefault();
        obj = $('#treDctxLeft').treegrid( 'getSelected' );
        if( obj.diff == '1' || obj.diff == '2'){
            bbsftj = '2';
        }else{
            bbsftj = '1';
        }
        bbhy(obj.lx,bbsftj,obj.id,'',obj.version );
    });
    //导出按钮
    $('#lbtnYwdcSubmit').click(function(){
        newWindow($("#dicExportMsgWindow"),'导出保存',450,260);
    });
    //导出时的取消按钮
    $('#lbtnExportCancel').click( function(e){
        e.preventDefault();
        $("#dicExportMsgWindow").window('close');
    });
    //导出时的导出按钮
    $('#lbtnExportSubmit').click( function(e){
        jy_lst = JSON.stringify( $('#treYwdc').treegrid('getChildren','交易流程') );
        zlc_lst = JSON.stringify( $('#treYwdc').treegrid('getChildren','子流程') );
        sjkmx_lst = JSON.stringify( $('#treYwdc').treegrid('getChildren','数据库模型') );
        gghs_lst = JSON.stringify( $('#treYwdc').treegrid('getChildren','公共函数') );
        jd_lst = JSON.stringify( $('#treYwdc').treegrid('getChildren','节点') );
        //通讯导出时，获取所有的根节点，并将节点的去除，只保留通讯的
        var tx_lst = $('#treYwdc').treegrid('getRoots')
        //取出所有的通讯ID    
        tx_id_lst = new Array();
        for(var i =0;i<tx_lst.length-1;i++){
            tx_id_lst[i]=tx_lst[i].id;
        }
        tx_id_lst = JSON.stringify(tx_id_lst);
        e.preventDefault();
        $('#dicExportMsgWindow').find('form').form('submit', {
            url: "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/data_export_submit_view",
            queryParams: {'ywid':$("#hidYwid").val(),'dclx':$("#hidDclx").val(),'jy_lst':jy_lst,'xtlx':$("#hidXtlx").val(),'zlc_lst':zlc_lst,'sjkmx_lst':sjkmx_lst,'gghs_lst':gghs_lst,'jd_lst':jd_lst,'tx_id_lst':tx_id_lst },
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
    // 最大值限制
    $("#txtDcms").next().children().attr("maxlength","50");
    $("#txtBzxx").next().children().attr("maxlength","150");
});

/*
*没有未提交的数据，直接展示数据
*/
function loadDcsj(){
    $('#treYwdc').treegrid({
        nowrap: true,
        fit: true,
        title: '本地库',
        url: "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/data_view",
        method: "GET",
        queryParams:{'ywid':$("#hidYwid").val(),'dclx':$("#hidDclx").val(),'txid':$('#hidTxid').val()},
        idField: 'id',
        treeField: 'name',
        onLoadSuccess: onLoadSuccess,
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
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'}, 
            {field: 'version',title: '版本号',width: '10%',align:'right', halign:'center', formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;       
                    }else{
                        return ''
                    }       
                }  
            }
        ]]
    });
}
/*
*加载未提交数据
*/
function loadWtjsj(){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_021/kf_ywgl_021_view/data_wtjsj_view",
        data:{'ywid':$("#hidYwid").val(),'dclx':$("#hidDclx").val(),'txid':$('#hidTxid').val()},
        success: function(data){
            if(data.state){
                loadLeft(data.leftRows);
                loadRight(data.rightRows);   
                //页面加载后节点为折叠状态
                $('#treDctxLeft').treegrid('collapseAll');
                $('#treDctxRight').treegrid('collapseAll');
                //左右滚动条同步
                $('#treDctxLeft').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
                    $('#treDctxRight').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
                });
                $('#treDctxRight').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
                    $('#treDctxLeft').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
                });    
            }else{
                //$.messager.alert('错误', data.msg, 'error');
                afterAjax(data, "", "");
            }
        },
        error: function () {
            errorAjax();
        }
    });
}
/*
*有未提交数据时,加载左侧数据
*/
function loadLeft(rows){
    $('#treDctxLeft').treegrid({
        nowrap: true,
        fit: true,
        title: '本地未提交的修改',
        method: "GET",
        idField: 'id',
        treeField: 'name',
        onClickRow: onClickRow,
        onLoadSuccess: onLoadSuccess,
        onExpand: onExpand,
        onCollapse: onCollapse,
        onContextMenu:onContextMenu,
        onDblClickRow:onDblClickRowLeft,
        rowStyler: function(row) {
            style_str = 'height:22px;';
            if (row.diff == 1) {
                style_str += "color:red;" + style_str;
            } else if (row.diff == 2) {
                style_str += "color:blue;" + style_str;
            }
            if (row.name === undefined) {
                style_str = "hidden";
            }
            return style_str
        },
        columns: [[
            {field: 'name',title: '文件名',width: '50%'}, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'},
            {field: 'version',title: '版本号',width: '10%',align:'right', halign:'center', formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;       
                    }else{
                        return value
                    }       
                }  
            }
        ]],
        data:rows,
        toolbar: '#dicLeftWindow'
    });
}
/*
*有未提交数据时,加载右侧数据
*/
function loadRight(rows){
    $('#treDctxRight').treegrid({
        nowrap: true,
        fit: true,
        title: '已提交的最新版本库',
        method: "GET",
        idField: 'id',
        treeField: 'name',
        fitColumns: true,
        onClickRow: onClickRow,
        onLoadSuccess: onLoadSuccess,
        onExpand: onExpand,
        onCollapse: onCollapse,
        onDblClickRow:onDblClickRowRight,
        rowStyler: function(row) {
            style_str = 'height:22px;';
            if (row.diff == 1) {
                style_str += "color:red;" + style_str;
            } else if (row.diff == 2) {
                style_str += "color:blue;" + style_str;
            } 
            if (row.name === undefined) {
                style_str = "hidden";
            }
            return style_str
        },
        columns: [[
            {field: 'name',title: '文件名',width: '50%'}, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'},
            {field: 'version',title: '版本号',width: '10%',align:'right', halign:'center', formatter: function(value,row,index){
                    if(value){
                        return accounting.formatNumber(value) ;       
                    }else{
                        return value
                    }       
                }  
            }
        ]],
        data:rows,
        toolbar: '#dicRightWindow'
    });
}
function onLoadSuccess( ) {
    //页面加载后节点为折叠状态
    $('#treYwdc').treegrid('collapseAll');
    // 新增的文件图标添加"加号"，改变的文件图标加"叹号"
    $("tr[style='hidden']").css("height","22px").find("div").css({"visibility": "hidden"});
    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:red']").bind('contextmenu', function(e) {
        e.preventDefault();
        $('#mm').menu('show', {
            left: e.pageX,
            top: e.pageY
        });
    }).find("td[field='name'] span[class='tree-title']").prev().html('<span class="modified"></span>')

    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:blue']").bind('contextmenu', function(e) {
        e.preventDefault();
        $('#mm').menu('show', {
            left: e.pageX,
            top: e.pageY
        });
    }).find("td[field='name'] span[class='tree-title']").prev().html('<span class="added"></span>')
}
function onClickRow(row) {
    $('#treDctxLeft').treegrid('select', row.id);
    $('#treDctxRight').treegrid('select', row.id);
}
function onExpand(row) {
    $('#treDctxLeft').treegrid('expand', row.id);
    $('#treDctxRight').treegrid('expand', row.id);
}
function onCollapse(row) {
    $('#treDctxLeft').treegrid('collapse', row.id);
    $('#treDctxRight').treegrid('collapse', row.id);
}
function onContextMenu(e,row){
    var xtlx = $('#hidXtlx').val();
    $('#treDctxLeft').treegrid('select',row.id);
    $('#treDctxRight').treegrid('select',row.id);
    if( $('#treDctxLeft').treegrid('getChildren',row.id).length!=0 ){        
        $('#mm').menu('hide');
    }
    if( $('#treDctxLeft').treegrid('getChildren',row.id).length==0 ){
        var obj = $('#treDctxLeft').treegrid("getChildren","数据库模型")
        var hyobj = $('#lbtnRollback')[0];
        for(var i=0;i<obj.length;i++){
            if(row.id==obj[i].id&&xtlx!='sc'){
                $('#mm').menu('hideItem', hyobj);
                return
            }else{
                $('#mm').menu('showItem', hyobj);
            }
        }
    }else{
        $('#mm').menu('hide');
    }
}
function onDblClickRow(row){
    $('#treYwdc').treegrid('toggle', row.id);
}
function onDblClickRowLeft(row){
    if ($('#treDctxLeft').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD") {
        var id = row.id;
        var bbh1 = $('#treDctxRight').treegrid('getSelected', row.id).version;
        var lx = row.lx;
        var mc = row.name;
        bbdb(id,lx,bbh1,mc,row.jdlx);
    }
    $('#treDctxLeft').treegrid('toggle', row.id);
}
function onDblClickRowRight(row){
    if ($('#treDctxRight').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD") {
        var obj = $('#treDctxLeft').treegrid('getSelected', row.id);
        var id = obj.id
        var bbh1 = obj.version;
        var lx = obj.lx;
        var mc = obj.name;
        bbdb(id,lx,bbh1,mc,row.jdlx);
    }
    $('#treDctxRight').treegrid('toggle', row.id);
}

/**
 *版本对比
 */
function bbdb(id,lx,bbh1,mc,jdlx) {
    var data = '?lx='+lx+'&id='+id+'&bbh1='+bbh1+'&type=bd'+'&jdlx='+jdlx;
    var url = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbdb_data_view';
    newTab(mc + '_版本对比', url+data);
}
