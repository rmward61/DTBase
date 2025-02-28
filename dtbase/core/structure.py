"""
Module to define the structure of the database. Each Class, defines a table in the
database.
    __tablename__: creates the table with the name given
    __table_args__: table arguments eg: __table_args__ = {'sqlite_autoincrement': True}
"""

import re
from typing import Any

from bcrypt import checkpw, gensalt, hashpw
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
FsqlaModel = db.Model

datatype_name = Enum("string", "float", "integer", "boolean", name="value_datatype")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Locations


class Location(FsqlaModel):
    """
    This class describes all the physical locations in the digital twin.
    """

    __tablename__ = "location"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(
        Integer,
        ForeignKey("location_schema.id"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # relationshionships (One-To-Many)
    string_values_relationship = relationship("LocationStringValue")
    integer_values_relationship = relationship("LocationIntegerValue")
    float_values_relationship = relationship("LocationFloatValue")
    boolean_values_relationship = relationship("LocationBooleanValue")

    # arguments
    __table_args__ = (UniqueConstraint("id"),)


class LocationIdentifier(FsqlaModel):
    """
    Variables that can be used to identify locations in the digital twin.
    """

    __tablename__ = "location_identifier"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    units = Column(String(100), nullable=True)
    datatype = Column(datatype_name, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("name", "units"),)


class LocationSchema(FsqlaModel):
    """Types of locations."""

    __tablename__ = "location_schema"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("name"),)


class LocationSchemaIdentifierRelation(FsqlaModel):
    """Relations on which location identifiers can and should be specified for which
    location schemas.
    """

    __tablename__ = "location_schema_identifier_relation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(
        Integer,
        ForeignKey(
            "location_schema.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    identifier_id = Column(
        Integer,
        ForeignKey("location_identifier.id"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("schema_id", "identifier_id"),)


class LocationStringValue(FsqlaModel):
    """
    The value of a string variable that can be used to identify locations in the digital
    twin.
    """

    __tablename__ = "location_string_value"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)
    identifier_id = Column(
        Integer,
        ForeignKey("location_identifier.id"),
        nullable=False,
    )
    location_id = Column(
        Integer,
        ForeignKey("location.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("identifier_id", "location_id"),)


class LocationIntegerValue(FsqlaModel):
    """
    The value of an integer variable that can be used to identify locations in the
    digital twin.
    """

    __tablename__ = "location_integer_value"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer, nullable=False)
    identifier_id = Column(
        Integer,
        ForeignKey("location_identifier.id"),
        nullable=False,
    )
    location_id = Column(
        Integer,
        ForeignKey("location.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("identifier_id", "location_id"),)


class LocationFloatValue(FsqlaModel):
    """
    The value of a floating point number variable that can be used to identify locations
    in the digital twin.
    """

    __tablename__ = "location_float_value"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Float, nullable=False)
    identifier_id = Column(
        Integer,
        ForeignKey("location_identifier.id"),
        nullable=False,
    )
    location_id = Column(
        Integer,
        ForeignKey("location.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("identifier_id", "location_id"),)


class LocationBooleanValue(FsqlaModel):
    """
    The value of a boolean variable that can be used to identify locations in the
    digital twin.
    """

    __tablename__ = "location_boolean_value"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Boolean, nullable=False)
    identifier_id = Column(
        Integer,
        ForeignKey("location_identifier.id"),
        nullable=False,
    )
    location_id = Column(
        Integer,
        ForeignKey("location.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("identifier_id", "location_id"),)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Sensors


class Sensor(FsqlaModel):
    """
    Class for sensors.
    """

    __tablename__ = "sensor"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(Integer, ForeignKey("sensor_type.id"), nullable=False)
    unique_identifier = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # relationshionships (One-To-Many)
    string_values_relationship = relationship("SensorStringReading")
    integer_values_relationship = relationship("SensorIntegerReading")
    float_values_relationship = relationship("SensorFloatReading")
    boolean_values_relationship = relationship("SensorBooleanReading")

    # arguments
    __table_args__ = (UniqueConstraint("unique_identifier"),)


class SensorMeasure(FsqlaModel):
    """
    Variables measured by sensors, e.g. temperature, pressure, electricity consumption.
    """

    __tablename__ = "sensor_measure"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    units = Column(String(100), nullable=True)
    datatype = Column(datatype_name, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("name", "units"),)


class SensorType(FsqlaModel):
    """Types of sensors."""

    __tablename__ = "sensor_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("name"),)


class SensorTypeMeasureRelation(FsqlaModel):
    """Relations on which sensor measures can and should have readings for which
    sensor types.
    """

    __tablename__ = "sensor_type_measure_relation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_id = Column(
        Integer,
        ForeignKey("sensor_type.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    measure_id = Column(
        Integer,
        ForeignKey("sensor_measure.id"),
        nullable=False,
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("type_id", "measure_id"),)


class SensorStringReading(FsqlaModel):
    """
    Sensor reading of a string variable.
    """

    __tablename__ = "sensor_string_reading"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)
    measure_id = Column(
        Integer,
        ForeignKey("sensor_measure.id"),
        nullable=False,
    )
    sensor_id = Column(
        Integer,
        ForeignKey("sensor.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("measure_id", "sensor_id", "timestamp"),)


class SensorIntegerReading(FsqlaModel):
    """
    Sensor reading of a integer variable.
    """

    __tablename__ = "sensor_integer_reading"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Integer, nullable=False)
    measure_id = Column(
        Integer,
        ForeignKey("sensor_measure.id"),
        nullable=False,
    )
    sensor_id = Column(
        Integer,
        ForeignKey("sensor.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("measure_id", "sensor_id", "timestamp"),)


class SensorFloatReading(FsqlaModel):
    """
    Sensor reading of a float variable.
    """

    __tablename__ = "sensor_float_reading"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Float, nullable=False)
    measure_id = Column(
        Integer,
        ForeignKey("sensor_measure.id"),
        nullable=False,
    )
    sensor_id = Column(
        Integer,
        ForeignKey("sensor.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("measure_id", "sensor_id", "timestamp"),)


class SensorBooleanReading(FsqlaModel):
    """
    Sensor reading of a boolean variable.
    """

    __tablename__ = "sensor_boolean_reading"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Boolean, nullable=False)
    measure_id = Column(
        Integer,
        ForeignKey("sensor_measure.id"),
        nullable=False,
    )
    sensor_id = Column(
        Integer,
        ForeignKey("sensor.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint("measure_id", "sensor_id", "timestamp"),)


class SensorLocation(FsqlaModel):
    """
    Location history of a sensor.
    """

    __tablename__ = "sensor_location"

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)

    sensor_id = Column(
        Integer,
        ForeignKey("sensor.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False)
    installation_datetime = Column(DateTime(timezone=True), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("sensor_id", "installation_datetime"),)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Model data


class Model(FsqlaModel):
    """
    Predictive models used in the digital twin.
    """

    __tablename__ = "model"

    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class ModelScenario(FsqlaModel):
    """
    Scenarios distinguish between different ways of running a model, e.g. varying some
    parameters in the model. Each row in this table corresponds to one scenario for how
    one model can be run.

    Currently the scenario feature is quite basic: The scenarios are simply described by
    strings. This is to accommodate the very different kinds of scenarios different
    models may have, without making the database schema overly complicated.
    """

    __tablename__ = "model_scenario"

    # columns
    id = Column(Integer, primary_key=True)
    model_id = Column(
        Integer,
        ForeignKey("model.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    description = Column(Text, nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("model_id", "description"),)


class ModelMeasure(FsqlaModel):
    """
    Measures that models can predict values for.

    Similar to SensorMeasure, but distinct, because models might for instance predict
    not only values for observables, but also e.g. upper and lower bounds.
    """

    __tablename__ = "model_measure"

    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    units = Column(String(100), nullable=False)
    datatype = Column(datatype_name, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("name", "units"),)


class ModelRun(FsqlaModel):
    """
    A ModelRun is a single instance of running a model at a particular time with a
    particular scenario.
    Optionally it may include a sensor_id and a measure for that sensor, so that
    we can compare to the actual values.
    """

    __tablename__ = "model_run"

    # columns
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("model.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("model_scenario.id"), nullable=True)
    sensor_id = Column(Integer, ForeignKey("sensor.id"), nullable=True)
    sensor_measure_id = Column(Integer, ForeignKey("sensor_measure.id"), nullable=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("model_id", "scenario_id", "time_created"),)


class ModelProduct(FsqlaModel):
    """
    A ModelProduct is a combination of a ModelRun and a ModelMeasure that is (one of)
    the output(s) of that run.
    """

    __tablename__ = "model_product"

    # columns
    id = Column(Integer, primary_key=True)
    run_id = Column(
        Integer,
        ForeignKey("model_run.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    measure_id = Column(Integer, ForeignKey("model_measure.id"), nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("run_id", "measure_id"),)


class ModelStringValue(FsqlaModel):
    """
    Predicted values from a model product, that are strings.
    """

    __tablename__ = "model_string_value"

    # columns
    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("model_product.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("product_id", "timestamp"),)


class ModelIntegerValue(FsqlaModel):
    """
    Predicted values from a model product, that are integers.
    """

    __tablename__ = "model_integer_value"

    # columns
    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("model_product.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("product_id", "timestamp"),)


class ModelFloatValue(FsqlaModel):
    """
    Predicted values from a model product, that are floats.
    """

    __tablename__ = "model_float_value"

    # columns
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("model_product.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("product_id", "timestamp"),)


class ModelBooleanValue(FsqlaModel):
    """
    Predicted values from a model product, that are booleans.
    """

    __tablename__ = "model_booleanvalue"

    # columns
    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("model_product.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Boolean, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("product_id", "timestamp"),)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Other


def is_email(candidate: str) -> bool:
    """Check whether a given string can plausibly be an email.

    Not a strict check for the official schema of email addresses, but more practically
    just checks if the string is of the form [blahblah]@[blah].
    """
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b"
    return re.fullmatch(regex, candidate) is not None


class User(FsqlaModel):
    """
    Class for user credentials.
    """

    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(LargeBinary, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self: "User", **kwargs: Any) -> None:
        for prop, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            setattr(self, prop, value)

    def __setattr__(self: "User", prop: str, value: str) -> None:
        """Like setattr, but if the property we are setting is the password, hash it."""
        if prop == "password":
            value = hashpw(value.encode("utf8"), gensalt())
        if prop == "email":
            if not isinstance(value, str) or not is_email(value):
                raise ValueError("Not a valid email address: %s", value)
        super().__setattr__(prop, value)

    def __repr__(self: "User") -> str:
        """
        Computes a string representation of the object.
        """
        return str(self.email)

    def check_password(self: "User", password: str) -> bool:
        """Return a boolean for whether this is the right password for this user."""
        return checkpw(password.encode("utf8"), self.password)
