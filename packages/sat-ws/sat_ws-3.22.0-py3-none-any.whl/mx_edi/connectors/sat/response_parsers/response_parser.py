from abc import ABC, abstractmethod
from typing import Dict


class ResponseParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(response: str) -> Dict[str, str]:
        """Parse an event from a source in XML representation."""
