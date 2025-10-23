from abc import ABC, abstractmethod
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class IHash(ABC):
    @abstractmethod
    def check(self, password: str, password_hash: str) -> bool:
        """Check if the password matches the hash"""
        pass

    @abstractmethod
    def make(self, password: str) -> str:
        """Generate a secure hash from a password"""
        pass


class ArgonHash(IHash):
    def __init__(self):
        self._hasher = PasswordHasher()  # default secure Argon2 parameters

    def make(self, password: str) -> str:
        """
        Hash the password using Argon2.
        Returns the hashed string.
        """
        return self._hasher.hash(password)

    def check(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        Returns True if match, False otherwise.
        """
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False