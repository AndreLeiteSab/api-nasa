"""Pacote de routers — um módulo por serviço da NASA.

``all_routers`` é a única lista que a aplicação inclui, então adicionar um novo
serviço só exige criar o módulo e acrescentar o router dele aqui. A ordem abaixo
segue os 16 serviços exigidos no trabalho (e, portanto, a ordem mostrada no
Swagger e na barra lateral do frontend).
"""

from app.routers import (
    apod,
    donki,
    eonet,
    epic,
    exoplanet,
    gibs,
    image_library,
    insight,
    neows,
    osdr,
    ssc,
    ssd,
    techport,
    techtransfer,
    tle,
    trek,
)

all_routers = [
    apod.router,
    neows.router,
    donki.router,
    eonet.router,
    epic.router,
    exoplanet.router,
    gibs.router,
    insight.router,
    image_library.router,
    osdr.router,
    ssc.router,
    ssd.router,
    techport.router,
    techtransfer.router,
    tle.router,
    trek.router,
]
