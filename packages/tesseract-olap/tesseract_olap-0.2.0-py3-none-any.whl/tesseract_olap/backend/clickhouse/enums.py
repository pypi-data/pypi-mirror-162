from tesseract_olap.backend import InvalidAggregatorError
from tesseract_olap.schema import aggregators


class ClickhouseAggregator:
    """"""

    @staticmethod
    def from_aggregator(agg: aggregators.Aggregator, measure_column: str):
        if isinstance(agg, aggregators.Sum):
            return f"SUM({measure_column})"

        if isinstance(agg, aggregators.Count):
            return "SUM({})"

        if isinstance(agg, aggregators.Average):
            return "SUM({})"

        if isinstance(agg, aggregators.Max):
            return "SUM({})"

        if isinstance(agg, aggregators.Min):
            return "SUM({})"

        if isinstance(agg, aggregators.BasicGroupedMedian):
            return "SUM({})"

        if isinstance(agg, aggregators.WeightedSum):
            return "SUM({})"

        if isinstance(agg, aggregators.WeightedAverage):
            return "SUM({})"

        if isinstance(agg, aggregators.ReplicateWeightMoe):
            return "SUM({})"

        if isinstance(agg, aggregators.CalculatedMoe):
            return "SUM({})"

        if isinstance(agg, aggregators.WeightedAverageMoe):
            return "SUM({})"

        raise InvalidAggregatorError("Clickhouse", str(agg))
