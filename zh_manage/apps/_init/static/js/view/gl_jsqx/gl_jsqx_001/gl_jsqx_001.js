/**
 * 页面初始化加载
*/
$(document).ready(function() {

    // 用户列表初始化加载
    dataGrid_js =$('#dgJs').datagrid({
        method: "post",
        nowrap : false,
        singleSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/jslst_view",
        idField:'id',
        columns: [
            [
                {field: 'id',  width: 40, checkbox:'true' },
                {field: 'jsmc', title: '角色列表', width: 100}
            ]
        ],
        onBeforeLoad : function(param){
                //清空选择
		    	$(this).datagrid('clearSelections').datagrid('unselectAll');
		    },
        onClickRow:function(rowIndex,rowData){
        },
        onSelect: function(rowIndex,rowData){
            //默认第一个tab页
            $("#tabsCdView").tabs( "select" , 0 );
            //触发点击数据，加载菜单
            cdlb_get(rowData);
        },
        onLoadSuccess: function(data) {
            var pagination = $('#dgJs').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
        }
    });

    // 渲染表格，菜单数列表页面初始化信息加载
    treeGrid = $('#dgCdgl').treegrid({
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/data_view",
        idField:'id',
        treeField:'text',
        columns: [
            [
                {field: 'id', title: '菜单ID', width: 40, checkbox:'true' },
                {field: 'text', title: '菜单名称', width: 100},
                {field: 'lxmc', title: '类型', width: 60, align:'center' },
                {field: 'bz', title: '备注', width: 100}
            ]
        ],
        onBeforeLoad : function(param){
                //清空选择
		    	$(this).treegrid('clearSelections').treegrid('unselectAll');
		    },
        onClickRow:function(row){
             //设置树折叠属性
             //treeGrid.treegrid('toggle', row.id);
            //级联选择
            $(this).treegrid('cascadeCheck',{
                id:row.id, //节点ID
                deepCascade:false //深度级联
            });
        },
        onCheck:function(row){
            //级联选择
            $(this).treegrid('cascadeCheck',{
                id:row.id, //节点ID
                deepCascade:false //深度级联
            });
        },
        onUncheck:function(row){
            //级联选择
            $(this).treegrid('cascadeCheck',{
                id:row.id, //节点ID
                deepCascade:false //深度级联
            });
        },
        onLoadSuccess: function(node,data) {
            //页脚处理，显示刷新和数据总数
            var pagination = $('#dgCdgl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
            //选中已经拥有的权限
            getId(data['rows']);
        }
    });

    tabQx = $('#tabsCdView').tabs({

        onSelect:function(title,index){
            //获取选择的菜单
            var rows = $('#dgCdgl').treegrid('getSelections');
            //获取选择的角色
            var jsData = $('#dgJs').datagrid('getSelections');
            //选择的菜单id
            var cdids = new Array();
             $(rows).each(function(index, item){
                cdids.push(item["id"]);
             });
             if(index == 1){
                 // 清空数据
                 $('#dgCdGngl').datagrid('reload', {});
                 if(jsData.length>0){
                    // 加载画面数据
                     url = "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/cdlst_view"
                     dataR = {'cdid':cdids.join(','), 'jsid':jsData[0].id
                     }
                    //发送请求
                    $.ajax({
                        type: 'POST',
                        dataType: 'text',
                        url: url,
                        data: dataR,
                        success: function(data){
                            dataRr = $.parseJSON(data);
                            //菜单树加载
                            $('#trCdqx').tree({
                                    data: dataRr['rows'],
                                    loadFilter:function(data,parent){
                                        if(data){
                                            return data
                                        }
                                    }
                                    });
                        },
                        error : function(){
                            $.messager.alert('提示', '菜单树数据加载异常', 'info');
                        }
                    });
                 }else{
                    $.messager.alert('提示', '请先选择角色再进行权限分配', 'info');
                    // 清空数据
                    $('#trCdqx').tree({
                                    data: [],
                                    loadFilter:function(data,parent){
                                        if(data){
                                            return data
                                        }
                                    }
                                    });
                    // 清空按钮权限数据
                    $('#dgCdGngl').datagrid('reload', {});
                    return false
                 }
             }
        }
    });

    treeCdqx = $('#trCdqx').tree({
        onClick: function(node){
            //选择的结束
            var js =$('#dgJs').datagrid('getSelected');
            //选择的菜单
            var rows =$('#dgCdgl').datagrid('getSelections');
            var mark = false;
            if(js){
                //判断是否拥有的菜单，用于功能列表的加载
                $(rows).each(function(index, item){
                    if(node.id == item["id"]){
                        gnlb_get(node.id);
                        mark = true;
                    }
                });
                if (mark==false){
                    $.messager.alert('提示', '当前角色不具备所选菜单权限', 'info');
                    //清空数据
                    $('#dgCdGngl').datagrid('reload', {});
                    return false
                }
            }else{
                $.messager.alert('提示', '请先选择角色再进行权限分配', 'info');
                //清空数据
                $('#dgCdGngl').datagrid('reload', {});
                return false
            }
        }
    });

  // 功能列表初始化加载
    dataGrid =$('#dgCdGngl').datagrid({
        method: "post",
        nowrap : false,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/gnlb_view",
        idField:'id',
        columns: [
            [
                {field: 'id',  width: 40, checkbox:'true' },
                {field: 'gndm', title: '功能代码', width: 100},
                {field: 'gnmc', title: '功能名称', width: 80},
                {field: 'bz', title: '备注', width: 100}
            ]
        ],
        onBeforeLoad : function(param){
                //清空选择
		    	$(this).datagrid('clearSelections').datagrid('unselectAll');
		    },
        onLoadSuccess: function(data) {
            //页脚设置，显示刷新按钮和总数
            var pagination = $('#dgCdGngl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
            //循环判断是否是当前角色已经拥有的权限
            for(var j = 0; j < data.rows.length; j++ ){
               if( data.rows[j].checked == true)
                 $('#dgCdGngl').datagrid('selectRow', j);
            }
           // 如果都已选中，全选复选框置为勾选状态
           if ($('.datagrid-cell-check input:enabled').length == $('#dgCdGngl').datagrid('getChecked').length && $('#dgCdGngl').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
           }
        }
    });

    // 绑定菜单一览窗口保存按钮的事件
    $('#lbtnJsqxSubmit').click(function(e){
        e.preventDefault();
        //获取选择的角色
        var jsData = $("#dgJs").datagrid('getSelected')
        if(jsData){
            //获取选择的tab页
            var tab = $('#tabsCdView').tabs('getSelected');
            var index = $('#tabsCdView').tabs('getTabIndex',tab);
            if (index == 0){
               // 模块权限tab页
               var rows = $("#dgCdgl").treegrid('getSelections');
               // 保存菜单权限
               url = "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/add_cdqx_view";
               // 提交后台操作
               add_qx(url,rows,jsData.id)
            }else if(index == 1){
                // 获取菜单
                var cdrow= $('#trCdqx').tree('getSelected');
                if(cdrow == "" || cdrow == null){
                    $.messager.alert('提示', '请先选择菜单权限再进行按钮权限分配', 'info');
                    return false
                }
                //功能权限
                var rows = $('#dgCdGngl').datagrid('getSelections')
                //保存功能权限
                url = "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/add_cdgn_view";
                // 提交后台操作
                add_qx(url,rows,jsData.id,cdrow.id)
            }
        }else{
            $.messager.alert('提示', '请先选择角色再进行权限分配', 'info');
            return false
        }
    });
});

/*
* 点击角色重复的事件：加载菜单数据并勾选已经拥有的菜单权限
* rows：角色信息
* */
function cdlb_get(rows){
    // 重新加载菜单权限
    $('#dgCdgl').treegrid('reload', {
        jsid: rows.id
    });
}

 /**
   * tree行单击事件.
   * @param row 行数据
   */
 function gnlb_get() {
    // 获取菜单
    var row= $('#trCdqx').tree('getSelected');
    // 获取用户数据
    var js =$('#dgJs').datagrid('getSelected')
     // 清空数据
  	$('#dgCdGngl').datagrid('reload', {});
    // 加载画面数据
  	$('#dgCdGngl').datagrid('reload', { jsid: js.id, 'cdid' : row.id});
 }

/*
* 增加权限给用户
* url:后台url
* rows:选择的权限列表
* jsid:角色id
* cdid: 菜单id
* */
function add_qx(url,rows,jsid,cdid){
    //选择的列表
    var ids = new Array();
    $(rows).each(function(index, item){
        ids.push(item["id"]);
    });
    //根据菜单ID的有无组织传给后台的数据
    if(cdid){
        var dataR = {'ids': ids.join(','), 'jsid':jsid, 'cdid':cdid}
    }else{
        var dataR = {'ids': ids.join(','), 'jsid':jsid}
    }
    //if (rows.length) {
        $.messager.confirm('提示', '您确定分配所选的权限么？', function(r) {
        if (r) {
             // 添加遮罩
            ajaxLoading();
            //发送请求
            $.ajax({
                type: 'POST',
                dataType: 'text',
                url: url,
                data: dataR,
                success: function(data){
                    //转json串
                    data = $.parseJSON(data)
                    // 提示
                    afterAjax(data, "", "");
                    // 取消遮罩
                    ajaxLoadEnd();
                },
                error : function(data){
                    data = $.parseJSON(data)
                    // 提示
                    afterAjax(data, "", "");
                    // 取消遮罩
                    ajaxLoadEnd();
                }
            });
        }
        })
    //} else {
    //    $.messager.alert('提示', '至少选择一项', 'info');
    //}
}

//递归树结构-选中已经拥有的权限
function getId(rowData){
    for (var menu in rowData){
        if (rowData[menu].children) {
            if(rowData[menu].checked){
                //勾选已经拥有的权限
                $('#dgCdgl').treegrid('selectRow', rowData[menu].id);
            }
            //递归
            getId(rowData[menu].children);
        }
         else {
             if(rowData[menu].checked){
              //   勾选已经拥有的权限
              $('#dgCdgl').treegrid('selectRow', rowData[menu].id);
            }
        }
    }
}

