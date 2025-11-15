from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.study.application.dto.picking_context import PickingContext
from src.study.domain.enum import LearningActivityType
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from src.study.application.repository.contracts import ISessionRepository
from src.study.application.services.exercise_factory import ExerciseFactory


class AddNextLearningStepHandler:
    def __init__(
        self,
        session_repository: ISessionRepository,
        exercise_factory: ExerciseFactory,
        flashcard_facade: IFlashcardFacade,
    ):
        self.session_repository = session_repository
        self.exercise_factory = exercise_factory
        self.flashcard_facade = flashcard_facade

    async def handle(self, user: IUser, session_id: LearningSessionId) -> LearningSession:
        session = await self.session_repository.find(session_id)
        session.check_if_finished()

        if session.needs_next():
            context = PickingContext(
                user=user,
                deck_id=session.deck_id,
                max_flashcards_count=session.limit,
                current_count=session.progress,
            )

            match session.pick_next_activity_type():
                case LearningActivityType.FLASHCARDS:
                    session.add_flashcard(
                        LearningSessionStepId.no_id(),
                        await self.exercise_factory.build_flashcard(context),
                    )
                case LearningActivityType.UNSCRAMBLE_WORDS:
                    exercise = await self.exercise_factory.build_unscramble_words(context)

                    session.add_unscramble_exercise(
                        LearningSessionStepId.no_id(),
                        exercise,
                    )
                case LearningActivityType.WORD_MATCH:
                    exercise = await self.exercise_factory.build_word_match(context)

                    session.add_word_match_exercise(
                        LearningSessionStepId.no_id(),
                        exercise,
                    )

        await self.session_repository.save_new_steps(session)

        return session
