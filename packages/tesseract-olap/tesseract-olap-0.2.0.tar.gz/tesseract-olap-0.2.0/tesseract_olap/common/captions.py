from typing import Mapping, Optional, overload

from typing_extensions import Literal


@overload
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
) -> Optional[str]:
    ...
@overload
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
    *,
    force: Literal[True],
) -> str:
    ...
def get_localization(
    dictionary: Mapping[str, str],
    locale: str,
    *,
    force: bool = False,
) -> Optional[str]:
    """Attempts to return the value from a dictionary of terms, where the locale
    code is the key.

    If it doesn't find the specific locale, looks for the general locale code,
    and if it's not available either, returns the value for the default locale.
    """
    if locale not in dictionary:
        locale = locale[0:2]
    if locale not in dictionary:
        locale = "xx"
    return dictionary[locale] if force else dictionary.get(locale)
