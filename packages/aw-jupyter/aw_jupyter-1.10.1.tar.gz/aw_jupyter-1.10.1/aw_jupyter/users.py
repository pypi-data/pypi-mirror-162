from typing import Union, Optional

import os

from pathlib import Path


class UserTokenStorage:

    def __init__(self, storage_root: Union[str, Path] = None):
        self.storage_root = (Path(storage_root) if storage_root else Path("./user_tokens")).absolute()

    def _data_token_path(self, aw_user_name: str):
        return self.storage_root / aw_user_name / "data_token"

    def save_data_token(self, aw_user_name: str, data_token: str):
        """ """
        token_file_path = self._data_token_path(aw_user_name)

        os.makedirs(token_file_path.parent, exist_ok=True)

        with open(token_file_path, "wt") as f:
            f.write(data_token)

    def load_data_token(self, aw_user_name: str) -> Optional[str]:
        """ """
        token_file_path = self._data_token_path(aw_user_name)
        token = None

        if os.path.exists(token_file_path):
            with open(token_file_path, "rt") as f:
                token = f.read()

        return token
