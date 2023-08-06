import os
from pathlib import Path

from aw_jupyter.users import UserTokenStorage
from aw_jupyter import config


def pre_spawn_hook(spawner):
    """ """
    username = spawner.escaped_name

    user_notebooks_host_path = Path(config.NOTEBOOKS_DIR) / username / "notebooks"

    os.makedirs(user_notebooks_host_path, exist_ok=True)
    os.chmod(user_notebooks_host_path, 0o777)

    user_token_storage = UserTokenStorage()
    data_token = user_token_storage.load_data_token(aw_user_name=spawner.user.name)

    if data_token:
        spawner.environment["AW_DATA_TOKEN"] = data_token
        spawner.environment["AW_URL"] = os.getenv("AW_URL")