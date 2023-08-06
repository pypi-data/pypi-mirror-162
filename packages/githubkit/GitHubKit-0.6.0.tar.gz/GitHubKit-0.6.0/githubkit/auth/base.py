import abc
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from githubkit import GitHub


class BaseAuthStrategy(abc.ABC):
    @abc.abstractmethod
    def get_auth_flow(self, github: "GitHub") -> httpx.Auth:
        raise NotImplementedError
