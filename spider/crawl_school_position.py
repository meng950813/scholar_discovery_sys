"""
author: xiaoniu
date: 2019-03-19
desc:本代码用于根据学校名和所在的市抓取地址和经纬度坐标，
基于chen的代码更新所得，目前仅仅考虑了985和211的学校
本代码依赖于db.py和config.py
TODO：由于百度坐标抓取是异步更新，因此目前每次分析时都会刷新一次
"""
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import random

import db
from config import DB_CONFIG


class CrawlPositionSpider:

    def __init__(self):
        self.url = 'http://api.map.baidu.com/lbsapi/getpoint/index.html'
        self.browser = webdriver.Chrome()
        # 显示等待
        self.wait = WebDriverWait(self.browser, 10)
        # 初始化配置
        self.browser.get(self.url)

    def change_city(self, city):
        """
        修改当前的城市
        :param city: 城市名称 如北京市
        :return:
        """
        city_text = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"#curCityText")))
        city_text.click()

        city_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#selCityInput")))

        submit_city = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,"#selCityButton")))

        city_input.clear()
        city_input.send_keys(city)
        submit_city.click()

        print("change city to %s" % city)

    def search(self, school_name):
        """
        根据学校名进行一次搜索
        :param school_name:
        :return:
        """
        # 获取输入框
        input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#localvalue')))
        # 获取提交按钮
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#localsearch')))
        # 等待id 为 no_0 的元素出现 ==> 有响应
        # 插入搜索内容
        input.send_keys(school_name)
        # 提交搜索
        submit.click()
        div = None
        try:
            div = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#no_0')))
        except Exception as e:
            print("404 not found (%s)" % school_name)
            raise TimeoutError

        return self.browser.page_source

    def analysis(self, source):
        """
        从响应文本中抽取数据，包括经纬度及地址
        :param source: 响应文本
        :return: { "add":"xx路xx号","point":("123.123456","123.123456") }
        """
        xy = re.findall('坐标：([\d.]+),([\d.]+)', source)
        add = re.findall('地址：(.*?)<br />', source)

        # 只取第一个,并对坐标点进行字符串拼接 ("123.123456","123.123456") ==> ""123.123456,123.123456""
        return {
            "ADDRESS": add[0].strip(),
            "POSITION": ",".join(xy[0])
        }

    def close(self):
        self.browser.close()


def main():
    spider = CrawlPositionSpider()
    # 获取所有的985和211学校
    # select_sql = 'select * from es_school where LEVEL in (985,211) order by CITY'
    select_sql = 'select * from es_school where POSITION is null and LEVEL in (985,211)'
    update_sql = "update es_school set ADDRESS='%s',POSITION='%s' where ID=%d;"
    total_schools = db.select(select_sql)
    # 当前所在市
    cur_city = '北京市'
    # 写入文件
    fp = open('es_school.sql', 'w', encoding='utf-8')
    # 统计数量
    count = 0
    # 遍历学校
    for school in total_schools:
        # 是否需要切换市
        if cur_city != school['CITY']:
            spider.change_city(school['CITY'])
        # 根据学校名进行搜索
        html = spider.search(school['NAME'])
        # 提取需要的数据
        data = spider.analysis(html)
        # 刷新一次
        spider.browser.refresh()

        line = update_sql % (data['ADDRESS'], data['POSITION'], school['ID'])
        fp.write(line)
        fp.write('\n')
        count += 1
        print(school['NAME'], line)
        # 随机睡眠 避免爬取过快
        time.sleep(random.randint(3, 5))

    spider.close()
    fp.close()
    print('爬取完成，学校共%s所，更新%s所' % (len(total_schools), count))


if __name__ == '__main__':
    db.create_engine(**DB_CONFIG)
    main()
