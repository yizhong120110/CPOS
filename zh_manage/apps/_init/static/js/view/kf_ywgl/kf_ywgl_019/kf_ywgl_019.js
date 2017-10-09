$(document).ready(function() {
    var drlx = $('#hidDrlx').val();
    var ywid = $('#hidYwid').val();
    var txid = $('#hidTxid').val();
    if((drlx == 'yw' && ywid == '-1')||(drlx == 'tx' && txid == '-1')){
        //如果是导入新业务、新通讯
        loadDrsj()
    }else{
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/data_import_jy_view",
            data: {"ywid":$('#hidYwid').val(),"drlx":$('#hidDrlx').val(),'txid':$('#hidTxid').val()},
            success: function(data){
                if( data.state){
                    //判断是否有未提交的数据
                    //有未提交数据，需同时加载左右两侧的数据
                    if( data.sfywtj ){
                        // 更新tab名称
                        $('#divImportWindow').hide();
                        $('#dicDrtxWindow').show();
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
                        //加载导入数据
                        $('#divImportWindow').show();
                        $('#dicDrtxWindow').hide();    
                        loadDrsj();
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
    }
    //提交按钮
    $('#lbtnCommit').click( function(e){
        obj = $('#treDrtxLeft').treegrid( 'getSelected' );
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
        obj = $('#treDrtxLeft').treegrid( 'getSelected' );
        if( obj.diff == '1' || obj.diff == '2'){
            bbsftj = '2';
        }else{
            bbsftj = '1';
        }
        bbhy(obj.lx,bbsftj,obj.id,'',obj.version );
    });
    var array;
    //导入按钮
    $('#lbtnYwdrSubmit').click(function(){
        array = new Array();
        var checkArray = $("input[name='selectRadio']:checked");
        if(checkArray.length == 0){
            $.messager.alert('提示', '请勾选要导入的内容!', 'info');
            return false;
        }else{
            $.each(checkArray, function(){
                var drxx = $(this).val();
                if(drxx.split('|')[1]!= 'JD'&&drxx.split('|')[1]!= 'YW'&&drxx.split('|')[1]!= 'JY'&&drxx.split('|')[1]!= 'ZLC'&&drxx.split('|')[1]!= 'DYMB'&&drxx.split('|')[1]!= 'GGHS'&&drxx.split('|')[1]!= 'SJKMX'&&drxx.split('|')[1]!= 'undefined'){
                    array.attach(drxx)
                }
            }); 
            if(array.length == 0){
                $.messager.alert('提示', '请勾选要导入的内容!', 'info');
                return false;
            }
        }
        $.ajax({
            type: 'POST',
            dataType: 'text',
            url: "/oa/kf_ywgl/kf_ywgl_022/kf_ywgl_022_view/drht_sel_view",
            success: function(data){
                data = $.parseJSON(data);
                if( data.state == true ){
                    newWindow($("#dicImportMsgWindow"),'导入保存',600,280);
                    // 复核人
                    $('#selFhr').combobox({
                        editable:false,
                        data:data.fhr_lst,
                        valueField:'hydm',
                        textField:'xm'
                    });
                    //默认选择第一个
                    if( data.fhr_lst.length > 0 ){
                        $("#selFhr").combobox('select', $("#selFhr").combobox("getData")[0].hydm);
                    }
                    // 重新初始化tabindex
                    $('#drForm').tabSort();
                }else{
                    //$.messager.alert('提示', data.msg, 'error');
                    afterAjax(data, "", "");
                }
            },
            error : function(){
                $.messager.alert('提示', '请求异常，请刷新页面后重试！', 'error');
            }
        });
    });
    //导入时的取消按钮
    $('#lbtnImportCancel').click( function(e){
        e.preventDefault();
        $("#dicImportMsgWindow").window('close');
    });
    //导入时的导入按钮
    $('#lbtnImportSubmit').click( function(e){
        e.preventDefault();
        // 添加遮罩
        ajaxLoading();
        // 如果导入的为新业务，传入后台的业务ID为待导入的业务ID
        if( $('#hidYwid').val() == '-1'){
            ywid = $('#treYwdrLeft').treegrid('getRoots')[0].id
        }else{
            ywid = $('#hidYwid').val()
        }
        $('#dicImportMsgWindow').find('form').form('submit', {
        url: '/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/dr_submit_view',
        queryParams:{'ywid':ywid,'drlx':$("#hidDrlx").val(),'txid':$('#hidTxid').val(),'drxx':JSON.stringify(array),xtlx:$('#hidXtlx').val(),'drlsid':$('#hidDrlsid').val()},
        onSubmit: function(){
            // 校验回退描述
            var drms = $("#txtDrms").textbox("getValue");
            var ret = checkNull( drms, '导入描述', 'txtDrms' );
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
                // 校验复核人
                var fhr = $("#selFhr").textbox("getValue");
                ret = checkNull( fhr, '复核人', 'selFhr' );
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            } else {
                // 校验复核人密码
                var fhrmm = $("#txtFhrmm").textbox("getValue");
                ret = checkNull( fhrmm, '复核人密码', 'txtFhrmm' );
            }
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
                return false
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, "", "dicImportMsgWindow");
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            $.messager.alert('提示','导入请求出现异常，请稍后重试','error');
        }
    });

    });
    // 最大值限制
    $("#txtDrms").next().children().attr("maxlength","50");
    $("#txtBzxx").next().children().attr("maxlength","150");
    //待导入文件对象
    var fileup = fileUpload({
        id: 'filDrwj',
        progressbar: 'scjd',
        url: '/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/data_drwj_add_view',
        submit: function(data) {
            // 组织上传携带的参数
            data.formData = {
                'ywid':$("#hidYwid").val(),
                'drlx':$("#hidDrlx").val(),
                'xtlx':$("#hidXtlx").val(),
                'txid':$('#hidTxid').val(),
                };
        },
        add: function(data) {
            if(!fileup.isAddFile){
                return false;
            }
            var fname_arr = fileup.filename.split('.');
            if (fname_arr.length <= 1 || fname_arr[fname_arr.length - 1] != 'dmp') {
                $.messager.alert('错误','导入文件必须已[.dmp]为后缀，请重新选择','error');
                return false;
            }
            ajaxLoading();
            $('#treYwdrRight').treegrid('collapseAll');
            fileup.submit();
        },
        success:function(data){
            if(data.result.state){
                ajaxLoadEnd();
                $('#treYwdrLeft').treegrid('loadData',data.result.leftRows);
                $('#treYwdrRight').treegrid('loadData',data.result.rightRows);
                //页面加载后节点为折叠状态
                $('#treYwdrRight').treegrid('collapseAll');
                $('#treYwdrLeft').treegrid('collapseAll');
                $('#hidDrlsid').val(data.result.drlsid)
            }else{
                //$.messager.alert('错误',data.result.msg,'error');
                afterAjax(data.result, "", "");
                ajaxLoadEnd();
            }
        },
        error: function () {
            errorAjax();
            ajaxLoadEnd();
        }
    });
});

/*
*没有未提交的数据，直接展示数据
*/
function loadDrsj(){
    $('#treYwdrRight').treegrid({
        nowrap: true,
        fit: true,
        title: '本地库',
        url:"/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/data_view",
        method: "GET",
        queryParams:{'ywid':$("#hidYwid").val(),'drlx':$("#hidDrlx").val(),'txid':$('#hidTxid').val()},
        idField: 'id',
        treeField: 'name',
        onClickRow: onClickRowImport,
        onLoadSuccess: onLoadSuccessImport,
        onExpand: onExpandImport,
        onCollapse: onCollapseImport,
        onDblClickRow:onDblClickRowImportRight,
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
            {field: 'name',title: '文件名',width: '60%',formatter: function(value, rowData, rowIndex) {
                    return rowData.name;
                }
            }, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'},
        ]],
        toolbar: '#dicDrRightWindow'
    });
    
    $('#treYwdrLeft').treegrid({
        nowrap: true,
        fit: true,
        title: '待导入库',
        method: "GET",
        idField: 'id',
        treeField: 'name',
        onLoadSuccess: onLoadSuccessImport,
        onClickRow: onClickRowImport,
        onExpand: onExpandImport,
        onCollapse: onCollapseImport,
        onDblClickRow:onDblClickRowImportLeft,
        onCheck:onCheck,
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
            {field: 'id', hidden: true},
            {field: 'name',title: '文件名',width: '60%',formatter: function(value, rowData, rowIndex) {
                    return "<input type='checkbox' checked='true' name='selectRadio'  value='" + rowData.id +'|'+rowData.lx+ "' id='" +'s'+rowData.id+ "'/>" + rowData.name;                    
                }
            }, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'},
        ]],
        toolbar: '#dicDrLeftWindow'
    });
    
}

