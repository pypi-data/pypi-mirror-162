from datetime import datetime


class RefreshTokenExpiredError(Exception):
    def __init__(self, creation_time: datetime, current_time: datetime):
        """
        Raised when the client tries to use an expired refresh token.

        Parameters
        ----------
        creation_time : datetime
            The time when the refresh token was created.
        current_time : datetime
            The time when this exception is thrown.
        """
        self.message = f'The refresh token created at {creation_time} was expired. Current time is {current_time}.'
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class NotLoginError(Exception):
    pass
