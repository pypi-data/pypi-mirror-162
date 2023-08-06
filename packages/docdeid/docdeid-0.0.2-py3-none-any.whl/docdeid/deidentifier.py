from typing import Optional, Union

from docdeid.annotation.annotation_processor import BaseAnnotationProcessor
from docdeid.annotation.annotator import BaseAnnotator
from docdeid.annotation.redactor import BaseRedactor, RedactAllText, SimpleRedactor
from docdeid.config import Config, ConfigMixin
from docdeid.document.document import Document
from docdeid.exceptions import ErrorHandling, NoAnnotatorsInDeidentifierError
from docdeid.tokenizer.tokenizer import BaseTokenizer


class DocDeid:
    """Main class. Needs more docs."""

    def __init__(
        self,
        tokenizer: Optional[BaseTokenizer] = None,
        config_items: Optional[dict] = None,
        redactor: Optional[BaseRedactor] = None,
        error_handling: ErrorHandling = ErrorHandling.RAISE,
    ):
        """Initialize the deidentifier."""
        self._tokenizer = tokenizer
        self._annotators = {}
        self._annotation_postprocessors = {}
        self._redactor = redactor or SimpleRedactor()
        self.error_handling = error_handling

        self._config = Config(config_items)
        self._init_property_configs()

    def _init_property_configs(self):
        """Add the config to all things that are ConfigMixin it."""

        for _, obj in self.__dict__.items():

            if isinstance(obj, ConfigMixin):
                obj.set_config(self._config)

            if isinstance(obj, list):

                for item in obj:

                    if isinstance(item, ConfigMixin):
                        item.set_config(self._config)

    @staticmethod
    def _get_version() -> str:

        # Todo how?
        return "1.0.0"

    def describe(self) -> dict:
        """Describe by listing all components."""

        description = {
            "docdeid_version": self._get_version(),
            "docdeid_class": type(self).__name__,
            "tokenizer": self._tokenizer.describe(),
            "annotators": [annotator.describe() for annotator in self._annotators],
            "annotation_postprocessors": [
                annotation_postprocessor.describe()
                for annotation_postprocessor in self._annotation_postprocessors
            ],
            "redactor": self._redactor.describe(),
            "config": self._config.describe(),
        }

        return description

    def add_annotator(self, name: str, annotator: BaseAnnotator):
        """Add annotator to the annotation pipeline"""
        self._annotators[name] = annotator

    def remove_annotator(self, name: str):
        """Remove annotator from the annotation pipeline"""

        try:
            del self._annotators[name]
        except KeyError as ex:
            raise KeyError(f"Trying to remove non-existing annotator {name}.") from ex

    def add_annotation_postprocessor(
        self, name: str, annotation_postprocessor: BaseAnnotationProcessor
    ):
        """Add annotation processor to the post-processing pipeline"""
        self._annotation_postprocessors[name] = annotation_postprocessor

    def remove_annotation_postprocessor(self, name: str):
        """Remove annotation processor from the post-processing pipeline"""

        try:
            del self._annotation_postprocessors[name]
        except KeyError as ex:
            raise KeyError(
                f"Trying to remove non-existing annotation postprocessor {name}."
            ) from ex

    def _annotate(self, document: Document) -> Document:
        """Annotate document, and then return it."""

        if len(self._annotators) == 0:
            raise NoAnnotatorsInDeidentifierError(
                "Trying to annotate a text while no annotators are present"
            )

        for annotator in self._annotators.values():
            annotator.annotate(document)

        return document

    def _postprocess_annotations(self, document: Document) -> Document:
        """Applies the annotation_postprocessors in the pipeline."""

        for annotation_processor in self._annotation_postprocessors.values():
            document.apply_annotation_processor(annotation_processor)

        return document

    def _redact(self, annotated_document: Document) -> Document:
        """Deidentify a previously annotated document."""

        annotated_document.apply_redactor(self._redactor)

        return annotated_document

    def deidentify(
        self,
        text: str,
        meta_data: Optional[dict] = None,
        return_only_deidentified_text: Optional[bool] = False,
    ) -> Union[Document, str]:
        """Deidentify a single text, by wrapping it in a Document and returning that."""

        document = Document(text, tokenizer=self._tokenizer, meta_data=meta_data)

        try:

            self._annotate(document)
            self._postprocess_annotations(document)
            self._redact(document)

        except Exception as exception:

            if self.error_handling == ErrorHandling.RAISE:
                raise exception

            if self.error_handling == ErrorHandling.REDACT:
                document.apply_redactor(RedactAllText())

            elif self.error_handling == ErrorHandling.WARN_AND_CONTINUE:
                print(
                    f"Warning: de-identificaiton raised {type(exception).__name__}, continuing."
                )  # TODO: setup logging and warn properly

            else:
                raise ValueError(f"Don't know how to handle {self.error_handling}")

        if return_only_deidentified_text:
            return document.deidentified_text

        return document
