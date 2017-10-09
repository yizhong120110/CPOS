# -*- coding: utf-8 -*-
'''
crondescriptor.py

Written 2015/04/13 by gaolycn
'''

import re

Resources = {
    'EveryMinute': '每分钟',
    'EveryHour': '每小时',
    'AnErrorOccuredWhenGeneratingTheExpressionD': '请检查cron表达式语法。',
    'AtSpace': '在 ',
    'EveryMinuteBetweenX0AndX1': '在 %s 和 %s 之间的每分钟',
    'At': '在',
    'SpaceAnd': ' 和',
    'EverySecond': '每秒',
    'EveryX0Seconds': '每 %s 秒',
    'SecondsX0ThroughX1PastTheMinute': '在每分钟的 %s 到 %s 秒',
    'AtX0SecondsPastTheMinute': '在每分钟的 %s 秒',
    'EveryX0Minutes': '每 %s 分钟',
    'MinutesX0ThroughX1PastTheHour': '在每小时的 %s 到 %s 分钟',
    'AtX0MinutesPastTheHour': '在每小时的 %s 分',
    'EveryX0Hours': '每 %s 小时',
    'BetweenX0AndX1': '在 %s 和 %s 之间',
    'AtX0': '在 %s',
    'ComaEveryDay': ', 每天',
    'ComaEveryX0DaysOfTheWeek': ', 每周的每 %s 天',
    'ComaX0ThroughX1': ', %s 到 %s',
    'First': '第一个',
    'Second': '第二个',
    'Third': '第三个',
    'Forth': '第四个',
    'Fifth': '第五个',
    'ComaOnThe': ', 在 ',
    'SpaceX0OfTheMonth': '%s 每月',
    'ComaOnTheLastX0OfTheMonth': ', 每月的最后一个 %s ',
    'ComaOnlyOnX0': ', 仅在 %s',
    'ComaEveryX0Months': ', 每 %s 月',
    'ComaOnlyInX0': ', 仅在 %s',
    'ComaOnTheLastDayOfTheMonth': ', 每月的最后一天',
    'ComaOnTheLastWeekdayOfTheMonth': ', 每月的最后一个平日',
    'FirstWeekday': '第一个平日',
    'WeekdayNearestDayX0': '最接近 %s 号的平日',
    'ComaOnTheX0OfTheMonth': ', 每月的 %s ',
    'ComaEveryX0Days': ', 每 %s 天',
    'ComaBetweenDayX0AndX1OfTheMonth': ', 在每月的 %s 和 %s 号之间',
    'ComaOnDayX0OfTheMonth': ', 每月的 %s 号',
    'SpaceAndSpace': ' 和 ',
    'ComaEveryMinute': ', 每分钟',
    'ComaEveryHour': ', 每小时',
    'ComaEveryX0Years': ', 每 %s 年'
}

DayNames = {
    0: '星期日',
    1: '星期一',
    2: '星期二',
    3: '星期三',
    4: '星期四',
    5: '星期五',
    6: '星期六'
}

MonthNames = {
    1: '一月',
    2: '二月',
    3: '三月',
    4: '四月',
    5: '五月',
    6: '六月',
    7: '七月',
    8: '八月',
    9: '九月',
    10: '十月',
    11: '十一月',
    12: '十二月',
}

WeekDay = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
Months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


