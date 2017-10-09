# -*- coding: utf-8 -*-
# Action: grid++打印的service
# Author: 张振峰
# AddTime: 2015-07-29
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, render_to_string, logger

@register_url('GET')
def print_view():
    """
    # 目录选择时执行的页面跳转
    """
    # URL
    data = eval(request.GET.data)
    # 判断js文件是否传参了
    if data.get('self_data') == '' or data.get('self_data') == None:
        data['self_data'] = 'False'
    if data.get('js_path') == '' or data.get('js_path') == None:
        data['js_path'] = ''
    # 预览窗口top显示的操作框哪些隐藏,传递需要隐藏操作按钮的枚举值（
    #           多个时以逗号进行分割，例如："isplayviewer": '5,6,60,'（ 隐藏：导出按钮，邮件发送按钮，导出 Excel 按钮 ））：
    #    2指定打印按钮。3指定打印页面设置按钮。4指定打印机设置按钮。5指定导出按钮。6指定邮件发送按钮。7指定保存打印文档按钮。
    #    14指定上一页按钮。15指定下一页按钮。16指定首页按钮。17指定最后页按钮。18指定页号编辑框。19指定关闭按钮。20指定按钮，尚未实现。
    #    21指定刷新按钮。25指定明细网格数据分页方式组合框与每页行数编辑框。30指定查找编辑框。31指定查找按钮。32指定继续查找按钮。
    #    33指定查找对话框按钮。40指定打印预览按钮。41指定打印提交布局选取框。50指定导出Excel菜单项。51指定导出文本菜单项。
    #    52指定导出HTML菜单项。53指定导出RTF菜单项。54指定导出PDF菜单项。55指定导出CSV菜单项。56指定导出图像菜单项。60指定导出Excel按钮。
    #    61指定导出PDF按钮。65指定导出Excel并发送Email菜单项。66指定导出文本并发送Email菜单项。67指定导出HTML并发送Email菜单项。
    #    68指定导出RTF并发送Email菜单项。69指定导出PDF并发送Email菜单项。70指定导出CSV并发送Email菜单项。71指定导出图像并发送Email菜单项。
    if data.get('isplayviewer') == '' or data.get('isplayviewer') == None:
        data['isplayviewer'] = ''
    url = 'grid_printer/grid_printer.html'
    # 页面跳转执行
    return render_to_string(url,data)