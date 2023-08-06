import requests
import json
import time

query_single_host = 'http://sl-trade-qa.myshopline.com/api/query/single'
query_reference_host = 'http://sl-trade-qa.myshopline.com/api/query/reference'
result_host = 'http://sl-trade-qa.myshopline.com/api/sql/result/'
headers = {
    "content-type": "application/json"
}


def single(data):
    """
    单表查询
    :param data:
    :return: response.body
    """
    return query(query_single_host, data)


def reference(data):
    """
    引用查询
    :param data:
    :return: response.body
    """
    return query(query_reference_host, data)


def query(url, data):
    """
    1、发起sql执行请求
    2、如果http响应的code不是200, 则组装好status_code和text并返回
    3、如果http响应体的code不是2000, 则将body直接返回
    4、从body中获取sql_record_id
    5、先等1秒再根据sql_record_id查询结果
    6、如果执行结果的code是7000, 说明sql还没开始查询, 则继续轮询, 每隔5秒查询1次, 会轮询2分钟
    7、如果执行结果的code不是7000, 都是直接返回
        7.1、code=7001, 查询失败
        7.2、code=2000, 查询成功
    :param url:
    :param data:
    :return:
    """
    response = requests.post(url, json=data, headers=headers)
    result_body = {}
    if response.status_code != 200:
        result_body = {
            "code": response.status_code,
            "data": response.text
        }
        return result_body
    body = json.loads(response.text)
    if body['code'] != 2000:
        return body
    sql_record_id = body['data']

    index = 0
    time.sleep(1)
    while index < 24:
        result_response = requests.get(result_host + str(sql_record_id), headers=headers)
        if result_response.status_code != 200:
            result_body = {
                "code": result_response.status_code,
                "data": result_response.text
            }
            break
        result_body = json.loads(result_response.text)
        if result_body['code'] != 7000:
            break
        index += 1
        time.sleep(5)

    return result_body