class CronDescriptor(object):
    def __init__(self):
        self._specialCharacters = ['/', '-', ',', '*']
    
    def getDescription(self, expression, options=None, type='FULL'):
        self._expression = expression
        self._options = options or Options()
        self._parsed = False
        
        description = ''
        try:
            if not self._parsed:
                parser = ExpressionParser(self._expression, self._options)
                self._expressionParts = parser.Parse()
                self._parsed = True
            
            if type == 'FULL':
                description = self.getFullDescription()
            elif type == 'TIMEOFDAY':
                description = self.getTimeOfDayDescription()
            elif type == 'HOURS':
                description = self.getHoursDescription()
            elif type == 'MINUTES':
                description = self.getMinutesDescription()
            elif type == 'SECONDS':
                description = self.getSecondsDescription()
            elif type == 'DAYOFMONTH':
                description = self.getDayOfMonthDescription()
            elif type == 'MONTH':
                description = self.getMonthDescription()
            elif type == 'DAYOFWEEK':
                description = self.getDayOfWeekDescription()
            elif type == 'YEAR':
                description = self.getYearDescription()
            else:
                description = self.getSecondsDescription()
        except:
            description = '解析失败，请检查格式是否正确'
            print(description)
        
        return description
    
    def getFullDescription(self):
        description = ''
        try:
            timeSegment = self.getTimeOfDayDescription()
            dayOfMonthDesc = self.getDayOfMonthDescription()
            monthDesc = self.getMonthDescription()
            dayOfWeekDesc = self.getDayOfWeekDescription()
            yearDesc = self.getYearDescription()
            
            description = '%s%s%s%s' % (
                timeSegment,
                dayOfWeekDesc if self._expressionParts[3] == "*" else dayOfMonthDesc,
                monthDesc,
                yearDesc
            )
            
            description = self.transformVerbosity(description)
        except:
            description = Resources['AnErrorOccuredWhenGeneratingTheExpressionD']
            print(description)
            raise
        
        return description
    
    def getTimeOfDayDescription(self):
        secondsExpression = self._expressionParts[0]
        minuteExpression = self._expressionParts[1]
        hourExpression = self._expressionParts[2]
        
        description = ''
        
        # handle special cases first
        if (max([minuteExpression.find(char) for char in self._specialCharacters]) == -1 \
            and max([hourExpression.find(char) for char in self._specialCharacters]) == -1 \
            and max([secondsExpression.find(char) for char in self._specialCharacters]) == -1):
            # specific time of day (i.e. 10 14)
            description += Resources['AtSpace']
            description += self.formatTime(hourExpression, minuteExpression, secondsExpression)
        elif ('-' in minuteExpression \
            and ',' not in minuteExpression \
            and max([hourExpression.find(char) for char in self._specialCharacters]) == -1):
            # minute range in single hour (i.e. 0-10 11)
            minuteParts = minuteExpression.split('-')
            description += Resources['EveryMinuteBetweenX0AndX1'] % (
                    self.formatTime(hourExpression, minuteParts[0]),
                    self.formatTime(hourExpression, minuteParts[1])
                )
        elif ',' in hourExpression and max([minuteExpression.find(char) for char in self._specialCharacters]) == -1:
            # hours list with single minute (o.e. 30 6,14,16)
            hourParts = hourExpression.split(',')
            description += Resources['At']
            for i, hp in enumerate(hourParts):
                description += ' '
                description += self.formatTime(hp, minuteExpression)
                
                if i < len(hourParts) -2:
                    description += ','
                
                if i == len(hourParts) -2:
                    description += Resources['SpaceAnd']
        else:
            # default time description
            secondsDescription = self.getSecondsDescription()
            minutesDescription = self.getMinutesDescription()
            hoursDescription = self.getHoursDescription()
            
            description += secondsDescription
            
            if len(description) > 0:
                description += ', '
            
            description += minutesDescription
            
            if len(description) > 0:
                description += ', '
            
            description += hoursDescription
        
        return description
    
    def getSecondsDescription(self):
        description = self.getSegmentDescription(
            self._expressionParts[0],
            Resources['EverySecond'],
            (lambda x:x.rjust(2, '0')),
            (lambda x:Resources['EveryX0Seconds'] % x),
            (lambda x:Resources['SecondsX0ThroughX1PastTheMinute']),
            (lambda x:Resources['AtX0SecondsPastTheMinute'])
        )
        
        return description
    
    def getMinutesDescription(self):
        description = self.getSegmentDescription(
            self._expressionParts[1],
            Resources['EveryMinute'],
            (lambda x:x.rjust(2, '0')),
            (lambda x:Resources['EveryX0Minutes'] % x.rjust(2, '0')),
            (lambda x:Resources['MinutesX0ThroughX1PastTheHour']),
            (lambda x:'' if x == '0' else Resources['AtX0MinutesPastTheHour'])
        )
        
        return description
    
    def getHoursDescription(self):
        expression = self._expressionParts[2]
        description = self.getSegmentDescription(
            expression,
            Resources['EveryHour'],
            (lambda x:self.formatTime(x, '0')),
            (lambda x:Resources['EveryX0Hours'] % x.rjust(2, '0')),
            (lambda x:Resources['BetweenX0AndX1']),
            (lambda x:Resources['AtX0'])
        )
        
        return description
    
    def getDayOfWeekDescription(self):
        def getSingleItemDescription(s):
            exp = s
            if '#' in s:
                exp = s[:s.index('#')]
            elif 'L' in s:
                exp = exp.replace('L', '')
            
            return DayNames[int(exp)]
        
        def getDescriptionFormat(s):
            format = None
            if '#' in s:
                dayOfWeekOfMonthNumber = s[s.index('#')+1:]
                dayOfWeekOfMonthDescription = None
                if dayOfWeekOfMonthNumber == '1':
                    dayOfWeekOfMonthDescription = Resources['First']
                elif dayOfWeekOfMonthNumber == '2':
                    dayOfWeekOfMonthDescription = Resources['Second']
                elif dayOfWeekOfMonthNumber == '3':
                    dayOfWeekOfMonthDescription = Resources['Third']
                elif dayOfWeekOfMonthNumber == '4':
                    dayOfWeekOfMonthDescription = Resources['Forth']
                elif dayOfWeekOfMonthNumber == '5':
                    dayOfWeekOfMonthDescription = Resources['Fifth']
                
                format = Resources['ComaOnThe'] + dayOfWeekOfMonthDescription + Resources['SpaceX0OfTheMonth']
            elif 'L' in s:
                format = Resources['ComaOnTheLastX0OfTheMonth']
            else:
                format = Resources['ComaOnlyOnX0']
            
            return format
        
        description = self.getSegmentDescription(
            self._expressionParts[5],
            Resources['ComaEveryDay'],
            getSingleItemDescription,
            (lambda x:Resources['ComaEveryX0DaysOfTheWeek'] % s),
            (lambda x:Resources['ComaX0ThroughX1']),
            getDescriptionFormat
        )
        
        return description
    
    def getMonthDescription(self):
        description = self.getSegmentDescription(
            self._expressionParts[4],
            '',
            (lambda x:MonthNames[int(x)]),
            (lambda x:Resources['ComaEveryX0Months'] % x),
            (lambda x:Resources['ComaX0ThroughX1']),
            (lambda x:Resources['ComaOnlyInX0'])
        )
        
        return description
    
    def getDayOfMonthDescription(self):
        description = None
        expression = self._expressionParts[3]
        expression = expression.replace('?', '*')
        
        if expression == 'L':
            description = Resources['ComaOnTheLastDayOfTheMonth']
        elif expression in ('WL', 'LW'):
            description = Resources['ComaOnTheLastWeekdayOfTheMonth']
        else:
            m = re.match(r'(\dW)|(W\d)', expression)
            if m:
                dayNumber = int(m.group(0).replace('W', ''))
                dayString = Resources['FirstWeekday'] if dayNumber == 1 else (Resources['WeekdayNearestDayX0'] % dayNumber)
                description = Resources['ComaOnTheX0OfTheMonth'] % dayString
            else:
                description = self.getSegmentDescription(
                    expression,
                    Resources['ComaEveryDay'],
                    (lambda x:x),
                    (lambda x:Resources['ComaEveryDay'] if x == '1' else Resources['ComaEveryX0Days']),
                    (lambda x:Resources['ComaBetweenDayX0AndX1OfTheMonth']),
                    (lambda x:Resources['ComaOnDayX0OfTheMonth'])
                )
        
        return description
    
    def getYearDescription(self):
        description = self.getSegmentDescription(
            self._expressionParts[6],
            '',
            (lambda x:str(int(x))),
            (lambda x:Resources['ComaEveryX0Years'] % x),
            (lambda x:Resources['ComaX0ThroughX1']),
            (lambda x:Resources['ComaOnlyInX0'])
        )
        
        return description
    
    def getSegmentDescription(self, 
        expression,
        allDescription,
        getSingleItemDescription,
        getIntervalDescriptionFormat,
        getBetweenDescriptionFormat,
        getDescriptionFormat):
        
        description = None
        
        if not expression:
            description = ''
        elif expression == "*":
            description = allDescription
        elif max([expression.find(char) for char in ('/', '-', ',')]) == -1:
            if '%s' in getDescriptionFormat(expression):
                description = getDescriptionFormat(expression) % getSingleItemDescription(expression)
            else:
                description = getDescriptionFormat(expression)
        elif '/' in expression:
            segments = expression.split('/')
            if '%s' in getIntervalDescriptionFormat(segments[1]):
                description = getIntervalDescriptionFormat(segments[1]) % getSingleItemDescription(segments[1])
            else:
                description = getIntervalDescriptionFormat(segments[1])
            
            # interval contains 'between' piece (i.e. 2-59/3 )
            if '-' in segments[0]:
                betweenSegmentOfInterval = segments[0]
                betweenSegements = betweenSegmentOfInterval.split('-')
                betweenSegment1Description = getSingleItemDescription(betweenSegements[0])
                betweenSegment2Description = getSingleItemDescription(betweenSegements[1])
                betweenSegment2Description = betweenSegment2Description.replace(":00", ":59")
                description += ", " + getBetweenDescriptionFormat(betweenSegmentOfInterval) % (betweenSegment1Description, betweenSegment2Description)
        elif '-' in expression:
            segments = expression.split('-')
            betweenSegment1Description = getSingleItemDescription(segments[0])
            betweenSegment2Description = getSingleItemDescription(segments[1])
            betweenSegment2Description = betweenSegment2Description.replace(":00", ":59")
            description = getBetweenDescriptionFormat(expression) % (betweenSegment1Description, betweenSegment2Description)
        elif ',' in expression:
            segments = expression.split(',')
            
            descriptionContent = ''
            for i, sgmt in enumerate(segments):
                if i > 0 and len(segments) > 2:
                    descriptionContent += ','
                    if i < len(segments) - 1:
                        descriptionContent += ' '
                
                if i > 0 and len(segments) > 1 and (i == len(segments) - 1 or len(segments) == 2):
                    descriptionContent += Resources['SpaceAndSpace']
                
                descriptionContent += getSingleItemDescription(sgmt)
            
            description = getDescriptionFormat(expression) % descriptionContent
        
        return description
    
    def formatTime(self, hourExpression, minuteExpression, secondExpression=None):
        hour = int(hourExpression)
        
        period = ''
        if not self._options.use24HourTimeFormat:
            period = " PM" if hour >= 12 else " AM"
            if hour > 12:
                hour -= 12
        
        minute = str(int(minuteExpression))
        second = ''
        if secondExpression:
            second = ':' + str(int(secondExpression)).rjust(2, '0')
        
        return '%s:%s%s%s' % (
            str(hour).rjust(2, '0'),
            minute.rjust(2, '0'),
            second,
            period
        )
    
    def transformVerbosity(self, description):
        if not self._options.verbose:
            description = description.replace(Resources['ComaEveryMinute'], '')
            description = description.replace(Resources['ComaEveryHour'], '')
            description = description.replace(Resources['ComaEveryDay'], '')
        
        return description


