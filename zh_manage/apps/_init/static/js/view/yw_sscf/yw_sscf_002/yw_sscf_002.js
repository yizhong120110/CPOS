// 请求的服务器信息
fwqxx = {}
// 定义一行显示多少个图标
row_char = 3;
// 刷新系统信息的定时器对象
var sys_interval = null;
// 内存图标对象
var memory_chart = null;
// cpu图标对象
var cpu_chart = null;
// io使用率对象
var io_chart = null;
// 重启进程的标志
var cqjc_mark = false;
// 最大化，最小化的状态
var w_state = 'small';
// 进程表格对象
var progress_datagrid = null;
// 遮罩高度
var overlay_height = 0;
// 遮罩宽度
var overlay_width = 0;
// 遮罩的数据源
var overlay_data = null;
// 当时间轴时空时，显示这个变量
var date_null = ["1900-01-01 00:00:00(无数据)"];
var all_wj = [];
// 选中重启进程名称
var lastActiveNode = null;
$(document).ready(function() {
    // 适应页面
    var rowCount = 3;
    if ($('#jk_container').width()<1100) {
        rowCount = 2;
    }
    // 当前页面刷新
    $("#sx").click(function(){
        // 刷新整个页面
        window.location.reload();
    });
    // 图标画布的高度和宽度
    var height = ($('#jk_container').height()-22)/2;
    overlay_height = height;
    var width = ($('.packery').width()-(rowCount-1)*10-2)/rowCount;
    overlay_width = width;
    $('.packery').find(".item").css({"width":width, "height":height});
    // 拖拽
    var draggie_arr = new Array();
    $container = $('.packery').packery({
        gutter: 10,
        columnWidth: width,
        rowHeight: height
    });
    $container.find('.item').each(function(i, itemElem){
        var draggie = new Draggabilly(itemElem);
        draggie_arr.push(draggie);
        $container.packery('bindDraggabillyEvents', draggie);
    });

    $(".chart_tr").mousedown(function(){
        draggie_arr[$(this).parents(".item").index()].disable();
    });
    $(".item").mousedown(function(){
        draggie_arr[$(this).index()].enable();
    });
    
    function charts_resize() {
        memory_chart.resize();
        if (all_wj){
            all_wj.shift();
            // 循环所有的文件系统饼图
            $.each(all_wj, function(i,w){
                w.resize();
            });
        }
        cpu_chart.resize();
        io_chart.resize();
        disk_chart.resize();
    };
    // 图标大小变化时调用的方法
    window.onresize = charts_resize;
    // 获取系统信息
    get_zjxx();
    // 点击打开授权页面
    $("#window_cancel_grant").click(function(){
        $("#divSqWindow").window("close");
    });
    // 开关监控按钮的单击事件
    $("#sfjk").click(function(){
        // 标记下当前处理是重启进程
        cqjc_mark = false;
        var sfjk = $("#sfjk")[0].checked;
        var zt = '0';
        if (sfjk) {
            zt = '1';
        }
        event = event || window.event
        event.stopPropagation();
        // 授权成功后的回调URL
        var cs_url = "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/able_jk_view?ip="+zjip+'*zt='+zt+'*zjmc='+zjmc;
        // 授权URL
        url = "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/ty_sq?url="+cs_url;
        $('#sqFrame').attr('src', url );
        newWindow($("#divSqWindow"), "授权确认", 348, 190);
        return false;
    });

    var state = new Array();
    // 点击最大化按钮的事件 
    $('.max-win-btn').click(function(){
        var item = $(this).parents(".item");
        var index = item.index();
        // 点击对象的id
        var chart_id = this.id;
        // 单个图标的最小高度
        var chart_height = ($('#jk_container').height())/2;
        // 图标个数
        var chart_size = 1;
        if(fwqxx[chart_id].hasOwnProperty('keys')){
            chart_size = fwqxx[chart_id].length;
        }
        // 图标的行数
        var chart_rows = parseInt(chart_size/row_char) + 1;
        // 最小化
        if (state.length>0 && state[index]['max']) {
            // 恢复
            state[index]['max'] = false;
            item.css('z-index','').animate({left:state[index]['left'], top:state[index]['top'], height:state[index]['height'], width:state[index]['width']}, 350, charts_resize);
            $container.find('.item').each(function(i, ele){
                if (i != index) {
                    $(ele).css({'top':state[i]['top'], 'left':state[i]['left']});
                }
            });
            var charts = item.find("div[data-type='max']");
            var siblings = charts.siblings();
            siblings.css('display', 'block');
            charts.css('display', 'none');
            if (charts.length == siblings.length) {
                // 这句话的意思是：设置第一个元素的高度和宽度。
                $(charts.get(0)).css({'display':'block', 'width':'100%', 'height':'255px'});
            }
            // 绑定拖拽排序
            draggie_arr[index].enable();
            w_state = 'small';
            
        } else {
            // 最大化
            draggie_arr[index].disable();
            // 保存当前状态
            state.length = 0;
            $container.find('.item').each(function(){
                state.push({'top':$(this).css('top'), 'left':$(this).css('left'), 'width':$(this).css('width'), 'height':$(this).css('height'), 'max':false});
            });
            // 放大
            state[index]['max'] = true;
            var height = 0;
            if (chart_rows > 1){
                height = chart_height * chart_rows + 130*chart_rows;
            }else{
                height = $('#jk_container').height()*0.98;
            }
            // 最大化画布的大小
            item.css({'z-index':'2'}).animate({left: 0, top: 0, height:height, width:'100%'}, 350, charts_resize);
            var charts = item.find("div[data-type='max']");
            charts.siblings().css('display', 'none');
            // 每一个图标的大小
            charts.css({'width':Math.floor(100/row_char)+'%', 'height':chart_height+110, 'display':'block', 'float':'left'});
            w_state = 'big';
        }
        // 显示或者隐藏遮罩层
        showHideOverflow(overlay_data,w_state);
        // 获取放大后的数据
        get_zjxx();
    });
    // 主机异常数量的点击事件
    $("span[class='c-box btn-danger']").parent().on('click',function(){
        // 异常信息
        open_yjxx_window("3");
    });
    // 主机警告数量的点击事件
    $("span[class='c-box btn-warning']").parent().on('click',function(){
        // 预警信息
        open_yjxx_window("2");
    });
    // 点击刷新频率按钮时触发的方法
    $("#sxplpz").click(function(e){
        newWindow($("#sxplpz_window"), "刷新频率配置", "300px", "200px");
        // 显示旧的刷新频率
        $('#ymsxpl').numberspinner('setValue',sxpl_v);
        // 页面 form tab排序
        $("#forSxpl").tabSort();
    });
    // 刷新频率配置页面确定按钮的方法绑定
    $("#lbtn_sxplpz_window_ok").click(function(e){
        e.preventDefault();
        // 跟新刷新频率
        set_sxpl();
    });
    // 刷新频率配置页面取消按钮的方法绑定
    $("#lbtn_sxplpz_window_cancel").click(function(e){
        e.preventDefault();
        // 关闭窗口
        $("#sxplpz_window").window("close");
    });
    // 处理过程确定按钮事件
    $("#lbtn_clgc_window_ok").click(function(e){
        e.preventDefault();
        // 跟新处理过程
        update_clgc();
    });
    // 处理过程取消按钮事件
    $("#lbtn_clgc_window_cancel").click(function(e){
        e.preventDefault();
        $("#clgc_window").window("close");
    });
    // 监控配置
    $("#lbtn_window_pz_ok").click(function(e){
        e.preventDefault();
        // 更新监控配置
        update_jkpz();
    });
    // 处理过程取消按钮事件
    $("#lbtn_window_pz_cancel").click(function(e){
        e.preventDefault();
        $("#jk_setting_window").window("close");
    });
    // 进程新增按钮
    $("#lbtnJcpzSubmit").click(function(e){
        e.preventDefault();
        // 新增进程
        add_jcpz();
    });
    // 进程新增取消按钮
    $("#lbtnJcpzCacel").click(function(e){
        e.preventDefault();
        $("#jcjkpzWindow").window("close");
    });
    
    // 查询按钮的方法
    $("#lbtnSearch").on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        // 查询
        doSearch();
    });
    // 初始化监控按钮
    $("#sfjk")[0].checked = zt == '1';
    // 如果监控状态为未监控，则不设置定时刷新
    if(zt == '1'){
        // 定时器，定时刷新获取系统信息
        sys_interval = setInterval(get_zjxx,sxpl_r);
    }
    // 进程名称最大值长度限制
    $("#txtJcmc").next().children().attr("maxlength","20");
    // 查看命令最大值长度限制
    $("#txtCkml").next().children().attr("maxlength","300");
    // 启动命令最大值长度限制
    $("#txtQdml").next().children().attr("maxlength","300");
    // 启动类型最大值长度限制
    $("#txtQdlx").next().children().attr("maxlength","50");
    // 进程数量最大值长度限制
    $("#txtJcsl").next().children().attr("maxlength","3");
    // 处理过程最大长度限制
    $("#txtClgc").next().children().attr("maxlength","200");
    // 创建所有的遮罩层
    create_allOverlay(height,width);
    // 动态的创建遮罩层
    getJkpzOv(zt);
    $("#datagrid_yjxx").datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        singleSelect:true,
        method:'post',
        columns:[[
            { field: 'zxjhid', title: '执行计划id', width: 70,hidden:true },
            { field: 'jkfxpzid', title: '监控分析配置id', width: 70,hidden:true },
            { field: 'lsh', title: '流水号', width: 70 },
            { field: 'jkmc', title: '监控名称', width: 80},
            { field: 'fxgzmc', title: '分析规则名称', width: 70 },
            { field: 'fxgzms', title: '分析规则描述', width: 70 },    
            { field: 'hsmc', title: '函数名称', width: 80 },    
            { field: 'zxxydzlb', title: '执行响应动作列表', width: 80 , formatter: function(value,row,index) {
                return '<a href="javascript:;" onclick="javascript:xydz_list(\'datagrid_yjxx\',' + index + ',event);">查看</a>';
            } },
            { field: 'cz', title: '操作', width: 60, formatter: function(value,row,index) {
                return '<a href="javascript:;" onclick="javascript:txclgc(\'datagrid_yjxx\',' + index + ',event);">填写处理过程</a>';

            } }
        ]]
    });
});

