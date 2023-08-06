class DescribeMixin:
    """Used to make an object describable."""

    def describe(self) -> str:
        """
        Default behaviour: Class(property1=value, property2=value)
        :return: The description.
        """
        args = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{type(self).__name__}({args})"
