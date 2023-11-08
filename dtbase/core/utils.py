"""
Utilities (miscellaneous routines) module
"""
import io
import json
import logging
import uuid
from datetime import datetime, timedelta

import pandas as pd
from flask import send_file
from sqlalchemy import exc

from dtbase.core.constants import SQL_CONNECTION_STRING, SQL_DBNAME
from dtbase.core.db import connect_db, session_close, session_open
from dtbase.core.structure import (
    LocationBooleanValue,
    LocationFloatValue,
    LocationIntegerValue,
    LocationStringValue,
    ModelBooleanValue,
    ModelFloatValue,
    ModelIntegerValue,
    ModelStringValue,
    SensorBooleanReading,
    SensorFloatReading,
    SensorIntegerReading,
    SensorStringReading,
)


def get_db_session(return_engine=False):
    """
    Get an SQLAlchemy session on the database.

    Log an error message an return None if the connection fails.

    Parameters
    ==========
    return_engine: bool, if True return the sqlalchmy engine as well as session

    Returns
    =======
    session: SQLAlchemy session object
    engine (optional): SQLAlchemy engine
    """
    success, log, engine = connect_db(SQL_CONNECTION_STRING, SQL_DBNAME)
    if not success:
        logging.error(log)
        return None
    session = session_open(engine)
    if return_engine:
        return session, engine
    else:
        return session


def query_result_to_array(query_result, date_iso=True):
    """
    Forms an array of ResultProxy results.
    Args:
        query_result: a ResultProxy representing results of the sql alchemy query
        execution
    Returns:
        results_arr: an array with ResultProxy results
    """

    dict_entry, results_arr = {}, []

    for rowproxy in query_result:
        # NOTE: added ._asdict() as rowproxy didnt come in the form of dict and could
        # not read .items.
        if "_asdict" in dir(rowproxy):
            rowproxy = rowproxy._asdict()
        elif "_mapping" in dir(rowproxy):
            rowproxy = rowproxy._mapping
        else:
            pass

        for column, value in rowproxy.items():
            if isinstance(value, datetime):
                if date_iso:
                    dict_entry = {**dict_entry, **{column: value.isoformat()}}
                else:
                    dict_entry = {
                        **dict_entry,
                        **{column: value.replace(microsecond=0)},
                    }
            else:
                dict_entry = {**dict_entry, **{column: value}}
        results_arr.append(dict_entry)

    return results_arr


def query_result_to_dict(query_result, date_iso=True):
    """
    If we have a single query result, return output as a dict rather than a list
    Args:
        query_result: a ResultProxy representing results of the sql alchemy query
        execution
    Returns:
        results_dict: a dict containing the results
    """
    if len(query_result) != 1:
        print("Only call query_result_to_dict if we have a single result.")
        return {}
    rowproxy = query_result[0]
    dict_entry = {}
    if "_asdict" in dir(rowproxy):
        rowproxy = rowproxy._asdict()
    for column, value in rowproxy.items():
        if isinstance(value, datetime):
            if date_iso:
                dict_entry = {**dict_entry, **{column: value.isoformat()}}
            else:
                dict_entry = {
                    **dict_entry,
                    **{column: value.replace(microsecond=0)},
                }
        else:
            dict_entry = {**dict_entry, **{column: value}}
    return dict_entry


def jsonify_query_result(query_result):
    """
    Jasonifies ResultProxy results.

    Args:
        query_result: a ResultProxy representing results of the sql alchemy query
        execution
    Returns:
        result: jsonified result of the query_result
    """

    results_arr = query_result_to_array(query_result)

    # extend the JSONEncode to deal with UUID objects
    class UUIDEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    result = json.dumps(
        results_arr, ensure_ascii=True, indent=4, sort_keys=True, cls=UUIDEncoder
    )

    return result


