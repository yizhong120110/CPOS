$(function() {
    if ($('#bbnr').val() == '' || $('#bbnr').val() == null || $('#bbnr').val() == 'None'){
        $('#nodeBox').text(eval('(' + $('#hsnr').val() + ')'));
    }else{
        $('#nodeBox').text($('#bbnr').val());
    }
    
    CodeMirror.fromTextArea(document.getElementById("nodeBox"), {
        mode: {
            name: "xml",
            version: 3,
            singleLineStringErrors: false
        },
        lineNumbers: true,
        indentUnit: 4,
        smartIndent:true,
        matchBrackets: true
    });
    var nro = ($('#txtBbxx').val()+'').replace(/None/gm,"''");
    nr = eval('(' + nro + ')');
    $('#bbxx').datagrid({
        nowrap: false,
        fit: true,
        rownumbers: true,
        fitColumns: true,
        method: "get",
        singleSelect: true,
        remoteSort: false,
        columns: [
            [{
                field: 'sxmc',
                title: '属性名称',
                width: 120
            }, {
                field: 'sxnr',
                title: '属性内容',
                width: 280
            }]
        ],
        data: nr.bbxx
    });
});