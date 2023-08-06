import pandas as pd
import numpy as np
import caveclient
import datetime

try:
    from scipy import sparse
except ImportError:
    print("install scipy for sparse matrix support")


def get_root_id_from_nuc_id(
    nuc_id,
    client,
    nucleus_table,
    config,
    timestamp=None,
):
    """Look up current root id from a nucleus id
    Parameters
    ----------
    nuc_id : int
        Annotation id from a nucleus
    client : CAVEclient
        CAVEclient for the server in question
    nucleus_table : str
        Name of the table whose annotation ids are nucleus lookups.
    timestamp : datetime.datetime, optional
        Timestamp for live query lookup. Required if live is True. Default is None.
    live : bool, optional
        If True, uses a live query. If False, uses the materialization version set in the client.
    Returns
    -------
    [type]
        [description]
    """
    df = client.materialize.query_table(
        nucleus_table,
        filter_equal_dict={config.nucleus_id_column: nuc_id},
        timestamp=timestamp,
    )
    if len(df) == 0:
        return None
    else:
        return df.iloc[0][config.soma_pt_root_id]


def get_nucleus_id_from_root_id(
    root_id,
    client,
    nucleus_table,
    config,
    timestamp=None,
):

    df = client.materialize.query_table(
        nucleus_table,
        filter_equal_dict={config.soma_pt_root_id: root_id},
        timestamp=timestamp,
    )

    if config.soma_table_query is not None:
        df = df.query(config.soma_table_query)

    if len(df) == 0:
        return None
    elif len(df) == 1:
        return df[config.nucleus_id_column].values[0]
    else:
        return df[config.nucleus_id_column].values


def get_soma_properties(
    client: caveclient.CAVEclient,
    cell_type_table: (str or pd.DataFrame) = None,
    timestamp: (datetime.datetime) = None,
    soma_table: (str or pd.DataFrame) = None,
    soma_root_id_column="pt_root_id",
    cell_type_root_id_column="pt_root_id",
    soma_pt_position="pt_position",
    soma_filters: dict = None,
    cell_type_filters: dict = None,
):
    """returns a dataframe which has a row for every soma in the table
    columns are added for n_soma and cell_type calls.

    For those with precisely 1 soma in the column, merges in cell type
    information found in the cell type table provided.

    For those somas with more than one, or zero

    Args:
        client (caveclient.CAVEclient): caveclient initialized with datastack of interest
        (default = None will use latest materialization or timestamp specified in client)
        cell_type_table (str or pd.DataFrame): name of cell_type table to merge on (or a dataframe with that table)
        timestamp (datetime.datetime, optional): timestamp for when to query (use datetime.datetime.utcnow() for now)
        soma_table (str, optional): name of soma table to use. Defaults to soma table specified by info service.
        soma_root_id_column (str, optional): what column in some to use for merging soma onto cell types (default=pt_root_id)
        cell_root_id_column (str, optional): what column to use for merging cell types onto somas (default=pt_root_id)
    Returns:
        soma_df: pd.DataFrame with a row for every soma, a column n_soma has been added to count how
    many soma have the same pt_root_id. For rows with n_soma=1 the cell type table has been merged.
    """
    if soma_table is None:
        soma_table = client.info._get_property("soma_table")
    if (soma_table is None) or (len(soma_table) == 0):
        raise ValueError("no soma table specified by function or in info service")

    if soma_filters is None:
        soma_filters = {}
    if cell_type_filters is None:
        cell_type_filters = {}

    if isinstance(soma_table, str):
        soma_table = client.materialize.query_table(
            soma_table, timestamp=timestamp, **soma_filters
        )

    if isinstance(cell_type_table, str):
        cell_type_table = client.materialize.query_table(
            cell_type_table, timestamp=timestamp, **cell_type_filters
        )

    soma_pos_df = soma_table.groupby(soma_root_id_column)[soma_pt_position].first()
    nsoma_pos_df = soma_table.groupby(soma_root_id_column)[soma_pt_position].agg(
        {"n_soma": len}
    )


def synapse_to_connections(
    syn_df,
    aggregate: (str or dict) = "count",
    pre_column: str = "pre_pt_root_id",
    post_column: str = "post_pt_root_id",
):
    """convert a synapse table to a connections table

    quantifies each connection with a common pre and post synaptic partner
    adds columns for number of synapses and summed synapse size (if present in table)

    Args:
        syn_df (_type_): _description_
        aggregate (str or dict, optional): How to quantify synapses per connection. Defaults to 'count' which
        simply counts synapses.

        Can pass a dictionary with keys as column names, and values as the functions to aggegate on those columns

        for example:
            {
                'gaba':np.mean,
                'size':np.sum,
            }
        would average the 'gaba' column and sum the size column in the synapse dataframe.

        pre_column (str, optional): _description_. Defaults to 'pre_pt_root_id'.
        post_column (str, optional): _description_. Defaults to 'post_pt_root_id'.
    """
    print("tbd")


def merge_cell_types_to_connections(
    conn_df: pd.DataFrame, cell_type_df: pd.DataFrame, remove_multi_calls: bool = True
):
    """_summary_

    Args:
        conn_df (pd.DataFrame): connection dataframe
         built with 'caveclient.analysis.synapse_to_connection'
        cell_type_df (pd.DataFrame): cell_type dataframe
        built with 'caveclient.analysis.get_somas_with_types'
        remove_multi_calls (bool, optional): whether to remove cell type calls for multi-soma. Defaults to True.
    """
    print("tbd")
    np.logical_or


def make_connection_matrix(
    df: pd.DataFrame,
    quantify: str = "n_synapses",
    return_as: str = "dataframe",
    fill_na: bool = True,
    soma_column_prefix: str = "n_soma",
):
    """convert a synapse or connection dataframe to a connection matrix
    raises a warning if you pass a dataframe without 'n_soma_pre' and 'n_soma_post' as a column
    or if included that there are entries with 'n_soma_pre' or 'n_soma_post' >1
    indicating you might be analyzing a graph with obvious errors.

    Args:
        df (pd.DataFrame): a dataframe containing synapses or connections
        quantify (str, optional): how to quantify connections.
                'n_synapses' counts the number of synapses
                'sum_size' sums the synapse sizes (if size or sum_size) is a column
        return_as (str, optional): how to return the result
                'dataframe' returns this as a dataframe with rows as pre-synaptic-ids
                            and columns as post-synaptic root-ids
                'sparse' returns this as a sparse.csgraph object
                'networkx' returns this as a networkx object
        fill_na (bool, optional): whether to fill missing entries with 0s. Defaults to True.
        soma_column_prefix (str, optional): what prefix to find the n_soma columns (_pre/_post).
                                            Defaults to "n_soma".
    """


def _soma_property_entry(soma_table, c):
    return {
        soma_table: {
            "root_id": c.soma_pt_root_id,
            "include": [c.soma_pt_position],
            "aggregate": {
                c.num_soma_prefix: {
                    "group_by": c.soma_pt_root_id,
                    "column": c.nucleus_id_column,
                    "agg": "count",
                }
            },
            "suffix": c.num_soma_suffix,
            "table_filter": c.soma_table_query,
            "data": None,
            "data_resolution": None,
        }
    }
