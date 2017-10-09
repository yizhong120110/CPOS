/**
 * 页面初始化加载
*/

var codeKzjyfsmkdm = null;
var codeLsdrmkdm = null;
$(document).ready(function() {
    
    // 页面初始化
    updataPageInit();
    
    //页面显示时，根据ID这个标签的值来判断是增加的方法还是编辑的方法
    var csid = $("#hidCsid").val();
    if (csid != "add"){
        // 初始化页面元素
        ajax_bjsj("/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/cx_ywpz_view", csid)
    }
    
    $('#tabsAddEdit').tabs({
        border:false,
        onSelect:function(title,index){
            // 当下标为1时为扩展模块，为2时是流水导入
            if(index == 1){
                var gtpm_kzjyfs = $.trim($("#combKzjyfs").textbox('getValue'));
                if(gtpm_kzjyfs == "MOD"){
                    $("#kzjyfs-sql-area").hide();
                    $("#kzjyfs-code-area").show();
                    $("#kzjyfs_label").show().find(".sql").hide().end().find(".mk").hide();
                    codeKzjyfsmkdm.refresh();
                }
            }else if( index == 2 ){
                var gtpm_lsdrfs = $.trim($("#combLsdrfs").textbox('getValue'));
                if(gtpm_lsdrfs == "MOD"){
                    $("#lsdrfs-sql-area").hide();
                    $("#lsdrfs-code-area").show();
                    $("#lsdrfs_label").show().find(".sql2").show().end().find(".mk2").hide();
                    codeLsdrmkdm.refresh();
                }
            }
        }
    });

    // 最大值限制
    $("#txtGtpmWjlx").next().children().attr("maxlength","20");
    
    // 按钮【保存】的click事件监听
    $("#ywGtpmYwpzSubmit").click(function(e){
        e.preventDefault();
        // 调用保存的方法
        add_submit();
    });
    // 按钮【取消】的click事件监听
    $("#ywGtpmYwpzCancel").click(function(e){
        e.preventDefault();
        // 关闭父窗口
        parent.$('#divYwGtpm002').window('close');
    });
    
    // 页面 form tab排序
    $("#forXinxi").tabSort();
});
/**
 * 初始化编辑窗口数据
 * @param d.id
 * 从后台获取编辑数据
 * 包括
 * 扣款明细金额sql，扣款明细查询sql，扩展校验方式，扩展校验sql或mod，
 * 流水导入方式，流水导入sql或mod，异常全部撤销，异常全部通过，异常单笔状态更新
 *
 **/
function ajax_bjsj(url,id){
    // ajax请求
    $.ajax({
        url:url,
        type : 'post',
        dataType : 'json',
        data : {'ywpz_id' : id},
        success:function(data){
            // 业务名称
            $("#combAddSsyw").textbox('setValue', data.ywmc);
            // 业务名称不可编辑
            $('#combAddSsyw').textbox('disable');
            // 文件类型
            $("#txtGtpmWjlx").textbox('setValue', data.wjlx);
            // 扣款明细金额sql
            $("#txtHqkkmxjesql").textbox('setValue',data.kkmxsqlid);
            // 扣款明细查询sql
            $("#txtKkmxsjcxsql").textbox('setValue',data.kkmxcxsqlid);
            
            // 扩展校验方式
            $("#combKzjyfs").combobox('setValue',data.kzjyfs);
            if (data.kzjyfs == null){
                $("#combKzjyfs").combobox('setValue',"请选择");
                $("#kzjyfs-sql-area").hide();
                $("#kzjyfs-code-area").hide();
                $("#kzjyfs_label").hide();
            }
            if (data.kzjyfs == 'SQL'){
                $("#txtKzjysql").textbox('setValue',data.kzjyid);
                $("#kzjyfs-sql-area").show();
                $("#kzjyfs-code-area").hide();
                $("#kzjyfs_label").show().find(".sql2").show().end().find(".mk2").hide();
            }
            if (data.kzjyfs == 'MOD') {
                $("#kzjyfs-sql-area").hide();
                $("#kzjyfs-code-area").show();
                codeKzjyfsmkdm.setValue("");
                codeKzjyfsmkdm.refresh();
                codeKzjyfsmkdm.options.readOnly = false;
                codeKzjyfsmkdm.setValue(data.kzjyid);
                $("#kzjyfs_label").show().find(".sql2").hide().end().find(".mk2").show();
            }
            
            // 流水导入方式
            $("#combLsdrfs").combobox('setValue',data.lsdrfs);
            if (data.lsdrfs == 'SQL'){
                $("#txtLsdrfssql").textbox('setValue',data.lsdrid);
                $("#lsdrfs-sql-area").show();
                $("#lsdrfs-code-area").hide();
                $("#lsdrfs_label").show().find(".sql2").show().end().find(".mk2").hide();
            }
            if (data.lsdrfs == 'MOD') {
                $("#lsdrfs-sql-area").hide();
                $("#lsdrfs-code-area").show();
                codeLsdrmkdm.setValue("");
                codeLsdrmkdm.refresh();
                codeLsdrmkdm.options.readOnly = false;
                codeLsdrmkdm.setValue(data.lsdrid);
                $("#lsdrfs_label").show().find(".sql2").hide().end().find(".mk2").show();
            }
            
            // 异常全部撤销
            $("#txtYcqbcxsql").textbox('setValue', data.YC_ALLCANCEL_SQLID);
            // 异常单笔状态更新
            $("#txtYcdbztgxsql").textbox('setValue', data.YC_SINGLE_SQLID);
            // 异常全部通过
            $("#txtYcqbtgsql").textbox('setValue', data.YC_ALLPASS_SQLID);
            // 原消息列表
            $("#yxxlb").val(data.yxxlb);
            $("#txtGtpmWjlx").next().children().focus();
        },
        error : function(){
            errorAjax();
        }
    });
}

