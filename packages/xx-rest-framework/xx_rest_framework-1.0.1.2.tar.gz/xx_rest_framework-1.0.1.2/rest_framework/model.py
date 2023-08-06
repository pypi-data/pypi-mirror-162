from rest_framework.conf import config
from rest_framework.torndb import Connection


class BaseModel(object):
    """"""

    def __init__(self):
        self.db = Connection(**config["mysql"])

    def filter(self, query_condition):
        """过滤"""
        assert isinstance(query_condition, dict)
        parameters = [f'%{value}%' for value in query_condition.values()]
        where = " AND ".join([f"{key} LIKE %s" for key in query_condition.keys()])
        where = f"WHERE {where}" if where else ""
        query = f"SELECT * FROM {self.Meta.table_name} {where}"
        return self.db.query(query, *parameters)

    def get(self, pk):
        """获取单个"""
        query = f"SELECT * FROM {self.Meta.table_name} WHERE `id` = %s"
        return self.db.get(query, pk)

    def create(self, data):
        """新增"""
        assert isinstance(data, dict)
        fields = ", ".join(data.keys())
        values = ", ".join([f"'{item}'" for item in data.values()])
        sql = f"INSERT INTO {self.Meta.table_name} ({fields}) VALUES ({values})"
        return self.db.execute(sql)

    def update(self, pk, data, partial=False):
        """更新"""
        return self.partial_update(pk, data)

    def partial_update(self, pk, data):
        """部分更新"""
        assert isinstance(data, dict)
        update_condition = ", ".join([f"{key}='{value}'" for key, value in data.items()])
        if not update_condition:
            return
        sql = f"UPDATE {self.Meta.table_name} SET {update_condition} WHERE `id` = {pk}"
        print(sql)
        return self.db.execute(sql)

    def delete(self, pk):
        """删除"""
        query = f"DELETE FROM {self.Meta.table_name} WHERE id = %s"
        return self.db.execute(query, pk)
