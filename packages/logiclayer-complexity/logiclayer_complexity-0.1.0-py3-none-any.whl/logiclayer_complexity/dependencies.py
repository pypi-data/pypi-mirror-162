from typing import Optional

from fastapi import Query
from tesseract_olap import DataRequest, DataRequestParams


def base_params(
    cube: str = Query(..., description=""),
    geography: str = Query(..., description=""),
    product: str = Query(..., description=""),
    measure: str = Query(..., description=""),
    year: str = Query(..., description=""),
    threshold_country: Optional[str] = Query(None, description=""),
    threshold_product: Optional[str] = Query(None, description=""),
    # subnational: bool = Query(..., description=""),
    locale: Optional[str] = Query(
        None, description="The locale for the labels in the data."
    ),
):
    params: DataRequestParams = {
        "drilldowns": [geography, product],
        "measures": [measure],
        "cuts_include": {
            "Year": [year],
            geography: []
                       if threshold_country is None else
                       threshold_country.split(","),
            product: []
                     if threshold_product is None else
                     threshold_product.split(","),
        },
    }

    if locale is not None:
        params["locale"] = locale

    return DataRequest.new(cube, params)