// 新增事件和编辑事件调用的方法
function add_submit(){
    // 添加遮罩
    ajaxLoading();
    // 出错提示
    var msg = "新增失败，请稍后再试";
    if ($("#hidCsid").val()=="add") {
        // 新增
        url = "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/add_ywpz_view";
    } else {
        // 修改
        url = "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/edit_ywpz_view";
        msg = "修改失败，请稍后再试";
    }
    // 提交表单
    $('#dgYwGtpm002Add').find('form').form('submit', {
        url: url ,
        type:'post',
        onSubmit: function(){
            var ret = validate();
            // 反馈校验结果
            if( ret == false ){
                // 取消遮罩
                ajaxLoadEnd();
            }
            return ret;
        },
        success: function(data){
            // 取消遮罩
            ajaxLoadEnd();
            if (typeof data == 'string') {
                data = $.parseJSON(data);
            }
            if (data.state == true) {
                $.messager.alert('提示', data.msg.replace("\n", "<br/>"), 'info',function() {
                    //添加成功后刷新grid
                    parent.$('#dgYwGtpm002').datagrid('load');
                    //关闭window
                    parent.$('#divYwGtpm002').window('close');
                });
            }else{
                // 提示错误信息
                afterAjax(data, "", "");
                // 根据提示消息确定前台错误代码区域并选中
                if( data.msg_show == "kzjy" ) {
                    $('#tabsAddEdit').tabs('select',1);
                    $("#txtKzjysql").next().children().focus();
                } else if( data.msg_show == "lsdr" ) {
                    $('#tabsAddEdit').tabs('select',2);
                    $("#txtLsdrmkdm").next().children().focus();
                }
                
            }
        },
        error: function () {
            // 取消遮罩
            ajaxLoadEnd();
            // 执行请求失败后的方法
            errorAjax();
        }
    });
}

