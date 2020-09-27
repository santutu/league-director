from marshmallow import fields

from leaguedirector.libs.scheme.baseClassSchema import BaseClassSchema
from leaguedirector.visible.visible import Visible


class VisibleScheme(BaseClassSchema):
    def getClass(self):
        return Visible

    fogOfWar = fields.Field()
    outlineSelect = fields.Field()
    outlineHover = fields.Field()
    floatingText = fields.Field()
    interfaceAll = fields.Field()
    interfaceReplay = fields.Field()
    interfaceScore = fields.Field()
    interfaceScoreboard = fields.Field()
    interfaceFrames = fields.Field()
    interfaceMinimap = fields.Field()
    interfaceTimeline = fields.Field()
    interfaceChat = fields.Field()
    interfaceTarget = fields.Field()
    interfaceQuests = fields.Field()
    interfaceAnnounce = fields.Field()
    healthBarChampions = fields.Field()
    healthBarStructures = fields.Field()
    healthBarWards = fields.Field()
    healthBarPets = fields.Field()
    healthBarMinions = fields.Field()
    environment = fields.Field()
    characters = fields.Field()
    particles = fields.Field()
