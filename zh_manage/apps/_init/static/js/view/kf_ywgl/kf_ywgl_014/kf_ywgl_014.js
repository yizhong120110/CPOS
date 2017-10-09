// 批次的UUID
var uuid = new UUID().toString();
// 获取的返回信息
var res_csjg = [];
// 停止标志
stop_mark = false;
// 测试案例执行的个数
csal_num = 0;
// 标识当前运行的最后一个测试案例的id
last_csalid = '';
// 标识当前已有错误提示，不在进行下一次提示，目的是为了避免出现多个弹出框
alertMark = false;
$(document).ready(function() {
    window.parent.$('#bean_window').window({
        onBeforeClose:function(){ 
            closeWin();
        }
    });
    window.parent.$('#window_cancel').click(function(e){
        e.preventDefault();
        closeWin();
    })
    $('#dgCsal').datagrid({
        nowrap : false,
        fit : true,
        rownumbers : true,
        singleSelect: true,
        fitColumns : true,
        method: "POST",
        url: "/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/get_zdcslb_view",
        queryParams:{"csalids":csalids, "csal":csal},
        remoteSort: false,
        columns: [[
            { field: 'id', title: '测试案例id', width: 1,hidden: true },
            { field: 'ssid', title: '所属id', width: 1,hidden: true },
            { field: 'demoid', title: 'demoid', width: 1,hidden: true },
            { field: 'ssywid', title: 'ssywid', width: 1,hidden: true },
            { field: 'lbvalue', title: '测试类型', width: 18 },
            { field: 'lb', title: '测试类型', width: 11,hidden: true },
            { field: 'csmkmc', title: '测试模块名称', width: 24, formatter: function(value,rowData,rowIndex){
                return value == 'null' ? "" : value;
            } },
            { field: 'mc', title: '测试案例名称', width: 25},
            { field: 'ms', title: '测试案例描述', width: 25},
            { field: 'csjg', title: '测试结果', width:15,
                formatter: function(value,rowData,rowIndex){
                    if (value == '1' ) {
                        return "<a href='javascript:;' onclick='javascript:parent.view_rz(\""+rowData.id+"\",\""+uuid+"\",\"成功\",\""+rowData.jgsm+"\",\""+rowData.demoid+"\",\""+rowData.ssid+"\",\""+rowData.lb+"\",event)'>成功</a>";
                    } else if (value == '0') {
                        return "<a href='javascript:;' onclick='javascript:parent.view_rz(\""+rowData.id+"\",\""+uuid+"\",\"失败\",\""+rowData.jgsm+"\",\""+rowData.demoid+"\",\""+rowData.ssid+"\",\""+rowData.lb+"\",event)'>失败</a>";
                    } else if(value == '3'){
                        return "<a href='javascript:;' onclick='javascript:parent.view_rz(\""+rowData.id+"\",\""+uuid+"\",\"异常\",\""+rowData.jgsm+"\",\""+rowData.demoid+"\",\""+rowData.ssid+"\",\""+rowData.lb+"\",event)'>异常</a>";
                    }
                }
            },
            { field: 'jgsm', hidden:true,title: '测试结果描述', width: 1}
        ]],
        toolbar : [ {
            id:'cs_start',
            iconCls : 'icon-reload',
            text : '开始测试',
            handler : function() {
                cs_start();
            }
        },
        {
            id : 'cs_stop',
            iconCls : 'icon-cancel',
            disabled : true ,
            text : '停止测试',
            handler : function() {
                cs_stop();
                // 测试结束后提示用户
                afterAjax({'state':true,'msg':'测试结束'})
            }
        }]
    });

    // 开始测试
    function cs_start(){
        stop_mark = false;
        alertMark = false;
        // 重置last_csalid
        last_csalid = '';
        // 获取当前表格的所有信息
        var row_data = $('#dgCsal').datagrid('getRows');
        var datas = $('#dgCsal').datagrid('getData');
        if (row_data.length == 0){
            $.messager.alert('提示', '请选择需要测试的测试案例！', 'info');
            return;
        }
        // 遍历循环放入自动化测试的结果的信息,将其清空
        for(var i = 0; i < row_data.length; i++){
            for(var j = 0; j < datas.rows.length; j++ ){
                datas.rows[j]['csjg'] = '';
                datas.rows[j]['jgsm'] = '';
                $('#dgCsal').datagrid('updateRow',{index:j,row:datas.rows[j]});
            }
        }        
        // 开始测试按钮不可用
         $("#cs_start").linkbutton({"disabled":true});
        // 停止测试按钮可用
         $("#cs_stop").linkbutton({"disabled":false});
        // 获取当前表格的所有信息
        var row_data = $('#dgCsal').datagrid('getData');
        last_csalid = row_data.rows[row_data.rows.length-1].id;
        csal_num = row_data.length;
        // 开始循环执行测试案例
        $.each(row_data.rows, function(j,w){
            // 当用户不点击停止时，一直运行。
            setTimeout(function(){
                if(stop_mark == false){
                    cs_start_ajax(w);
                }
            },500*j)
            
        });
        
    }
    
    // 自动化测试的请求ajax
    function cs_start_ajax(row_data){
        $.ajax({
            url: "/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/cs_start_view",
            type: 'POST',
            async: false,
            data: {"row_data":JSON.stringify(row_data),"pc":uuid},
            success: function(data){
                if(data.state == true){
                    cs_getCsjg(row_data.id);
                }else if(data.state == false && alertMark == false){
                    alertMark = true;
                    afterAjax(data);
                    cs_stop();
                }
            },
            error: function(){
                errorAjax();
                // 开始测试按钮可用
                cs_stop();
            }
        });
    }

    // 停止测试
    function cs_stop(){
        stop_mark = true;
        // 开始测试按钮不可用
        $("#cs_start").linkbutton({"disabled":false});
        // 停止测试按钮不可用
        $("#cs_stop").linkbutton({"disabled":true});

        // 获取当前表格的所有信息
        var row_data = $('#dgCsal').datagrid('getData');

        // 循环遍历开启测评,写入自动化测试临时表信息
        $.ajax({
            url: "/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/cs_stop_view",
            type: 'POST',
            data: {"pc" : uuid},
            success: function(redata){
            },
            error: function(){
                errorAjax();
            }
        });
    }

    // 获取测试结果
    function cs_getCsjg(csalids){
        $.ajax({
            url: "/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/get_cs_zxjg_view",
            type: 'POST',
            dataType: 'json',
            data: {"pc" : uuid, 'csalids':csalids},
            success: function(redata){
                res_csjg = redata.rows;
                // 获取当前表格的所有信息
                var row_data = $('#dgCsal').datagrid('getData');
                var datagrid_target = $('#dgCsal');
                 // 遍历循环放入自动化测试的结果的信息
                for(var i = 0; i < res_csjg.length; i++){
                    for(var j = 0; j < row_data.rows.length; j++ ){
                        if( res_csjg[i]['csal_id'] == row_data.rows[j]['id']){
                            row_data.rows[j]['csjg'] = res_csjg[i]['zxjg'];
                            row_data.rows[j]['jgsm'] = res_csjg[i]['jgsm'];
                            datagrid_target.datagrid('updateRow',{index:j,row:row_data.rows[j]});
                        }
                    }
                }
                if(stop_mark == false && res_csjg.length > 0 && last_csalid == res_csjg[0]['csal_id']){
                    // 测试结束后提示用户
                    afterAjax({'state':true,'msg':'测试结束'});
                    cs_stop();
                }
              },
              error: function(){
                  errorAjax();
              }
         });
    }
    function closeWin(){
        $.ajax({
            url: "/oa/kf_ywgl/kf_ywgl_014/kf_ywgl_014_view/cs_close_view",
            type: 'POST',
            data: {"pc" : uuid},
            success: function(redata){
                res_csjg = redata.data;
            },
            error: function(){
                errorAjax();
            }
        });
        // 停止测试
        cs_stop();
    }
});