// 输入框校验
function validate(){
    // 业务名称
    var gtpm_ywmc = $.trim($("#combAddSsyw").combobox('getValue'));
    // 文件类型
    var gtpm_wjlx = $.trim($("#txtGtpmWjlx").textbox('getValue'));
    // 获取扣款明细金额SQL
    var gtpm_hqkkmmjesql = $.trim($("#txtHqkkmxjesql").textbox('getValue'));
    // 扣款明细数据查询SQL
    var gtpm_kkmxsjcxsql = $.trim($("#txtKkmxsjcxsql").textbox('getValue'));
    // 业务名称
    if (gtpm_ywmc=="" || gtpm_ywmc==null || gtpm_ywmc=="请选择" || gtpm_ywmc=="0") {
        $.messager.alert('错误','业务名称不可为空，请选择','error', function(){
            $("#combAddSsyw").next().children().focus();
        });
        return false;
    }
    // 文件类型
    if (gtpm_wjlx=="" || gtpm_wjlx==null) {
        $.messager.alert('错误','文件类型不可为空，请输入','error', function(){
            $("#txtGtpmWjlx").next().children().focus();
        });
        return false;
    }
    if(!checkBm2(gtpm_wjlx, '文件类型', 'txtGtpmWjlx')) {
        return false;
    }
    // 获取扣款明细金额SQL
    if (gtpm_hqkkmmjesql=="" || gtpm_hqkkmmjesql==null) {
        $.messager.alert('错误','获取扣款明细金额SQL不可为空，请输入','error', function(){
            $('#tabsAddEdit').tabs('select',0);
            $("#txtHqkkmxjesql").next().children().focus();
        });
        return false;
    }

    // 扣款明细数据查询SQL
    if (gtpm_kkmxsjcxsql=="" || gtpm_kkmxsjcxsql==null) {
        $.messager.alert('错误','扣款明细数据查询SQL不可为空，请输入','error', function(){
            $('#tabsAddEdit').tabs('select',0);
            $("#txtKkmxsjcxsql").next().children().focus();
        });
        return false;
    }
    
    // 扩展校验方式为SQL
    var gtpm_kzjyfs = $.trim($("#combKzjyfs").combobox('getValue'));
    if (gtpm_kzjyfs=="SQL"  ) {
        // 扩展校验SQL
        var gtpm_kzjysql = $.trim($("#txtKzjysql").textbox('getValue'));
        if(gtpm_kzjysql=="" || gtpm_kzjysql==null) {
            $.messager.alert('错误', '扩展校验方式为SQL，扩展校验SQL不可为空，请录入', 'error', function () {
                $('#tabsAddEdit').tabs('select',1);
                $("#txtKzjysql").next().children().focus();
            });
            return false;
        }
    }
    
   // 扩展校验方式为模块代码
    if ( gtpm_kzjyfs=="MOD" ) {
        // 扩展校验模块代码
        var gtpm_kzjymkdm = $.trim(codeKzjyfsmkdm.getValue());
        if(gtpm_kzjymkdm=="" || gtpm_kzjymkdm==null) {
            $.messager.alert('错误', '扩展校验方式为模块代码，扩展校验模块代码不可为空，请录入', 'error', function () {
                $('#tabsAddEdit').tabs('select',1);
                $("#txtKzjyfsmkdm").next().children().focus();
            });
            return false;
        }
    }
    
    // 导入流水方式不可为空
    var gtpm_lsdrfs = $.trim($("#combLsdrfs").combobox('getValue'));
    if (gtpm_lsdrfs=="" || gtpm_lsdrfs==null || gtpm_lsdrfs=="请选择") {
        $.messager.alert('错误','流水导入方式不可为空，请选择','error', function(){
            $('#tabsAddEdit').tabs('select',2);
            $("#combLsdrfs").next().children().focus();
        });
        return false;
    }
    
   // 导入流水方式为SQL
    if (gtpm_lsdrfs=="SQL") {
        // 流水导入SQL
        var gtpm_lsdrsql = $.trim($("#txtLsdrfssql").textbox('getValue'));
        if(gtpm_lsdrsql=="" || gtpm_lsdrsql==null) {
            $.messager.alert('错误', '流水导入方式为SQL，流水导入SQL不可为空，请录入', 'error', function () {
                $('#tabsAddEdit').tabs('select',2);
                $("#txtLsdrfssql").next().children().focus();
            });
            return false;
        }
    }
    
    // 流水导入方式为模块代码
    if ( gtpm_lsdrfs=="MOD" ) {
        // 流水导入模块代码
        var gtpm_lsdrmkdm = $.trim(codeLsdrmkdm.getValue());
        if(gtpm_lsdrmkdm=="" || gtpm_lsdrmkdm==null) {
            $.messager.alert('错误', '流水导入方式为模块代码，流水导入模块代码不可为空，请录入', 'error', function () {
                $('#tabsAddEdit').tabs('select',2);
                $("#txtLsdrmkdm").next().children().focus();
            });
            return false;
        }
    }
    
    // 异常全部撤销SQL
    var gtpm_ycqbcxsql = $.trim($("#txtYcqbcxsql").textbox('getValue'));
    if (gtpm_ycqbcxsql=="" || gtpm_ycqbcxsql==null) {
        $.messager.alert('错误',' 异常全部撤销SQL不可为空，请输入','error', function(){
            $('#tabsAddEdit').tabs('select',3);
            $("#txtYcqbcxsql").next().children().focus();
        });
        return false;
    }
    
    // 异常单笔状态更新SQL
    var gtpm_ycdbztgxsql = $.trim($("#txtYcdbztgxsql").textbox('getValue'));
    if (gtpm_ycdbztgxsql=="" || gtpm_ycdbztgxsql==null) {
        $.messager.alert('错误','异常单笔状态更新SQL不可为空，请输入','error', function(){
            $('#tabsAddEdit').tabs('select',3);
            $("#txtYcdbztgxsql").next().children().focus();
        });
        return false;
    }
    
    // 异常全部通过SQL
    var gtpm_ycqbtgsql = $.trim($("#txtYcqbtgsql").textbox('getValue'));
    if (gtpm_ycqbtgsql=="" || gtpm_ycqbtgsql==null) {
        $.messager.alert('错误','异常全部通过SQL不可为空，请输入','error', function(){
            $('#tabsAddEdit').tabs('select',3);
            $("#txtYcqbtgsql").next().children().focus();
        });
        return false;
    }
    // 当扩展模块为请选择时，清空当前文本
    if( gtpm_kzjyfs == "请选择" ){
        $("#combKzjyfs").combobox('setValue','')
    }
    return true;
}

