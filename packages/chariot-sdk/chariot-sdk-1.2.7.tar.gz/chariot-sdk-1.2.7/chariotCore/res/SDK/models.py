

from pydantic import BaseModel

#   json测试文件验证类，仅用于验证json数据的验证
class PLUGIN_TEST_MODEL(BaseModel):
    version: str
    type: str
    body: dict