/*
*加载未提交数据
*/
function loadWtjsj(){
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/data_wtjsj_view",
        data:{'ywid':$("#hidYwid").val(),'drlx':$("#hidDrlx").val(),'txid':$('#hidTxid').val()},
        success: function(data){
            if(data.state){
                loadLeft(data.leftRows);
                loadRight(data.rightRows);   
                //页面加载后节点为折叠状态
                $('#treDrtxLeft').treegrid('collapseAll');
                $('#treDrtxRight').treegrid('collapseAll');
                //左右滚动条同步
                $('#treDrtxLeft').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
                    $('#treDrtxRight').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
                });
                $('#treDrtxRight').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
                    $('#treDrtxLeft').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
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
    $('#treDrtxLeft').treegrid({
        nowrap: true,
        fit: true,
        title: '本地未提交的修改',
        method: "GET",
        idField: 'id',
        treeField: 'name',
        onClickRow: onClickRowExport,
        onLoadSuccess: onLoadSuccessExport,
        onExpand: onExpandExport,
        onCollapse: onCollapseExport,
        onContextMenu:onContextMenu,
        onDblClickRow:onDblClickRowExportLeft,
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
            {field: 'name',title: '文件名',width: '60%',formatter: function(value, rowData, rowIndex) {
                    return rowData.name;
                }
            }, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'}
        ]],
        data:rows,
        toolbar: '#dicLeftWindow'
    });
}

