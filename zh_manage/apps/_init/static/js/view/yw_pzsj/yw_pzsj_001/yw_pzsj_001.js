// 导入流水
var drlsid = '';
// 【数据采集配置】和【适用对象(监控对象)】的对应关系；【监控配置】和【分析规则，响应动作】的对应关系；
var relation = {};
// 【数据采集配置】和【适用对象(监控对象)】的对应关系；【监控配置】和【分析规则，响应动作】的反转对应关系；
var relation_reverse = {}
// 记录警告次数
var alertNum = 0;
$(document).ready(function() {
    loadDrsj();
    var array = new Array()
    //导入按钮
    $('#lbtnYwdrSubmit').click(function(){
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
        // 获取用户选择的内容
        var sel_id_dic = get_sel_dic();
        $('#dicImportMsgWindow').find('form').form('submit', {
        url: '/oa/yw_pzsj/yw_pzsj_001/yw_pzsj_001_view/dr_submit_view',
        queryParams:{'id_dic':JSON.stringify(sel_id_dic),'drlsid':drlsid},
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
        url: '/oa/yw_pzsj/yw_pzsj_001/yw_pzsj_001_view/data_drwj_add_view',
        submit: function(data) {
            // 组织上传携带的参数
            data.formData = {};
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
                //页面加载后节点为展开状态
                $('#treYwdrLeft').treegrid('expandAll');
                $('#treYwdrRight').treegrid('expandAll');
                $('#hidDrlsid').val(data.result.drlsid);
                // 导入流水
                drlsid = data.result.drlsid;
                // 对应关系
                relation = data.result.relation;
                relation_reverse = data.result.relation_reverse
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
        url:"/oa/yw_pzsj/yw_pzsj_001/yw_pzsj_001_view/local_data_view",
        method: "POST",
        queryParams:{},
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
            {field: 'czr',title: '修改人',width: '15%'}, 
            {field: 'czsj',title: '修改时间',width: '25%',align:'center'},
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
            {field: 'czr',title: '修改人',width: '15%'}, 
            {field: 'czsj',title: '修改时间',width: '25%',align:'center'},
        ]],
        toolbar: '#dicDrLeftWindow'
    });
    
}

/*
*没有未提交的数据时，表格加载成功后为表格增加样式并创建fileup对象
*/
function onLoadSuccessImport( row,data ) {
    if (data.msg){
        afterAjax(data, "", "");
        return false;
    }
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
    //页面加载后节点为展开状态
    $('#treYwdrLeft').treegrid('expandAll');
    $('#treYwdrRight').treegrid('expandAll');
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
*左侧表格双击事件，若diff为1修改时且该节点下没有子节点时，进行版本比对
*/
function onDblClickRowImportLeft(row){
    $('#treYwdrLeft').treegrid('toggle', row.id);
    if($('#treYwdrRight').treegrid('getData').length!=0){
        if(row.id.length < 32 && row.lx != 'jcxxpz'){
            return ;
        }
        if ($('#treYwdrLeft').treegrid('getChildren',row.id).length==0 && row.id) {
            var id = row.id;
            var mc = row.name;
            if(!mc){
                mc = $('#treYwdrRight').treegrid('getSelected',row.id).name;
            }
            var gzid = row.gzid;
            if (!row.gzid){
                gzid = $('#treYwdrRight').treegrid('getSelected',row.id).gzid;
            }
            var zbid = row.zbid;
            if (!row.zbid){
                zbid = $('#treYwdrRight').treegrid('getSelected',row.id).zbid;
            }
            bbdb(id,mc,row.lx,row.zbid,gzid);
        }
    }
}

/*
*右侧表格双击事件，通过表格的触发器自动展开、折叠节点
*/
function onDblClickRowImportRight(row){
    $('#treYwdrRight').treegrid('toggle', row.id);
    if($('#treYwdrLeft').treegrid('getData').length!=0){
        if(row.id.length < 32 && row.lx != 'jcxxpz'){
            return ;
        }
        if ($('#treYwdrRight').treegrid('getChildren',row.id).length==0 && row.id) {
            var id = row.id;
            var mc = row.name;
            if(!mc){
                mc = $('#treYwdrLeft').treegrid('getSelected',row.id).name
            }
            var gzid = row.gzid;
            if (!row.gzid){
                gzid = $('#treYwdrRight').treegrid('getSelected',row.id).gzid;
            }
            var zbid = row.zbid;
            if (!row.zbid){
                zbid = $('#treYwdrRight').treegrid('getSelected',row.id).zbid;
            }
            bbdb(id,mc,row.lx,zbid,gzid);
        }
    }
}

/*
*版本对比
*/
function bbdb(id,mc,lx,zbid,gzid){
    var data = '?lx='+lx+'&id='+id+"&mc="+mc+"&zbid="+zbid+"&gzid="+gzid
    var url = '/oa/yw_pzsj/yw_pzsj_001/yw_pzsj_001_view/bbdb_data_view';
    newTab(mc + '_版本对比', url+data);
}

/*
*在用户勾选一行的时候触发,将右侧本地库的treegrid状态改为选中状态
*/
function onCheck(row){
    var cur_flag =  $("#s"+row.id)[0].checked;
    // 获取该节点所有的子节点
    var all_childs = [];
    all_childs = get_all_child(row.id,all_childs);
    // 选中所有点击节点下的子节点所引用的内容
    $.each(all_childs,function(index,aid){
        check_par(row.id,aid,cur_flag);
    })
    
    // 如果点击的节点有引用其他节点，那么选中那些引用的节点
    check_par(row.id,row.id,cur_flag);
    alertNum += 1;
    // 如果是子引用并且在引用关系中，就要校验父引用是否选中了，如果选中，则不能取消子引用的选中
    var link = false;
    // 当前选中节点的父引用节点的状态
    var parYt = false;
    // 判断当前节点有没有被引用
    if (relation_reverse[row.id]){
        link = true;
    }
    // 判断当前节点的父引用节点的选中状态
    if (relation_reverse[row.id]){
        $.each(relation_reverse[row.id],function(index,id_){
            if ($('#s'+id_)[0].checked){
                parYt = true;
            }
        });
    }
    // 全部取消或者选中整个监控定义，那么不做校验
    if (row.id != '监控定义'){
        $.each(all_childs,function(index,id){
            if (relation_reverse[id]){
                link = true;
                // 判断父引用的选中状态
                if (relation_reverse[id]){
                    $.each(relation_reverse[id],function(index,id_){
                        if ($('#s'+id_)[0].checked){
                            parYt = true;
                        }
                    });
                }
            }
        });
        if(link){
            var curYt = $('#s'+row.id)[0].checked;
            if(parYt && curYt==false && alertNum%2!=0){
                $('#s'+row.id)[0].checked = true;
                $.messager.alert('警告','该选项被【数据采集配置】或【监控配置】引用，不可取消导入！','warning');
            }
        }
    }
    cArray = $('#treYwdrRight').treegrid('getChildren',row.id)
    for(j=0;j<cArray.length;j++){
        cObj = cArray[j]
        $("#s"+cObj.id)[0].checked = cur_flag;
    }
}

/*
* 选中该节点引用的节点。
*/
function check_par(checkid,aid,cur_flag){
    // 如果该节点引用了其他节点，其该节点的状态是选中
    if (relation[aid] && cur_flag){
        $.each(relation[aid],function(index,id){
            var flag = $("#s"+checkid)[0].checked;
            //当左侧表格有数据时,选中对应节点
            if($('#treYwdrLeft').treegrid('getData').length!=0){
                $('#s'+id)[0].checked = flag;
            }
        });
    }
}

/*
* 获取用户勾选的节点的所有子节点id
*/
function get_all_child(id,id_list){
    var ls = $('#treYwdrLeft').treegrid('getChildren',id);
    $.each(ls,function(index,obj){
        id_list.push(obj.id);
        get_all_child(obj.id,id_list);
    });
    return id_list;
}

/*
* 获取用户勾选的需要导入的内容id
*/
function get_sel_dic(){
    var tree_node = ["jkdx","fxgz","xydz","sjcjpz","jkfxpz","yzjypz","yzjycspz","jcxxpz"];
    
    var input_lst = $("input[name='selectRadio']:checked");
    var id_dict = {"fxgz_ids":[],"jcxxpz_ids":[],"jkdx_ids":[],"jkfxpz_ids":[],"sjcjpz_ids":[],"xydz_ids":[],"yzjycspz_ids":[],"yzjypz_ids":[]};
    for (var i = 0 ; i < input_lst.length; i++){
        // 获取节点的值  id|类型
        var input_value = input_lst[i].value;
        var sp = input_value.split("|");
        if(tree_node.indexOf(sp[1]) != -1){
            id_dict[sp[1]+"_ids"].push(sp[0]);
        }
    }
    return id_dict;
}