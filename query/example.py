from utils.query import query_all

#搜索学校

#无限制范围（全国范围内搜索）
#返回学校的搜索结果，学校名+省+城市名+评分
result =query_all('学校','发动机')
print(result)
#
# #有限制范围(本例中限制在北京市内搜索）
# result = query_all('学校','发动机','北京市')
# print(result)

#搜索院系

#无限制范围（全国范围内搜索）
# result =query_all('学院','发动机')
# print(result)

#有限制范围(本例中限制在清华大学内搜索）
# result = query_all('学院','发动机','清华大学')
# print(result)

#搜索教师
# 无限制范围（全国范围内搜索）
# result =query_all('教师','发动机')
# print(result)

#有限制范围(本例中限制清华上海交通大学航空航天学院（由学院id限制搜索）
# result = query_all('学校','发动机','752')
# print(result)