/*
*有未提交数据时,加载右侧数据
*/
function loadRight(rows){
    $('#treDrtxRight').treegrid({
        nowrap: true,
        fit: true,
        title: '已提交的最新版本库',
        method: "GET",
        idField: 'id',
        treeField: 'name',
        onLoadSuccess: onLoadSuccessExport,
        onClickRow: onClickRowExport,
        onExpand: onExpandExport,
        onCollapse: onCollapseExport,
        onDblClickRow:onDblClickRowExportRight,
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
            {field: 'name',title: '文件名',width: '60%',formatter: function(value, rowData, rowIndex) {
                    return rowData.name;
                }
            }, 
            {field: 'xgr',title: '修改人',width: '15%'}, 
            {field: 'xgsj',title: '修改时间',width: '25%',align:'center'}
        ]],
        data:rows,
        toolbar: '#dicRightWindow'
    });
}
/*
*有未提交数据时,当表格加载成功后，为记录增加提交、还原菜单
*/
function onLoadSuccessExport( row,data ) {
    $("tr[style='hidden']").css("height","22px").find("div").css({"visibility": "hidden"});
    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:red']")
        .bind('contextmenu', function(e) {
            e.preventDefault();
            $('#mm').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        })
        .find("td[field='name'] span[class='tree-title']")
        .prev()
        .html('<span class="modified"></span>')

    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:blue']")
        .bind('contextmenu', function(e) {
            e.preventDefault();
            $('#mm').menu('show', {
                left: e.pageX,
                top: e.pageY
            });
        })
        .find("td[field='name'] span[class='tree-title']")
        .prev()
        .html('<span class="added"></span>')
}

/*
*没有未提交的数据时，表格加载成功后为表格增加样式并创建fileup对象
*/
function onLoadSuccessImport( row,data ) {
    $("tr[style='hidden']").css("height","22px").find("div").css({"visibility": "hidden"});
    if($('#treYwdrLeft').treegrid('getData').length==0&&$('#treYwdrRight').treegrid('getData').length!=0 ){
        $('#treYwdrRight').treegrid('collapseAll');
    }
    if($('#treYwdrLeft').treegrid('getData').length!=0){
        $('#treYwdrLeft').treegrid('collapseAll');
        $('#treYwdrRight').treegrid('collapseAll');
        //左右滚动条同步
        $('#treYwdrLeft').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
            $('#treYwdrRight').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
        });
        $('#treYwdrRight').parent().find('.datagrid-view2 .datagrid-body').scroll(function(e) {
            $('#treYwdrLeft').parent().find('.datagrid-view2 .datagrid-body').scrollTop($(e.target).scrollTop());
        });    
    }
    var panel = undefined;
    var gridBody = undefined;
    var height = undefined;
    var gridHeader = undefined;
    panel = $('#treYwdrLeft').treegrid('getPanel');
    gridBody = panel.find('.datagrid-view2 > .datagrid-body');
    gridHeader = panel.prev();
    height = gridBody.outerHeight();
    // 当没有数据时
    if ( $('#treYwdrLeft').treegrid('getData').length==0 ) {
        gridBody.append('<div style="text-align: center; font-size: 3em; margin-top: ' + height / 3 + 'px">请选择待导入的文件</div>');
    }
    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:red']")
        .find("td[field='name'] span[class='tree-title']")
        .prev()
        .html('<span class="modified"></span>')
    $("div[data-options='region:\\'west\\',split:true'] tr[style*='color:blue']")
        .find("td[field='name'] span[class='tree-title']")
        .prev()
        .html('<span class="added"></span>')
    
}

