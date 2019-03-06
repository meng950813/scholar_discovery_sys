"""
created by chen
2019/3/5

该文件是用于获取高校学院地图坐标的爬虫

主要基于百度地图的 坐标拾取系统 (http://api.map.baidu.com/lbsapi/getpoint/index.html) 获取数据

使用该网站需要给定的数据包括 ： 学校名，学院名，以及学院所在城市

爬虫会根据返回值，利用正则 获取其中的地址及坐标

可以根据需要写入文件，本次操作最终会生成一个 .sql 的文件
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import random

import sys
# 退回上级目录
sys.path.append("..")

from dbhelper import DBhelper

class spider_baiduMap(object):
    def __init__(self):
        # 火狐浏览器地址
        self.binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        # 启动火狐的插件地址
        self.geck = r'D:\Program Files\geckodriver-v0.24.0-win64\geckodriver.exe'

        # 创建浏览器驱动对象
        self.driver = webdriver.Firefox(firefox_binary = self.binary, executable_path = self.geck)

        self.basicSetting()

    def basicSetting(self):
        # 设定爬取目标
        self.driver.get('http://api.map.baidu.com/lbsapi/getpoint/index.html')
        # 显式等待，设置timeout
        self.wait = WebDriverWait(self.driver, 9)

        # 判断输入框是否加载
        self.input = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#localvalue')))

        # 判断搜索按钮是否加载
        self.submit = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#localsearch')))

    def changeCity(self,city):
        """
        修改城市信息
        :param city: 城市名
        :return:
        """
        cityText = self.wait.until(
            EC.element_to_be_clickable(
                ( By.CSS_SELECTOR,"#curCityText")
            )
        )
        cityText.click()

        cityInput = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,"#selCityInput")
            )
        )

        submitCity = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,"#selCityButton")
            )
        )

        cityInput.clear()
        cityInput.send_keys(city)
        submitCity.click()

        print("change city to %s" % city)

    def searchOne(self,key):
        """
        根据学校名及学院名进行一次搜索
        :param key: 学校名+学院名 eg: 清华大学材料学院
        :return:
        """
        # 清空搜索框
        self.input.clear()
        # 插入搜索内容
        self.input.send_keys(key)
        # 提交搜索
        self.submit.click()

        # 等待id 为 no_0 的元素出现 ==> 有响应
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#no_0')))
        except Exception as e:
            print("404 not found (%s)" % key)
            raise TimeoutError

        # 获取网页文本，提取经纬度
        return self.analy(self.driver.page_source)

    def analy(self,source):
        """
        从响应文本中抽取数据，包括经纬度及地址
        :param source: 响应文本
        :return: { "add":"xx路xx号","point":("123.123456","123.123456") }
        """
        xy = re.findall('坐标：([\d.]+),([\d.]+)', source)
        add = re.findall('地址：(.*?)<br>', source)

        # 只取第一个,并对坐标点进行字符串拼接 ("123.123456","123.123456") ==> ""123.123456,123.123456""
        return {"add" : add[0].strip(), "point" : ",".join(xy[0])}


    def closeConnection(self):
        """
        关闭浏览器驱动连接
        :return:
        """
        self.driver.close()

    def run(self,add_list):
        """
        给定一个搜索列表，完成搜索
        :param add_list: 搜索地址列表
        :return:
        """
        for add in add_list:
            time.sleep(5)
            print(add,self.searchOne(add))


class getDBData(object):
    """
    从数据库中获取数据的类
    """
    def __init__(self):
        self.DB = DBhelper

        # 字典，保存学院信息，格式： insitution_id:{school_name:"xx",institution_name:"xxx",city:"xx市"}
        self.insitution_info = {}

        # 表示当前定位城市
        self.nowCity = "北京市"

        # 记录错误数据，元素为 字符串：" 学院id, 学校名，学院名 "
        self.ERROR = []
        self.getInfoFromDB()

    def getInfoFromDB(self):
        """
        从数据库中获取学校及学院地址数据
        :return:
        """
        sql = "SELECT es_institution.ID,SCHOOL_NAME,es_institution.`NAME`,CITY FROM es_institution LEFT JOIN es_school ON es_institution.SCHOOL_ID = es_school.ID  ORDER BY CITY "
        data = self.DB.execute(sql,errorMsg = "left join 查询学院地址数据")
        self.formatData2Dict(data)

    def formatData2Dict(self,data):
        """
        将从数据返回的数据格式化为 dict 形式
        :param data: ((es_institution.ID,SCHOOL_NAME,es_institution.`NAME`,CITY),....)
        :return:
        """
        for item in data:
            self.insitution_info[item[0]] = {
                "school_name":item[1],
                "institution_name":item[2],
                "city":item[3]
            }

        print("**"*30)
        print("format data successful")
        print("**" * 30)

    def getInstitutionDict(self):
        """
        将数据返回
        :return:
        """
        return self.insitution_info

    def isNowCity(self,city_name):
        """
        表示传入的参数是否与当前城市名相同
        :param city_name: 城市名
        :return: True or False
        """
        return self.nowCity == city_name

    def setNowCity(self,city_name):
        """
        重置城市名
        :param city_name:
        :return:
        """
        self.nowCity = city_name

    def addError(self,id,item):
        """
        记录错误/无法查询到的内容
        :param id: 学院id
        :param item: 学院名，学校名
        :return:
        """
        self.ERROR.append("%s , %s ,%s " % (id, item['school_name'],item['institution_name'] ) )

    def writeError(self):
        """
        返回ERROR列表中的内容，写入文件
        :return: None
        """
        # 若 ERROR 列表中记录为 0 ，结束
        if len(self.ERROR) == 0:
            return

        print("has error record ,total num is  %s " % len(self.ERROR))

        with open("error.log","a",encoding = "utf-8") as f:
            for i in range(len(self.ERROR)):
                f.write(self.ERROR[i] + "\n")

if __name__ == '__main__':
    # addlist = ['清华大学材料学院','清华大学软件学院','清华大学航空航天学院',
    #            '清华大学计算机学院','清华大学土木水利学院']
    # add_hunan = ["湖南大学机器人学院","湖南大学工商管理学院"]
    # spider = spider_baiduMap()
    # spider.changeCity("湖南")
    # spider.run(add_hunan)
    # spider.changeCity("北京")
    # spider.run(addlist)
    #
    # spider.closeConnection()

    # 清华大学材料学院 {'北京市海淀区双清路30号清华园清华大学      ',"point": ('116.340541', '40.004187')}

    count = 0

    DBData = getDBData()
    addDict = DBData.getInstitutionDict()

    spider = spider_baiduMap()

    # print(addDict)
    basic_sql = "update es_institution set INSTITUTION_ADDRESS = '%s', POSITION = '%s' where ID = %d"
    with open("position.sql","a",encoding="utf-8") as f:
        for id in addDict:

            item , city = addDict[id], addDict[id]['city']

            # 若当前城市名与上一个不同，则重置城市
            if not DBData.isNowCity(city):
                DBData.setNowCity(city)
                spider.changeCity(city)

            try:
                # 获取查询结果 : {"add":'双清路30号清华大学',"point":'116.340188,40.007008'}
                back = spider.searchOne(item['school_name']+item['institution_name'])
                sql = basic_sql % (back["add"],back["point"],id)

                print(sql)

                f.write(sql)
                f.write("\n")

                count += 1
                print(" %d items processed ,now is ( %s : %s ) " % (count,item['school_name'],item['institution_name']))

                time.sleep(random.randint(3,5))
            except Exception as e:
                print("finally catch error : %s" % e)
                DBData.addError(id,item)

    DBData.writeError()

    spider.closeConnection()