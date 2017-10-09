$(function() {

    /**
     * add by bianl 2015-02-03 基于bug #1608
     * menu的默认onShow函数，当menu展开时调用，所有menu都调用
     * 依赖css/style.css .menu-size
     * 注意：勿重写
     */
    $.extend($.fn.menu.defaults, {
        onShow: function() {
            $(this).addClass('menu-size');
        }
    });

    // 为tabs组件扩展一个方法名为'header'
    $.extend($.fn.tabs.methods, {
        header: function(jq) {
            return $.data(jq[0], "tabs").tabs[0].closest('div.tabs-panels').prev();
        }
    });

    // 为datagrid组件扩展一个方法名为'getBody'
    $.extend($.fn.datagrid.methods, {
        getBody: function(jq) {
            return jq
                .datagrid('getPanel')
                .find('.datagrid-view2>.datagrid-body');
        }
    });

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
    };

    /**
     * 针对textbox - 使用easyui-tooltip
     * 位置：right默认
     * 内容从data-msg中获取 换行符\n 标签替换规则[x][/x] 目前支持cb,cg,cr,样式在css/style.css中
     * 拥有data-plugin="ttip"的input会自动调用ttip
     * 内容在data-ttip-msg中
     * 显示事件data-ttip-event中，h(hover), f(focus)
     * @param options
     */
    $.fn.ttip = function(options) {

        options || (options = {});


        this.each(function(i, ele) {
            var $ele = $(ele);

            // 属性data-ttip-msg
            var msg = $ele.data('ttipMsg');
            var ttipEvent = $ele.data('ttipEvent');
            var ttipPosition = $ele.data('ttipPosition') || 'right';

            // 如果options.msg存在，则使用
            msg = options.msg || msg;
            ttipEvent = options.ttipEvent || ttipEvent;
            ttipPosition = options.ttipPosition || ttipPosition;

            switch (ttipEvent) {
                case 'h':
                case 'hover':
                    ttipEvent = ["mouseenter", "mouseleave"];
                    break;
                case 'f':
                case 'focus':
                    ttipEvent = ["focus", "blur"];
                    break;
                default:
                    ttipEvent = ["focus", "blur"];
                    break;
            }

            var cb = /\[cb\](.+?)\[\/cb\]/;
            var cg = /\[cg\](.+?)\[\/cg\]/;
            var cr = /\[cr\](.+?)\[\/cr\]/;

            // [x][/x]标签替换规则
            // [cb][/cb]
            // [cg][/cg]
            // [cr][/cr]
            // 以后还可以扩展规则
            msg = msg
                .replace(cb, '<span class="cb">$1</span>')
                .replace(cg, '<span class="cg">$1</span>')
                .replace(cr, '<span class="cr">$1</span>');

            // 支持\n换行，注意，不要把\n写在[x][/x]内
            msg = $.map(msg.split("\\n"), function(str) {
                return '<p>' + str + '</p>';
            }).join('');

            // 外部包裹div，设置css样式ttip
            msg = $('<div>')
                .addClass('ttip')
                .append(msg);

            $ele.hasClass('easyui-textbox') ?
                ($ele = $ele
                    .next()
                    .children('input.textbox-text')) :
                $ele;
            $ele
                .tooltip({
                    position: ttipPosition,
                    showEvent: ttipEvent[0],
                    hideEvent: ttipEvent[1],
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
        // del by bianl 页面加载后调用一次
        //$oneform.tabSort();

    });

    // ttip
    $('input[data-toggle="ttip"]').ttip();

    /**
     * add by houpp 2015-09-06
     * 扩展树表格级联勾选方法：
     * @param {Object} container
     * @param {Object} options
     * @return {TypeName}
     */
    $.extend($.fn.treegrid.methods,{
        /**
         * 级联选择
         * @param {Object} target
         * @param {Object} param
         *      param包括两个参数:
         *          id:勾选的节点ID
         *          deepCascade:是否深度级联
         * @return {TypeName}
         */
        cascadeCheck : function(target,param){
            var opts = $.data(target[0], "treegrid").options;
            if(opts.singleSelect)
                return;
            var idField = opts.idField;//这里的idField其实就是API里方法的id参数
            var status = false;//用来标记当前节点的状态，true:勾选，false:未勾选
            var selectNodes = $(target).treegrid('getSelections');//获取当前选中项
            for(var i=0;i<selectNodes.length;i++){
                if(selectNodes[i][idField]==param.id)
                    status = true;
            }
            //级联选择父节点
            selectParent(target[0],param.id,idField,status);
            selectChildren(target[0],param.id,idField,param.deepCascade,status);
            /**
             * 级联选择父节点
             * @param {Object} target
             * @param {Object} id 节点ID
             * @param {Object} status 节点状态，true:勾选，false:未勾选
             * @return {TypeName}
             */
            function selectParent(target,id,idField,status){
                var parent = $(target).treegrid('getParent',id);
                if(parent){
                    var parentId = parent[idField];
                    if(status)
                        $(target).treegrid('select',parentId);
                    else
                        $(target).treegrid('unselect',parentId);
                    selectParent(target,parentId,idField,status);
                }
            }
            /**
             * 级联选择子节点
             * @param {Object} target
             * @param {Object} id 节点ID
             * @param {Object} deepCascade 是否深度级联
             * @param {Object} status 节点状态，true:勾选，false:未勾选
             * @return {TypeName}
             */
            function selectChildren(target,id,idField,deepCascade,status){
                //深度级联时先展开节点
                if(!status&&deepCascade)
                    $(target).treegrid('expand',id);
                //根据ID获取下层孩子节点
                var children = $(target).treegrid('getChildren',id);
                for(var i=0;i<children.length;i++){
                    var childId = children[i][idField];
                    if(status)
                        $(target).treegrid('select',childId);
                    else
                        $(target).treegrid('unselect',childId);
                    selectChildren(target,childId,idField,deepCascade,status);//递归选择子节点
                }
            }
        }
    });

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
                    o[this.name] = [o[this.name]];
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
function setRowToWin(win_id, data) {
        var id = ' '; //获取标签的name值 
        $('#' + win_id + ' input,select').each(function() {
            id = $(this).attr('id');
            if (id) {
                if ($(this).attr('type') == 'radio') {
                    $('#' + win_id + ' [type=radio][value=' + data.id + ']').attr('checked', 'checked');
                } else {
                    $('#' + id).textbox('setValue', data[id]);
                }
            }
        });
    }
    /**
     * ajax 状态为error时调用的方法
     * @param data
     */
function errorAjax() {
        // 取消遮罩
        ajaxLoadEnd();
        $.messager.alert('警告', '请求失败，请稍后重试', 'warning');
    }
    /**
     * 封装方法：Ajax请求成功后执行的操作，包括关闭window.刷新grid
     * data: Ajax返回的数据
     */
function afterAjax(data, gridID, windowID) {
        // 是否是在父框架内显示提示
        var parentType = arguments[3] ? arguments[3] : false;
        // 取消遮罩
        ajaxLoadEnd();
        if (typeof data == 'string') {
            data = $.parseJSON(data);
        }
        if (data.state == true) {
            //添加成功后刷新grid
            if (gridID != '' && gridID != null) {
                $('#' + gridID).datagrid('reload');
            }

            //关闭window
            if (windowID != '') {
                $('#' + windowID).window('close');
            }
            // 正常信息提示不需要使用提示框处理
            if( parentType == true ){
                parent.$.messager.alert('提示', '<p id="msgPre">'+data.msg.replace("\n", "<br/>")+'</p>', 'info');
                // 根据提示信息的长度来确定当前提示框的高度
                if ( data.msg.length >=0 && data.msg.length <= 40 ) {
                    parent.$('#msgPre').css({'height': '35px'});
                } else if ( data.msg.length > 40 && data.msg.length <= 80 ){
                    parent.$('#msgPre').css({'height': '80px'});
                } else {
                    parent.$('#msgPre').css({'height': '120px'});
                };
                parent.$('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '255px');
                var msgWin = parent.$('#msgPre').parents('.messager-window');
                msgWin.css({'width': '320px'});
                msgWin.find('.window-header').css('width', '');
                msgWin.find('.messager-body').css('width', '');
                // 去掉因提示信息过长而出现的白色区域
                msgWin.siblings('.window-shadow').css({'height':'0px'});
            }
            else{
                $.messager.alert('提示', '<p id="msgPre">'+data.msg.replace("\n", "<br/>")+'</p>', 'info');
                // 根据提示信息的长度来确定当前提示框的高度
                if ( data.msg.length >=0 && data.msg.length <= 40 ) {
                    $('#msgPre').css({'height': '35px'});
                } else if ( data.msg.length > 40 && data.msg.length <= 80 ){
                    $('#msgPre').css({'height': '80px'});
                } else {
                    $('#msgPre').css({'height': '120px'});
                };
                $('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '255px');
                var msgWin = $('#msgPre').parents('.messager-window');
                msgWin.css({'width': '320px', 'left': ($(window).width()-400)*0.5});
                msgWin.find('.window-header').css('width', '');
                msgWin.find('.messager-body').css('width', '');
                // 去掉因提示信息过长而出现的白色区域
                msgWin.siblings('.window-shadow').css({'height':'0px'});
            }
        } else {
            if( parentType == true ){
                parent.$.messager.alert('错误', '<p id="msgPre">'+data.msg.replace("\n", "<br/>")+'</p>', 'error', function() {
                    //选中需要重新输入的内容
                    if (data.msg.indexOf("[") > 0) {
                        var lable = data.msg.split("[")[0];
                        var selector = windowID == "" ? "html" : "#" + windowID;
                        parent.$(selector).find(":contains('" + lable + "：'), :contains('" + lable + ":')").last().nextAll().find(".textbox-text").first().select();
                    }
                });
                // 根据提示信息的长度来确定当前提示框的高度
                if ( data.msg.length >=0 && data.msg.length <= 40 ) {
                    parent.$('#msgPre').css({'height': '40px'});
                } else if ( data.msg.length > 40 && data.msg.length <= 80 ){
                    parent.$('#msgPre').css({'height': '80px'});
                } else {
                    parent.$('#msgPre').css({'height': '120px'});
                };
                parent.$('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '315px');
                var msgWin = parent.$('#msgPre').parents('.messager-window');
                msgWin.css({'width': '380px'});
                msgWin.find('.window-header').css('width', '');
                msgWin.find('.messager-body').css('width', '');
                // 去掉因提示信息过长而出现的白色区域
                msgWin.siblings('.window-shadow').css({'height':'0px'});
                return true;
            }else{
                $.messager.alert('错误', '<p id="msgPre">'+data.msg.replace("\n", "<br/>")+'</p>', 'error', function() {
                    //选中需要重新输入的内容
                    if (data.msg.indexOf("[") > 0) {
                        var lable = data.msg.split("[")[0];
                        var selector = windowID == "" ? "html" : "#" + windowID;
                        $(selector).find(":contains('" + lable + "：'), :contains('" + lable + ":')").last().nextAll().find(".textbox-text").first().select();
                    }
                });
                // 根据提示信息的长度来确定当前提示框的高度
                if ( data.msg.length >=0 && data.msg.length <= 40 ) {
                    $('#msgPre').css({'height': '40px'});
                } else if ( data.msg.length > 40 && data.msg.length <= 80 ){
                    $('#msgPre').css({'height': '80px'});
                } else {
                    $('#msgPre').css({'height': '120px'});
                };
                $('#msgPre').css({'overflow': 'auto', 'margin-bottom': '0'}).parent().css('width', '315px');
                var msgWin = $('#msgPre').parents('.messager-window');
                msgWin.css({'width': '380px', 'left': ($(window).width()-400)*0.5});
                msgWin.find('.window-header').css('width', '');
                msgWin.find('.messager-body').css('width', '');
                // 去掉因提示信息过长而出现的白色区域
                msgWin.siblings('.window-shadow').css({'height':'0px'});
            }
            
        }
    }
    /**
     * 警告必须选择一项
     * @returns
     */
function checkSelected(id) {
        var rows = $('#' + id).datagrid('getSelections');
        if (rows == '') {
            $.messager.alert('错误', '至少选择一项', 'error');
            return false;
        }
        return true;
    }
    /**
     * 警告不可选择多行
     */
function checkSelections(id) {
        var rows = $('#' + id).datagrid('getSelections');
        if (rows.length > 1) {
            $.messager.alert('警告', '只能选择一项', 'error');
            return false;
        }
        return true;
    }
    /**
     * 显示提示信息
     */
function showMsg(data, timeout) {
    $.messager.show({
        title: '提示',
        msg: data.msg,
        timeout: timeout,
        showType: 'slide'
    });
}

/**
 * 取得字段长度
 *   1个汉字对应oracle数据库的字段长度为3
 * @param val
 * @returns 对应oracle数据库的字段长度
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
function newWindow(beanWindow, title, width, height, left, top) {
    // 清空window中的值
    var ck_state = new Array();
    $(".onoffswitch-checkbox").each(function() {
        ck_state.push(this.checked);
    });
    beanWindow.form('clear');
    $(".onoffswitch-checkbox").each(function(i) {
        this.checked = ck_state[i];
    });
    // 创建window
    var top = top == null ? ($(window).height() - height) * 0.35 : top;
    var left = left == null ? ($(window).width() - width) * 0.5 : left;
    beanWindow.window({
        title: title,
        width: width,
        height: height,
        top: top < 0 ? 0 : top,
        left: left < 0 ? 0 : left,
        closed: false,
        cache: false,
        modal: true,
        onBeforeOpen: function() {
            beanWindow.find("form").form("disableValidation");
        },
        // 在关闭window之后，干点啥 mod by
        onBeforeClose: function() {
            // 如果iframe是创建出来的，在这里，建议释放iframe内存。
        }
    });
    // 新增弹框时光标定位第一个输入框
    window.setTimeout(function() {
        var focus = true;
        $(beanWindow.find("span>.textbox-text:not(:disabled):not([readonly])")).each(function() {
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

    var exists = false;
    var which = 0;
    $($main.tabs('tabs')).each(function(index, element) {
        if ($(element).find('iframe').attr('src') == href) {
            exists = true;
            which = index;
            return false;
        }
    });
    if (exists) {
        $main.tabs('select', which);
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
        fileType: undefined, ///(\.|\/)(gif|jpe?g|png)$/i
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
    if (progressbar = (options.progressbar && $('#' + options.progressbar))) {
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
            function() {
                $(this).css('border-color', '#ccc');
            },
            function() {
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
                        fType.test(file.name))) {
                    uploadErrors.push('文件类型不支持');
                }
            }

            // check file max size
            if (fMSize) {
                // 变成字节 要求最大值
                fMSize = fMSize * 1000000;
                // 上传的文件的具体大小
                filesize = data.files[0]['size']
                    // 比较大小
                if (filesize > fMSize) {
                    uploadErrors.push('文档大小超过最大限制（200M），系统不允许上传，请重新选择');
                }

                if (filesize == 0) {
                    uploadErrors.push('文档为空文件，不允许上传，请重新选择');
                }
            }


            if (uploadErrors.length > 0) {
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
            "top": ($(window).height() - 45) / 2,
            "z-index": 999999,
            "font-size": "11px"
        });
}

/** easyui 取消加载效果
 */
function ajaxLoadEnd() {
    $("#datagrid-mask-cpos").remove();
    $("#datagrid-mask-msg-cpos").remove();
}

/* 校验元素是否为空，为空将光标定位到此元素
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
function checkNull(eleVal, labelMc, eleId) {
    if (eleVal == "") {
        $.messager.alert('错误', labelMc + '不可为空，请输入', 'error', function() {
            $("#" + eleId).next().children().focus();
        });
        return false;
    }
    return true;
}

/* 校验元素是否为空，为空将光标定位到此元素(下拉列表)
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
function checkNull2(eleVal, labelMc, eleId) {
    if (eleVal == "") {
        $.messager.alert('错误', labelMc + '不可为空，请选择', 'error', function() {
            $("#" + eleId).next().children().focus();
        });
        return false;
    }
    return true;
}

/* 校验元素选择是否在系统中存在，不存在则将光标定位到此元素(下拉列表)
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
function checkNull3(eleVal, labelMc, eleId) {
    if (eleVal == null ) {
        $.messager.alert('错误', labelMc + '选择有误，请重新选择', 'error', function() {
            $("#" + eleId).next().children().focus();
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
function checkInt(eleVal, labelMc, eleId) {
    if (!/^[0-9]*$/.test(eleVal)) {
        $.messager.alert('错误', labelMc + '只能输入数字，请重新输入', 'error', function() {
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
        $.messager.alert('错误', labelMc + '格式不符，正确格式为[yyyy-mm-dd]', 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    if (new Date(eleVal).getDate() != eleVal.split("-")[2]) {
        $.messager.alert('错误', labelMc + '范围错误，请重新输入', 'error', function() {
            $("#" + eleId).next().children().select();
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
function checkValZw(eleVal, labelMc, eleId) {
    if (/[^\x00-\xff]/g.test(eleVal)) {
        $.messager.alert('提示', labelMc + '不可为中文，请重新输入', 'error', function() {
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
function getEasyuiPluginName($ele) {
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
    return $oneform.data('index') * 1 * 100 + 1;
}

/* 动态获取所有匹配的元素 - 过滤form表单中的元素
 * 支持easyui-控件和原生控件两种形式
 * 包括下面的元素
 *  class包含 textbox-text 的 input 元素
 *  class包含 onoffswitch-checkbox 的 input[type=checkbox] 元素
 *  class包含 .filebox>a.textbox-button的<a>元素
 *  class包含 原生的 textarea 元素
 *  class包含 easyui-linkbutton 的 button 元素
 * @param oneform 表单(jQuery类型对象)
 * @returns 过滤后的表单
 */
function getAllelements(oneform) {
    return oneform
        .find(
            'input.textbox-text,' + // easyui-textbox
            'a.onoffswitch,' + // 开关控件<a>
            '.filebox>a.textbox-button,' + // easyui-filebox<a>
            'textarea,' + // 普通 <textarea>
            'button.easyui-linkbutton' // easyui-linkbutton <button>
        )
        // mod by bianl 2015-02-02
        // 过滤掉被禁用的
        .filter(':not(:disabled)')
        // 过滤掉隐藏的
        .filter(':not(:hidden)');
}

/* 创建tab排序
 * 增加命名空间 tab
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
            arguments.callee(index + 1);
            // 当元素只读时 跳过焦点
        } else {
            allelements.eq(index).focus();
        }
    };

    var allelementsFocus = function(e) {
        var currentTarget = $(e.currentTarget);
        var currentEle = currentTarget.parent().prev();
        // 监听所有form表单域，如果是combobox，则打开下拉面板
        if (currentEle.hasClass('easyui-combobox')) {
            // 根据需要修改为，combobox获得焦点，不展开
            //currentEle.combobox('showPanel');
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
    };

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
    };

    var easyuiNoLinkbuttonBlur = function(e) {
        var target = e.currentTarget;
        var nodeName = null;
        var currentTarget = null;
        if (nodeName = target.nodeName,
            nodeName == 'INPUT' ||
            nodeName == 'TEXTAREA'
        ) {
            currentTarget = $(target);
            var currentEle = currentTarget.parent().prev();
            var plugnName = getEasyuiPluginName(currentEle);
            var hasComboClass = currentTarget.parent().hasClass('combo');
            var trimAfterValue = $.trim(currentTarget.val());
            // console.log(hasComboClass)

            // if (currentEle[plugnName] && plugnName != 'combobox') {
            //     currentEle[plugnName]('setValue', trimAfterValue);
            // }
            // 此处判断非combo类型控件
            // 2015-05-20
            if (currentEle[plugnName] && !hasComboClass) {
                currentEle[plugnName]('setValue', trimAfterValue);
            }
        }
    };

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
    };

    var allelementsFileboxKeydown = function(e) {
        var currentTarget = $(e.currentTarget);
        // console.log(e.which)
        if (e.type == 'keydown') {
            // 如果不是按下enter键
            if (e.which == 13 || e.which == 32) {
                currentTarget.find('label').click();
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
    };

    var allelementsTextboxKeypress = function(e) {
        var target = e.currentTarget;
        var currentTarget = $(target);
        var currentEle = currentTarget.parent().prev();
        var value = currentTarget.val();
        currentEle.textbox('setValue', currentEle.textbox('getText'));
        // 如果按键叫enter且节点是input则去掉字符串起始和结尾的空格
        if (e.which === 13 && target.nodeName == 'INPUT') {
            currentEle.textbox('setValue', $.trim(currentEle.textbox('getText')));
        }
    };


    // 为过滤后的easyui控件，添加tabindex属性
    //console.log(

    allelements
        .each(function(i, oneelement) {
            if ($(oneelement).hasClass('onoffswitch')) {
                // 针对onoffswitch处理
                $(oneelement)
                    // .parent() mod by bianl 2015-02-02
                    .attr('tabindex', tabindex++)
                    .off('keydown.tab', allelementsFileboxKeydown)
                    .on('keydown.tab', allelementsFileboxKeydown);
            } else if ($(oneelement).parent().hasClass('textbox') && !$(oneelement).parent().hasClass('combo')) {
                // add by bianl 2015-02-05 easyui-textbox任何输入即时change
                // 非combo类型 2015-05-20
                $(oneelement)
                    .attr('tabindex', tabindex++)
                    .off('keypress.tab', allelementsTextboxKeypress)
                    .on('keypress.tab', allelementsTextboxKeypress);
            } else {
                $(oneelement).attr('tabindex', tabindex++);
            }
        })
        // 监听获得焦点事件
        .off('focus.tab', allelementsFocus)
        .on('focus.tab', allelementsFocus)
        // 屏蔽linkbutton上的除enter键和tab以外的其他键
        .filter('.easyui-linkbutton')
        .off('keydown.tab', easyuiLinkbuttonKeydown)
        .on('keydown.tab', easyuiLinkbuttonKeydown)
        .end()
        // 过滤linkbutton
        // 失去焦点
        // 基于bug #1533 textbox未进行trim处理
        .filter(':not(.easyui-linkbutton)')
        .off('blur.tab', easyuiNoLinkbuttonBlur)
        .on('blur.tab', easyuiNoLinkbuttonBlur)
        .end()
        // 最后一个控件的按tab键后，第一个控件获得焦点
        .eq(-1)
        .off('keydown.tab', allelementsEndKeydown)
        .on('keydown.tab', allelementsEndKeydown)
        .end();

    //);

}

/**
 * 版本提交
 **/
function bbtj(lx, bbsftj, id, gridid) {
    var event = event || window.event;
    event.stopPropagation();
    url = "/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/last_bbxx_view";
    // 判断有无内容需要提交
    if (bbsftj == 1 || bbsftj == '1') {
        $.messager.alert('警告', '本地内容未修改，无法提交。', 'warning');
    } else {
        $('#bbtj_window iframe')[0].src = url + "?lx=" + lx + "&gridid=" + gridid + "&id=" + id;
        newWindow($("#bbtj_window"), '版本提交', 450, 350);
    }
}

/**
 * 版本还原
 **/
function bbhy(lx, bbsftj, id, gridid, bbh) {
    var event = event || window.event;
    event.stopPropagation();
    url = "/oa/kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj_view/bbhy_index_view";
    if (bbsftj == 1 || bbsftj == '1') {
        $.messager.alert('警告', '本地内容未修改，无法还原', 'warning');
        return;
    } else if (bbh == 0 || bbh == '0') {
        $.messager.alert('警告', '未提交版本，无法还原', 'warning');
        return;
    } else {
        window.bbhyIfram.location.href = url + "?lx=" + lx + "&gridid=" + gridid + "&id=" + id;
        newWindow($("#bbhy_window"), '版本还原', 440, 300);
    }
}

/* 校验编码是否符合规则：只能输入英文字母、半角下数字、英文下划线，必须以字母开头
 * 提示信息：xxx只能输入英文字母、半角下数字、英文下划线，必须以字母开头，请重新输入
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
//$(selector).find(":contains('"+lable+"：'), :contains('"+lable+":')").last().nextAll().find(".textbox-text").first().select();
function checkBm(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^[a-zA-Z][\w]*$/;
    var msg = "只能输入字母、数字、下划线，且必须以字母开头，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}
/* 校验编码是否符合规则：只能输入英文字母、半角下数字、英文下划线
 * 提示信息：xxx只能输入英文字母、半角下数字、英文下划线， 请重新输入
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
//$(selector).find(":contains('"+lable+"：'), :contains('"+lable+":')").last().nextAll().find(".textbox-text").first().select();
function checkBm2(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^[\w]+$/;
    var msg = "只能输入字母、数字、下划线，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}

/* 校验编码是否符合规则：只能输入英文字母、半角下数字、英文下划线、英文横线
 * 提示信息：xxx只能输入英文字母、半角下数字、英文下划线、英文横线， 请重新输入
 * @param eleVal 元素值
 * @param labelMc 元素标签名称
 * @param eleId  校验元素id
 */
//$(selector).find(":contains('"+lable+"：'), :contains('"+lable+":')").last().nextAll().find(".textbox-text").first().select();
function checkBm3(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^[\w-]+$/;
    var msg = "只能输入字母、数字、下划线、横线，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
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
function checkMc(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^[\w\u4e00-\u9fa5]+$/;
    var msg = "只能输入汉字、字母、数字、下划线，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}

/**
 * 两个datagrid的对比
 * @datagrid1 jQery对象
 * @datagrid2 jQery对象
 */
function datagridCompare(datagrid1, datagrid2) {
    datagrid1.datagrid('getBody').scroll(function(e){
        datagrid2
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
    datagrid2.datagrid('getBody').scroll(function(e){
        datagrid1
            .datagrid('getBody')
            .scrollTop($(e.currentTarget).scrollTop());
    });
}

/**
* 函数说明：自动发起配置翻译
* zdfqpzid: 自动发起配置元素id
* zdfqpzsmid: 自动发起配置说明元素id
* zdfqpzlabel: 自动发起配置标签
* 自动发起配置为空是否提示不可为空，为True直接返回成功，不做操作，如果非true则提示不可为空
*/
function zdfqpzFy( zdfqpzid, zdfqpzsmid, zdfqpzlabel ){
    // 自动发起配置
    var zdfqpz = $("#" + zdfqpzid).textbox("getValue");
    // 判断是否为空
    if( zdfqpzlabel == undefined )
        zdfqpzlabel = '自动发起配置'
    var ret = checkNull( zdfqpz, zdfqpzlabel, zdfqpzid );
    // 信息存在
    if( ret == true ){
        // 后台获取翻译信息
        $.ajax({
            type: 'POST',
            dataType: 'text',
            url: "/oa/kf_ywgl/kf_ywgl_003/kf_ywgl_003_view/zdfqpzfy_view",
            data: { 'zdfqpz': zdfqpz },
            success: function(data){
                // 反馈信息
                data = $.parseJSON( data );
                if( data.state == true ){
                    // 将说明信息赋值到输入框内
                    $("#" + zdfqpzsmid).textbox('setValue', data.zdfqpzsm);
                    return true;
                }else{
                    $("#" + zdfqpzsmid).textbox('setValue', '');
                    afterAjax(data, '', '');
                    return false;
                }
                // 取消遮罩
                ajaxLoadEnd();
            },
            error: function(){
                errorAjax();
                // 取消遮罩
                ajaxLoadEnd();
                return false;
            }
        });
    }else{
        // 取消遮罩
        ajaxLoadEnd();
        return false;
    }
}

/*
* 校验手机号码是否符合要求
* @param eleVal 元素值
* @param labelMc 元素标签名称
* @param eleId  校验元素id
* */
function checkMobile(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^(13|15|18|17)\d{9}$/;
    var msg = "格式错误，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}

/*
* 校验电话号码是否符合要求
* @param eleVal 元素值
* @param labelMc 元素标签名称
* @param eleId  校验元素id
* */
function checkPhone(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^((\(\d{2,3}\))|(\d{3}\-))?(\(0\d{2,3}\)|0\d{2,3}-)?[1-9]\d{6,7}(\-\d{1,4})?$/;
    var msg = "格式错误，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}

/*
* 校验电子邮件格式是否正确
* @param eleVal 元素值
* @param labelMc 元素标签名称
* @param eleId  校验元素id
* */
function checkEmail(eleVal, labelMc, eleId) {
    // 正则校验
    var mode = /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/;
    var msg = "格式错误，请重新输入";
    if (mode.test(eleVal) == false) {
        $.messager.alert('错误', labelMc + msg, 'error', function() {
            $("#" + eleId).next().children().select();
        });
        return false;
    }
    return true;
}

/*
 * grid++的报表打印方法
 * json_data:生成报表的参数
 */
function grid_report(json_data){
    // 将数据转换为字符串，这样后台统一用eval就可以转换为python对象了。
    // 在浏览器中打开报表。
    window.open('/oa/grid_printer/grid_printer/print_view?data='+JSON.stringify(json_data),'','height=900,width=1000,z-look=yes');
}

var toolbar_lst=[];
/*
* add by houpp 2015-09-02
* 调用后台-获取按钮权限列表
* @param cddm:菜单代码
* @param buttonID_lst:按钮列表-非toolbar
* @param dviID：列表的div
* @flag：1 按钮-非toolbar；2 toolbar 按钮
*
* */
function get_anqxLst_gn(cddm,buttonID_lst,dviID){
     //调用后台-获取按钮权限列表
     $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/common_anqx/common_anqx_view/index_view",
                data: {
                    'menuDm': cddm
                },
                success: function(data){
                    //json串
                    data = $.parseJSON(data);
                    //拥有的按钮权限列表
                    if (data['an_lst'].length >0){
                        for(var i=0; i< data['an_lst'].length; i++) {
                            toolbar_lst[i]=data['an_lst'][i].gndm
                        }
                    }
                     //button 按钮的设置
                    if(buttonID_lst.length>0){
                        set_anqx_button(buttonID_lst,toolbar_lst)
                    }
                     //datagrid列表toolbar按钮的设置
                    get_anqxLst_toolbar(dviID,toolbar_lst)

                },
                error : function(){
                    errorAjax();
                }
     });
}

/*
* add by houpp 2015-09-02
* * 调用后台-获取按钮权限列表并加载--非toolbar中的按钮
* @param cddm:菜单代码
* @param buttonID_lst：按钮ID列表
* @toolbar_lst:功能按钮列表
*
* */
function set_anqx_button(buttonID_lst,toolbar_lst){
    if(buttonID_lst.length>0 ){
        for(var i=0; i< buttonID_lst.length; i++ ){
          if ( toolbar_lst.length>0){
            for (var j=0; j< toolbar_lst.length; j++ ){
                if(buttonID_lst[i]==toolbar_lst[j]){
                    $('#' + buttonID_lst[i]).show();
                    break;
                }else{
                    $('#' + buttonID_lst[i]).hide();
                }
            }
          }else{
              $('#' + buttonID_lst[i]).hide();
          }
        }
    }
}

/*
* add by houpp 2015-09-02
* 调用后台-获取按钮权限列表并加载--toolbar中的按钮
* @param cddm:菜单代码
* @param divID：datagrid列表所在div的ID
* @toolbar_lst:功能按钮列表
*
*
* */
function get_anqxLst_toolbar(divID,toolbar_lst){
    //菜单按钮加载--列表toolbar中的按钮
    if (divID){
        var toolbar_gn= $('#' + divID).find('.datagrid-toolbar');
        for (var i=0;i< toolbar_gn.find('table td').length; i++){
            if (toolbar_lst.length > 0){
                for (var j=0; j< toolbar_lst.length; j++){
                     if(toolbar_gn.find('a').eq(i)[0].id == toolbar_lst[j]){
                        toolbar_gn.find('a').eq(i).show();
                        toolbar_gn.find('div').eq(i).show();
                         break;
                     }else{
                        toolbar_gn.find('a').eq(i).hide();
                        toolbar_gn.find('div').eq(i).hide();
                     }
                }
            }else{
                toolbar_gn.find('a').eq(i).hide();
                toolbar_gn.find('div').eq(i).hide();
            }
        }
    }
}

/*
add by houpp 2015-09-01
* 调用后台-获取按钮权限列表并加载--toolbar中的按钮
* @param cddm:菜单代码
* @param divID：datagrid列表所在div的ID
* @toolbar_lst:功能按钮列表
* */
function get_anqxLst(cddm,divID){
     //调用后台-获取按钮权限列表
     $.ajax({
                type: 'POST',
                dataType: 'text',
                url: "/oa/common_anqx/common_anqx_view/index_view",
                data: {
                    'menuDm': cddm
                },
                success: function(data){
                    //json串
                    data = $.parseJSON(data);
                    //拥有的按钮权限列表
                    if (data['an_lst'].length >0){
                        for(var i=0; i< data['an_lst'].length; i++) {
                            toolbar_lst[i]=data['an_lst'][i].gndm
                        }
                    }
                     //菜单按钮加载--列表toolbar中的按钮
                    var toolbar_gn= $('#' + divID).find('.datagrid-toolbar');
                    for (var i=0;i< toolbar_gn.find('table td').length; i++){
                        if (toolbar_lst.length > 0){
                            for (var j=0; j< toolbar_lst.length; j++){
                                 if(toolbar_gn.find('a').eq(i)[0].id == toolbar_lst[j]){
                                    toolbar_gn.find('a').eq(i).show();
                                    toolbar_gn.find('div').eq(i).show();
                                     break;
                                 }else{
                                    toolbar_gn.find('a').eq(i).hide();
                                    toolbar_gn.find('div').eq(i).hide();
                                 }
                            }
                        }else{
                            toolbar_gn.find('a').eq(i).hide();
                            toolbar_gn.find('div').eq(i).hide();
                        }
                    }
                },
                error : function(){
                    errorAjax();
                }
     });
}
/*
*判断不一致属性
*/
function dif_field(field,row){
    // 获取改行的id对应的列有无版本内容不一致情况
    if(row.diff){
        difArray = row.diff.split(',');
        for(var i = 0; i < difArray.length; i++){
            var diffField = difArray[i];
            if(field == diffField ){
                return 'background-color:#ffee00;color:red;';
            }
        }
    }
}


/**
* 代码下载
*/
function dm_down( dgid, downtype, ywid, to_path, txid ) {
    // 下载交易id集合
    var ids = new Array();
    var downUrl = undefined;
    if( downtype != 'yw' && downtype != 'tx' ){
        //获取下载交易列表
        if (!checkSelected(dgid)) {
            return;
        }
        // 当前选中的记录
        var checkedItems = $('#' + dgid).datagrid('getChecked');
        $(checkedItems).each(function(index, item) {
            ids.push(item['id']);
        });
    }
    // 前面调用处都没有给txid赋值，所有做此处处理
    if ( txid == undefined )
        txid = ''
    // 访问url
    downUrl = "/oa/kf_ywgl/kf_ywgl_025/kf_ywgl_025_view/dm_down_view?downtype="+ downtype +"&idstr=" + ids.join(",") + "&ywid=" + ywid + '&to_path=' + to_path + '&txid=' + txid;
    // 添加遮罩
    ajaxLoading();
    // jquery down
    $.fileDownload(downUrl)
        .done(function () {
            console.log('File download a success!');
            // 取消遮罩
            ajaxLoadEnd();
        })
        .fail(function () {
            console.log('File download failed!');
            $.messager.alert('错误', '下载失败！', 'error');
            // 取消遮罩
            ajaxLoadEnd();
        });
    
}

/* 创建新的窗体(宽度自适应)
 * @param beanWindow 窗体对象
 * @param title 窗体的标题
 * @param width 窗体的宽度
 * @param height 窗体的高度
 */
function newWindow2(beanWindow, title, width, height, left, top) {
    // 清空window中的值
    var ck_state = new Array();
    $(".onoffswitch-checkbox").each(function() {
        ck_state.push(this.checked);
    });
    beanWindow.form('clear');
    $(".onoffswitch-checkbox").each(function(i) {
        this.checked = ck_state[i];
    });
    // 创建window
    var top = top == null ? ($(window).height() - height) * 0.35 : top;
    var left = left == null ? ($(window).width() - $(window).width() * 0.01 * parseInt(width)) * 0.5 : left;
    beanWindow.window({
        title: title,
        width: width + '%',
        height: height,
        top: top < 0 ? 0 : top,
        left: left < 0 ? 0 : left,
        closed: false,
        cache: false,
        modal: true,
        onBeforeOpen: function() {
            beanWindow.find("form").form("disableValidation");
        },
        // 在关闭window之后，干点啥 mod by
        onBeforeClose: function() {
            // 如果iframe是创建出来的，在这里，建议释放iframe内存。
        }
    });
    // 新增弹框时光标定位第一个输入框
    window.setTimeout(function() {
        var focus = true;
        $(beanWindow.find("span>.textbox-text:not(:disabled):not([readonly])")).each(function() {
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