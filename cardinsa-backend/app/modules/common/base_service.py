from __future__ import annotations
from typing import Generic, TypeVar

RepoT = TypeVar("RepoT")

class BaseService(Generic[RepoT]):
    def __init__(self, repo: RepoT):
        self.repo = repo
