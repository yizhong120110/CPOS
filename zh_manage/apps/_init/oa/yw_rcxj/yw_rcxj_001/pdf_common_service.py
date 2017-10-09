# -*- coding: utf-8 -*-
# Action: 生成pdf的service
# Author: zhangzhf
# AddTime: 2015-07-18
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus.paragraph import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.pdfbase.ttfonts

import os,platform,unittest,copy,re
from reportlab.lib.units import inch

def creat_pdf(path,data_list):
    """
    # 创建pdf
    # path ：生成pdf的目录
    # data_list ：pdf的数据，格式为[{'data':[{'abc':'111'}],'title_code':['abc']}]
    """
    # 设置字体
    if 'Windows' in platform.system():
        reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont('hei', 'SIMHEI.TTF'))
    else:
        reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont('hei', '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc'))
        
    stylesheet=getSampleStyleSheet()
    normalStyle = copy.deepcopy(stylesheet['BodyText'])
    normalStyle.fontName ='hei'
    normalStyle.fontSize = 12
    # 行高
    rowheights = 0.3*inch
    # 行宽
    colwidths = 2.5*inch
    # （1,2）是行列的意思，第一个元素是列，第二个元素是行，这两个元素可以定位一个单元格
    common_style_list = [
         ('GRID', (0,0), (-1,-1), 0.25, colors.black),
         ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
         # 居中显示
         ('ALIGN', (0,1), (-1,1), 'CENTER'),
         ('ALIGN', (0,0), (-1,0), 'CENTER'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,0),(-1,2),12),
         # 设置字体
         ('FONTSIZE',(0,2),(-1,-1),9),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,1), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    base_style_list = [
         ('GRID', (0,0), (-1,-1), 0.25, colors.black),
         ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
         # 居中显示
         ('ALIGN', (0,0), (-1,0), 'CENTER'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,1), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    null_base_style_list = [
         ('GRID', (0,0), (-1,-1), 0.25, colors.black),
         # 居中显示
         ('ALIGN', (0,0), (-1,1), 'CENTER'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,1), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    jcxjjg_grid_list = [('GRID', (0,0), (-1,-1), 0.25, colors.black),
         ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
         ('ALIGN', (0,0), (-1,0), 'LEFT'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,1),(-1,-1),9),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,0), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    jy_grid_list = [('GRID', (0,0), (-1,-1), 0.25, colors.black),
         ('ALIGN', (1,1), (-1,-1), 'LEFT'),
         ('ALIGN', (0,0), (-1,0), 'CENTER'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,1),(-1,-1),9),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,0), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    jyyc_grid_list = [('GRID', (0,0), (-1,-1), 0.25, colors.black),
         ('ALIGN', (0,0), (-1,0), 'CENTER'),
         ('ALIGN', (0,1), (0,-1), 'RIGHT'),
         ('ALIGN', (1,1), (1,-1), 'LEFT'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,1),(-1,-1),9),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,0), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    jc_style_list = [
         ('GRID', (0,0), (-1,-1), 0.25, colors.black),
         # 居中显示
         ('ALIGN', (0,0), (-1,1), 'CENTER'),
         #进程个数居右
         ('ALIGN', (1,2), (1,-1), 'RIGHT'),
         #平台进程检查居左
         ('ALIGN', (0,2), (0,-1), 'LEFT'),
         #启动时间居中
         ('ALIGN', (2,2), (2,-1), 'CENTER'),
         #其他居左
         ('ALIGN', (3,2), (3,-1), 'LEFT'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,0),(-1,2),12),
         # 设置字体
         ('FONTSIZE',(0,2),(-1,-1),9),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,1), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    tong_style_list = [
         ('GRID', (0,0), (-1,-1), 0.25, colors.black),
         # 居中显示
         ('ALIGN', (0,0), (-1,1), 'CENTER'),
         # 所有都居左
         ('ALIGN', (0,2), (-1,-1), 'LEFT'),
         # 字体
         ('FONT',(0,0),(-1,-1),'hei'),
         # 设置字体
         ('FONTSIZE',(0,0),(-1,2),12),
         # 设置字体
         ('FONTSIZE',(0,2),(-1,-1),9),
         # 合并单元格
         ('SPAN',(0,0), (-1,0)),
         # 背景颜色
         ('BACKGROUND',(0,0), (-1,1), colors.gray),
         ('VALIGN',(0,0), (-1,-1),'MIDDLE')
    ]
    common_grid_style = TableStyle(common_style_list)
    tong_grid_style = TableStyle(tong_style_list)
    null_base_grid_style = TableStyle(null_base_style_list)
    base_grid_style = TableStyle(base_style_list)
    jc_grid_style = TableStyle(jc_style_list)
    jcxjjg_grid_style = TableStyle(jcxjjg_grid_list)
    jy_grid_style = TableStyle(jy_grid_list)
    jyyc_grid_style = TableStyle(jyyc_grid_list)
    
    # pdf中的内容
    pdf_data = []
    # 主机监控信息 
    zjjk_title = [['主机检查','',''],['监控内容', '阈值', '监控情况']]
    set_cart_data(pdf_data,data_list[0],zjjk_title,"一、特色业务系统主机",normalStyle,colwidths,rowheights,common_grid_style if len(data_list[0]['data']) > 0 else null_base_grid_style,True,2)
    # 表空间监控信息
    sjkxj_title = [['表空间使用情况','',''],['表空间名', '阈值', '表空间使用比例']]
    set_cart_data(pdf_data,data_list[1],sjkxj_title,"二、Oracle数据库表空间检",normalStyle,colwidths,rowheights,common_grid_style if len(data_list[1]['data']) > 0 else null_base_grid_style,True,2)
    # 平台进程检查表
    jc_title = [['平台进程检查表','','',''],['平台进程检查表', '进程个数', '启动时间','其他(是否有错误)']]
    set_cart_data(pdf_data,data_list[2],jc_title,"三、特色业务系统进程检查机",normalStyle,1.875*inch,rowheights,jc_grid_style if len(data_list[2]['data']) > 0 else null_base_grid_style,True,2)
    # 日常巡检结果描述
    jc_title = [['日常巡检结果描述']]
    set_cart_data(pdf_data,data_list[3],jc_title,"",normalStyle,7.5*inch,(0.3*inch,0.6*inch),jcxjjg_grid_style,False,1)
    # tong主机
    tong_title = [['主机检查','',''],['日志名称', '日志大小', '异常或错误']]
    set_cart_data(pdf_data,data_list[4],tong_title,"四、Tong中间件日志检查",normalStyle,colwidths,rowheights,tong_grid_style if len(data_list[4]['data']) > 0 else null_base_grid_style,True,2)
    # 分行特色业务平台系统交易情况 
    jy_title = [['分行特色业务平台系统交易情况']]
    set_cart_data(pdf_data,data_list[5],jy_title,"五、特色业务系统交易情况",normalStyle,(2.5*inch,5*inch),rowheights,jy_grid_style,True,1)
    # 分行特色业务平台系统交易异常情况 
    jyyc_title = [['序号', '异常描述', '异常原因及措施']]
    set_cart_data(pdf_data,data_list[6],jyyc_title,"",normalStyle,colwidths,rowheights,jyyc_grid_style,False,1)
    
    # 日常巡检结果描述
    xjxj_title = [['巡检小结']]
    set_cart_data(pdf_data,data_list[7],xjxj_title,"",normalStyle,7.5*inch,(0.3*inch,0.6*inch),jcxjjg_grid_style,False,1)

    SimpleDocTemplate(path, rightMargin=72,leftMargin=72,topMargin=20,bottomMargin=20).build(pdf_data)

