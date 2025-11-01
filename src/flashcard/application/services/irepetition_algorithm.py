from abc import ABC, abstractmethod
from src.flashcard.application.contracts import IRepetitionAlgorithmDTO


class IRepetitionAlgorithm(ABC):
    @abstractmethod
    async def handle(self, dto: IRepetitionAlgorithmDTO) -> None:
        """
        Process a repetition algorithm for the given DTO.
        """
        pass
