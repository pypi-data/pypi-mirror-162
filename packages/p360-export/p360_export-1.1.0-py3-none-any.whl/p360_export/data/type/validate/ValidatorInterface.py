from abc import ABC, abstractmethod


class ValidatorInterface(ABC):
    @abstractmethod
    def validate(self, value: str) -> bool:
        pass
