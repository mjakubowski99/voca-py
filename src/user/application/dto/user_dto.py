from src.user.domain.contracts import IUser
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.shared.user.iuser import IUser as ISharedUser


class UserDTO(ISharedUser):
    def __init__(self, domain_user: IUser):
        self._domain_user = domain_user

    def get_id(self) -> UserId:
        return self._domain_user.get_id()

    def get_password(self) -> str:
        return self._domain_user.get_password()

    def get_email(self) -> str:
        return self._domain_user.get_email()

    def get_name(self) -> str:
        return self._domain_user.get_name()

    def get_user_language(self) -> Language:
        return self._domain_user.get_user_language()

    def get_learning_language(self) -> Language:
        return self._domain_user.get_learning_language()

    def profile_completed(self) -> bool:
        return self._domain_user.get_profile_completed()
