from abc import ABC, abstractmethod
import asyncio
import json

class Runner(ABC):

  # Python 3.10: -> dict | asyncio.Future
  @abstractmethod
  def solve(self, problem_file: str, spec: dict, blocking : bool, **kwargs):
    pass