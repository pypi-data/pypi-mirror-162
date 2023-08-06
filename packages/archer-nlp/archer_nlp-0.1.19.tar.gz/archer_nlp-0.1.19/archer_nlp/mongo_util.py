import sys

from pymongo import MongoClient
from json import JSONEncoder
from bson import ObjectId

from archer_nlp.common_utils import except_info


class ObjectIdJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return JSONEncoder.default(self, o)


class Mongo:
    def __init__(self, config=None):
        self.config = config
        self.db = self.get_database()

    def get_database(self):
        try:
            client = MongoClient(self.config.get('host', '127.0.0.1'), self.config.get('port', 27017))
            db = client.get_database(self.config.get('db_name', ''))
            user = self.config.get("db_user", '')
            pwd = self.config.get("db_pwd", '')
            if user and pwd:
                db.authenticate(user, pwd)
            return db
        except Exception as e:
            print(except_info(e))
            raise Exception('connect to mongo error!')

    def get_list(self, table, where={}, columns=None):
        try:
            if columns is None:
                data = self.db[table].find(where)
            else:
                data = self.db[table].find(where, columns)

            return data
        except Exception as e:
            print(except_info(e))
            return None

    def get_list_by_limit(self, table, where={}, start=0, limit=30):
        try:
            return self.db[table].find(where).skip(start).limit(limit)
        except Exception as e:
            print(except_info(e))
            return None

    def get_count(self, table, where={}):
        try:
            if where:
                count = self.db[table].count_documents(where)
            else:
                count = self.db[table].estimated_document_count()
            return count
        except Exception as e:
            print(except_info(e))
            return None

    def insert(self, table, data):
        try:
            return self.db[table].insert(data)
        except Exception as e:
            print(except_info(e))
            return None

    def del_primary_id(self, data, where):
        """
        当更新操作的时候，由于data包含了_id，而where条件搜索出来的数据的主键不是该_id，会引起MongoDB异常
        :param data: 需要更新的数据
        :param where: 更新条件
        :return: 返回主键_id，注意有可能为None值
        """
        primary_id = None
        if where and data and '_id' in data and data['_id']:
            primary_id = data['_id']
            del data['_id']
        return primary_id

    def update(self, table, data, where={}, multi=False):
        try:
            primary_id = self.del_primary_id(data, where)
            return self.db[table].update(where, data, multi=multi)
        except Exception as e:
            print(except_info(e))
            return None
        finally:
            if primary_id:
                data['_id'] = primary_id

    def deleteMany(self, table, where={}):
        """
        清空数据，也可删除指定条件数据
        :param table:
        :param where:
        :return:
        """
        try:
            return self.db[table].delete_many(where)
        except Exception as e:
            print(except_info(e))
            return None
