from pypika.terms import Parameter, AggregateFunction


class StringParameter(Parameter):
    """Bracket style with parameter name, e.g. ...WHERE name = {p0}"""

    def get_sql(self, **kwargs) -> str:
        return "{{{0}:String}}".format(self.placeholder)