/* 创建新的窗体
 * @param beanWindow 窗体对象
 * @param title 窗体的标题
 * @param width 窗体的宽度
 * @param height 窗体的高度
 */
function newWindow(beanWindow,title,width,height) {
    // 清空window中的值
    clearWindow(beanWindow);
    // 创建window
    var top = ($(window).height()-height)*0.35;
    var left = ($(window).width()-width)*0.5;
    beanWindow.window({
        title : title,
        width : width,
        height : height,
        top: top < 0 ? 0 : top,
        left: left < 0 ? 0 : left,
        closed : false,
        cache : false,
        modal : true
    });
};

/**
 * 清空window中input中的数据
 * @param beanWindow 要清理的window对象
 */
function clearWindow(beanWindow){
    // 清空下拉框中的值，默认选中第一个
    beanWindow.form('clear');
}

function jk_setting() {
    newWindow($("#jk_setting_window"), "监控配置", 650, 270);
    // 动态加载监控配置的元素
    get_jkpz();
}

//查看预警信息
function open_yjxx_window(type){
    var titleStr = '';
    if (type == '3') {
        titleStr = '异常信息查看';
    }else if(type == '2'){
        titleStr = '预警信息查看';
    }
    // 加载预警信息
    load_datagrid_yjxx(type);
    // 预警，异常信息window
    newWindow($("#yjxx_window"), titleStr, 920, 401);
}
//加载预警信息表格 
function load_datagrid_yjxx(type){
    // 预警，异常信息grid
    url="/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/get_yjxx_view";
    $("#datagrid_yjxx").datagrid({'url':url});
    $("#datagrid_yjxx").datagrid('load',{
        'yjjb':type,
        'ip':zjip
    });
}
//加载响应动作列表
function xydz_list(gridid,index,event){
    if (event){
        event.stopPropagation();
    }
    // 获取行数据
    var row_xx = $('#'+gridid).datagrid('getData').rows[index];
    //获取参数
    $("#datagrid_xydz").datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        singleSelect:true,
        method:'post',
        queryParams:{
            'jkfxpzid':row_xx.jkfxpzid,
            'lsh':row_xx.lsh
        },
        url: "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/get_xydzxx_view",
        columns:[[
            { field: 'hsmc', title: '响应动作函数名称', width: 70 },
            { field: 'zwmc', title: '中文名称', width: 80},
            { field: 'fxjgcf', title: '分析结果触发', width: 70 },
            { field: 'fqfs', title: '发起方式', width: 60 },
            { field: 'jhsj', title: '计划时间', width: 60, align: 'center'},
        { field: 'dzzxsj', title: '动作执行时间', width: 100, align: 'center'}
        ]]
    });
    newWindow($("#xydz_window"), "响应动作列表查看", 790, 363);
}
//处理过程窗口
function txclgc(gridid,index,event){
    if (event){
        event.stopPropagation();
    }
    // 获取行数据
    var row_xx = $('#'+gridid).datagrid('getData').rows[index];
    newWindow($("#clgc_window"), "填写处理过程", 350, 261);
    // 函数名称
    $('#hidHsmc').val(row_xx.hsmc);
    // 中文名称
    $('#hidZwmc').val(row_xx.fxgzmc);
    // 规则描述
    $('#hidGzms').val(row_xx.fxgzms);
    // 流水号
    $('#hidLsh').val(row_xx.lsh);
    // 执行计划id
    $('#hidZxjhid').val(row_xx.zxjhid);
}

