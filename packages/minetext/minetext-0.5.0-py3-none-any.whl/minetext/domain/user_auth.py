import pickle
from datetime import datetime
from pathlib import Path

import requests

from ..config import Config
from ..exceptions import RefreshTokenExpiredError
from ..model.access_token import AccessToken
from ..model.device_token import DeviceToken


class UserAuth:
    _host: str
    _default_file_location: Path

    @property
    def default_file_location(self):
        return self._default_file_location

    def __init__(self, host: str):
        """
        This class encapsulates all authentication-related actions.

        Parameters
        ----------
        host : str
            Base URL of the Single Sign-On service.
        """

        self._host = host

        # The default location where users' credentials are stored.
        self._default_file_location = Path.home() / Config.dir_name / 'user.pickle'

    def create_device_token(self) -> DeviceToken:
        """
        Request a device login. Check
        `OAuth 2.0 Device Authorization Grant <https://github.com/keycloak/keycloak-community/blob/main/design/oauth2-device-authorization-grant.md>`_
        for more information.

        Returns
        -------
        :py:class:`~minetext.model.device_token.DeviceToken`
            An instance of the :py:class:`~minetext.model.device_token.DeviceToken` class.

        Raises
        ------
        HTTPError
            When device login could not be requested.
        """
        response = requests.get(f'{self._host}/auth/device_token')
        response.raise_for_status()
        json = response.json()

        return DeviceToken(
            device_code=json['device_code'],
            user_code=json['user_code'],
            verification_uri=json['verification_uri'],
            verification_uri_complete=json['verification_uri_complete']
        )

    def create_access_token(self, device_code: str) -> AccessToken:
        """
        Request the access token from the device code.

        Parameters
        ----------
        device_code : str
            The device code in the :py:class:`~minetext.model.device_token.DeviceToken`.

        Returns
        -------
        :py:class:`~minetext.model.access_token.AccessToken`
            The new access token object.

        Raises
        -------
        HTTPError
            When access token could not be created. This happens mostly when the user did not log in properly
            but stated they did so.
        """
        response = requests.post(f'{self._host}/auth/token', json={'device_code': device_code})
        response.raise_for_status()

        response_json = response.json()
        return AccessToken(
            access_token=response_json['access_token'],
            refresh_token=response_json['refresh_token'],
            expires_in=response_json['expires_in'],
            refresh_expires_in=response_json['refresh_expires_in'],
            creation_time=datetime.now()
        )

    @classmethod
    def is_token_expired(cls, creation_time: float, expires_in: int, limit: int = 20) -> bool:
        """
        Checks if the token is still usable within the next ``limit`` seconds.

        Parameters
        ----------
        creation_time : float
            The timestamp when the token was created.
        expires_in : int
            Number of seconds since the `creation_time` until the token expires.
        limit : int, default=20

        Returns
        -------
        True
            if the token is (almost) expired.
        False
            if the token is still usable.
        """
        curr_time = datetime.now().timestamp()
        return curr_time - creation_time > 1000 * (expires_in - limit)

    def refresh_token(self, ac_token: AccessToken) -> AccessToken:
        """
        Creates a new access token with the refresh token.

        Parameters
        ----------
        ac_token : :py:class:`~minetext.model.access_token.AccessToken`
            The current :py:class:`~minetext.model.access_token.AccessToken` object.

        Returns
        -------
        AccessToken
            The new access token object.

        Raises
        ------
        RefreshTokenExpiredError
            When the refresh token is already expired.
        HTTPError
            When there is an error during the process.
        """
        if self.is_token_expired(creation_time=ac_token.creation_time.timestamp(),
                                 expires_in=ac_token.refresh_expires_in):
            current_time = datetime.now()
            raise RefreshTokenExpiredError(creation_time=ac_token.creation_time, current_time=current_time)

        payload = {
            'refresh_token': ac_token.refresh_token
        }
        response = requests.post(f'{self._host}/auth/refresh_token', json=payload)
        response.raise_for_status()

        response_json = response.json()
        return AccessToken(
            access_token=response_json['access_token'],
            refresh_token=response_json['refresh_token'],
            expires_in=response_json['expires_in'],
            refresh_expires_in=response_json['refresh_expires_in'],
            creation_time=datetime.now()
        )

    def save_credentials(self, token: AccessToken, location: Path = None) -> None:
        """
        Serialize the access token to a file.

        Parameters
        ----------
        token : :py:class:`~minetext.model.access_token.AccessToken`
            The :py:class:`~minetext.model.access_token.AccessToken` object.
        location : :py:class:`~pathlib.Path`, default=$HOME/.minetext/user.pickle
            Where the file should be stored. The path must also include the file name.
        """
        if location is None:
            location = self._default_file_location

        # Create the path if it does not exist yet
        self._default_file_location.parent.mkdir(parents=True, exist_ok=True)

        with location.open(mode='wb') as file:
            pickle.dump(token, file=file)

    def load_credentials(self, location: Path = None) -> AccessToken:
        """
        Load the :py:class:`~minetext.model.access_token.AccessToken` object from a file.

        Parameters
        ----------
        location : :py:class:`~pathlib.Path`, default=$HOME/.minetext/user.pickle
            Where the file is stored. The path must also include the file name.

        Returns
        -------
        :py:class:`~minetext.model.access_token.AccessToken`
            The :py:class:`~minetext.model.access_token.AccessToken` object loaded from the specified file.
        """
        if location is None:
            location = self._default_file_location
        with location.open(mode='rb') as file:
            token = pickle.load(file=file)
        return token
