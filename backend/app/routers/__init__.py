"""Routers package — one module per NASA service.

``all_routers`` is the single list the application includes, so adding a new
service only requires creating the module and appending its router here.
"""

from app.routers import (
    apod,
    donki,
    earth,
    eonet,
    epic,
    exoplanet,
    image_library,
    insight,
    mars_rover,
    neows,
    ssd,
    techtransfer,
    tle,
)

all_routers = [
    apod.router,
    neows.router,
    donki.router,
    earth.router,
    eonet.router,
    epic.router,
    mars_rover.router,
    image_library.router,
    techtransfer.router,
    insight.router,
    exoplanet.router,
    tle.router,
    ssd.router,
]
