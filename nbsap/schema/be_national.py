import flatland

from common import I18nString, CommonString, CommonList

Subobjective = flatland.Dict.of(
            I18nString.named('title'),
            I18nString.named('body'),
            CommonString.named('id'),
        )

_ObjectiveSchemaDefinition = flatland.Dict.of(
            I18nString.named('title'),
            I18nString.named('body'),
            CommonString.named('id'),
            CommonList.named('subobjs').of(Subobjective),
        )

class Objective(_ObjectiveSchemaDefinition):

    def __init__(self, init_objective):
        objective = dict(init_objective)
        objective.pop('_id', None)
        self.set(objective)

    def flatten(self):
        return self.value