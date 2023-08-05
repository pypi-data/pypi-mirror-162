#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : aizoo.
# @File         : demo
# @Time         : 2022/7/15 上午10:23
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


from pinferencia import Server

# ME
from meutils.pipe import *
from meutils.str_utils import json_loads


class MyModel:

    @lru_cache()
    def predict(self, data):
        time.sleep(3)
        return json_loads(data)


model = MyModel()

service = Server()
service.register(model_name="mymodel", model=model, entrypoint="predict")