/*
*表格的点击事件，当选择左侧或右侧某一节点时，另一侧也选择
*/
function onClickRowExport(row) {
    $('#treDrtxLeft').treegrid('select', row.id);
    $('#treDrtxRight').treegrid('select', row.id);
}

/*
*在节点被展开的时候触发，同时将左右两侧对应的节点展开
*/
function onExpandExport(row) {
    $('#treDrtxLeft').treegrid('expand', row.id);
    $('#treDrtxRight').treegrid('expand', row.id);
}

/*
*在节点被折叠的时候触发，同时将左右两侧对应的节点折叠
*/
function onCollapseExport(row) {
    $('#treDrtxLeft').treegrid('collapse', row.id);
    $('#treDrtxRight').treegrid('collapse', row.id);
}

/*
*表格的点击事件，当选择左侧或右侧某一节点时，另一侧也选择，因左侧或右侧可能没有数据，无法选中，所以需要增加判断
*/
function onClickRowImport(row) {
    //当左侧表格有数据时,选中对应节点
    if($('#treYwdrLeft').treegrid('getData').length!=0){
        $('#treYwdrLeft').treegrid('select', row.id);
    }
    //当右侧表格有数据时,选中对应节点
    if($('#treYwdrRight').treegrid('getData').length!=0){
        $('#treYwdrRight').treegrid('select', row.id);
    }
}

/*
*在节点被展开的时候触发，同时将左右两侧对应的节点展开
*/
function onExpandImport(row) {
    $('#treYwdrLeft').treegrid('expand', row.id);
    $('#treYwdrRight').treegrid('expand', row.id);
}

/*
*在节点被折叠的时候触发，同时将左右两侧对应的节点折叠
*/
function onCollapseImport(row) {
    if($('#treYwdrLeft').treegrid('getData').length!=0){
        $('#treYwdrLeft').treegrid('collapse', row.id);
    }
    if($('#treYwdrRight').treegrid('getData').length!=0){
        $('#treYwdrRight').treegrid('collapse', row.id);
    }
}

