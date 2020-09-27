import inspect

from marshmallow import Schema, post_load

from leaguedirector.libs.scheme.baseScheme import BaseSchema


class BaseClassSchema(BaseSchema):

    def getClass(self):
        raise Exception("no implements")

    @post_load
    def postLoad(self, data, **kwargs):
        signature = inspect.signature(self.getClass().__init__)

        args = {}
        for arg in signature.parameters:
            if arg == 'self' or arg == 'args' or arg == 'kwargs':
                continue
            args[arg] = data[arg]

        instance = self.getClass()(**args)

        for prop, val in data.items():
            setattr(instance, prop, val)

        return instance
