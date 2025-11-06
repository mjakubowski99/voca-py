from src.shared.flashcard.contracts import IFlashcardFacade
from src.study.application.dto.picking_context import PickingContext
from src.study.domain.enum import LearningActivityType
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.value_objects import LearningSessionId
from src.study.application.repository.contracts import ISessionRepository
from src.study.application.services.exercise_factory import ExerciseFactory


class AddNextSessionStep:
    def __init__(
        self,
        session_repository: ISessionRepository,
        exercise_factory: ExerciseFactory,
        flashcard_facade: IFlashcardFacade,
    ):
        self.session_repository = session_repository
        self.exercise_factory = exercise_factory
        self.flashcard_facade = flashcard_facade

    async def handle(self, session_id: LearningSessionId) -> LearningSession:
        session = await self.session_repository.find(session_id)

        if session.needs_next():
            context = PickingContext(
                user_id=session.user_id, flashcard_deck_id=session.flashcard_deck_id
            )

            match session.pick_next_activity_type():
                case LearningActivityType.FLASHCARDS:
                    session.add_flashcard(await self.exercise_factory.build_flashcards(context))
                case LearningActivityType.UNSCRAMBLE_WORDS:
                    session.add_flashcard(
                        await self.exercise_factory.build_unscramble_exercise(context)
                    )

            self.session_repository.save(session)

        return session
