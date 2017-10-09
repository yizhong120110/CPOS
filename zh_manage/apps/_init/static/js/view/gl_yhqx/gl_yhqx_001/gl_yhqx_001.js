/**
 * 页面初始化加载
*/
$(document).ready(function() {
    //按钮列表-非toolbar
    //buttonlst=['lbtnYhqxSubmit'];
    ////设置按钮显示与隐藏
    //get_anqxLst_gn('yhqxgl',buttonlst,'','1');

    // 部门树加载
    treeBm = $('#trBm').tree({
        method: "post",
        //checkbox:'true',
        url: "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/bmlst_view",
        loadFilter: function(data,parent){
            if(data){
                return data['rows']
            }
        },
        onSelect: function(node){
            //默认选中第一个tab页-菜单权限tab页
            $("#tabsCdView").tabs( "select" , 0 );
            //取消原勾选的菜单权限
            $('#dgCdgl').treegrid('clearSelections').datagrid('unselectAll');
            //加载用户列表
            yh_load();
        },
        formatter: function(node) {
            //格式化用户数，标注为蓝色
            var s = node.text;
            s += '<span style=\'color:blue\'>(' + node.persons + ')</span>';
            return s;
        }
    });

    // 用户列表初始化加载
    dataGrid_yh =$('#dgYh').datagrid({
        method: "post",
        nowrap : false,
        singleSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/yhlst_view",
        idField:'id',
        columns: [
            [
                {field: 'id',  title: '用户ID',width: 40, checkbox:'true' },
                {field: 'xm', title: '用户列表', width: 100}
            ]
        ],
        toolbar:[],
        onBeforeLoad : function(param){
                //清空选择
		    	$(this).datagrid('clearSelections').datagrid('unselectAll');
		    },
        onSelect: function(rowIndex,rowData){
            //默认选中第一个tab页
            $("#tabsCdView").tabs( "select" , 0 );
            //触发点击事件，加载菜单
            cdlb_get(rowData);
        },
        onLoadSuccess: function(data) {
            //页脚处理，显示数据总数和刷新按钮
            var pagination = $('#dgYh').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
        }
    });

    // 搜索框设置
    var fields =  $('#dgYh').datagrid('getColumnFields');
    var muit="";
    for(var i=0; i<fields.length; i++){
        var opts = $('#dgYh').datagrid('getColumnOption', fields[i]);
        if( fields[i] != 'id' ){
            muit += "<div data-options=\"name:'"+  fields[i] +"'\">"+ opts.title +"</div>";
        }
    };

    $('#divSearch').html($('#divSearch').html()+muit);
    $('#search_box').searchbox({
        menu:'#divSearch'
    });
    //隐藏查询条件名称
    $('#dgYhylForm').find('.l-btn-text').hide();

    $("#dgYhylForm").find(".validatebox-text").width( parseInt($("#dgYhylForm").find(".validatebox-text")[0].style.marginLeft.split("p")[0])+$("#dgYhylForm").find(".validatebox-text").width() );

    $("#dgYhylForm").find(".validatebox-text")[0].style.marginLeft = "0px";








    // 渲染表格，菜单数列表页面初始化信息加载
    treeGrid = $('#dgCdgl').treegrid({
        method: "post",
        singleSelect: false,
        selectOnCheck: true,
        checkOnSelect: true,
        rownumbers: true,
        fitColumns: true,
        pagination:true,
        url: "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/data_view",
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
		    	$(this).treegrid('clearSelections').treegrid('unselectAll');
		    },
        onClickRow:function(row){
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
        onLoadSuccess: function(row,data) {
            //显示记录数以及刷新按钮
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
            //获取用户
            var yhData = $('#dgYh').datagrid('getSelections');
            //选择的菜单ID
            var cdids = new Array();
             $(rows).each(function(index, item){
                cdids.push(item["id"]);
             });
             if(index == 1){
                  // 清空数据
                 $('#dgCdGngl').datagrid('reload', {});
                 if(yhData.length>0){
                    // 加载画面数据
                     url = "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/cdlst_view"
                     dataR = {'cdid':cdids.join(','), 'yhid':yhData[0].id
                     }
                    //发送请求
                    $.ajax({
                        type: 'POST',
                        dataType: 'text',
                        url: url,
                        data: dataR,
                        success: function(data){
                            dataRr = $.parseJSON(data);
                            //菜单树数据加载
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
                            $.messager.alert('提示','菜单树数据加载异常', 'info');
                        }
                    });
                 }else{
                    $.messager.alert('提示', '请先选择用户再进行权限分配', 'info');
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
            //获取选中的用户
            var yh =$('#dgYh').datagrid('getSelected');
            //获取选中的菜单
            var rows =$('#dgCdgl').datagrid('getSelections');
            var mark = false;
            if(yh){
                //判断是否拥有的菜单权限
                $(rows).each(function(index, item){
                    if(node.id == item["id"]){
                        gnlb_get(node.id);
                        mark = true;
                    }
                });
                if (mark==false){
                    $.messager.alert('提示', '当前用户不具备所选菜单权限', 'info');
                    //清空数据
                    $('#dgCdGngl').datagrid('reload', {});
                    return false
                }
            }else{
                $.messager.alert('提示', '请先选择用户再进行权限分配', 'info');
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
        url: "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/gnlb_view",
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
            //处理页脚，展示数据总数和刷新按钮
            var pagination = $('#dgCdGngl').parent().next();
            var pi = pagination.find('.pagination-info');
            if (pagination.find('table td').length == 13) {
                pagination.find('table td:lt(12)').hide();
            }
            pi.text(pi.text().split(',')[1]);
            //循环判断是否是当前用户已经拥有的权限
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
    $('#lbtnYhqxSubmit').click(function(e){
        e.preventDefault();
        // 出错提示
        var msg = "保存失败，请稍后再试";
        var yhData = $("#dgYh").datagrid('getSelected')
        if(yhData){
            var tab = $('#tabsCdView').tabs('getSelected');
            var index = $('#tabsCdView').tabs('getTabIndex',tab);
            if (index == 0){
               var rows = $("#dgCdgl").treegrid('getSelections');
               // 保存菜单权限
               url = "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/add_cdqx_view";
               // 提交后台操作
               add_qx(url,rows,yhData.id)
            }else if(index == 1){
                // 获取菜单
                var cdrow= $('#trCdqx').tree('getSelected');
                if(cdrow == "" || cdrow == null){
                    $.messager.alert('提示', '请先选择菜单权限再进行按钮权限分配', 'info');
                    return false
                }
                //获取所有的功能权限选择数据
                var rows = $('#dgCdGngl').datagrid('getSelections')
                //保存功能权限
                url = "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/add_cdgn_view";
                // 提交后台操作
                add_qx(url,rows,yhData.id,cdrow.id)
            }
        }else{
            $.messager.alert('提示', '请先选择用户再进行权限分配', 'info');
            return false
        }
    });
});

/*
* 加载部门下的用户
* node : 部门信息
* */
function yh_load(){

    var rows= $('#trBm').tree('getSelected');
    $('#dgYh').datagrid('reload', {});
    // 加载画面数据
    $('#dgYh').datagrid('reload', {'bmid' : rows.id});
}

function cdlb_get(rows){
    // 重新加载菜单权限
    $('#dgCdgl').treegrid('reload', {
        yhid: rows.id
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
    var yh =$('#dgYh').datagrid('getSelected')
     // 清空数据
  	$('#dgCdGngl').datagrid('reload', {});
    // 加载画面数据
  	$('#dgCdGngl').datagrid('reload', { yhid: yh.id, 'cdid' : row.id});
 }

/*
* 增加权限给用户
* url:后台url
* rows:选择的权限列表
* yhid:用户id
* cdid: 菜单id
* */
function add_qx(url,rows,yhid,cdid){
    var ids = new Array();
    //列表选择的数据
    $(rows).each(function(index, item){
        ids.push(item["id"]);
    });
    //根据菜单ID的有误组织传给后台的数据，用于区分菜单权限和功能权限操作
    if(cdid){
        var dataR = {'ids': ids.join(','), 'yhid':yhid, 'cdid':cdid}
    }else{
        var dataR = {'ids': ids.join(','), 'yhid':yhid}
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
                    // 取消遮罩
                    ajaxLoadEnd();
                    //返回数据转为json串
                    afterAjax(data, "", "");
                },
                error : function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    $.messager.alert('错误', '分配权限失败', 'error');
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
            //递归循环
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


// 执行搜索
function doSearch(value,name){
    var rows= $('#trBm').tree('getSelected');
    if(rows != null){
        bmid=rows.id
    }else{
        bmid='-9999999999999999'
    }
    //重新定义url
    var tj_str = 'search_name=' + name + '&search_value=' + value;
    //$('#dgYh').datagrid( {url:'/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/yhlst_view?' + tj_str });
    $('#dgYh').datagrid('reload', {
        search_name: name,
        search_value: value,
        'bmid' : bmid
    });
    // 清空数据
  	$('#dgCdgl').treegrid('reload', {});
    $('#trCdqx').tree('reload');
    // 清空数据
  	$('#dgCdGngl').datagrid('reload', {});
}