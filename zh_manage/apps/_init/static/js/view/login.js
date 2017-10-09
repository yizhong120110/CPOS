	
$(function() {
	// 登录Dialog不可见
	$("#loginForm").hide();

	// 页面如期时请求后台
	$.ajax({
		url : 'portalinit',
		type : 'POST',
		success : function(result) {
			if (result == 'OK') {
				window.location.href = "/weibss/portal";
			} else {
				// 显示登录页面
				$("#loginForm").show();
				// 初始化
				init();
			}
		}
	});
	
	function init() {
		// 初始化页面
		$('#loginForm').dialog({
			closable : false,
			buttons : [{
				text : '登录',
				width : 80,
				handler : function() {
					// 用户名
					var strUserName = $.trim($('#username').val());
					// 密码
					var strPasswd = $.trim($('#passwd').val());

					// 用户名和密码不能为空
					if (strUserName == '') {
						$.messager.alert('错误', '用户名不能为空!', 'error');
						return;
					}

					if (strPasswd == '') {
						$.messager.alert('错误', '密码不能为空!', 'error');
						return;
					}

					// 向后台发送请求
					$.ajax({
						url : 'login',
						type : 'POST',
						data : {
							username : strUserName,
							passwd : $.md5(strPasswd)
						},
						error : function() {
							$.messager.alert('失败', '登录失败,请与管理员联系!', 'warning');
						},
						success : function(result) {
							var data = jQuery.parseJSON(result);
							// 成功时
							if (data.state == true) {
								window.location.href = "/weibss/portal";
							} else {
								$.messager.alert('失败', data.msg, 'error');
							}
						}
					});
				}
			},{
				text : '重置',
				width : 80,
				handler : function() {
					// 重置为空
					$('#username').textbox('clear');
					$('#passwd').textbox('clear');
				}
			}]
		});
	}
});