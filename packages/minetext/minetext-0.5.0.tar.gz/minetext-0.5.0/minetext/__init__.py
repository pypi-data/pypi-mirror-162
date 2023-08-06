import os
from pathlib import Path

from .domain.es_request import EsRequest
from .domain.user_auth import UserAuth
from .mine import Mine

package_root_dir = Path(__file__).parent.parent
with open(os.path.join(package_root_dir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

__all__ = [
    'Mine',
    'EsRequest',
    'UserAuth'
]
