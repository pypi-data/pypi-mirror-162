from abc import ABC, abstractmethod


class ConfigGetterInterface(ABC):
    @abstractmethod
    def get(self, config_id: str) -> dict:
        pass
