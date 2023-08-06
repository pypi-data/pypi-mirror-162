import json

import tornado.web

from rest_framework.filter import BaseFilter
from rest_framework.model import BaseModel


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self) -> None:
        self.query_condition = self.parse_query_arguments()  # 查询条件
        self.update_condition = self.parse_body_arguments()  #

    def parse_query_arguments(self):
        query_condition = {}
        filter_class = self.get_filter_class()
        if not filter_class:
            return
        for key in filter_class.__annotations__.keys():
            if self.request.query_arguments.__contains__(key):
                query_condition[key] = self.request.query_arguments.get(key)[0].decode()
        return query_condition

    def parse_body_arguments(self):
        update_condition = {}
        serializer_class = self.get_serializer_class()
        for key in serializer_class.Meta.fields:
            if self.request.body_arguments.__contains__(key):
                update_condition[key] = self.request.body_arguments.get(key)[0].decode()
        return update_condition

    def get_update_condition(self):
        return getattr(self, "update_condition", None)

    def get_query_condition(self):
        return getattr(self, "query_condition", None)

    def get_query_set(self):
        return getattr(self, "query_set", None)

    def get_model_class(self):
        model_class = getattr(self, "model_class", None)
        assert issubclass(model_class, BaseModel)
        return model_class

    def get_serializer_class(self):
        return getattr(self, "serializer_class", None)

    def get_filter_class(self):
        if (filter_class := getattr(self, "filter_class", None)) is None:
            return
        assert issubclass(filter_class, BaseFilter)
        return filter_class


class ListHandler(BaseHandler):

    async def get(self, *args, **kwargs):
        model_class = self.get_model_class()
        model = model_class().filter(self.get_query_condition())
        self.write(json.dumps(model, ensure_ascii=False))

    async def post(self, *args, **kwargs):
        model_class = self.get_model_class()
        model = model_class().create(self.get_update_condition())
        self.write(json.dumps(model, ensure_ascii=False))


class DetailHandler(BaseHandler):

    async def get(self, **kwargs):
        model_class = self.get_model_class()
        model = model_class().get(kwargs["id"])
        self.write(json.dumps(model, ensure_ascii=False))

    async def put(self, **kwargs):
        model_class = self.get_model_class()
        model = model_class().update(kwargs["id"], self.get_update_condition())
        self.write(json.dumps(model, ensure_ascii=False))

    async def patch(self, **kwargs):
        model_class = self.get_model_class()
        model = model_class().update(kwargs["id"], self.get_update_condition(), partial=True)
        self.write(json.dumps(model, ensure_ascii=False))

    async def delete(self, **kwargs):
        model_class = self.get_model_class()
        model = model_class().delete(kwargs["id"])
        self.write(json.dumps(model, ensure_ascii=False))
