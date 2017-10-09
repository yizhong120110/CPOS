/**
 * 页面初始化加载
*/
$(document).ready(function() {
    // 报表的用户名，固定写死
    ReportViewer.UserName = 'Shandongcposkejigufenyouxiangongsi';
    // 报表的注册码，固定写死
    ReportViewer.SerialNo = 'TX488VDM68BSMC55BK164CHN4TKAE6AP319KZJ5690FC6K6UC9XNQP5KJSC64WV48X7198TMAE6ZRVC8V9394TKAE68ZC19'
    // 修改html的标题
    document.title = html_title;
    // 判断开发人员是否加了分页，如果没有加分页的话就显示所有的数据
    if((search_data['rows'] == undefined || search_data['rows'] == '') || (search_data['page'] == undefined || search_data['page'] == '')){
        search_data['rows'] = 999999999;
        search_data['page'] = 1;
    }
    // 添加请求数据类型
    search_data['req_lx'] = 'bb'
    // 生成报表
    $.post(search_url, search_data, function(data) {
        if ( ReportViewer.Running !=0 ) { //正在运行
            ReportViewer.Stop();
        }
        if(data.filepath){
            // 非for循环处理方式
            ReportViewer.Report.LoadFromURL(real_path+grf_path);
            ReportViewer.Report.LoadDataFromURL('/tmp/'+data.filepath);
            // 设置分页
            ReportViewer.RowsPerPage = -1;  // <0: 自适应分页  >0:每页显示行数
            ReportViewer.Start();
        }else{
            // 调用for循环处理数据
            set_data_grid(data);
        }
        
    }, "json");
    // 隐藏预览页面的操作按钮
    removeToolbarControl();
});

/**
    前台处理数据，显示数据
*/
function set_data_grid(data){
    // 加载模板
    ReportViewer.Report.LoadFromURL(real_path+grf_path);
    // 设置分页
    ReportViewer.RowsPerPage = -1;  // <0: 自适应分页  >0:每页显示行数
    var Recordset = ReportViewer.Report.DetailGrid.Recordset;
    ReportViewer.Report.PrepareRecordset();
    for (var i=0 ; i< data.rows.length; i++){
        Recordset.Append();
        // 循环设置报表的内容。
        for (var j = 0; j < report_title.length; j++){
            ReportViewer.Report.FieldByName(report_title[j]).AsString = ""+data.rows[i][report_title[j]]+"";
        }
        Recordset.Post();
    }
    // 启动，显示报表。
    ReportViewer.Start();
}

/**
*  隐藏报表页面操作按钮
*/
function removeToolbarControl(){
    //定义一数组 
    var isplayviewer_arr= new Array(); 
    //字符分割 
    isplayviewer_arr=isplayviewer.split(",");
    //循环隐藏标签
    for (i=0;i<isplayviewer_arr.length ;i++ ){
        var sep = isplayviewer_arr[i];
        var ret_str = strToInt( sep );
        if( ret_str != 'false' ){
            ReportViewer.RemoveToolbarControl( ret_str );
        }
    }
}

/**
* 将字符串转化为数字
*/
function strToInt( str ){
    var ret_str = '';
    try{
        ret_str = parseInt( str );
    }
    catch(e){
        ret_str = 'false';
    }
    return ret_str
}