def get_default_datetime_range():
    """
    Returns a default datetime range (7 days): dt_from, dt_to
    """

    time_delta = -7

    dt_to = (
        datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        + timedelta(days=1)
        + timedelta(milliseconds=-1)
    )

    dt_from = (dt_to + timedelta(time_delta)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return dt_from, dt_to


def parse_date_range_argument(request_args):
    """
    Parses date range arguments from the request_arguments string.

    Arguments:
        request_args - request arguments as a string
        arg - argument to be extracted from the request arguments

    Returns:
        tuple of two datetime objects
    """

    if request_args is None:
        return get_default_datetime_range()

    try:
        dt_to = (
            datetime.strptime(request_args.split("-")[1], "%Y%m%d").replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            + timedelta(days=1)
            + timedelta(milliseconds=-1)
        )

        dt_from = datetime.strptime(request_args.split("-")[0], "%Y%m%d").replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        return dt_from, dt_to

    except ValueError:
        return get_default_datetime_range()


def insert_to_db_from_df(engine, df, DbClass):
    """
    Read a CSV file into a pandas dataframe, and then upload to
    database table

    Parameters
    ==========
    engine: SQL engine object
    df:pandas.DataFrame, input data
    DbClass:class from core.structure.py
    """
    assert not df.empty

    # Creates/Opens a new connection to the db and binds the engine
    session = session_open(engine)

    # Check if table is empty and bulk inserts if it is
    first_entry = session.query(DbClass).first()

    if first_entry is None:
        session.bulk_insert_mappings(DbClass, df.to_dict(orient="records"))
        session_close(session)
        assert session.query(DbClass).count() == len(df.index)
    else:
        records = df.to_dict(orient="records")
        for record in records:
            try:
                session.add(DbClass(**record))
                session.commit()
            except exc.SQLAlchemyError:
                session.rollback()
    session_close(session)
    print(f"Inserted {len(df.index)} rows to table {DbClass.__tablename__}")


location_value_class_dict = {
    bool: LocationBooleanValue,
    float: LocationFloatValue,
    int: LocationIntegerValue,
    str: LocationStringValue,
    "boolean": LocationBooleanValue,
    "float": LocationFloatValue,
    "integer": LocationIntegerValue,
    "string": LocationStringValue,
}


model_value_class_dict = {
    bool: ModelBooleanValue,
    float: ModelFloatValue,
    int: ModelIntegerValue,
    str: ModelStringValue,
    "boolean": ModelBooleanValue,
    "float": ModelFloatValue,
    "integer": ModelIntegerValue,
    "string": ModelStringValue,
}


sensor_reading_class_dict = {
    bool: SensorBooleanReading,
    float: SensorFloatReading,
    int: SensorIntegerReading,
    str: SensorStringReading,
    "boolean": SensorBooleanReading,
    "float": SensorFloatReading,
    "integer": SensorIntegerReading,
    "string": SensorStringReading,
}


def check_datatype(value, datatype_name):
    if datatype_name == "string":
        return isinstance(value, str)
    if datatype_name == "integer":
        return isinstance(value, int)
    if datatype_name == "float":
        return isinstance(value, float)
    if datatype_name == "boolean":
        return isinstance(value, bool)
    raise ValueError(f"Unrecognised datatype: {datatype_name}")


def row_mappings_to_dicts(rows):
    """Convert the list of RowMappings that SQLAlchemy's mappings() returns into plain
    dicts.
    """
    return [{k: v for k, v in row.items()} for row in rows]


def download_csv(readings, filename_base="results"):
    """
    Use Pandas to convert array of readings into a csv
    Args:
       readings: a list of records to be written out as csv
       filename (optional): str, name of downloaded file
    Returns:
        send_file: function call to flask send_file, will send csv file to client.
    """
    df = pd.DataFrame(readings)
    output_buffer = io.BytesIO()
    df.to_csv(output_buffer)
    output_buffer.seek(0)
    filename = (
        filename_base + "_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".csv"
    )
    print(f"Saving file to {filename}")
    return send_file(
        output_buffer, download_name=filename, mimetype="text/csv", as_attachment=True
    )