class Options(object):
    def __init__(self, casingType='Sentence', verbose=False, dayOfWeekStartIndexZero=True, use24HourTimeFormat=True):
        self._casingType = casingType
        self._verbose = verbose
        self._dayOfWeekStartIndexZero = dayOfWeekStartIndexZero
        self._use24HourTimeFormat = use24HourTimeFormat
    
    @property
    def casingType(self):
        return self._casingType
    
    @casingType.setter
    def casingType(self, casingType):
        self._casingType = casingType
    
    @property
    def verbose(self):
        return self._verbose
    
    @verbose.setter
    def verbose(self, verbose):
        self._verbose = verbose
    
    @property
    def dayOfWeekStartIndexZero(self):
        return self._dayOfWeekStartIndexZero
    
    @dayOfWeekStartIndexZero.setter
    def dayOfWeekStartIndexZero(self, dayOfWeekStartIndexZero):
        self._dayOfWeekStartIndexZero = dayOfWeekStartIndexZero
    
    @property
    def use24HourTimeFormat(self):
        return self._use24HourTimeFormat
    
    @use24HourTimeFormat.setter
    def use24HourTimeFormat(self, use24HourTimeFormat):
        self._use24HourTimeFormat = use24HourTimeFormat


class ExpressionParser(object):
    def __init__(self, expression, options):
        self._expression = expression
        self._options = options
    
    def Parse(self):
        # Initialize all elements of parsed array to empty strings
        parsed = [''] * 7
        
        if not self._expression:
            raise Exception('MissingFieldException')
        else:
            expressionPartsTemp = self._expression.split(' ')
            
            if len(expressionPartsTemp) < 5:
                raise Exception('Error: Expression only has {0} parts.  At least 5 part are required.' % len(expressionPartsTemp))
            elif len(expressionPartsTemp) == 5:
                # 5 part cron so shift array past seconds element
                parsed[1:6] = expressionPartsTemp[:5]
            elif len(expressionPartsTemp) == 6:
                # If last element ends with 4 digits, a year element has been supplied and no seconds element
                m = re.match(r'.*\d{4}$', expressionPartsTemp[5])
                if m:
                    parsed[1:7] = expressionPartsTemp[:7]
                else:
                    parsed[:6] = expressionPartsTemp[:6]
            elif len(expressionPartsTemp) == 7:
                parsed = expressionPartsTemp
            else:
                raise Exception('Error: Expression has too many parts ({0}).  Expression must not have more than 7 parts.' % len(expressionPartsTemp))
        
        self.NormalizeExpression(parsed)
        
        return parsed
    
    def NormalizeExpression(self, expressionParts):
        # convert ? to * only for DOM and DOW
        expressionParts[3] = expressionParts[3].replace('?', '*')
        expressionParts[5] = expressionParts[5].replace('?', '*')
        
        # convert 0/, 1/ to */
        if expressionParts[0].startswith('0/'):
            expressionParts[0] = expressionParts[0].replace('0/', '*/')  # seconds
        
        if expressionParts[1].startswith('0/'):
            expressionParts[1] = expressionParts[1].replace('0/', '*/')  # minutes
        
        if expressionParts[2].startswith('0/'):
            expressionParts[2] = expressionParts[2].replace('0/', '*/')  # hours
        
        if expressionParts[3].startswith('1/'):
            expressionParts[3] = expressionParts[3].replace('1/', '*/')  # DOM
        
        if expressionParts[4].startswith('1/'):
            expressionParts[4] = expressionParts[4].replace('1/', '*/')  # Month
        
        if expressionParts[5].startswith('1/'):
            expressionParts[5] = expressionParts[5].replace('1/', '*/')  # DOW
        
        # convert */1 to *
        for i, ep in enumerate(expressionParts):
            if ep == '*/1':
                expressionParts[i] = '*'
        
        # handle DayOfWeekStartIndexZero option where SUN=1 rather than SUN=0
        if not self._options.dayOfWeekStartIndexZero:
            dowChars = list(expressionParts[5])
            for i, char in enumerate(dowChars):
                charNumeric = None
                if (i==0 or dowChars[i-1] != '#') and char.isdigit():
                    dowChars[i] = str(int(char) - 1)
            
            expressionParts[5] = ''.join(dowChars)
        
        # convert SUN-SAT format to 0-6 format
        for i, week in enumerate(WeekDay):
            expressionParts[5] = expressionParts[5].replace(week, str(i))
        
        # convert JAN-DEC format to 1-12 format
        for i, month in enumerate(Months):
            expressionParts[4] = expressionParts[4].replace(month, str(i+1))
        
        # convert 0 second to (empty)
        if expressionParts[0] == '0':
            expressionParts[0] = ''