def listToYzTuple(data,title_code_lst,title,title_num):
    """
    # 将list转为元组
    # data ：数据[{'a':'a'},{'a':'a'}]
    # title_code_lst : 标题的顺序
    # title : 标题
    """
    # 保存一行中，每个单元格的行数
    line_height_list = []
    for i in range(title_num):
        line_height_list.append(0.3*inch)
    re_data_list = []
    data_list = []
    for d in data:
        re_data_list = []
        # 每行的单元格的行数
        line_height = []
        for title_code in title_code_lst:
            mark_line_num = 0
            mark_word = d.get(str(title_code),'')
            hh_num = len(re.findall('\n',str(mark_word)))
            if hh_num > 0:
                mark_line_num = hh_num
            else:
                mark_word,mark_line_num = wrap_pdf_data(data = mark_word, line_width = 106/len(title_code_lst))
            line_height.append(mark_line_num)
            re_data_list.append(mark_word)
        data_list.append(re_data_list)
        line_height.sort(reverse=True)
        if line_height:
            het = line_height[0]*0.3*inch
            if line_height[0] > 1:
               het = line_height[0]*0.2*inch
            line_height_list.append(het)
    # 将标题数据添加到数据中
    max = len(title) - 1
    for i in range(0, len(title)):
        data_list.insert(0,title[max-i])
    return tuple(data_list),tuple(line_height_list)
    
def set_cart_data(pdf_data,cart_data,title,table_title,normalStyle,colwidths,rowheights,GRID_STYLE,have_table_title,title_num = 2):
    """
    # 设置pdf中table的数据
    # pdf_data ：整个pdf的数据对象
    # cart_data : 某一个table的数据对象
    # title : table的列标题
    # table_title ：table外面的标题
    # normalStyle ：样式
    # colwidths ：列宽
    # rowheights : 行高
    # GRID_STYLE : 表格样式
    # have_table_title 有没有table外面的标题
    """
    # 主机监控信息 
    zjjk_data,line_height_list = listToYzTuple(cart_data['data'],cart_data['title_code'],title,title_num)
    if have_table_title:
        pdf_data.append(Paragraph(table_title, normalStyle))
        pdf_data.append(Spacer(0,5))
    zjjk_table = Table(zjjk_data, colwidths, line_height_list,GRID_STYLE)
    pdf_data.append(zjjk_table)
    
def wrap_pdf_data(data = '', line_width = 27):
    """
    # 将表格的内容进行换行
    # data : 要进行加换行符的的数据
    # line_width : 每行显示的字符的个数：英文占一个，中文占两个。
    # return : 返回格式化后的数据和行数
    """
    # 每一行的文字
    lineWords = ''
    # 每一行的实际字节长度
    mark_line_width = 0
    # 文字可以占的行数
    line_num = 1
    data = str(data)
    for word in data:
        if check_is_chinese(word):
            mark_line_width += 2
        else:
            mark_line_width += 1
        lineWords = lineWords + word
        # 如果当前的一行的文字超过line_width了就需要加一个换行符
        if mark_line_width >= line_width:
            lineWords = lineWords + '\n'
            line_num += 1
            mark_line_width = 0
    return lineWords,line_num
    
def check_is_chinese(word):
    """
    # 判断文字是不是中文
    # word ；要判断的文字
    """
    # 将正则表达式编译成Pattern对象
    pattern = re.compile(r'^[\u4E00-\u9FA5]+$')
     
    # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    match = pattern.match(word)
    if match:
        return True