from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session
from tornado.options import options


class SqlAlchemyHelper:
    def __init__(self, pool):
        """
        初始化sql工具
        :param pool: 连接池名称
        """
        if isinstance(pool, str):
            self.pool, self.dialect = options.database[pool]
        else:
            self.pool = pool

    def make_session(self, autocommit=True, **kwargs):
        session = Session(self.pool, autocommit=autocommit, **kwargs)
        return session


def alchemy_default_to_dict(params, data, repetition=False):
    data_list = []
    key_list = []
    if repetition:
        for arg in params:
            if arg.key:
                key_list.append(arg.key)
            else:
                key_list.append(arg.name)
    else:
        for arg in params:
            arg = str(arg)
            if "(" in arg and ")" in arg:
                key_list.append(arg.split(".")[-1][:-1])
            else:
                key_list.append(arg.split(".")[-1])
    if isinstance(data, list):
        for d in data:
            dict_data = dict(zip(key_list, d))
            data_list.append(dict_data)
        return data_list
    else:
        if data:
            return dict(zip(key_list, data))
        else:
            return {}


def sqlalchemy_paging(Query, limit_number, offset_number):
    data_list = Query.limit(limit_number).offset(offset_number).all()
    data_count = Query.count()
    return {"count": data_count, "dataSource": data_list}


def query_set_to_dict(obj):
    if hasattr(obj, "__table__"):
        obj_dict = {}
        for column in obj.__table__.columns.keys():
            if hasattr(obj, column):
                val = getattr(obj, column)
                if isinstance(val, Decimal):
                    val = float(val)
                obj_dict[column] = val
        return obj_dict
    else:
        return dict(obj)


def query_set_to_list(query_set):
    ret_list = []
    for obj in query_set:
        ret_dict = query_set_to_dict(obj)
        ret_list.append(ret_dict)
    return ret_list


def result_to_json(data):
    if isinstance(data, list):
        return query_set_to_list(data)
    else:
        return query_set_to_dict(data)


def result_page(query, page_num=1, page_size=10):
    offset_number = (page_num - 1) * page_size if page_num >= 1 else 0
    data_list = result_to_json(query.limit(page_size).offset(offset_number).all())
    data_count = query.count()
    return {"count": data_count, "dataSource": data_list}