/**
*授权处理
* drzxjhid：当日执行计划id
**/
function sqCheck(){
    event = event || window.event
    event.stopPropagation();
    // 标记下当前处理是重启进程
    cqjc_mark = true;
    // 授权成功后的回调URL
    var cs_url = "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/kr_jc_view?ip="+zjip + "*jcmc=" + lastActiveNode;
    // 授权URL
    url = "/oa/yw_jhrw/yw_jhrw_003/yw_jhrw_003_view/ty_sq?url="+cs_url;
    // 授权iframe的url
    $('#sqFrame').attr('src', url );
    newWindow( $( "#divSqWindow" ),'授权',400,190 );
}
/**动作
* 更新刷新频率
* sxpl
**/
function set_sxpl(){
    // 添加遮罩
    ajaxLoading();
    // 刷新频率
    var sxpl = $('#ymsxpl').textbox('getValue');
    if (sxpl == ''){
         $.messager.alert('错误','页面刷新频率不可为空，请输入','error', function(){
            $("#ymsxpl").next().children().focus();
        });
        // 取消遮罩
        ajaxLoadEnd();
        return false;
    }
    // 更新刷新频率
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/set_refresh_view',
        type : 'post',
        data : {
            'sxpl':sxpl,
            'ip':zjip
        },
        dataType : 'json',
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, '','sxplpz_window');
            sxpl_r = parseInt(data.sxpl)*1000*60;
            // 清除之前的定时器
            clearInterval(sys_interval);
            sys_interval = null;
            // 重新创建定时器
            sys_interval = setInterval(get_zjxx,sxpl_r);
            // 更新页面上的刷新频率
            sxpl_v = data.sxpl;
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
// 添加处理过程
function update_clgc(){
    $('#clgc_window').find('form').form('submit', {
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/update_clgc_view',
        dataType : 'json',
        type : 'post',
        onSubmit: function(){
            // 校验输入值的合法性
            var clgc = $('#txtClgc').textbox('getValue');
            if (clgc == ''){
                $.messager.alert('错误','处理过程不可为空，请输入','error', function(){
                    $("#txtClgc").next().children().focus();
                });
                return false;
            }
            return true;
        },
        success: function(data){
            afterAjax(data, 'datagrid_yjxx','clgc_window');
            // 更新页面的预警和异常数量
            update_yj_yc();
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
// 更新页面的预警和异常数量
function update_yj_yc(){
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/update_yj_yc_view',
        type : 'post',
        data : {
            'ip':zjip
        },
        async: false,//设置为同步
        dataType : 'json',
        success:function(data){
            $("#yc_span").text("异常("+data.yc+")");
            $("#yj_span").text("预警("+data.yj+")");
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
function get_zjxx() { 
    //ajax获取系统信息
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/zjxx_view',
        type : 'post',
        data : {
            'ip':zjip,
            'mark':w_state
        },
        async: false,//设置为同步
        dataType : 'json',
        success:function(data){
            // 将最新的服务器信息，赋值给全局变量
            fwqxx = data;
            // 更新页面的预警和异常数量
            update_yj_yc();
            // 更新主机的图标信息
            set_zjxx(data);
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
/** 
 * 将获取到的服务器信息展示到页面上
 **/
function set_zjxx(fwqxx){
    // cpu信息
    cpu = fwqxx.cpu;
    // 主机进程
    zjjc = fwqxx.zjjc.jcxx;
    // 文件系统使用率
    wj = fwqxx.wj;
    // io繁忙率
    io = fwqxx.io;
    // 物理内存使用情况
    wlnc = fwqxx.wlnc;
    
    // 物理内存的option
    var wlnc_option = {
        timeline : {
            data :wlnc.time.length == 0?date_null:wlnc.time,
            label : {
                formatter : function(s) {
                    return s.slice(11, s.length);
                }
            }
        },
        options : [
            {
                title : {
                    text: '物理内存',
                    x:'center',
                    show: false
                },
                legend: {
                    orient : 'vertical',
                    x : 'left',
                    data:['已使用内存','剩余内存']
                },
                tooltip : {
                    trigger: 'item',
                    formatter: "{b} : {c}K ({d}%)"
                },
                series : [
                    {
                        name:'内存使用率',
                        type:'pie',
                        radius: '55%',
                        center: ['50%', '40%'],
                        data:[
                            {value:wlnc.xx.length==0?0:wlnc.xx[0][2], name:'已使用内存'},
                            {value:wlnc.xx.length==0?0:wlnc.xx[0][3], name:'剩余内存'}
                        ],
                        itemStyle:{
                            normal:{
                                label:{
                                    show: true,
                                    formatter: '{d}%'
                                },
                                labelLine :{show:true}
                            }
                        }
                    }
                ]
            }
        ]
    }
    //图标每个时间段信息的对象
    function wlnc_detail_func(){
        this.series = [
            {
                name:'内存使用率',
                type:'pie',
                data:[
                    {value:0, name:'已使用内存'},
                    {value:0, name:'剩余内存'}
                ],
                itemStyle:{
                    normal:{
                        label:{
                            show: true,
                            formatter: '{d}%'
                        },
                        labelLine :{show:true}
                    }
                }
            }
        ]
    }
    // 当有数据时才显示图标信息
    if(wlnc.time.length != 0 && wlnc.xx.length != 0){
        // 循环添加各个时间段的图标信息
        //删除第一个元素，以为第一个元素已使用
        var wlnc_xx = wlnc.xx.shift();
        $.each(wlnc.xx, function(i,val){      
            //val是每个时间段内的物理内存的信息
            var data = [{value:val[2], name:'已使用内存'}, {value:val[3], name:'剩余内存'}];
            var wlnc_detail = new wlnc_detail_func();
            wlnc_detail.series[0].data = data;
            // 给option添加图标信息
            wlnc_option.options.push(wlnc_detail);
        });
    }
    // 图表
    memory_chart = echarts.init($('#memory_chart')[0]);
    memory_chart.setOption(wlnc_option);
    
    // 磁盘使用率
    function wj_func () {
        this.timeline = {
            data : wj.time.length==0?date_null:wj.time,
            label : {
                formatter : function(s) {
                    return s.slice(11, s.length);
                }
            }
        };
        this.options = [
            {
                title : {
                    text: wj.keys.length==0?"数据为空":wj.keys[0],
                    x:'center',
                    show: false,
                    textStyle:{
                        fontSize: 15
                    }  
                },
                legend: {
                    orient : 'vertical',
                    x : 'left',
                    data:['已使用空间','剩余空间']
                },
                tooltip : {
                    trigger: 'item',
                    formatter: "{b} : {c}K ({d}%)"
                },
                series : [
                    {
                        name:wj.keys.length==0?"数据为空":wj.keys[0],
                        type:'pie',
                        radius: ['27%', '55%'],
                        center: ['50%', '40%'],
                        data:[
                            {value:wj.keys.length==0?0:wj.xx[wj.keys[0]][0][3], name:'已使用空间'},
                            {value:wj.keys.length==0?0:wj.xx[wj.keys[0]][0][4], name:'剩余空间'}
                        ],
                        itemStyle:{
                            normal:{
                                label:{
                                    show: true,
                                    formatter: '{d}%'
                                },
                                labelLine :{show:true}
                            }
                        }
                    }
                ]
            }
        ];
    }
    // 文件系统使用率详细信息
    function wj_detail_func() {
        this.series = [
            {
                name:'磁盘使用率',
                type:'pie',
                data:[
                    {value:510, name:'已使用空间'},
                    {value:590, name:'剩余空间'}
                ],
                itemStyle:{
                    normal:{
                        label:{
                            show: true,
                            formatter: '{d}%'
                        },
                        labelLine :{show:true}
                    }
                }
            }
        ]
    }
    var first_file = new wj_func();
    if (wj.keys.length > 0){
        // 对主页显示的图标进行赋值
        $.each(wj.xx[wj.keys[0]], function(j,w){
            var data = [{value:w[3], name:'已使用空间'}, {value:w[4], name:'剩余空间'}];
            //如果是第一个时间的信息，那么让他默认显示
            if(j == 0){
                first_file.options[0].series[0].data = data;
            }else{
                var wj_detail = new wj_detail_func();
                wj_detail.series[0].data = data;
                // 给option添加图标信息
                first_file.options.push(wj_detail);
            }
        });
    }
    $('#disk_chart').css('height',$('#jk_container').height()*0.41);
    disk_chart = echarts.init($('#disk_chart')[0]);
    disk_chart.setOption(first_file);
    if(w_state == 'small'){
        // 重新加载图标对象前先清空之前的图标对象
        $("tr[id*='_copy']").remove();
        $("div[id*='_copy']").remove();
    }
    if(wj.xx.length !=0 && wj.time.length != 0){
        // 所有文件使用率饼图的集合
        all_wj = []
        all_wj = [disk_chart]
        // 标识是否是换行显示的饼图
        var mark = '';
        // 计算每一行的高度
        var height = (100/(parseInt(wj.keys.length/4)+1))+'%';
        // 设置第一行高度
        $("#wj_tr").css('height',height);
        // 由于内层each获取不到外层each内容，所以定义一个变量记录key
        var key_to = '';
        // wj_option对象
        var wj_option_n = null;      
        // 循环所有的文件系统，动态的创建饼图
        $.each(wj.keys, function(i,key){
            wj_option_n = new wj_func();
            wj_option_n.timeline.data = wj.time;
            key_to = key;
            //key是每个时间段内的物理内存的信息,循环创建每个饼图在不同时间端内的信息
            $.each(wj.xx[key_to], function(j,w){
                var data = [{value:w[3], name:'已使用空间'}, {value:w[4], name:'剩余空间'}];
                //如果是第一个时间的信息，那么让他默认显示
                if(j == 0){
                    wj_option_n.options[0].series[0].data = data;
                }else{
                    var wj_detail = new wj_detail_func();
                    wj_detail.series[0].data = data;
                    // 给option添加图标信息
                    wj_option_n.options.push(wj_detail);
                }
            });
            // 一行只显示4个
            if(i%row_char == 0 && i != 0){
                // 创建td
                var td = '<tr class="chart_tr" id="wj_tr_copy"'+i+'><td id="wj_td'+i+'" ></td></tr>';
                $("#wj_table").append(td);
                mark = i;
            }
            wj_option_n.options[0].title.text = key_to
            // 动态创建饼图元素
            var htm = '<div id="disk_chart_copy'+i+'" style="width:100%;height:100%;display:none;" data-type="max"></div>';
            $("#wj_td"+mark).append(htm); 
            var disk_chart_s = echarts.init($('#disk_chart_copy'+i)[0]);
            disk_chart_s.setOption(wj_option_n);
            all_wj.push(disk_chart_s);
        }); 
    }
    
    io_option = {
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:io.keys.length==0?["数据为空"]:io.keys
        },
        dataZoom : {
            show : true,
            realtime : true,
            start : 0,
            end : 100
        },
        grid: {
            x: 50,
            x2: 30,
            y: 50
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : io.time.length==0?["00:00:00(无数据)"]:io.time
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel : {
                    formatter: '{value} %'
                }
            }
        ],
        series : [{
            name:'数据为空',
            type:'line',
            smooth:true,
            data:['0'],
            itemStyle: {
                normal: {
                    lineStyle: {width: 2}
                }
            },
        }]
    };
    if(io.time.length!=0){
        // 删除默认数据
        io_option.series=[];
        // 循环获取每个磁盘的使用率
        $.each(io.keys,function(i,key){
            // 定义在内部的原因是，每次循环都创建一个对象。如果不，则循环的是一个io_line对象。
            var io_line = {
                name:'',
                type:'line',
                smooth:true,
                data:[],
                
                itemStyle: {
                    normal: {
                        lineStyle: {width: 2}
                    }
                },
            }
            io_line.name = key;
            io_line.data = io.values[key];
            io_option.series.push(io_line);
        });
    }
    io_chart = echarts.init($('#io_chart')[0]);
    io_chart.setOption(io_option);
    
    // cpu信息
    cpu_chart = echarts.init($('#cpu_chart')[0]);
    cpu_chart.setOption({
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:cpu.key_c
        },
        dataZoom : {
            show : true,
            realtime : true,
            start : 0,
            end : 100
        },
        grid: {
            x: 50,
            x2: 30,
            y: 50
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : cpu.time.length==0?["00:00:00(无数据)"]:cpu.time
            }
        ],
        yAxis : [
            {
                type : 'value',
                axisLabel : {
                    formatter: '{value} %'
                }
            }
        ],
        series : [
            {
                name:'用户使用',
                type:'line',
                smooth:true,
                itemStyle: {normal: {areaStyle: {type: 'default'}}},
                data: cpu.values.us.length==0?["0"]:cpu.values.us
            },
            {
                name:'系统使用',
                type:'line',
                smooth:true,
                itemStyle: {normal: {areaStyle: {type: 'default'}}},
                data: cpu.values.sy.length==0?["0"]:cpu.values.sy
            },
            {
                name:'IO等待',
                type:'line',
                smooth:true,
                itemStyle: {normal: {areaStyle: {type: 'default'}}},
                data: cpu.values.wa.length==0?["0"]:cpu.values.wa
            }
        ]
    });
    // 进程grid
    progress_datagrid = $("#progress_datagrid").treegrid({
        nowrap : false,
        fit : true,
        singleSelect: true,
        fitColumns : true,
        method: "get",
        url: "",
        'data':zjjc,
        idField:'id',
        treeField:'jcmc',
        columns: [[
            { field: 'id', title: 'id', width: 20, hidden:true },
            { field: 'jcmc', title: '进程信息', width: 20 }
        ]],
        onContextMenu: function(e, row) {
            if (row.parent == false){
                return;
            }
            e.preventDefault();
            // 选中
            lastActiveNode = row.jcmc;
            $("#mm").menu('show', {
                left:e.pageX,
                top:e.pageY
            });
        },
        onClickRow:function(row){
            // 点击行
            progress_datagrid.treegrid('toggle',row.id);
        }
    });
}

/**
 * 启用，禁用监控，调用业务url之前的调用方法
 **/
function ywcl_start(url,g_data){
    // 添加遮罩
    ajaxLoading();
}
/**
 * 启用，禁用监控，调用业务url之后的调用方法
 **/
function ywcl_end(url,g_data){
    // 取消遮罩
    ajaxLoadEnd();
}

/**
 * 启用，禁用监控，成功的回调方法
 **/
function succ_func(data){
    // 只有当开关监控时才改变监控按钮的状态
    if(cqjc_mark == false){
        $("#sfjk")[0].checked = data.zt == '1';
    }
    
    // 如果是禁用的话，将监控项禁用，停止刷新
    if (data.zt == '0'){
        // 清除之前的定时器
        clearInterval(sys_interval);
    } else {
        // 重新创建定时器
        sys_interval = setInterval(get_zjxx,sxpl_r);
        // 监控项置成可用
        $('#jk_container').find("*").each(function() { 
            $(this).removeAttr("disabled");
        }); 
    }
    // 如果是禁用，给所有的图标加遮罩
    getJkpzOv(data.zt)
}
/**
 * 启用，禁用监控，异常的回调方法
 **/
function error_func(){
    // 取消遮罩
    ajaxLoadEnd();
}
/**
 * 动态创建监控对象
 **/
function modeLi(id,zbmc,zbbm,cjpzzt){
    var selected = "selected";
    if(cjpzzt!='1'){
        selected = "";
    }
    // 监控对象
    var modeLi = '<li data-cjpzzt="'+cjpzzt+'" class="'+selected+'"><input name="jqdemo" value="value2" type="checkbox"><label for="choice_b">'+zbmc+'</label><img src="'+root_image_dic+'/memory_chart.png" style="width:80%;height:30%;"><a class="checkbox-select" href="###">选 择</a><a class="checkbox-deselect" href="###">取 消</a><input type="hidden" id='+id+' value='+zbbm+','+zbmc+'></li> ';
    return modeLi;
}
    
/**
 * 获取监控配置的元素
 **/
function get_jkpz(){
    // 请求，获取监控配置元素
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/jkpzgl_view',
        type : 'post',
        dataType : 'json',
        data:{
            'ip':zjip
        },
        success:function(data){
            $(".checklist li").remove();
            // 动态给监控配置窗口添加数据
            $.each(data,function(index,d){
                //复制页面对象监控配置对象
                var jk = modeLi(d.id, d.zbmc, d.zbbm, d.cjpzzt);
                $(".checklist").append(jk);
            });
            // 给监控配置元素添加点击事件
            setClick();
            // 将旧的监控配置信息保存到隐藏域中
            $('#hidJkxx').text(JSON.stringify(data));
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 * 给监控配置元素添加点击事件
 **/
function setClick(){
    /* see if anything is previously checked and reflect that in the view*/
    $(".checklist input:checked").parent().addClass("selected");
    /* handle the user selections */
    $(".checklist .checkbox-select").click(
        function(event) {
            event.preventDefault();
            // 判断该采集配置的状态是否是None，如果是，则说明主机没有对该采集配置进行采集
            if($(this).parent().attr("data-cjpzzt") == ''){
                $.messager.alert('提示', '未进行数据采集配置，无法选择', 'warning');
                return;
            }
            $(this).parent().addClass("selected");
            $(this).parent().find(":checkbox").attr("checked","checked");
        }
    );
    $(".checklist .checkbox-deselect").click(
        function(event) {
            event.preventDefault();
            $(this).parent().removeClass("selected");
            $(this).parent().find(":checkbox").removeAttr("checked");
            $(this).parent().find("span[class*='jk_home']").attr('class', 'jk_home');
        }
    );
}

/**
 * 监控配置保存方法
 **/
function update_jkpz(){
    // 添加遮罩
    ajaxLoading();
    // 要组织的数据
    var data = {'ip':zjip,'xx':[]};
    // 获取选择的监控配置
    get_jkpz_xx(data,'selected','1');
    // 获取未选择的监控配置
    get_jkpz_xx(data,'','0');
    // 进行保存
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/update_jkpzgl_view',
        type : 'post',
        dataType : 'json',
        data : {
            'ip':data.ip,
            'xx':JSON.stringify(data.xx),
            'oldxx':$('#hidJkxx').text()
        },
        success:function(data){
            // 取消遮罩
            ajaxLoadEnd();
            afterAjax(data, '','jk_setting_window');
            // 如果是禁用，给所有的图标加遮罩
            getJkpzOv(zt);
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
/**
 * 获取监控配置的信息
 **/
function get_jkpz_xx(data, cl, zt){
    var ls = $(".checklist li[class='"+cl+"']").find("input[type='hidden']");
    $.each(ls,function(index,l){
        var s = l.value.split(',');
        // 组织数据
        data.xx.push({'zbmc':s[1], 'zbbm':s[0], 'zt':zt});
    });
}
/**
 * 进程配置管理界面
 **/
function jcpzgl(){
    newWindow($("#jkpz_window"), "进程配置管理", 1000, 450);
    init_jcpzgl();
    // 获取搜索框的下拉框数据
    getComb();
}

/**
 * 初始化进程配置管理grid
 **/
function init_jcpzgl(){
    $("#dgJkpz").datagrid({
        nowrap : true,
        fit : true,
        rownumbers : true,
        pagination : true,
        pageSize: 50,
        fitColumns : true,
        method: "post",
        queryParams:{
            'ip':zjip
        },
        url: "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/jkjcpz_view",
        frozenColumns: [
            [{
                field: 'select_box',
                checkbox: true
            }]
        ],
        columns: [[
            // 进程名称、进程数量、启动命令、启动类型、查看命令、状态、来源
            {field: 'id', title: '进程id', hidden: true },
            {field: 'jclx', title: '进程类型', hidden: true },
            {field: 'jcmc', title: '进程名称', width: 20 },
            {field: 'jcsl', title: '进程数量',align:'right', width: 10 },
            {field: 'qdml', title: '启动命令', width: 40 },
            {field: 'txwjmc', title: '启动类型', width: 20 },
            {field: 'ckml', title: '查看命令', width: 25 },
            {field: 'zt',title: '状态',width: 8,
                formatter: function(value, rowData, rowIndex) {
                    return value == '1' ? "启用" : "禁用"
                }
            }, 
            {field: 'ly',title: '来源',width: 8,
                formatter: function(value, rowData, rowIndex) {
                    return value == 'pd' ? "铺底" : "自定义"
                }
            }, 
            {field: 'cz',title: '操作',width: 8,
                formatter: function(value, rowData, rowIndex) {
                    var czStr = '';
                    if (rowData) {
                        czStr += '<a href="javascript:;" onclick="javascript:jcjkpz_add2upd(\'dgJkpz\',' + rowIndex + ',\'upd\',event);">编辑</a> ';
                    }
                    return czStr;
                }
            }
        ]],
        toolbar: [{
            iconCls: 'icon-add',
            text: '新增',
            handler: function() {
                // 新增
                jcjkpz_add2upd('dgJkpz', '', 'add');
            }
        }, '-', {
            iconCls: 'icon-remove',
            text: '删除',
            handler: function() {
                // 删除
                removechecked();
            }
        }],
        onLoadSuccess: function(data){ // 加载完毕后获取所有的checkbox遍历
            if (data.rows.length > 0) {
                // 循环判断操作为新增的不能选择
                for (var i = 0; i < data.rows.length; i++) {
                    // 根据引用次数让某些行不可选
                    if (data.rows[i].ly == 'pd') {
                        $("input[type='checkbox']")[i + 2].disabled = true;
                    }
                }
            }
        },
        onClickRow: function(rowIndex, rowData){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgJkpz').datagrid('unselectRow', index - 2);
                }
            });
            // 如果可选的都已选中，全选复选框置为勾选状态
            if ($('.datagrid-cell-check input:enabled').length == $('#dgJkpz').datagrid('getChecked').length && $('#dgJkpz').datagrid('getChecked').length != 0) {
                $('.datagrid-header-check input').get(0).checked = true;
            }
        },
        onCheckAll: function(rows){
            // 获取所有的checkbox遍历
            $("input[type='checkbox']").each(function(index, el){
                // 如果当前的复选框不可选，则不让其选中
                if (el.disabled == true) {
                    $('#dgJkpz').datagrid('unselectRow', index - 2);
                }
            });
            // 全选复选框置为勾选状态
            $('.datagrid-header-check input').get(0).checked = true;
        }
    });
}
/**
 * 进程配置管理搜索框的数据
 **/
function getComb( flag ){
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/get_jclxzt_view',
        type : 'post',
        data : {
            'ip': zjip
        },
        dataType : 'json',
        success:function(data){
            // 新增编辑状态
            $("#combJcjk_zt").combobox({
                data: data.jczt,
                valueField: 'bm',
                textField: 'mc',
                onLoadSuccess: function(data){
                    // 默认选择第一项
                    $("#combJcjk_zt").combobox('select', data[0].bm);
                }
            });
            // 设置主机名称
            $('#txtZjmc').text(data.zjmc);
            // 设置hostname
            $('#txtHostname').text(zjip);
            $("#combSearch_zt").combobox('setValue',data.jczt[0]['bm']);
            
            // 根据传来的方法参数进行确认Tab顺的使用
            if (flag == 0) {
                $('#jcjkpzWindow').find('form').tabSort();
            } else {
                $("#combSearch_zt").combobox({
                    data: data.jczt,
                    valueField: 'bm',
                    textField: 'mc',
                    onLoadSuccess: function(data){
                        // 默认选择第一项
                        $("#combSearch_zt").combobox('select', data[0].bm);
                    }
                });
                $('#dxForm').tabSort();
            }
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });       
    
}
/**
 *删除进程
 */
function removechecked() {
    // 获取所有选中的采集配置
    var checkedItems = $('#dgJkpz').datagrid('getChecked');
    // 校验至少选择一项
    if (!checkSelected("dgJkpz")){
        return;
    }
    $.messager.confirm("提示", "删除后其业务下的所有内容将不可恢复，您确定要删除吗？", function(flag) {
        if (flag) {
            // 添加遮罩
            ajaxLoading();
            url = '/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/del_jcpz_view';
            // 删除进程
            var rows = $('#dgJkpz').datagrid('getSelections');
            // ajax请求
            $.ajax({
                url:url,
                type : 'post',
                dataType : 'json',
                data : {
                    'rows' : JSON.stringify(rows),
                    'ip': zjip,
                    'zjmc':$('#txtZjmc').text()
                },
                success:function(data){
                    // 取消遮罩
                    ajaxLoadEnd();
                    //执行请求后的方法
                    afterAjax(data, 'dgJkpz','');
                },
                error : function(){
                    // 取消遮罩
                    ajaxLoadEnd();
                    // 失败后要执行的方法
                    errorAjax();
                }
            }); 
        }
    });
}

// 查询方法
function doSearch() {
    // 进程名称
    jcmc = $("#txtSearch_jcmc").textbox('getValue')
    // 状态
    jczt = $("#combSearch_zt").combobox('getValue');
    if(jczt == '-1'){
        jczt = '';
    }
    // 根据条件查询管理对象
    $("#dgJkpz").datagrid('load',{
        jcmc: jcmc,
        jczt: jczt,
        ip:zjip
    });
}
//新增或编辑
function jcjkpz_add2upd(datagrid_id, index, type,event) {
    if (event){
        event.stopPropagation();
    }
    if (type == 'add') {
        // 创建新增窗口
        newWindow($('#jcjkpzWindow'), "新增进程", '660', '260');
        // 进程默认数量
        $('#txtJcsl').numberbox('setValue',1);
        $("#txtQdml").textbox("enable");
        $("#txtQdlx").textbox("enable");
        getComb(0);

    } else if (type = 'upd') {
        newWindow($('#jcjkpzWindow'), "编辑进程", '660', '260');
        //赋值
        var row_xx = $('#'+datagrid_id).datagrid('getData').rows[index];
        $("#hidId").val(row_xx.id);
        // 获取编辑对象的属性
        get_edit(row_xx.id);
    }
    $('#hidHostname').val(zjip);
    $('#hidZjmc').val($('#txtZjmc').text());
}
/**
 * 获取要编辑的内容的属性
 */
function get_edit(id){
    // ajax请求
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/get_jcpz_edit_view',
        type : 'post',
        data : {
            'id':id,
            'ip':zjip
        },
        dataType : 'json',
        success:function(data){
            //执行请求后的方法
            if(data.state == true){
                $('#hidOldData').val(JSON.stringify(data.xx));
                // 如果查询成功
                // 进程名称
                $('#txtJcmc').textbox('setValue', data.xx.jcmc);
                // 进程数量
                $('#txtJcsl').numberbox('setValue', data.xx.jcsl);
                // 查看命令
                $('#txtCkml').textbox('setValue', data.xx.ckml);
                // 启动命令
                $('#txtQdml').textbox('setValue', data.xx.qdml);
                // 启动类型
                $('#txtQdlx').textbox('setValue', data.xx.txwjmc);
                if ( data.xx.ly == "pd") {
                    $("#txtQdml").textbox("disable");
                    $("#txtQdlx").textbox("disable");
                }else{
                    $("#txtQdml").textbox("enable");
                    $("#txtQdlx").textbox("enable");
                }
                // 状态
                $("#combJcjk_zt").combobox("select", data.xx.zt);
                $('#jcjkpzWindow').find('form').tabSort();
                
            }else{
                // 如果查询失败
                afterAjax(data, "", "");
            }
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 * 添加进程
 **/
function add_jcpz(){
    // 添加遮罩
    ajaxLoading();
    url = '/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/add_jcpz_view';
    if( $('#hidId').val()){
        url = '/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/edit_jcpz_view';
    }
    $('#jcjkpzWindow').find('form').form('submit', {
        url:url,
        dataType : 'json',
        type : 'post',
        onSubmit: function(){
            // 校验输入值的合法性
            var ret = validate_jcpz();
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
            //执行请求后的方法
            afterAjax(data, 'dgJkpz','jcjkpzWindow');
        },
        error : function(){
            // 取消遮罩
            ajaxLoadEnd();
            // 失败后要执行的方法
            errorAjax();
        }
    });
}

/**
 * 添加进程的校验
 **/
function validate_jcpz(){
    // 进程名称
    var jcmc = $("#txtJcmc").textbox('getValue');
    // 进程数量
    var jcsl = $("#txtJcsl").textbox('getValue');
    // 启动命令
    var qdml = $("#txtQdml").textbox('getValue');
    // 启动类型
    var qdlx = $("#txtQdlx").textbox('getValue');
    // 查看命令
    var ckml = $("#txtCkml").textbox('getValue');
    // 状态
    var xz_jczt = $("#combJcjk_zt").combobox('getValue');

    // 进程名称
    if(!checkNull(jcmc, '进程名称', 'txtJcmc')) {
        return false;
    }
    // 进程数量
    if(!checkNull(jcsl, '进程数量', 'txtJcsl')) {
        return false;
    }
    // 启动命令
    if(!checkNull(qdml, '启动命令', 'txtQdml')) {
        return false;
    }
    // 启动命令
    if(!checkValZw(qdml, '启动命令', 'txtQdml')) {
        return false;
    }
    // 启动类型
    if(!checkValZw(qdlx, '启动类型', 'txtQdlx')) {
        return false;
    }
    // 查看命令
    if(!checkValZw(ckml, '查看命令', 'txtCkml')) {
        return false;
    }
    // 状态
    if(xz_jczt == -1 || xz_jczt == "请选择"){
        $.messager.alert('错误','状态不可为空，请选择','error', function(){
                $("#combJcjk_zt").next().children().focus();
            });
            return false;
    }
    return true
}

/* 显示遮罩层 */
function createOverlay(id, height, width, top, left) {
    $("<div id='"+id+"'></div>").css({
        position:'absolute',
        top:top+6,
        left:left+6,
        backgroundColor:"#004400",
        opacity:0.1,
        zIndex:300,
        height:height,
        width:width
    }).appendTo("#jk_container");
}

/* 隐藏覆盖层 */
function hideOverlay(id) {
    $("#"+id).hide();
}
/* 显示覆盖层 */
function showOverlay(id) {
    $("#"+id).show();
}
/* 创建所有的遮罩层 */
function create_allOverlay(height,width){
    // 现将所有的遮罩层全部创建好，然后后面的只是显示也隐藏即可了。
    // 内存使用率
    createOverlay("get_ram", height, width, 0, 0);
    // 磁盘空间使用率
    createOverlay("get_filesystem", height, width, 0, width+10);
    // 磁盘I/O繁忙率
    createOverlay("get_io", height, width, 0, width*2+10*2);
    // CPU使用率
    createOverlay("get_cpu", height, width, height+10, 0);
}

/* 根据监控状态创建遮罩层 */
function getJkpzOv(zt){
    if(zt == '0'){
        // 内存使用率
        showOverlay("get_ram");
        // 磁盘空间使用率
        showOverlay("get_filesystem");
        // 磁盘I/O繁忙率
        showOverlay("get_io");
        // CPU使用率
        showOverlay("get_cpu");
        return ;
    }
    // 如果是监控启用的状态，就查询那些图标需要遮罩层
    $.ajax({
        url:'/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/jkpzgl_view',
        type : 'post',
        dataType : 'json',
        data:{
            'ip':zjip
        },
        success:function(data){
            // 动态给监控配置窗口添加数据
            showHideOverflow(data,w_state);
            // 更新数据源对象
            overlay_data = data;
        },
        error : function(){
            // 失败后要执行的方法
            errorAjax();
        }
    });
}
/** 根据监控的对象数据隐藏和显示遮罩 **/
function showHideOverflow(data,mark){
    // 如果mark是big那么就将所有的遮罩隐藏
    if(mark == 'big'){
        // 内存使用率
        hideOverlay("get_ram");
        // 磁盘空间使用率
        hideOverlay("get_filesystem");
        // 磁盘I/O繁忙率
        hideOverlay("get_io");
        // CPU使用率
        hideOverlay("get_cpu");
        return;
    }
    $.each(data,function(index,d){
        // 动态的显示和隐藏遮罩层 'get_cpu()','get_ram()','get_filesystem()','get_io()'
        var zbbm = d.zbbm.replace("()","");
        if(d.cjpzzt == '1'){
            hideOverlay(zbbm);
        }else{
            showOverlay(zbbm);
        }
    });
}