/**
 * 页面元素初始化
 */
function updataPageInit(){
    codeKzjyfsmkdm = CodeMirror.fromTextArea(document.getElementById("txtKzjyfsmkdm"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent: true,
        matchBrackets: true,
        autofocus: false
    });
    //将tab换为4个空格
    codeKzjyfsmkdm.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    window.codeKzjyfsmkdm = codeKzjyfsmkdm;

    codeLsdrmkdm = CodeMirror.fromTextArea(document.getElementById("txtLsdrmkdm"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent: true,
        matchBrackets: true,
        autofocus: false
    });
    //将tab换为4个空格
    codeLsdrmkdm.setOption("extraKeys", {
        Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
        }
    });
    window.codeLsdrmkdm = codeLsdrmkdm;
    
    //新增编辑框中扩展业务模式Tab页下拉框选择触发事件
    $('#combKzjyfs').combobox({
        onBeforeLoad: function(){
            $("#kzjyfs-sql-area").hide();
            $("#kzjyfs-code-area").hide();
            $("#kzjyfs_label").hide();
        },
        onSelect: function(record){
            $("#kzjyfs-sql-area").hide();
            $("#kzjyfs-code-area").hide();
            $("#kzjyfs_label").hide();
            if (record.value == "SQL") {
                $("#kzjyfs-sql-area").show();
                $("#kzjyfs-code-area").hide();
                $("#kzjyfs_label").show().find(".sql").show().end().find(".mk").hide();
            } else if (record.value == "MOD") {
                $("#kzjyfs-sql-area").hide();
                $("#kzjyfs-code-area").show();
                $("#kzjyfs_label").show().find(".sql").hide().end().find(".mk").hide();
                $("#txtKzjyfsmkdm").next().children().focus();
                codeKzjyfsmkdm.refresh();
            }
        }
    });
    //新增编辑框中流水导入方式Tab页下拉框选择触发事件
    $('#combLsdrfs').combobox({
        onBeforeLoad: function(){
            $("#lsdrfs-sql-area").hide();
            $("#lsdrfs-code-area").hide();
            $("#lsdrfs_label").hide();
        },
        onSelect: function(record){
            $("#kzjyfs-sql-area").hide();
            $("#kzjyfs-code-area").hide();
            $("#kzjyfs_label").hide();
            if (record.value == "SQL") {
                $("#lsdrfs-sql-area").show();
                $("#lsdrfs-code-area").hide();
                $("#lsdrfs_label").show().find(".sql2").show().end().find(".mk2").hide();
            } else if (record.value == "MOD") {
                $("#lsdrfs-sql-area").hide();
                $("#lsdrfs-code-area").show();
                $("#lsdrfs_label").show().find(".sql2").show().end().find(".mk2").hide();
                $("#txtLsdrmkdm").next().children().focus();
                codeLsdrmkdm.refresh();
            }
        }
    });
}