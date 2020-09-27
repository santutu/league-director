from marshmallow import Schema, INCLUDE
import json
import os


class BaseSchema(Schema):
    class Meta:
        ordered = True
        unknown = INCLUDE

    def toJson(self, obj):
        return self.dumps(obj)

    def loadFromJsonFile(self, jsonFilePath: str):
        if not os.path.isfile(jsonFilePath):
            raise Exception(f"cant not find {jsonFilePath}")
        with open(jsonFilePath, 'r', encoding='UTF8') as f:
            obj = json.load(f)

        return self.load(obj)

    def saveToJson(self, jsonPath: str, obj):
        with open(jsonPath, 'w') as f:
            f.write(self.dumps(obj))
