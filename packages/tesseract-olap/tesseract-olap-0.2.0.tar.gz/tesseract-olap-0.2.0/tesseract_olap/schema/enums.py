from enum import Enum
from typing import Optional


class AggregatorType(Enum):
    """Lists the possible aggregation operations to perform on the data to
    return a measure."""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "avg"
    MAX = "max"
    MIN = "min"
    BASICGROUPEDMEDIAN = "basic_grouped_median"
    WEIGHTEDSUM = "weighted_sum"
    WEIGHTEDAVERAGE = "weighted_avg"
    REPLICATEWEIGHTMOE = "replicate_weight_moe"
    CALCULATEDMOE = "moe"
    WEIGHTEDAVERAGEMOE = "weighted_average_moe"

    @classmethod
    def from_str(cls, value: str):
        try:
            return next((item for item in cls if item.value == value))
        except StopIteration:
            raise ValueError(f"Invalid AggregatorType value: {value}")


class DimensionType(Enum):
    """Lists the kinds of data a dimension is storing."""
    STANDARD = "standard"
    TIME = "time"
    GEO = "geo"

    @classmethod
    def from_str(cls, value: Optional[str]):
        if value is None:
            return cls.STANDARD
        value = value.lower()
        return next((item for item in cls if item.value == value), cls.STANDARD)


class MemberType(Enum):
    """Lists the types of the data the user can expect to find in the associated
    column."""
    BOOLEAN = "bool"
    DATE = "date"
    TIME = "time"
    DATETIME = "dttm"
    TIMESTAMP = "stmp"
    FLOAT32 = "f32"
    FLOAT64 = "f64"
    INT8 = "i8"
    INT16 = "i16"
    INT32 = "i32"
    INT64 = "i64"
    STRING = "str"

    @classmethod
    def from_str(cls, value: Optional[str]):
        if value is None:
            return cls.INT64
        value = value.lower()
        return next((item for item in cls if item.value == value), cls.INT64)
