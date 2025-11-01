from src.shared.flashcard.contracts import IAnswerOption


class AnswerOption(IAnswerOption):
    def __init__(self, option: str):
        self._option = option

    def get_option(self) -> str:
        return self._option

    def __str__(self) -> str:
        return self._option
