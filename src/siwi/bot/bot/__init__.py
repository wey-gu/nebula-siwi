from siwi.bot.actions import SiwiActions
from siwi.bot.classifier import SiwiClassifier


class SiwiBot():
    def __init__(self, connection_pool) -> None:
        self.classifier = SiwiClassifier()
        self.actions = SiwiActions()
        self.connection_pool = connection_pool

    def query(self, sentence):
        intent = self.classifier.get(sentence)
        action = self.actions.get(intent)
        return action.execute(self.connection_pool)
