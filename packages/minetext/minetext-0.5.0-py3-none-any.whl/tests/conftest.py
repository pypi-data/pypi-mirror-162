from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from minetext import UserAuth
from minetext.config import Config
from minetext.model.access_token import AccessToken
from minetext.model.device_token import DeviceToken


@pytest.fixture
def mocked_requests_get(mocker: MockerFixture) -> MagicMock:
    requests_get = mocker.patch('requests.get')
    return requests_get


@pytest.fixture
def mocked_requests_post(mocker: MockerFixture) -> MagicMock:
    requests_post = mocker.patch('requests.post')
    return requests_post


@pytest.fixture
def access_token() -> AccessToken:
    return AccessToken(
        access_token='1234',
        refresh_token='5678',
        creation_time=datetime.now(),
        expires_in=300,
        refresh_expires_in=600
    )


@pytest.fixture
def device_token() -> DeviceToken:
    return DeviceToken(
        device_code='device_code',
        user_code='user_code',
        verification_uri='https://example.com/verify',
        verification_uri_complete='https://example.com/verify?code=user_code'
    )


@pytest.fixture
def user_auth() -> UserAuth:
    return UserAuth(host=Config.host)


@pytest.fixture
def mocked_user_auth(access_token: AccessToken, device_token: DeviceToken) -> MagicMock:
    mocked_user_auth = MagicMock(spec=UserAuth)

    # Mock the refresh token method
    new_token = AccessToken(
        access_token='new token',
        refresh_token='new refresh token',
        creation_time=datetime.now(),
        expires_in=300,
        refresh_expires_in=600
    )
    mocked_user_auth.refresh_token.return_value = new_token

    # Mock the device token method
    mocked_user_auth.create_device_token.return_value = device_token

    # Mock the access token method
    mocked_user_auth.create_access_token.return_value = access_token
    return mocked_user_auth
