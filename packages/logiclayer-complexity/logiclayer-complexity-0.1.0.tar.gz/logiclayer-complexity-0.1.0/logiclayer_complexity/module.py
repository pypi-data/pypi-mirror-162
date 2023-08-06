"""Economic Complexity adapter for use in LogicLayer.

Contains a module to enable endpoints which return economic complexity
calculations, using a Tesseract OLAP server as data source.
"""

import pandas as pd
from fastapi import Depends, HTTPException
from logiclayer import LogicLayerModule, route
from tesseract_olap import DataRequest, OlapServer
from tesseract_olap.backend.exceptions import BackendError
from tesseract_olap.query.exceptions import QueryError

from .calculations import calculate_rca
from .dependencies import base_params


class EconomicComplexityModule(LogicLayerModule):
    """Economic Complexity calculations module class for LogicLayer."""

    server: "OlapServer"

    def __init__(self, server: "OlapServer"):
        """Setups the server for this instance."""
        super().__init__()

        if server is None:
            raise ValueError(
                "EconomicComplexityModule needs an OlapServer instance, "
                "or a server url to create it."
            )
        self.server = server

    async def fetch_data(self, query: DataRequest):
        """Retrieves the data from the backend, and handles related errors."""
        try:
            res = await self.server.get_data(query)
        except QueryError as exc:
            raise HTTPException(status_code=400, detail=exc.message) from None
        except BackendError as exc:
            raise HTTPException(status_code=500, detail=exc.message) from None

        return pd.DataFrame.from_dict(res.data)


    @route("GET", "/")
    def route_root():
        return {
            "module": "logiclayer-complexity"
        }

    @route("GET", "/rca")
    async def route_rca(
        self,
        geography: str,
        measure: str,
        product: str,
        query: DataRequest = Depends(base_params),
    ):
        """RCA calculation endpoint."""
        data = await self.fetch_data(query)
        rca = calculate_rca(data, index=geography, columns=product, values=measure)

        return {
            "data": rca.to_dict("records"),
        }

    @route("GET", "/eci")
    async def route_eci(self):
        """ECI calculation endpoint."""
        return {"error": "Unavailable"}
