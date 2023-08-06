from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from requests import Response

from minetext import UserAuth
from minetext.config import Config
from minetext.exceptions import RefreshTokenExpiredError
from minetext.model.access_token import AccessToken
from minetext.model.device_token import DeviceToken


class TestUserAuth:

    def test_create_device_token(self, user_auth: UserAuth, device_token: DeviceToken, mocked_requests_get: MagicMock):
        # Fake a successful response. No exception must be thrown.
        fake_response = Response()
        fake_response.status_code = 200
        fake_response.json = lambda: device_token.dict()
        mocked_requests_get.return_value = fake_response

        response_token = user_auth.create_device_token()

        # Make sure that the request is correct
        mocked_requests_get.assert_called_once()
        correct_url = f'{Config.host}/auth/device_token'
        mocked_requests_get.assert_called_with(correct_url)

        # Make sure that the response is correct
        assert response_token.device_code == device_token.device_code

    def test_create_access_token(self, user_auth: UserAuth, access_token: AccessToken, mocked_requests_post: MagicMock):
        # Fake a successful response. No exception must be thrown.
        fake_response = Response()
        fake_response.status_code = 200
        fake_response.json = lambda: access_token.dict()
        mocked_requests_post.return_value = fake_response

        device_code = '1234'
        response_token = user_auth.create_access_token(device_code)

        # Make sure that the request is correct
        mocked_requests_post.assert_called_once()
        correct_url = f'{Config.host}/auth/token'
        mocked_requests_post.assert_called_with(correct_url, json={'device_code': device_code})

        # Make sure that the response is correct
        assert response_token.access_token == access_token.access_token

    def test_is_token_expired_no(self):
        """
        Test the function when the token is not expired yet.
        """
        current_time = datetime.now()
        expires_in = 300
        assert not UserAuth.is_token_expired(current_time.timestamp(), expires_in, limit=20)

    def test_is_token_expired_yes(self):
        """
        Test the function when the token is expired.
        """
        current_time = datetime.now()
        expires_in = 10
        assert UserAuth.is_token_expired(current_time.timestamp(), expires_in, limit=20)

    def test_refresh_token_success(self, user_auth: UserAuth, access_token: AccessToken,
                                   mocked_requests_post: MagicMock):
        new_token = AccessToken(
            access_token='new_token',
            refresh_token='new_rf_token',
            creation_time=datetime.now(),
            expires_in=300,
            refresh_expires_in=600
        )
        fake_response = Response()
        fake_response.status_code = 200
        fake_response.json = lambda: new_token.dict()
        mocked_requests_post.return_value = fake_response

        response_token = user_auth.refresh_token(access_token)

        # Make sure that the request is correct
        payload = {
            'refresh_token': access_token.refresh_token
        }
        mocked_requests_post.assert_called_once()
        correct_url = f'{Config.host}/auth/refresh_token'
        mocked_requests_post.assert_called_with(correct_url, json=payload)

        # Make sure that the response is correct
        assert response_token.access_token == new_token.access_token

    def test_refresh_token_failed(self, user_auth: UserAuth, access_token: AccessToken,
                                  mocked_requests_post: MagicMock):
        """
        An exception with a proper message must be thrown when the provided refresh token is already expired.
        """
        access_token.refresh_expires_in = 0

        error_message_format = r'The refresh token created at .* was expired. Current time is .*\.'
        with pytest.raises(RefreshTokenExpiredError, match=error_message_format):
            user_auth.refresh_token(access_token)

    def test_save_load_token_default_path(self, user_auth: UserAuth, access_token: AccessToken):
        user_auth.save_credentials(access_token)
        token = user_auth.load_credentials()
        assert token.access_token == access_token.access_token

        # Clean up
        user_auth.default_file_location.unlink()

    def test_save_load_token_custom_path(self, user_auth: UserAuth, access_token: AccessToken, tmp_path: Path):
        location = tmp_path / 'custom.pickle'
        user_auth.save_credentials(access_token, location=location)
        token = user_auth.load_credentials(location=location)
        assert token.access_token == access_token.access_token