/*
*节点右键时，选中该节点
*/
function onContextMenu(e,row){
    if($('#treDrtxLeft').treegrid('getChildren',row.id).length!=0){
        $('#mm').menu('hide');
    }
    $('#treDrtxLeft').treegrid('select',row.id);
    $('#treDrtxRight').treegrid('select',row.id);
    var xtlx = $('#hidXtlx').val();
    if( $('#treDrtxLeft').treegrid('getChildren',row.id).length==0 ){
        var obj = $('#treDrtxLeft').treegrid("getChildren","数据库模型")
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

/*
*左侧表格双击事件，若diff为1修改时且该节点下没有子节点时，进行版本比对
*/
function onDblClickRowExportLeft(row){
    if ($('#treDrtxLeft').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD") {
            var id = row.id;
            var bbh1 = $('#treDrtxRight').treegrid('getSelected', row.id).version;
            var lx = row.lx;
            var mc = row.name;
            bbdb_wtj(id,lx,bbh1,mc,row.jdlx);
    }
    $('#treDrtxLeft').treegrid('toggle', row.id);
}

/*
*右侧表格双击事件，通过表格的触发器自动展开、折叠节点
*/
function onDblClickRowExportRight(row){
    if ($('#treDrtxRight').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD") {
        var obj = $('#treDrtxLeft').treegrid('getSelected', row.id);
        var id = obj.id
        var bbh1 = obj.version;
        var lx = obj.lx;
        var mc = obj.name;
        bbdb_wtj(id,lx,bbh1,mc,row.jdlx);
    }
    $('#treDrtxRight').treegrid('toggle', row.id);
}

/*
*左侧表格双击事件，若diff为1修改时且该节点下没有子节点时，进行版本比对
*/
function onDblClickRowImportLeft(row){
    if($('#treYwdrRight').treegrid('getData').length!=0){
        if ($('#treYwdrLeft').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD"&&row.lx!="DYMB") {
            //if(row.diff == '1'){
            var id = row.id;
            var lx = row.lx;
            if(!lx){
                var mc = $('#treYwdrRight').treegrid('getSelected',row.id).name
                var lx = $('#treYwdrRight').treegrid('getSelected',row.id).lx
            }else{
                var mc = row.name;
            }
            var drlx = $('#hidDrlx').val();
            var ywid = $('#hidYwid').val()
            var txid = ''
            //获取通讯节点
            if(drlx == 'tx' && lx != 'jd'){
                tx_arr = $('#treYwdrLeft').treegrid('getRoots')
                outerloop:
                for(i=0;i<tx_arr.length-1;i++){
                    pObj = tx_arr[i]
                    //-1是为了去除根节点
                    cArray = $('#treYwdrLeft').treegrid('getChildren',pObj.id)
                    for(j=0;j<cArray.length;j++){
                        cObj = cArray[j]
                        if(cObj.id == id ){
                            txid = pObj.id;
                            break outerloop;
                        }
                    }
                }
            }    
            bbdb(id,lx,mc,drlx,ywid,txid,row.jdlx);
            //}
        }
    }
    $('#treYwdrLeft').treegrid('toggle', row.id);
}

/*
*右侧表格双击事件，通过表格的触发器自动展开、折叠节点
*/
function onDblClickRowImportRight(row){
    if($('#treYwdrLeft').treegrid('getData').length!=0){
        if ($('#treYwdrRight').treegrid('getChildren',row.id).length==0&&row.lx!="YWCS"&&row.lx!="JY"&&row.lx!="ZLC"&&row.lx!="GGHS"&&row.lx!="SJKMX"&&row.lx!="JD"&&row.lx!="DYMB") {
            //if(row.diff == '1'){
            var id = row.id;
            var lx = row.lx;
            if(!lx){
                var mc = $('#treYwdrLeft').treegrid('getSelected',row.id).name
                var lx = $('#treYwdrLeft').treegrid('getSelected',row.id).lx
            }else{
                var mc = row.name;
            }
            var drlx = $('#hidDrlx').val();
            var ywid = $('#hidYwid').val()
            var txid = ''
            //获取通讯节点
            if(drlx == 'tx' && lx != 'jd'){
                tx_arr = $('#treYwdrRight').treegrid('getRoots')
                outerloop:
                for(i=0;i<tx_arr.length-1;i++){
                    pObj = tx_arr[i]
                    //-1是为了去除根节点
                    cArray = $('#treYwdrRight').treegrid('getChildren',pObj.id)
                    for(j=0;j<cArray.length;j++){
                        cObj = cArray[j]
                        if(cObj.id == id ){
                            txid = pObj.id;
                            break outerloop;
                        }
                    }
                }
            }    
            bbdb(id,lx,mc,drlx,ywid,txid,row.jdlx);
            //}
        }
    }
    $('#treYwdrRight').treegrid('toggle', row.id);
}

/**
 *版本对比-未提交
 */
function bbdb_wtj(id,lx,bbh1,mc,jdlx) {
    var data = '?lx='+lx+'&id='+id+'&bbh1='+bbh1+'&type=bd'+"&jdlx="+jdlx;
    var url = '/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbdb_data_view';
    newTab(mc + '_版本对比', url+data);
}

/*
*版本对比
*/
function bbdb(id,lx,mc,drlx,ywid,txid,jdlx){
    var data = '?lx='+lx+'&id='+id+'&drlx='+drlx+'&ywid='+ywid+"&txid="+txid+"&jdlx="+jdlx;
    var url = '/oa/kf_ywgl/kf_ywgl_019/kf_ywgl_019_view/bbdb_data_view';
    newTab(mc + '_版本对比', url+data);
}

function onCheck(row){
    flag = $("#s"+row.id)[0].checked;
    cArray = $('#treYwdrRight').treegrid('getChildren',row.id)
    for(j=0;j<cArray.length;j++){
        cObj = cArray[j]
        $("#s"+cObj.id)[0].checked = flag;    
    }
}