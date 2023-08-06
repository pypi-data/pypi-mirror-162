from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from promoted_python_delivery_client.model.browser import Browser
from promoted_python_delivery_client.model.locale import Locale
from promoted_python_delivery_client.model.location import Location
from promoted_python_delivery_client.model.screen import Screen


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Device:
    brand: str
    browser: Browser
    device_type: int
    identifier: str
    ip_address: str
    locale: Locale
    location: Location
    manufacturer: str
    os_version: str
    platform_app_version: str
    promoted_mobile_sdk_version: str
    screen: Screen
