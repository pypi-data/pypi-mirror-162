from abc import ABC, abstractmethod

from docdeid.annotation.annotation import Annotation
from docdeid.config import ConfigMixin
from docdeid.describe import DescribeMixin


class BaseAnnotationProcessor(ABC, DescribeMixin, ConfigMixin):
    """An AnnotationProcessor performs operations on a list of annotations."""

    @abstractmethod
    def process(self, annotations: set[Annotation]) -> set[Annotation]:
        """
        Process the annotations.

        Args:
            annotations: The input annotations.

        Returns: A set of annotations, processed.

        """


class LeftRightOverlapResolver(BaseAnnotationProcessor):
    """Does a pass from left to right, and only includes non-overlapping annotations."""

    def process(self, annotations: set[Annotation]) -> set[Annotation]:

        annotations = sorted(list(annotations), key=lambda a: a.start_char)

        result = set()
        last_end_char = -1

        for annotation in annotations:

            if annotation.start_char >= last_end_char:
                result.add(annotation)
                last_end_char = annotation.end_char

        return result
