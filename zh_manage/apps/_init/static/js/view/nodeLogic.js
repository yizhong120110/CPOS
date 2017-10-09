$(document).ready(function() {

    var editor = CodeMirror.fromTextArea(document.getElementById("nodeBox"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true
    });
    
    //初始化节点名称
    var xz_id = getUrlParam('dqxzjd');
    var nodeStyle = getUrlParam('nodeStyle');   //节点类型
    
    if (getUrlParam('hide_save_btn')=='true') {
        $('#savelbt').hide();
        $('#cancel_btn').show();
    }
    
    
    if( nodeStyle == undefined )
        nodeStyle = 'enabled'
    var nodeName = decodeURI(decodeURI(getUrlParam('nodeName')));
    $("#nodeName").textbox('setValue', nodeName);
    $("#nodeStyle").combobox("select",nodeStyle);
    
    $('#savelbt').click(function(){
        //初始化节点名称
        var xz_obj = parent.$('#' + xz_id);
        var lines = '';
        if( xz_obj.val() != 'txgl' )
            lines = parent.window.getLineByNode( xz_obj );
        if ( lines && lines.length ) {
            for( var i=0; i < 1; i++ ){
                line = parent.window.setLineColor( lines[i], 'red' );
            }
//            $.messager.alert('提示', '未定义下列输入：<br/>项目代码1', 'info');
//            setTimeout (function () {
//                parent.window.resetLineColor( line );
//            }, 2000);
        }
        $.messager.alert('提示', '保存成功', 'info');
//        parent.$("#codeEdit").window('close');
    });
    
    $('#datagrid_srys').datagrid({
        nowrap : false,
        fit : false,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: false,
        fitColumns : false,
        method: "get",
        remoteSort: false,
        onClickRow: onClickRow,
        frozenColumns: [[
            { field: 'select_box', checkbox: true, width: '2%', formatter: function(value,rowData,rowIndex) {
                return 'aa';
            } }
        ]],
        columns: [[
            { field: 'srys', title: '输入要素', width: '20%', editor:{
                type:'text'
            } },
            { field: 'bzxx', title: '备注', width: '30%', editor:{
                type:'text'
            } },
            { field: 'lb', title: '类别', width: '15%', editor:{
                type:'text'
            } },
            { field: 'origin', title: '来源', width: '10%' }
        ]],
        toolbar : "#tb"
    });
    
    $('#datagrid_scys').datagrid({
        nowrap : false,
        fit : false,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: false,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        onClickRow: onClickRow_sc,
        frozenColumns: [[
            { field: 'select_box', checkbox: true }
        ]],
        columns: [[
            { field: 'scys', title: '输出要素', width: '20%', editor:{
                type:'text'
            } },
            { field: 'bzxx', title: '备注', width: '30%', editor:{
                type:'text'
            } },
            { field: 'lb', title: '类别', width: '15%', editor:{
                type:'text'
            } },
            { field: 'origin', title: '来源', width: '10%' }
        ]],
        toolbar : "#tb_sc"
    });
    
    $("#add_btn").click(function(){
        append();
    });
    $("#delete_btn").click(function(){
        removechecked('datagrid_srys');
    });
    $("#add_sc_btn").click(function(){
        append_sc();
    });
    $("#delete_sc_btn").click(function(){
        removechecked('datagrid_scys');
    });
    
    $('#datagrid_dycs').datagrid({
        nowrap : false,
        fit : false,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        columns: [[
            { field: 'jymc', title: '交易名称', width: 50, editor:{
                type:'text'
            } },
            { field: 'cs', title: '引用次数', width: 50, editor:{
                type:'text'
            } }
        ]]
    });
    
    var editIndex = undefined;
    function endEditing(){
        if (editIndex == undefined){return true}
        if ($('#datagrid_srys').datagrid('validateRow', editIndex)){
            $('#datagrid_srys').datagrid('endEdit', editIndex);
            editIndex = undefined;
            return true;
        } else {
            return false;
        }
    }
    function onClickRow(index){
        if (editIndex != index){
            if (endEditing()){
                $('#datagrid_srys').datagrid('selectRow', index)
                        .datagrid('beginEdit', index);
                editIndex = index;
            } else {
                $('#datagrid_srys').datagrid('selectRow', editIndex);
            }
        }
    }
    function append(){
        if (endEditing()){
            $('#datagrid_srys').datagrid('appendRow',{status:'P'});
            editIndex = $('#datagrid_srys').datagrid('getRows').length-1;
            $('#datagrid_srys').datagrid('updateRow', {
                index: editIndex,
                row: {
                    origin: '手工添加'
                }
            });
            $('#datagrid_srys').datagrid('selectRow', editIndex)
                    .datagrid('beginEdit', editIndex);
        }
    }
    function removeit(){
        if (editIndex == undefined){return}
        $('#datagrid_srys').datagrid('cancelEdit', editIndex)
                .datagrid('deleteRow', editIndex);
        editIndex = undefined;
        //删除后导致删除行后的index不正确，所以需要重新加载
        var rows = $('#datagrid_srys').datagrid("getRows");
        if (rows.length > 0) {
            $('#datagrid_srys').datagrid("loadData", rows);
        }
    }
    function accept(){
        if (endEditing()){
            $('#datagrid_srys').datagrid('acceptChanges');
        }
    }
    
    /**
    *批量删除
    */
    function removechecked(id){
        var checkedItems = $('#'+id).datagrid('getChecked');
        $($(checkedItems).get().reverse()).each(function(index, item){
            $('#'+id).datagrid('deleteRow', $('#'+id).datagrid('getRowIndex', item));
        });
        //删除后导致删除行后的index不正确，所以需要重新加载
        var rows = $('#'+id).datagrid("getRows");
        if (rows.length > 0) {
            $('#'+id).datagrid("loadData", rows);
        }
    }
    
    
    var editIndex_sc = undefined;
    function endEditing_sc(){
        if (editIndex_sc == undefined){return true}
        if ($('#datagrid_scys').datagrid('validateRow', editIndex_sc)){
            $('#datagrid_scys').datagrid('endEdit', editIndex_sc);
            editIndex_sc = undefined;
            return true;
        } else {
            return false;
        }
    }
    function onClickRow_sc(index){
        if (editIndex_sc != index){
            if (endEditing_sc()){
                $('#datagrid_scys').datagrid('selectRow', index)
                        .datagrid('beginEdit', index);
                editIndex_sc = index;
            } else {
                $('#datagrid_scys').datagrid('selectRow', editIndex_sc);
            }
        }
    }
    function append_sc(){
        if (endEditing_sc()){
            $('#datagrid_scys').datagrid('appendRow',{status:'P'});
            editIndex_sc = $('#datagrid_scys').datagrid('getRows').length-1;
            editIndex = $('#datagrid_scys').datagrid('getRows').length-1;
            $('#datagrid_scys').datagrid('updateRow', {
                index: editIndex,
                row: {
                    origin: '手工添加'
                }
            });
            $('#datagrid_scys').datagrid('selectRow', editIndex_sc)
                    .datagrid('beginEdit', editIndex_sc);
        }
    }
    function removeit_sc(){
        if (editIndex_sc == undefined){return}
        $('#datagrid_scys').datagrid('cancelEdit', editIndex_sc)
                .datagrid('deleteRow', editIndex_sc);
        editIndex_sc = undefined;
        //删除后导致删除行后的index不正确，所以需要重新加载
        var rows = $('#datagrid_scys').datagrid("getRows");
        if (rows.length > 0) {
            $('#datagrid_scys').datagrid("loadData", rows);
        }
    }
    function accept_sc(){
        if (endEditing_sc()){
            $('#datagrid_scys').datagrid('acceptChanges');
        }
    }
    
    // 获取url中的参数
    function getUrlParam(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
        var r = window.location.search.substr(1).match(reg);  //匹配目标参数
        if (r != null) return unescape(r[2]); return null; //返回参数值
    }
    
    $("#cancel_btn").click(function(){
        parent.$("#codeEdit").window('close');
    });
    
    $('#datagrid_fhz').datagrid({
        nowrap : false,
        fit : false,
        border: false,
        height: '300px',
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        remoteSort: false,
        columns: [[
            { field: 'fhz', title: '返回值', width: 50, editor:{
                type:'text'
            } },
            { field: 'bz', title: '备注', width: 50, editor:{
                type:'text'
            } }
        ]]
    });
    
    
});
