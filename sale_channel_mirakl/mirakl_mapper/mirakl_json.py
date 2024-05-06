from abc import abstractmethod

from pydantic import BaseModel


class MiraklJson(BaseModel):
    @abstractmethod
    def to_json(self):
        """
        Allow
        :return:
        """

    @classmethod
    def get_file_header(cls):
        return []

    @classmethod
    def get_additional_options(cls):
        return {}
