from abc import abstractmethod

from pydantic import BaseModel


class MiraklExportMapper(BaseModel):
    def get_key(self):
        return getattr(self, self._identity_key, "")

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
