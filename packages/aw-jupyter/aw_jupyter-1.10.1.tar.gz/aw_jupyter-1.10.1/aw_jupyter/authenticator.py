from urllib.parse import urljoin

from oauthenticator.generic import GenericOAuthenticator
from traitlets import default

from aw_jupyter.users import UserTokenStorage
from aw_jupyter import config


class AWAuthenticator(GenericOAuthenticator):
    """
    """
    async def authenticate(self, handler, data=None):
        user_info = await super().authenticate(handler, data)

        # сохраняем информацию о пользователе
        token_storage = UserTokenStorage()
        token_storage.save_data_token(
            aw_user_name=user_info["auth_state"]["oauth_user"]["username"],
            data_token=user_info["auth_state"]["oauth_user"]["data_token"]
        )

        return user_info

    @default("authorize_url")
    def _authorize_url_default(self):
        """ """
        return urljoin(config.AW_URL, "/oauth/authorize/")