if __name__ == '__main__':
    descriptor = CronDescriptor()
    assert "每分钟" == descriptor.getDescription("* * * * *")
    assert "每分钟" == descriptor.getDescription("*/1 * * * *")
    assert "每分钟" == descriptor.getDescription("0 0/1 * * * ?")
    assert "每小时" == descriptor.getDescription("0 0 * * * ?")
    assert "每小时" == descriptor.getDescription("0 0 0/1 * * ?")
    assert "在 23:00, 星期一 到 星期五" == descriptor.getDescription("0 23 ? * MON-FRI")
    assert "每秒" == descriptor.getDescription("* * * * * *")
    assert "每 45 秒" == descriptor.getDescription("*/45 * * * * *")
    assert "每 05 分钟" == descriptor.getDescription("*/5 * * * *")
    assert "每 10 分钟" == descriptor.getDescription("0 0/10 * * * ?")
    assert "每 05 分钟" == descriptor.getDescription("0 */5 * * * *")
    assert "在 11:30, 星期一 到 星期五" == descriptor.getDescription("30 11 * * 1-5")
    assert "在 11:30" == descriptor.getDescription("30 11 * * *")
    assert "在 11:00 和 11:10 之间的每分钟" == descriptor.getDescription("0-10 11 * * *")
    assert "每分钟, 仅在 三月" == descriptor.getDescription("* * * 3 *")
    assert "每分钟, 仅在 三月 和 六月" == descriptor.getDescription("* * * 3,6 *")
    assert "在 14:30 和 16:30" == descriptor.getDescription("30 14,16 * * *")
    assert "在 06:30, 14:30 和 16:30" == descriptor.getDescription("30 6,14,16 * * *")
    assert "在 09:46, 仅在 星期一" == descriptor.getDescription("46 9 * * 1")
    assert "在 12:23, 每月的 15 号" == descriptor.getDescription("23 12 15 * *")
    assert "在 12:23, 仅在 一月" == descriptor.getDescription("23 12 * JAN *")
    assert "在 12:23, 仅在 一月" == descriptor.getDescription("23 12 ? JAN *")
    assert "在 12:23, 一月 到 二月" == descriptor.getDescription("23 12 * JAN-FEB *")
    assert "在 12:23, 一月 到 三月" == descriptor.getDescription("23 12 * JAN-MAR *")
    assert "在 12:23, 仅在 星期日" == descriptor.getDescription("23 12 * * SUN")
    assert "每 05 分钟, 在 15:00, 星期一 到 星期五" == descriptor.getDescription("*/5 15 * * MON-FRI")
    assert "每分钟, 在 第三个星期一 每月" == descriptor.getDescription("* * * * MON#3")
    assert "每分钟, 每月的最后一个 星期四 " == descriptor.getDescription("* * * * 4L")
    assert "每 05 分钟, 每月的最后一天, 仅在 一月" == descriptor.getDescription("*/5 * L JAN *")
    assert "每分钟, 每月的最后一个平日" == descriptor.getDescription("* * LW * *")
    assert "每分钟, 每月的最后一个平日" == descriptor.getDescription("* * WL * *")
    assert "每分钟, 每月的 第一个平日 " == descriptor.getDescription("* * 1W * *")
    assert "每分钟, 每月的 第一个平日 " == descriptor.getDescription("* * W1 * *")
    assert "每分钟, 每月的 最接近 5 号的平日 " == descriptor.getDescription("* * 5W * *")
    assert "每分钟, 每月的 最接近 5 号的平日 " == descriptor.getDescription("* * W5 * *")
    assert "在 14:02:30" == descriptor.getDescription("30 02 14 * * *")
    assert "在每分钟的 05 到 10 秒" == descriptor.getDescription("5-10 * * * * *")
    assert "在每分钟的 05 到 10 秒, 在每小时的 30 到 35 分钟, 在 10:00 和 12:59 之间" == descriptor.getDescription("5-10 30-35 10-12 * * *")
    assert "在每分钟的 30 秒, 每 05 分钟" == descriptor.getDescription("30 */5 * * * *")
    assert "在每小时的 30 分, 在 10:00 和 13:59 之间, 仅在 星期三 和 星期五" == descriptor.getDescription("0 30 10-13 ? * WED,FRI")
    assert "在每分钟的 10 秒, 每 05 分钟" == descriptor.getDescription("10 0/5 * * * ?")
    assert "每 03 分钟, 在每小时的 02 到 59 分钟, 在 01:00, 09:00, 和 22:00, 在每月的 11 和 26 号之间, 一月 到 六月" == descriptor.getDescription("2-59/3 1,9,22 11-26 1-6 ?")
    assert "在 06:00" == descriptor.getDescription("0 0 6 1/1 * ?")
    assert "在每小时的 05 分" == descriptor.getDescription("0 5 0/1 * * ?")
    assert "每秒, 仅在 2013" == descriptor.getDescription("* * * * * * 2013")
    assert "每分钟, 仅在 2013 和 2014" == descriptor.getDescription("* * * * * 2013,2014")
    assert "在 12:23, 一月 到 二月, 2013 到 2014" == descriptor.getDescription("23 12 * JAN-FEB * 2013-2014")
    assert "在 12:23, 一月 到 三月, 2013 到 2015" == descriptor.getDescription("23 12 * JAN-MAR * 2013-2015")
    assert "每 30 分钟, 在 08:00 和 09:59 之间, 每月的 5 和 20 号" == descriptor.getDescription("0 0/30 8-9 5,20 * ?")
    assert "在 12:23, 在 第二个星期日 每月" == descriptor.getDescription("23 12 * * SUN#2")
    
    options = Options()
    options.dayOfWeekStartIndexZero = False
    assert "在 12:23, 在 第二个星期日 每月" == descriptor.getDescription("23 12 * * 1#2", options)
    assert "在每小时的 25 分, 每 13 小时, 在 07:00 和 19:59 之间" == descriptor.getDescription("0 25 7-19/13 ? * *")
    assert "在每小时的 25 分, 每 13 小时, 在 07:00 和 20:59 之间" == descriptor.getDescription("0 25 7-20/13 ? * *")
