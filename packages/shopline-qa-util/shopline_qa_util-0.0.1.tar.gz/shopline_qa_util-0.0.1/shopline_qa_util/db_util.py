import requests
import json
import time

query_single_host = 'http://127.0.0.1:8090/api/query/single'
query_reference_host = 'http://127.0.0.1:8090/api/query/single'
result_host = 'http://127.0.0.1:8090/api/sql/result/'


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
    5、根据sql_record_id查询sql执行结果
    6、如果执行结果的code是7001, 或2000, 前者说明执行失败, 后者说明执行成功, 则直接返回
    7、如果执行结果的code是7000, 则继续轮询
    :param url:
    :param data:
    :return:
    """
    response = requests.post(url, data=data)
    result_body = {}
    if response.status_code != 200:
        result_body = {
            "statusCode": response.status_code,
            "bodyText": response.text
        }
        return result_body
    body = json.loads(response.text)
    if body['code'] != 2000:
        return body
    sql_record_id = body['data']

    # 等待5秒后再查询结果, 一共查询两分钟
    index = 0
    while index < 24:
        time.sleep(5)
        result_response = requests.get(result_host + str(sql_record_id))
        if result_response.status_code != 200:
            result_body = {
                "statusCode": result_response.status_code,
                "bodyText": result_response.text
            }
            break
        result_body = json.loads(result_response.text)
        if result_body['code'] != 7000:
            break
        index += 1
    return result_body

