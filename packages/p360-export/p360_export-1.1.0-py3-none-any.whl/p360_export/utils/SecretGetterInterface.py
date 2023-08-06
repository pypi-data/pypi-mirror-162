from abc import ABC, abstractmethod


class SecretGetterInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> str:
        pass
