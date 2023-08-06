import hashlib
from datetime import datetime

from .base import BaseDatafile


class FileTokens(BaseDatafile):
    ATTR_TOKEN = "token"
    ATTR_ACCESS_NUM = "accessNum"

    def check_token(self, filepath: str, token: str):
        if filepath in self.data:
            return self.get_data(filepath)[self.ATTR_TOKEN] == token
        return False

    def add_file_token(self, filepath: str) -> str:
        """
        Add token into dict for selected file-path
        :param filepath: Relative file path
        :return: New created token
        """
        datetime_str = str(datetime.now())
        token_prepare = f"{filepath}||{datetime_str}"
        hash_object = hashlib.sha1(bytes(token_prepare, "utf-8"))
        hash_str = hash_object.hexdigest()
        self.set_data(filepath, self.ATTR_TOKEN, hash_str)
        return hash_str

    def remove_file_token(self, filepath: str) -> bool:
        """
        Remove token from dict for selected file-path
        :param filepath: Relative file path
        :return: True if file-path exists in dict
        """
        if filepath in self.data:
            del self.data[filepath]
            return True
        return False

    def remove_file_tokes_beginig(self, filepath_beging: str) -> bool:
        """
        Remove token from dict for selected file-paths begining with specified part of path
        :param filepath_beging: Beging part of relative file path
        :return: True if at least one token removed
        """
        items_to_delete = []
        for path, token in self.data.items():
            if path.startswith(filepath_beging):
                items_to_delete.append(path)
        for path in items_to_delete:
            del(self.data[path])
        return len(items_to_delete) > 0

    def inc_access_num(self, path) -> int:
        access_num = self.get_data(path)[self.ATTR_ACCESS_NUM] + 1
        self.set_data(path, self.ATTR_ACCESS_NUM, access_num)
        return access_num

    def get_data(self, path: str) -> dict:
        stored_data = self.data.get(path)
        if stored_data and isinstance(stored_data, str):
            return {self.ATTR_TOKEN: stored_data, self.ATTR_ACCESS_NUM: 0}
        elif isinstance(stored_data, dict):
            return stored_data
        return {self.ATTR_TOKEN: "", self.ATTR_ACCESS_NUM: 0}

    def set_data(self, path: str, key: str, value) -> dict:
        stored_data = self.get_data(path)
        stored_data[key] = value
        self.data[path] = stored_data
        return stored_data
