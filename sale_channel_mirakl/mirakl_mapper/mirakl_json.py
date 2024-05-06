from abc import abstractmethod

from pydantic import BaseModel


class MiraklJson(BaseModel):
    @abstractmethod
    def to_json(self):
        """
        Allow
        :return:
        """
