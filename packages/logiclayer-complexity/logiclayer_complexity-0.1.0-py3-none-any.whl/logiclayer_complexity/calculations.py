import economic_complexity
import pandas as pd


def calculate_rca(data: pd.DataFrame, *, index: str, columns: str, values: str):
    """Execute RCA calculations"""

    # Guess ID column names
    index_id = f"{index} ID"
    index_id = index if index_id not in data.columns else index_id
    columns_id = f"{columns} ID"
    columns_id = columns if columns_id not in data.columns else columns_id

    # pivot the table and remove NAs
    tbl = pd.pivot_table(data, index=index_id, columns=columns_id, values=values)
    tbl.dropna(axis=1, how="all", inplace=True)
    tbl.fillna(0, inplace=True)

    # perform RCA calculation
    result = economic_complexity.rca(tbl.astype(float))
    result.reset_index(inplace=True)

    # unpivot the table
    rca = pd.melt(result, id_vars=[index_id], value_name=f"{values} RCA")

    # restore index labels
    if index != index_id:
        df_index = data[[index_id, index]].set_index(index_id)
        dict_index = df_index[index].to_dict()
        rca[index] = rca[index_id].map(dict_index)

    # restore columns labels
    if columns != columns_id:
        df_columns = data[[columns_id, columns]].set_index(columns_id)
        dict_columns = df_columns[columns].to_dict()
        rca[columns] = rca[columns_id].map(dict_columns)

    return rca
