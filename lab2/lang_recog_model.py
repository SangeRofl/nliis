from abc import ABC, abstractmethod
from enum import Enum


class Lang(Enum):
    fr = "французский"
    en = "английский"


class LangRecognModel(ABC):
    @abstractmethod
    def recognize_language(self, text: str):
        pass