from __future__ import annotations

from portal.composition import PortalContainer, get_container


def container() -> PortalContainer:
    return get_container()
