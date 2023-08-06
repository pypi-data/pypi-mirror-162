import asyncio
from decimal import Decimal
from operator import index
from aiohttp import ClientSession
import aiohttp
from aiohttp.client_exceptions import ClientError

import logging
from typing import Dict, List, Type, TypeVar

from pytrutankless.device import Device
from pytrutankless.errors import GenericHTTPError, InvalidCredentialsError

BASE_URL = f"https://home.trutankless.com/"
DEVICES_URL = f"{BASE_URL}api/dashboard/devices/"
LOCATIONS_URL = f"{BASE_URL}api/dashboard/locations"
TOKEN_URL = f"{BASE_URL}api/dash-oauth/token"
HEADERS = {"Content-Type": "application/json"}
GRANT_TYPE = "password"
CLIENT_ID = "123"

_LOGGER = logging.getLogger(__name__)

ApiType = TypeVar("ApiType", bound="TruTanklessApiInterface")


class TruTanklessApiInterface:
    """API Interface object."""

    def __init__(self, email: str, password: str) -> None:
        """Create the TruTankless API interface object."""

        self.email: str = email
        self.password: str = password
        self._access_token: str
        self._token_type: str
        self._customer_id: str
        self._user_id: str
        self._locations: List = {}
        self._devices: Dict = {}

    @property
    def customer_id(self) -> str:
        """Return the customer id."""
        return self._customer_id
    
    @property
    def locations(self) -> List[Dict]:
        """Return a list of locations as json objects."""
        return self._locations

    @property
    def user_id(self) -> str:
        """Return the user id."""
        return self._user_id

    @classmethod
    async def login(cls: Type[ApiType],
                    email: str,
                    password: str) -> ApiType:
        """Create a TruTanklessApiInterface object using email and password."""
        this_class = cls(email, password)
        await this_class._authenticate({"username": email, "password": password, "grant_type": GRANT_TYPE, "client_id": CLIENT_ID})
        return this_class

    async def _authenticate(self, payload: dict) -> None:
        async with aiohttp.ClientSession() as _session:
            try:
                async with _session.post(TOKEN_URL, data=payload) as token_resp:
                    if token_resp.status == 200:
                        _token_json = await token_resp.json()
                        _LOGGER.debug(_token_json)
                        self._access_token = _token_json["access_token"]
                        self._token_type = _token_json["token_type"].capitalize()
                        self._user_id = _token_json["user_id"]
                        await _session.close()
                    elif token_resp.status == 401:
                        raise InvalidCredentialsError(token_resp.status)
                    else:
                        raise GenericHTTPError(token_resp.status)
            except ClientError as err:
                raise err
            finally:
                await _session.close()

    async def get_devices(self) -> None:
        """Get a list of all the devices for this user and instantiate device objects."""
        _locations: Dict = await self._get_locations()
        for _locindex in _locations:
            _location = _locations[_locindex]
            for _devlist in _location.get("devices"):
                _dev_obj = Device(_devlist, self)
                self._devices[_dev_obj.device_id] = _dev_obj 

    async def refresh_device(self, device: str) -> Dict:
        """Fetch updated data for a device."""
        _device = device
        _headers = HEADERS
        _headers["authorization"] = f"{self._token_type} {self._access_token}"

        async with ClientSession() as _refresh_session:
            _device_url = f"{DEVICES_URL}{_device}"
            try:
                async with _refresh_session.get(_device_url, headers=_headers) as refr:
                    if refr.status == 200:
                        _refdata = await refr.json()
                        _LOGGER.debug(_refdata)
                        _dev_obj: Device = None
                        device = self._devices.get(_refdata.get("id", ""), None)
                        if device:
                            device.update_device_info(_refdata)
            except ClientError as err:
                _LOGGER.error("Failed to fetch device.")
                raise err
            finally:
                await _refresh_session.close()
            
    async def _get_locations(self) -> Dict:
        if self._access_token is None:
            print("Access Token is not present. Logging in...")
            await self.login(email=self.email, password=self.password)
        _headers = HEADERS
        _headers["authorization"] = f"{self._token_type} {self._access_token}"
            
        async with ClientSession() as _location_session:
            try:
                async with _location_session.get(LOCATIONS_URL, headers=_headers) as resp:
                    if resp.status == 200:
                        _json = await resp.json()
                        _LOGGER.debug(_json)
                        _ind = len(_json) - 1
                        while _ind >= 0:
                            self._customer_id = _json[_ind]["customer_id"]
                            # self._location_id = _json[_ind]["id"]
                            self._locations[_ind] = _json[_ind]
                            _ind -= 1
                        return self._locations
                    elif resp.status == 401:
                        raise InvalidCredentialsError(resp.status)
                    else:
                        raise GenericHTTPError(resp.status)
            except ClientError as err:
                raise err
            finally:
                await _location_session.close()

if __name__ == "__main__":

    # test = asyncio.run(TruTanklessApiInterface.login(email="mdcoleman001@gmail.com", password="k9oAEmdEwVrJ8V"))
    session = asyncio.run(TruTanklessApiInterface.login(email="mdcoleman001@gmail.com", password="k9oAEmdEwVrJ8V"))

    asyncio.run(session.get_devices())
    asyncio.run(session.refresh_device("1061"))