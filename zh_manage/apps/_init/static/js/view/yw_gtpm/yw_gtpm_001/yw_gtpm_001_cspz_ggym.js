/*
  页面元素初始化
*/
$(document).ready(function() {
    //默认显示和隐藏的文本框
    var trs = $("#beanWindow").find('tr[class^="cspz-"]');
    trs.hide();
    //页面显示时，根据ID这个标签的值来判断是增加的方法还是编辑的方法
    var csid = $("#hidCsid").val();
    if (csid == "add"){
        // 初始化页面元素
        updataPageInit();
    }else{
        //请求后台信息
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/search_view",
            data: {'csid': csid},
            success: function(data){
                // 初始化页面元素
                updataPageInit();
                //文本默赋编辑信息的值
                $("#selCsdm").combobox('select', data.csdm).combobox('disable');
                $("#selYwmc").combobox('select', data.ssywid).combobox('disable');
                $("#txtCsms").textbox('setValue', data.csms);
                $("#nfsKgl").get(0).checked = (data.kgl==1);
                $("#txtJksj").textbox('setValue', data.csz);
                $("#txtDbzdje").textbox('setValue', data.csz);
                $("#txtJyzq").textbox('setValue', data.csz);
                $("#txtJyyz").textbox('setValue', data.csz2);
            },
            error : function(){
                errorAjax();
            }
        });
    }
    
    //参数代码下拉列表控制
    $("#selCsdm").combobox({
        onSelect: function(record) {
            switch (record.bmmc) {
                case "YZJY_JK":
                    trs.hide().filter('.cspz-jksj').show();
                    break;
                case "YZJY_DBJE":
                    trs.hide().filter('.cspz-dbzdje').show();
                    break;
                case "YZJY_YZ":
                    trs.hide().filter('.cspz-xyzq, .cspz-xyyz').show();
                    break;
                case "YZJY_CFJE":
                default:
                    trs.hide();
                    break;
            }
        }
    });
    
    // 按钮【保存】的click事件监听
    $("#windowOk").click(function(e){
        e.preventDefault();
        add_submit(csid);
    });
    // 按钮【取消】的click事件监听
    $("#windowCancel").click(function(e){
        e.preventDefault();
        //打印这句话会使浏览器崩溃
        //print(parent.$('#div_xzcs').window('close'));
        parent.$('#divXzcs').window('close');
    });
    
    // 主页面 form tab排序
    $("#dgSearch").tabSort();
    
});
/**
 * 页面元素初始化
 */
function updataPageInit(){
    
    //设置默认的参数状态为开启
    $("#nfsKgl").get(0).checked=("1"=="1");
    // 最大值限制
    $("#txtDbzdje").next().children().attr("maxlength","16");
    $("#txtJyzq").next().children().attr("maxlength","20");
    $("#txtJyyz").next().children().attr("maxlength","20");
    $("#txtCsms").next().children().attr("maxlength","100");

}
/**
 * 执行保存事件
 */
function add_submit(csid){
    // 添加遮罩
    ajaxLoading();
    // 参数状态，业务id，参数代码
    var cszt = $("#nfsKgl").get(0).checked ? "1" : "0";
    var ywid = $("#selYwmc").textbox("getValue");
    var csdm = $("#selCsdm").textbox("getValue");
    var csms = $("#txtCsms").textbox("getValue");
    var jksj = $("#txtJksj").timespinner("getValue");
    var dbzdje = $("#txtDbzdje").numberbox("getValue");
    var jyzq = $("#txtJyzq").numberbox("getValue");
    var jyyz = $("#txtJyyz").numberbox("getValue");
    if (csid == "add") {
        // 新增
        url = "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/add_view";
    } else {
        // 修改
        url = "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/update_view";
    }
    // 提交表单
    $('#formWindow').find('form').form('submit', {
        url: url ,
        queryParams: {'cszt': cszt, 'ywid': ywid, 'csdm': csdm, 'csms':csms, 'jksj':jksj, 'dbzdje':dbzdje, 'jyzq':jyzq, 'jyyz':jyyz},
        onSubmit: function(){
            if (ywid=="") {
                $.messager.alert('错误','所属业务不可为空，请输入','error');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
            if (csdm=="") {
                $.messager.alert('错误','参数代码不可为空，请输入','error');
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            } else if(csdm == "YZJY_JK"){
                if( jksj == "" ){
                    $.messager.alert('错误','监控时间不可为空，请输入','error');
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                } 
            } else if(csdm == "YZJY_DBJE"){
                if( dbzdje == "" ){
                    $.messager.alert('错误','单笔最大金额不可为空，请输入','error');
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
            } else if(csdm == "YZJY_YZ"){
                if( jyzq == "" ){
                    $.messager.alert('错误','校验周期不可为空，请输入','error');
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
                if( jyyz == "" ){
                    $.messager.alert('错误','校验阈值不可为空，请输入','error');
                    // 取消遮罩
                    ajaxLoadEnd();
                    return false;
                }
            }
            return true;
        },
        success: function(data){
            if (typeof data == 'string') {
                data = $.parseJSON(data);
            }
            if (data.state == true) {
                $.messager.alert('提示', data.msg.replace("\n", "<br/>"), 'info',function() {
                    //添加成功后刷新grid
                    parent.$('#dgCspz').datagrid('load');
                    //关闭window
                    parent.$('#divXzcs').window('close');
                });
            }else{
                afterAjax(data, "", "");
            }
            // 取消遮罩
            ajaxLoadEnd();
        },
        error: function () {
            errorAjax();
            // 取消遮罩
            ajaxLoadEnd();
        }
    });
}