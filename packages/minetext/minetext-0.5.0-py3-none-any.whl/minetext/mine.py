from pathlib import Path
from typing import Optional

import requests
from elasticsearch_dsl import Search
from elasticsearch_dsl.response import Response

from minetext import EsRequest, UserAuth
from .config import Config
from .exceptions import NotLoginError
from .model.access_token import AccessToken
from .model.device_token import DeviceToken


class Mine:
    _host: str
    es_request: EsRequest
    _user_auth: UserAuth
    _access_token: Optional[AccessToken]
    _device_token: Optional[DeviceToken]

    def __init__(self, es_request: EsRequest):
        """
        Initialize the MINE object. All interactions with the MINE system are done via the MINE object.

        Parameters
        ----------
        es_request : :py:class:`~minetext.domain.es_request.EsRequest`
            the object containing request information to Elasticsearch
        """
        self._host = Config.host
        self.es_request = es_request
        self._user_auth = UserAuth(host=Config.host)
        self._access_token = None
        self._device_token = None

    def search(self) -> Response:
        """
        Call the search endpoint with parameters provided via the
        :py:class:`~minetext.domain.es_request.EsRequest` property.

        Returns
        -------
        result : :ref:`Response <es-dsl:search_dsl>`
            the search result wrapped in the :ref:`Response <es-dsl:search_dsl>` object.

        Raises
        ------
        HTTPError
            if the request failed.
        """
        url = f'{self._host}/document/search'

        payload = {
            'q': self.es_request.search_term,
            'r[]': self.es_request.resources,
            'f[]': self.es_request.filters,
            'a': self.es_request.aggregation,
            'p': self.es_request.page,
            's': self.es_request.size,
            'wa': self.es_request.analytics
        }

        if self._access_token:

            # Refresh the access token if necessary
            if UserAuth.is_token_expired(creation_time=self._access_token.creation_time.timestamp(),
                                         expires_in=self._access_token.expires_in):
                self._access_token = self._user_auth.refresh_token(self._access_token)

            # Use the access token
            headers = {
                'Authorization': f'Bearer {self._access_token.access_token}'
            }

            try:
                result = requests.get(url, params=payload, headers=headers)
            except requests.HTTPError as e:
                # This is when the user is unauthorized. If they have an _access_token but 
                # are unauthorized the _access_token probably expired. 401 is unauthorized.
                if e.response.status_code == 401:
                    self._access_token = self._user_auth.refresh_token(self._access_token)
                    headers['Authorization'] = f'Bearer {self._access_token.access_token}'
                    result = requests.get(url, params=payload, headers=headers)
                else:
                    raise e
        else:
            result = requests.get(url, params=payload)

        # Parse the result using Elasticsearch Response
        response = Response(Search(), result.json())

        return response

    def login(self) -> None:
        """
        Calls the functions to authorize user.

        Waits for the user to log in into the verification uri and afterwards creates an access token if the user
        stated they granted access.
        """
        self._device_token = self._user_auth.create_device_token()
        print(f'Please sign in at this website and grant access: {self._device_token.verification_uri_complete}')
        input_str = input('Did you grant the access? [y/N]')
        if input_str != 'y':
            return
        self._access_token = self._user_auth.create_access_token(device_code=self._device_token.device_code)
        print('Login successful! You are now authorized.')

    def save_credentials(self, location: Path = None) -> None:
        """
        Serialize the access token to a file.

        Parameters
        ----------
        location : :py:class:`~pathlib.Path`, default=$HOME/.minetext/user.pickle
            Where the file should be stored. The path must also include the file name.

        Raises
        ------
        NotLoginError
            When the access token does not exist yet.
        """
        if self._access_token:
            self._user_auth.save_credentials(self._access_token, location)
        else:
            raise NotLoginError('The credentials is missing. Maybe you did not log in yet.')

    def load_credentials(self, location: Path = None) -> None:
        """
        Load the :py:class:`~minetext.model.access_token.AccessToken` object from a file.

        Parameters
        ----------
        location : :py:class:`~pathlib.Path`, default=$HOME/.minetext/user.pickle
            Where the file is stored. The path must also include the file name.
        """
        self._access_token = self._user_auth.load_credentials(location)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value.rstrip('/')
