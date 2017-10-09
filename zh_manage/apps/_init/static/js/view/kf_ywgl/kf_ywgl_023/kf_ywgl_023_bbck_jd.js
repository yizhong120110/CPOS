$(function() {
    var nro = ($('#txtBbxx').val()+'').replace(/None/gm,"''");
    nr = eval('(' + nro + ')');
    $('#nodeBox').text(eval('(' + $('#data_nr').val() + ')'));
    CodeMirror.fromTextArea(document.getElementById("nodeBox"), {
        mode: {
            name: "python",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        readOnly:true,
        matchBrackets: true
    });
    jdlx = $('#jdlx').val();
    hid = true;
    if(jdlx == '5' || jdlx == 5){
        hid = false;
    }
    $('#gdbbxx').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280
            }]
        ],
        data: nr.gl_jddy
    });
    
    $('#gdsrys').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'bm',
                title: '要素编码',
                width: 120
            },{
                field: 'ysmc',
                title: '要素名称',
                width: 120
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50
            }, {
                field: 'ly',
                title: '来源',
                width: 50
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                hidden:hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                hidden:hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                hidden:hid
            }]
        ],
        data: nr.gl_srys
    });
    $('#gdscys').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'bm',
                title: '要素编码',
                width: 120
            },{
                field: 'ysmc',
                title: '要素名称',
                width: 120
            }, {
                field: 'gslb',
                title: '归属类别',
                width: 50
            }, {
                field: 'ly',
                title: '来源',
                width: 50
            }, {
                field: 'mrz',
                title: '默认值',
                width: 50
            }, {
                field: 'jkjy',
                title: '是否接口校验',
                width: 70,
                hidden:hid
            }, {
                field: 'ssgzmc',
                title: '校验规则名称',
                width: 70,
                hidden:hid
            }, {
                field: 'zjcs',
                title: '追加参数',
                width: 50,
                hidden:hid
            }]
        ],
        data: nr.gl_scys
    });
    $('#gdfhz').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: false,
        remoteSort: true,
        columns: [
            [{
                field: 'id',
                title: 'id',
                width: 120,
                hidden:true
            },{
                field: 'bm',
                title: '返回值',
                width: 120
            }, {
                field: 'ysmc',
                title: '备注',
                width: 280
            }]
        ],
        data: nr.gl_fhz
    });
});