from abc import ABC, abstractmethod
import asyncio
import json

class Runner(ABC):

  @abstractmethod
  def solve(self, problem_file: str, spec: dict, blocking : bool, **kwargs) -> dict | asyncio.Future:
    pass