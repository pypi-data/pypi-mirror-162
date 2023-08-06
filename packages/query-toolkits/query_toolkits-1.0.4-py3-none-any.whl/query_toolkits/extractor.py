#!/usr/bin/python3.7
# -*- coding: utf-8 -*-

import re
# 第一个datetime是包，第二个datetime是模块
#import time
from datetime import datetime, timedelta
#import jieba.posseg as psg


class Extractor:

    def _check_time_valid(self, word):
        m = re.match("\d+$", word)
        if m:
            if len(word) <= 6:
                return None
        word1 = re.sub('[号|日]\d+$', '日', word)
        if word1 != word:
            return self._check_time_valid(word1)
        else:
            return word1


    def _check_valid(self, number_str, type):
        special_num_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
        if type == "year":
            if int(number_str) > 1000 and int(number_str) < 3000:
                return True
        elif type == "month":
            if number_str in list(map(str, range(1, 13))) + special_num_list:
                return True
        elif type == "day":
            if number_str in list(map(str, range(1, 32))) + special_num_list:
                return True
        elif type == "hour":
            if number_str in list(map(str, range(0, 25))) + special_num_list + ["00"]:
                return True
        elif type == "second":
            if number_str in list(map(str, range(0, 61))) + special_num_list + ["00"]:
                return True
        elif type == "minute":
            if number_str in list(map(str, range(0, 61))) + special_num_list + ["00"]:
                return True
        return False


    def _fill_slot(self, text):
        year = None
        month = None
        day = None
        hour = None
        second = None
        minute = None
        case_year = "(\d{4})年"
        case_month = "(\d{1,2})(月份|月)"
        case_day = "(\d{1,2})[日|号]"
        case_hour = "(\d{1,2})[点|时]"
        case_second = "(\d{1,2})(分钟|分)"
        case_minute = "(\d{1,2})秒"
        key_year = {'今年': 0, '去年': -1, '前年': -2, "明年": 1, "前一年": -1, "大前年":-3}
        for key in key_year:
            if key in text:
                year = str(datetime.now().year + key_year[key])
        res_year = re.search(case_year, text)
        res_month = re.search(case_month, text)
        res_day = re.search(case_day, text)
        res_hour = re.search(case_hour, text)
        res_second = re.search(case_second, text)
        res_minute = re.search(case_minute, text)
        if res_year:
            year = res_year.group(1)
        if res_month:
            month = res_month.group(1)
        if res_day:
            day = res_day.group(1)
        if res_hour:
            hour = res_hour.group(1)
        if res_second:
            second = res_second.group(1)
        if res_minute:
            minute = res_minute.group(1)
        case_year_month_day = "(\d{4})[-\./](\d{1,2})[-\./](\d{1,2})"
        res_year_month_day = re.search(case_year_month_day, text)
        if res_year_month_day:
            year = res_year_month_day.group(1)
            month = res_year_month_day.group(2)
            day = res_year_month_day.group(3)
            if not(self._check_valid(year, "year") and self._check_valid(month, "month") and self._check_valid(day, "day")):
                year = None
                month = None
                day = None

        case_year_month_day = "^(\d{4})年(\d{1,2})月(\d{1,2})$"
        res_year_month_day = re.search(case_year_month_day, text)
        if res_year_month_day:
            year = res_year_month_day.group(1)
            month = res_year_month_day.group(2)
            day = res_year_month_day.group(3)
            if not (self._check_valid(year, "year") and self._check_valid(month, "month") and self._check_valid(day, "day")):
                year = None
                month = None
                day = None

        case_year_month = "(\d{4})[-\./](\d{1,2})"
        res_year_month = re.search(case_year_month, text)
        if res_year_month:
            year = res_year_month.group(1)
            month = res_year_month.group(2)
            if not (self._check_valid(year, "year") and self._check_valid(month, "month")):
                year = None
                month = None

        case_hour_second_minute = "(\d{2})[:：](\d{2})[:：](\d{2})"
        res_hour_second_minute = re.search(case_hour_second_minute, text)
        if res_hour_second_minute:
            hour = res_hour_second_minute.group(1)
            second = res_hour_second_minute.group(2)
            minute = res_hour_second_minute.group(3)
            if not (self._check_valid(hour, "hour") and self._check_valid(second, "second") and self._check_valid(minute, "minute")):
                hour = None
                second = None
                minute = None

        case_month_day = "^(d{1,2})月(\d{1,2})$"
        res_month_day = re.search(case_month_day, text)
        if res_month_day:
            month = res_month_day.group(1)
            day = res_month_day.group(2)
            if not (self._check_valid(month, "month") and self._check_valid(day, "day")):
                month = None
                day = None


        case_hour_second = "(\d{2})[:：](\d{2})"
        res_hour_second = re.search(case_hour_second, text)
        if res_hour_second:
            hour = res_hour_second.group(1)
            second = res_hour_second.group(2)
            if not (self._check_valid(hour, "hour") and self._check_valid(second, "second")):
                hour = None
                second = None

        if year:
            year = int(year) if self._check_valid(year, "year") else None
        if month:
            month = int(month) if self._check_valid(month, "month") else None
        if day:
            day = int(day) if self._check_valid(day, "day") else None
        if hour:
            hour = int(hour) if self._check_valid(hour, "hour") else None
        if second:
            second = int(second) if self._check_valid(second, "second") else None
        if minute:
            minute = int(minute) if self._check_valid(minute, "minute") else None

        if year or month or day or hour or second or minute:
            return (year, month, day, hour, second, minute)
        return None



    def _compare_res(self, res1, res2):
        win1, win2 = True, True
        for elem1, elem2 in zip(res1, res2):
            if elem1 is not None and elem2 is not None and elem1 != elem2:
                return -1
            if elem1 is None and elem2 is not None:
                win1 = False
            elif elem2 is None and elem1 is not None:
                win2 = False
        if win1:
            return 1
        if win2:
            return 0
        return -1



    # 时间提取
    def extract_time(self, text, cut_res):
        time_res = []
        date_list = []
        index_list = []
        # 字典键值对用冒号分割，每个键值对之间用逗号分割，整个字典包括在花括号{}中
        # dict.get(key, default=None)返回指定键的值，如果值不在字典中返回default值
        key_date = {'前天': -2, '前日': -2, '昨天': -1, '昨日': -1, '今天': 0, '今日': 0, '明天': 1, '明日': 1, '后天': 2, "现在": 0}
        week_day = {'周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周天': 6, '周日': 6,
                    "上周一":-7, "上周二":-6, "上周三":-5, "上周四":-4, "上周五":-3, "上周六":-2, "上周日":-1, "上周天":-1,
                    "上上周一":-14, "上上周二":-13, "上上周三":-12, "上上周四":-11, "上上周五":-10, "上上周六":-9, "上上周日":-8, "上上周天":-8}

        # 检测英文写法日期8位数字
        date_dig = re.finditer(
            "(去年|今年|前年|明年|前一年)?\d{1,2}月\d{1,2}[号|日]|\d{4}年\d{1,2}月\d{1,2}[号|日]|\d{4}[-\./]\d{1,2}[-\./]\d{1,2}|"
            "\d{4}年\d{1,2}月|\d{4}-\d{1,2}|\d{4}\.\d{1,2}|\d{4}/\d{1,2}|"
            "\d{2}[:：]\d{2}([:：]\d{2})?|\d{1,2}[点｜时]\d{1,2}[分｜分钟](\d{1,2}[秒])?",
            text)
        if date_dig:
            for dd in date_dig:
                date_list.append(dd.group(0))
                index_list.append(dd.span())
        phrase = ""
        phrase_list = []
        for i, (k, v) in enumerate(cut_res):
            if k in key_date:
                word = (datetime.today() + timedelta(days=key_date.get(k, 0))).strftime(
                    '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
                time_res.append(word)
            elif k in week_day:
                today_num = datetime.weekday(datetime.today())
                delta_num = (week_day.get(cut_res[i - 1].word + k) if (i >= 1 and (cut_res[i - 1].word + k) in week_day) else week_day.get(k)) - today_num
                word = (datetime.today() + timedelta(delta_num)).strftime(
                        '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
                time_res.append(word)
            elif v in ("m", "t", "x"):
                phrase += k
            elif v not in ("m", "t", "x") and phrase != "":
                phrase_list.append(phrase)
                phrase = ""
        if phrase != "":
            phrase_list.append(phrase)

        result = list(filter(lambda x: x is not None, [self._check_time_valid(w) for w in time_res + date_list + phrase_list]))
        final_res = [self._fill_slot(x) for x in result]
        final_res = [x for x in final_res if x is not None]
        final_res_copy = final_res.copy()
        remove_set = set()
        final_res = []
        for i1, res1 in enumerate(final_res_copy):
            for i2 in range(i1, len(final_res_copy)):
                res2 = final_res_copy[i2]
                if i1 != i2:
                    tmp_index = self._compare_res(res1, res2)
                    if tmp_index != -1:
                        remove_set.add([i1, i2][tmp_index])
        for i in range(len(final_res_copy)):
            if i not in remove_set:
                final_res.append(final_res_copy[i])
        return final_res




    def extract_number(self, cut_res):
        direct_transform = {
            "个百分点": ["%", 1],

            "M": ["米", 1],
            "毫米": ["米", 0.001],
            "mm": ["米", 0.001],
            "厘米": ["米", 0.01],
            "cm":  ["米", 0.01],
            "分米": ["米", 0.1],
            "微米": ["米", 0.000001],
            "千米": ["米", 1000],
            "KM": ["米", 1000],
            "公里": ["米", 1000],
            "μm": ["米", 0.000001],
            "英寸": ["米", 0.0254],
            "inch": ["米", 0.0254],
            "里": ["米", 500],
            "尺": ["米", 0.3333333],

            "毫升": ["L", 0.001],
            "mL": ["L", 0.001],
            "升": ["L", 1],
            "L": ["L", 1],
            "nL": ["L", 0.000000001],
            "纳升": ["L", 0.000000001],
            "立方米": ["L", 1000],
            "立方分米": ["L", 1],
            "立方厘米": ["L", 0.001],
            "立方毫米": ["L", 0.000001],
            "分升": ["L", 0.1],
            "厘升": ["L", 0.01],

            "平方千米": ["平方米", 1000000],
            "公顷": ["平方米", 10000],
            "平": ["平方米", 1],
            "亩": ["平方米", 666.666666667],

            "千克": ["千克", 1],
            "吨": ["千克", 1000],
            "g": ["千克", 0.001],
            "克": ["千克", 0.001],
            "公斤": ["千克", 1],
            "斤": ["千克", 0.5],
            "kg": ["千克", 1],
            "t": ["千克", 1000],
            "lb": ["千克", 0.4535924],

            "人民币": ["元", 1],

            "倍": ["倍", 1],
            "辆": ["辆", 1],
            "元": ["元", 1],

            "米": ["米", 1],
            "%": ["%", 1],
            "平方米": ["平方米", 1],
            "个": ["个", 1],
            "股": ["股", 1],
            "人次": ["人次", 1],
            "颗": ["颗", 1],
            "台": ["台", 1],
            "瓶": ["瓶", 1],
            "张": ["张", 1],
            "篇": ["篇", 1],
            "件": ["件", 1],

            "伏特": ["V", 1],
            "V": ["V", 1],
            "伏": ["V", 1],

            "赫兹": ["Hz", 1],
            "Hz": ["Hz", 1],

            "瓦": ["W", 1],
            "瓦特": ["W", 1],
            "千瓦": ["W", 1000],
            "W": ["W", 1],
            "kW": ["W", 1000],

        }

        general_transform = {
            "万": 10000,
            "亿": 100000000,
            "万亿": 1000000000000,
            "万万": 100000000,
            "千": 1000,
            "百": 100,
            "千万": 10000000,
            "万千": 10000000
        }

        #分词、词性
        candidates = []
        candidate = ""
        start_index = None
        end_index = 0
        for i, (word, flag) in enumerate(cut_res):
            end_index += len(word)
            if flag in ("m", "q", "mq"):
                if not start_index:
                    start_index = end_index - len(word)
                candidate += word
            elif word == "%":
                candidate += word
                candidates.append((candidate, start_index, end_index))
                start_index = None
                candidate = ""
            else:
                if candidate != "":
                    candidates.append((candidate, start_index, end_index))
                    start_index = None
                candidate = ""
        if candidate != "":
            candidates.append((candidate, start_index, end_index))
        final_res = []
        #再正则处理
        pattern = "^([0-9]+(\.[0-9]+)?)([^0-9]+)$"
        for candidate in candidates:
            word, start_index, end_index = candidate[0], candidate[1], candidate[2]
            res = re.search(pattern, word)
            if res:
                number = float(res.group(1))
                unit = res.group(3)
                if unit in direct_transform:
                    norm_unit = direct_transform[unit]
                    unit, times = norm_unit[0], norm_unit[1]
                    number *= times
                    final_res.append((number, unit, start_index, end_index))
                else:
                    for i in range(1, len(unit)):
                        if unit[i:] in direct_transform:
                            norm_unit = direct_transform[unit[i:]]
                            tmp_unit, times = norm_unit[0], norm_unit[1]
                            number *= times
                            if unit[:i] in general_transform:
                                number *= general_transform[unit[:i]]
                                final_res.append((number, tmp_unit, start_index, end_index))
        return final_res



et = Extractor()
import jieba.posseg as psg
li = [
    "今年产量10万吨",
    "今年产量10.5L",
    "pe 15倍的股票",
    "涨了15%的股票",
    "10万亿元",
    "234立方厘米",
    "目标是5个百分点"
]

for text in li:
    cut_res = psg.lcut(text)
    print(cut_res)
    res = et.extract_number(cut_res)
    print(res)



















"""
if __name__ == '__main__':
    et = Extractor()
    print(datetime.today())
    start = time.time()
    # text = "2021-03-0914:00开庭审理杨峰？"
    # get_range_time_from_query(text)
    # exit(0)
    li = [
        '上周六的股票',
        '我前天来的',
        '我今天到的',
        '12月26号的天气怎么样',
        '2020.10.03的2022.1.5利率是多少？',
        "周二的api是多少",
        "2018/1/1,利率",
        "现在，利率",
        "8月1日，利率",
        "9.8，利率",
        "第3026期，利率",
        "2019年7月1日的利率是多少",
        "2020年8月1日 利率",
        "8月1日 利率",
        "1月5日 利率",
        "2022年11月1日中国历史",
        "中国2021年9月18日历史",
        "利现在，率",
        "利2018/1/1,率",
        "利8月1日 率",
        "20年8月1日 利率",
        '的2022.1.5利率是多少？',
        '去年9月10日利率是多少？',
        '2020年12月利率是多少？',
        '2020.1/26利率是多少？',
        '利率2020.1/26是多少？',
        '利率是多少？2020.1/26',
        '利率2020.1月26是多少？',
        '利率2020年1月2日是多少？',
        '我可以9月10日利率是多少？',
        '2021-03-09 14:00开庭审理杨峰',
        '2021-03-0914:00开庭审理杨峰',
        '01-09 14:00开庭审理杨峰',
        '03 09 yuhuagangtie',
        '2022年11月12日 14:00开庭审理杨峰',
        '我上上周五的时候利率',
        '2015年3月5日 14：32到5月22日 13：00',
        '1993年5月28',
        '大前年',
        '达观数据']
    for text in li:
        cut_res = list(psg.cut(text))
        #print(text, get_range_time_from_query(text), sep=':')
        print(text)
        res = et.time_extract(text, cut_res)
        print(res)
    print((time.time() - start)/len(li))

"""