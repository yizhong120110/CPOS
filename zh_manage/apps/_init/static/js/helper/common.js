// 定义模块
define(['jquery', 'jeasyui'], function($) {

    $(function() {

        // 扩展tabs的函数header
        $.fn.tabs.methods.header = function(ele) {
            return $.data(ele[0],"tabs").tabs[0].closest('div.tabs-panels').prev();
        }

        // 扩展jQuery插件 - 按tab键切换焦点的函数
        // 调用方法：$(form).tabSort();
        $.fn.tabSort = function() {
            this.each(function(i, oneform) {
                createTabSort($(oneform));
                // 添加了100秒的延迟
                setTimeout(function() {
                    // 得到这个oneform的所有符合过滤条件的元素，先blur然后第一个元素focus
                    getAllelements($(oneform))
                        .blur()
                        .first()
                        .focus();
                }, 100);
            });
        }

        // 针对textbox - 使用easyui-tooltip
        // 位置：right默认
        // 内容从data-msg中获取 换行符\n
        $.fn.ttip = function() {

            this.each(function(i, ele) {
                var $ele = $(ele);

                var msg = $ele.data('ttipMsg');

                msg = $.map(msg.split('\n'), function(str) {
                    return '<p>'+str+'</p>'
                }).join('');

                $ele
                    .next()
                    .children('input.textbox-text')
                    .tooltip({
                        position: 'right',
                        showEvent: 'focus',
                        hideEvent: 'blur',
                        content: msg
                    });
            });

        };

        // v1.0 add by bianl 2015-01-21
        // 获得所有表单
        var allforms = $('form');

        // 遍历所有表单
        // 仅仅为每个form添加属性data-index
        $.each(allforms, function(i, oneform) {
            // 为每个表单处理
            // 目前支持tab排序的easyui表单控件有：
            // easyui-textbox，easyui-combobox，easyui-linkbutton


            var $oneform = $(oneform);

            var index = i + 1;

            // 为form建立索引 - 1,2,3,4,5,6
            $oneform.attr('data-index', index);

            // 为所有form添加索引排序
            // del by bianl 页面加载后
            // 不再进行自动tab，需要手动调用tabSort函数进行排序
            // $oneform.tabSort();

        });

        // ttip 气泡
        $('input[data-plugin="ttip"]').ttip();

    });

    /**
     * 将form转换为json对象。
     * @returns {___anonymous5630_5631}
     */
    function formToJson(formID) {
        var o = {};
        var a = $('#' + formID).serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [ o[this.name] ];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    }
    /**
     * 动态给某div下的input赋值。
     * @param win_id
     * @param data
     */
    function setRowToWin(win_id,data){
        var id=' ';//获取标签的name值
        $('#' + win_id + ' input,select').each(function(){
            id=$(this).attr('id');
            if(id) {
                if($(this).attr('type')=='radio') {
                    $('#'+win_id+' [type=radio][value='+data.id+']').attr('checked','checked');
                }else {
                    $('#' + id).textbox('setValue',data[id]);
                }
            }
        });
    }
    /**
     * ajax 状态为error时调用的方法
     * @param data
     */
    function errorAjax(){
        $.messager.alert('警告', '请求失败，请稍后重试', 'warning');
    }
    /**
     * 封装方法：Ajax请求成功后执行的操作，包括关闭window.刷新grid
     * data: Ajax返回的数据
     */
    function afterAjax(data,gridID,windowID){
        ajaxLoadEnd();
        if(typeof data == 'string'){
            data = $.parseJSON(data);
        }
        if(data.state == true){
            //添加成功后刷新grid
            if(gridID != '' && gridID != null){
                $('#'+ gridID).datagrid('reload');
            }

            //关闭window
            if(windowID != ''){
                $('#'+ windowID).window('close');
            }
            $.messager.alert('提示', data.msg, 'info');
        }else{
            $.messager.alert('提示', data.msg, 'error', function(){
                //选中需要重新输入的内容
                if (data.msg.indexOf("[") > 0) {
                    var lable = data.msg.split("[")[0];
                    var selector = windowID=="" ? "html" : "#"+windowID;
                    $(selector).find(":contains('"+lable+"：'), :contains('"+lable+":')").last().nextAll().find(".textbox-text").first().select();
                }
            });
        }
    }
    /**
     * 警告必须选择一项
     * @returns
     */
    function checkSelected(id){
        var rows = $('#' + id).datagrid('getSelections');
        if(rows == ''){
            $.messager.alert('警告', '至少选择一项', 'error');
            return false;
        }
        return true;
    }
    /**
     * 警告不可选择多行
     */
    function checkSelections(id){
        var rows = $('#' + id).datagrid('getSelections');
        if(rows.length > 1){
            $.messager.alert('警告', '只能选择一项', 'error');
            return false;
        }
        return true;
    }
    /**
     * 显示提示信息
     */
    function showMsg(data,timeout){
        $.messager.show({
            title : '提示',
            msg:data.msg,
            timeout:timeout,
            showType:'slide'
        });
    }

    /**
     * 取得字段长度
     *   1个汉字对应postgre数据库的字段长度为3
     * @param val
     * @returns 对应postgre数据库的字段长度
     */
    function getByteLen(val) {
        var len = 0;
        for (var i = 0; i < val.length; i++) {
            var a = val.charAt(i);
            if (a.match(/[^\x00-\xff]/ig) != null) {
                len += 3;
            } else {
                len += 1;
            }
        }
        return len;
    }

    /* 创建新的窗体
     * @param beanWindow 窗体对象
     * @param title 窗体的标题
     * @param width 窗体的宽度
     * @param height 窗体的高度
     */
    function newWindow(beanWindow,title,width,height) {
        // 清空window中的值
        var ck_state = new Array();
        $(".onoffswitch-checkbox").each(function(){
            ck_state.push(this.checked);
        });
        beanWindow.form('clear');
        $(".onoffswitch-checkbox").each(function(i){
            this.checked = ck_state[i];
        });
        // 创建window
        var top = ($(window).height()-height)*0.35;
        var left = ($(window).width()-width)*0.5;
        // 显示
        beanWindow.show();
        beanWindow.window({
            title : title,
            width : width,
            height : height,
            top: top < 0 ? 0 : top,
            left: left < 0 ? 0 : left,
            closed : false,
            cache : false,
            modal : true,
            onBeforeOpen: function(){
                beanWindow.find("form").form("disableValidation");
            },
            // 在关闭window之后，干点啥 mod by
            onBeforeClose: function() {
                // 如果iframe是创建出来的，在这里，建议释放iframe内存。
            }
        });
        // 新增弹框时光标定位第一个输入框
        window.setTimeout(function(){
            var focus = true;
            $(beanWindow.find("span>.textbox-text:not(:disabled):not([readonly])")).each(function(){
                if ($(this).val() != "") {
                    focus = false;
                    return false;
                }
            });
            if (focus) {
                beanWindow.find("span>.textbox-text:not(:disabled):not([readonly])").first().focus();
            }
        }, 100);
    }

    /* 创建新的Tab
     * @param title Tab的标题
     * @param href Tab的链接
     */
    function newTab(title, href) {
        var content = undefined;
        var $main = window.top.jQuery("#pnlMain");
        var len = $main.tabs('tabs').length;
        var msg = 'tab页已经超过10个，请先关闭其他页面再打开！';

        if ($main.tabs('exists', title)) {
            $main.tabs('select', title);
        } else {
            // tabs不能超过10个
            if (len == 10) {
                return $.messager.alert('提示', msg, 'info');
            }
            // 创建原生iframe
            content = document.createElement("iframe");
            content.style.width = '100%';
            content.style.height = '100%';
            content.scrolling = "auto";
            content.frameBorder = 0;
            content.src = href;

            $main.tabs('add', {
                title: title,
                content: content,
                closable: true
            });
        }
    }

    /* 为文件提供上传服务
     * 期望服务端返回json响应
     * 融合easyui的easyui-progressbar
     *
     * 事件发生的顺序 add>submit>start>process>success or error
     *
     * @param opts
     * opts.id input[id]
     * opts.url 上传http请求地址
     * opts.fileType 文件类型 正则表达式 默认支持所有类型
     * opts.maxSize 文件大小 单位MB 默认200MB
     * opts.progressbar 进度条(id)
     * opts.add 添加一个文件触发该事件
     * opts.submit 上传文件时触发该事件
     * opts.start 文件开始上传时触发该事件
     * opts.progress 文件进度中触发
     * opts.success 文件上传成功触发 server返回json在data.result中
     * opts.error 文件上传出错时触发
     *
     * @returns obj
     * obj.submit 函数 开始上传
     * obj.setUrl 改变上传http地址
     * obj.isAddFile 是否添加文件-true表示已经添加了文件,否则没有添加文件
     */
    function fileUpload(opts) {

        // input[class="easyui-filebox"]的jQuery对象
        var fileinput = undefined;

        // easyui的filebox控件生成的input[type=file]jQuery对象
        var fileuploadEasyui = undefined;

        // easyui的filebox控件生成的可见的inputjQuery对象
        var fileuploadInput = undefined;

        // easyui的filebox控件生成的可见的按钮jQuery对象
        var fileuploadA = undefined;

        // 是否有错误
        var hasError = false;

        // 错误消息
        var errorMessage = '';

        // 文件
        var filedata = undefined;

        // 进度条
        var progressbar = undefined;

        // 返回对象
        var obj = {
            // 重新设置上传地址
            setUrl: $.noop,
            // 上传命令
            submit: $.noop,
            // 是否添加文件 - false表示没有添加文件;true表示已经添加了文件
            isAddFile: false,
            // 上传的文件name
            filename: undefined
        };

        var options = {
            // 上传空间原生type=file元素的id
            id: '',
            url: '',
            // 默认支持所有类型
            fileType: undefined,///(\.|\/)(gif|jpe?g|png)$/i
            // 默认最大值200MB
            maxSize: undefined || 200,
            add: $.noop,
            submit: $.noop,
            start: $.noop,
            progress: $.noop,
            // progressbar容器id
            progressbar: undefined,
            success: $.noop,
            error: $.noop
        }

        // 合并参数
        options = $.extend({}, options, opts);

        // 对外接口
        fileinput = $('#' + options.id);

        // 寻找隐藏在暗处的easyui input[type=file]元素
        fileuploadEasyui = fileinput.next().children('input.textbox-value');
        fileuploadInput = fileinput.next().children('input.textbox-text');
        fileuploadA = fileinput.next().children('a.textbox-button');

        // progressbar对象
        if(progressbar = (options.progressbar && $('#'+options.progressbar))) {
            progressbar.css({
                width: '100%',
                display: 'none'
            });
        }

        // 如果可见input对象存在
        if (fileuploadInput) {
            fileuploadInput
                .prop('disabled', true)
                // input样式 背景从rgb(235, 235, 228)变为white
                // 鼠标样式变成not-allowed
                // 2015-01-22 add by bianl
                .css({
                    'background-color': 'white',
                    'cursor': 'not-allowed'
                });
        }

        // 如果可见的按钮对象存在
        if (fileuploadA) {
            fileuploadA.hover(
                function () {
                    $(this).css('border-color', '#ccc');
                },
                function () {
                    $(this).css('border-color', '#84909c');
                }
            );
        }

        // 调用fileupload方法
        fileuploadEasyui
            .fileupload({
                url: options.url,
                type: "POST",
                dataType: "json",
                autoUpload: false,
                // 1个文件
                maxNumberOfFiles: 5,
                // 如果文件是多个，true表示请求是按顺序的，false则表示请求是同步的
                sequentialUploads: true,
                // 表示xhr上传类型：multipart/form-data
                multipart: true
            })
            // 添加文件时触发
            // 添加一次，触发一次
            .on('fileuploadadd', function(e, data) {
                var uploadErrors = [],
                    filename,
                    filesize,
                    file,
                    fType = options.fileType,
                    fMSize = options.maxSize;

                // 每次默认是没有错误的
                hasError = false;

                // 每次默认是没有错误消息的
                errorMessage = '';

                // 每次默认已经添加文件
                obj.isAddFile = true;

                // 把data绑定到返回值filedata
                filedata = data;

                file = filedata.files[0];

                filename = file['name'];

                obj.filename = filename;

                // 赋值file name给input
                fileinput.next().children('input.textbox-text').val(filename);

                // check file type
                if (fType && filename) {
                    if (fType &&
                        !(fType.test(file.type) ||
                        fType.test(file.name))){
                        uploadErrors.push('文件类型不支持');
                    }
                }

                // check file max size
                if(fMSize) {
                    // 变成字节 要求最大值
                    fMSize = fMSize*1000000;
                    // 上传的文件的具体大小
                    filesize = data.files[0]['size']
                    // 比较大小
                    if(filesize > fMSize) {
                        uploadErrors.push('文档大小超过最大限制（200M），系统不允许上传，请重新选择');
                    }

                    if(filesize == 0) {
                        uploadErrors.push('文档为空文件，不允许上传，请重新选择');
                    }
                }


                if(uploadErrors.length > 0) {
                    // 有错误，则置hasError为true
                    hasError = true;
                    // 每次错误都要重新设置为没有添加文件
                    obj.isAddFile = false;
                    // check 失败 file name 置空
                    fileinput.next().children('input.textbox-text').val('');
                    // 清除filename
                    obj.filename = undefined;
                    // 保存错误消息
                    errorMessage = uploadErrors.join("，");
                    // 打印错误消息
                    $.messager.alert('提示', errorMessage, 'error');
                }


                // 执行add方法
                if ($.type(options.add) == 'function') {
                    options.add(data);
                } else {
                    console.error('add is not function.');
                }

            })
            .on('fileuploadstart', function(e) {
                if (progressbar) {
                    progressbar.progressbar('setValue', '0');
                    progressbar.show();
                }

                if ($.type(options.start) == 'function') {
                    options.start(e);
                } else {
                    console.error('start is not function.');
                }
            })
            // 监听submit事件
            // 需要传递额外的参数给服务器 formData
            .on('fileuploadsubmit', function(e, data) {
                if ($.type(options.submit) == 'function') {
                    // 没有错误才可以submit
                    return options.submit(data);
                } else {
                    console.error('submit is not function.');
                    return false;
                }
            })
            // progressall不能直接监听options.progress，下面匿名函数方式可用
            .on('fileuploadprogressall', function(e, data) {
                // 兼容easyui的进度条
                var progressInt = undefined;
                if (progressbar) {
                    progressInt = parseInt(data.loaded / data.total * 100, 10);
                    progressbar.progressbar('setValue', progressInt);
                }
                if ($.type(options.progress) == 'function') {
                    options.progress(data);
                } else {
                    console.error('progress is not function.');
                }
            })
            .on('fileuploaddone', function(e, data) {
                if (progressbar) {
                    progressbar.hide();
                }
                if ($.type(options.success) == 'function') {
                    options.success(data);
                } else {
                    console.error('success is not function.');
                }
            })
            .on('fileuploadfail', function(e, data) {
                if ($.type(options.error) == 'function') {
                    options.error(data);
                } else {
                    console.error('error is not function.');
                }
            });

        // 重新设置上传地址
        obj.setUrl = function(url) {
            $('#' + options.id)
                .next()
                .children('input.textbox-value')
                .fileupload('option', 'url', url);
        }

        obj.submit = function(callback) {
            if (!hasError && filedata) {
                if ($.type(callback) == 'function') {
                    callback();
                }
                filedata.submit();
            }
            // del by bianl 2015-01-22 上传提交后，保留filedata数据
            // filedata = undefined;
        }

        return obj;
    }


    /* easyui 加载效果
     * @param msg 提示文字 不传值默认为(正在处理，请稍候。。。)
     */
    function ajaxLoading(msg) {
        var content = msg || '正在处理，请稍候。。。';
        $("<div id=\"datagrid-mask-cpos\" class=\"datagrid-mask\"></div>")
            .css({
                "display": "block",
                "width": "100%",
                "height": $(window).height(),
                "z-index": 999999
            })
            .appendTo("body");

        $("<div id=\"datagrid-mask-msg-cpos\" class=\"datagrid-mask-msg\"></div>")
            .html(content)
            .appendTo("body")
            .css({
                "display": "block",
                "left": ($(document.body).outerWidth(true) - 190) / 2,
                "top":($(window).height() - 45) / 2,
                "z-index": 999999
            });
    }

    /** easyui 取消加载效果
     */
    function ajaxLoadEnd(){
        $("#datagrid-mask-cpos").remove();
        $("#datagrid-mask-msg-cpos").remove();
    }

    /* 校验元素是否为空，为空将光标定位到此元素
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    function checkNull( eleVal, labelMc, eleId ){
        if (eleVal=="") {
            $.messager.alert('提示', labelMc + '不可为空，请输入','error', function(){
                $("#" + eleId).next().children().focus();
            });
            return false;
        }
        return true;
    }

    /* 校验不可为中文
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    function checkValZw( eleVal, labelMc, eleId ){
        if (/[^\x00-\xff]/g.test(eleVal)) {
            $.messager.alert('提示',labelMc + '不可为中文，请重新输入','error', function(){
                $("#"+eleId).next().children().focus();
            });
            return false;
        }
        return true;
    }

    /* 校验只可为数字
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    function checkInt( eleVal, labelMc, eleId ){
        if (!/^[0-9]*$/.test(eleVal)) {
            $.messager.alert('提示', labelMc + '只可为数字，请重新输入','error', function(){
                $("#" + eleId).next().children().focus();
            });
            return false;
        }
        return true;
    }

    /* 校验10位日期格式和范围合法性
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    function checkDate10(eleVal, labelMc, eleId) {
        if (!/^\d{4}\-\d{2}\-\d{2}$/.test(eleVal)) {
            $.messager.alert('提示', labelMc + '格式不符，正确格式为[yyyy-mm-dd]', 'error', function(){
                $("#" + eleId).next().children().focus();
            });
            return false;
        }
        if (new Date(eleVal).getDate() != eleVal.split("-")[2]) {
            $.messager.alert('提示', labelMc + '范围错误，请重新输入', 'error', function(){
                $("#" + eleId).next().children().focus();
            });
            return false;
        }
        return true;
    }

    /* 得到easyui插件名称
     * @param $ele easyui表单控件jQuery对象 如：$('#name')
     * @returns String 如textbox,combobox
     */
    function getEasyuiPluginName( $ele ) {
        var eleCls = $ele.attr('class');
        var eleClass = eleCls ? eleCls.split(' ') : [];
        var easyui_str = 'easyui-';
        var sliceLen = eleClass.length ? easyui_str.length : 0;
        return $(eleClass).map(function(i, cls) {
            return cls.indexOf(easyui_str) == 0 ? cls : '';
        }).get().join('').slice(sliceLen);
    }

    /* 得到form表单内控件tabindex的起始值
     * @param formDataIndex form表单的属性[data-index]的值
     * @returns Number 如form[data-index="1"]的tabindex起始值是101
     */
    function getTabIndexByForm($oneform) {
        return $oneform.data('index')*1*100 + 1;
    }

    /* 动态获取所有匹配的元素 - 过滤form表单中的元素
     * 支持easyui-控件和原生控件两种形式
     * 包括下面的元素
     *  class包含 textbox-text 的 input 元素
     *  class包含 onoffswitch-checkbox 的 input[type=checkbox] 元素
     *  class包含 textbox-text 的 textarea 元素
     *  class包含 easyui-linkbutton 的 button 元素
     * @param oneform 表单(jQuery类型对象)
     * @returns 过滤后的表单
     */
    function getAllelements(oneform) {
        return oneform
            .find(
            'input.textbox-text,'+
            'a.onoffswitch,'+
            'textarea.textbox-text,'+
            'button.easyui-linkbutton'
        )
            // mod by bianl 2015-02-02
            // 过滤掉被禁用的
            .filter(':not(:disabled)')
            // 过滤掉隐藏的
            .filter(':not(:hidden)');
    }

    /* 创建tab排序
     * @param oneform 一个form的jQuery对象
     * @returns undefind
     */
    function createTabSort(oneform) {

        var $oneform = oneform;

        // tabindex 排序 第一个form从101开始，第二个form从201开始
        var tabindex = getTabIndexByForm($oneform);

        var allelements = getAllelements($oneform);

        //console.log(allelements)

        // 结束后，遇到disabled的跳过
        var focusNextOneElements = function(index) {
            var allelements = getAllelements($oneform);
            // 当元素禁用时 跳过焦点
            if (allelements.eq(index).prop('disabled')) {
                arguments.callee(index+1);
                // 当元素只读时 跳过焦点
            } else {
                allelements.eq(index).focus();
            }
        }

        var allelementsFocus = function(e) {
            var currentTarget = $(e.currentTarget);
            var currentEle = currentTarget.parent().prev();
            // 监听所有form表单域，如果是combobox，则打开下拉面板
            if (currentEle.hasClass('easyui-combobox')) {
                currentEle.combobox('showPanel');
                // 基于bug #1568 combobox高度设定
                // add by bianl 2015-01-22
                currentEle
                    .data()
                    .combo
                    .panel
                    .css({
                        'height': 'auto',
                        'max-height': '200px'
                    });
            }
        }

        var easyuiLinkbuttonKeydown = function(e) {
            if (e.type == 'keydown') {
                // 如果不是按下enter键
                if (e.which != 13) {
                    // 如果按下的是tab键
                    if (e.which == 9) {
                        return true;
                    }
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }
            }
        }

        var easyuiNoLinkbuttonBlur = function(e) {
            var currentTarget = $(e.currentTarget);
            var currentEle = currentTarget.parent().prev();
            var plugnName = getEasyuiPluginName( currentEle );
            var trimAfterValue = $.trim(currentTarget.val());

            if (currentEle[plugnName] && plugnName != 'combobox') {
                currentEle[plugnName]('setValue', trimAfterValue);
            }
        }

        var allelementsEndKeydown = function(e) {
            if (e.type == 'keydown') {
                // 如果不是按下enter键
                if (e.which != 13) {
                    // 如果按下的是tab键
                    if (e.which == 9) {
                        focusNextOneElements(0);
                    }
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }
            }
        }

        var allelementsFileboxKeydown = function(e) {
            var currentTarget = $(e.currentTarget);
            // console.log(e.which)
            if (e.type == 'keydown') {
                // 如果不是按下enter键
                if (e.which == 13 || e.which == 32) {
                    currentTarget.find('label').click();
                    // console.log(currentTarget.find('input').prop('checked'));
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                } else if (e.which == 9) {
                    // 如果按下的是tab键
                    return true;
                } else {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }
            }
        }


        // 为过滤后的easyui控件，添加tabindex属性
        //console.log(

        allelements
            .each(function(i, oneelement) {
                // 如果是filebox，则让按钮得到tabindex属性
                // console.log($(oneelement))
                if ($(oneelement).parent().hasClass('filebox')) {
                    // 针对filebox
                    $(oneelement).parent().children('.textbox-button').attr('tabindex', tabindex++);
                } else if($(oneelement).hasClass('onoffswitch')) {
                    // 针对onoffswitch处理
                    $(oneelement)
                        // .parent() mod by bianl 2015-02-02
                        .attr('tabindex', tabindex++)
                        .off('keydown', allelementsFileboxKeydown)
                        .on('keydown', allelementsFileboxKeydown);
                } else {
                    $(oneelement).attr('tabindex', tabindex++);
                }
            })
            // 监听获得焦点事件
            .off('focus', allelementsFocus)
            .on('focus', allelementsFocus)
            // 屏蔽linkbutton上的除enter键和tab以外的其他键
            .filter('.easyui-linkbutton')
            .off('keydown', easyuiLinkbuttonKeydown)
            .on('keydown', easyuiLinkbuttonKeydown)
            .end()
            // 过滤linkbutton
            // 失去焦点
            // 基于bug #1533 textbox未进行trim处理
            .filter(':not(.easyui-linkbutton)')
            .off('blur', easyuiNoLinkbuttonBlur)
            .on('blur', easyuiNoLinkbuttonBlur)
            .end()
            // 最后一个控件的按tab键后，第一个控件获得焦点
            .eq(-1)
            .off('keydown', allelementsEndKeydown)
            .on('keydown', allelementsEndKeydown)
            .end();

        //);

    }
    /**
     * 版本提交
     **/
    function bbtj(lx,bbsftj,id,gridid){
        url = "/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_index";
        // 判断有无内容需要提交
        if(bbsftj==1 || bbsftj=='1'){
            $.messager.alert('警告', '本地内容未修改，无法提交。', 'warning');
        }else{
            // 获取版本提交的iframe
            var bbtjIfram = document.all("bbtjIfram");
            window.bbtjIfram.location.href = url+"?lx="+lx+"&gridid="+gridid+ "&id=" + id;
            newWindow($("#bbtj_window"), '版本提交', 450, 300);
        }
    }
    /**
     * 版本提交
     **/
    function bbhy(lx,bbsftj,id,gridid,bbh){
        url = "/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbhy_index";
        if (bbsftj==1 || bbsftj=='1') {
            $.messager.alert('警告', '本地内容未修改，无法还原', 'warning');
            return;
        } else if(bbh == 0 || bbh == '0') {
            $.messager.alert('警告', '未提交版本，无法还原', 'warning');
            return;
        } else {
            window.bbhyIfram.location.href= url+"?lx="+lx+"&gridid="+gridid+ "&id=" + id;
            newWindow($("#bbhy_window"), '版本还原', 400, 230);
        }
    }
    /* 校验编码是否符合规则：只能输入英文字母、半角下数字、英文下划线，必须以字母开头
     * 提示信息：xxx只能输入英文字母、半角下数字、英文下划线，必须以字母开头，请重新输入
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    //$(selector).find(":contains('"+lable+"：'), :contains('"+lable+":')").last().nextAll().find(".textbox-text").first().select();
    function checkBm ( eleVal, labelMc, eleId ){
        // 正则校验
        var mode =  /^[a-zA-Z][\w]*$/;
        var msg= "只能输入字母、数字、下划线，且必须以字母开头，请重新输入";
        if (mode.test(eleVal) == false) {
            $.messager.alert('错误', labelMc + msg,'error', function(){
                $("#" + eleId).next().children().select();
            });
            return false;
        }
        return true;
    }
    /* 校验名称是否符合规则：只能输入汉字、英文字母、半角下数字、英文下划线
     * 提示信息：xxx只能输入汉字、字母、数字、下划线，请重新输入
     * @param eleVal 元素值
     * @param labelMc 元素标签名称
     * @param eleId  校验元素id
     */
    function checkMc ( eleVal, labelMc, eleId ){
        // 正则校验
        var mode =  /^[\w\u4e00-\u9fa5]+$/;
        var msg= "只能输入汉字、字母、数字、下划线，请重新输入";
        if (mode.test(eleVal) == false) {
            $.messager.alert('错误', labelMc + msg,'error', function(){
                $("#" + eleId).next().children().select();
            });
            return false;
        }
        return true;
    }


    return {
        formToJson: formToJson,
        setRowToWin: setRowToWin,
        errorAjax: errorAjax,
        afterAjax: afterAjax,
        checkSelected: checkSelected,
        checkSelections: checkSelections,
        showMsg: showMsg,
        getByteLen: getByteLen,
        newWindow: newWindow,
        newTab: newTab,
        fileUpload: fileUpload,
        ajaxLoading: ajaxLoading,
        ajaxLoadEnd: ajaxLoadEnd,
        checkNull: checkNull,
        checkValZw: checkValZw,
        checkInt: checkInt,
        checkDate10: checkDate10,
        bbtj: bbtj,
        bbhy: bbhy,
        checkBm: checkBm,
        checkMc: checkMc
    }

});