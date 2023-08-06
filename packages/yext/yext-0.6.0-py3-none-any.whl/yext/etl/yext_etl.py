from typing import List, Optional, Callable
from .transform_profile import transform_profile
from .mapping import Mapping
from ..yext_client import YextClient
from ..exceptions import YextException


class YextETL(YextClient):

    """
    A class for running ETLs with Yext. YextETL is a sub-class of YextClient,
    so it has all the associated methods.

    Args:
    ----
        entity_type: str
            The API name of the target entity type in the Knowledge Graph.
        mappings: List[dict]
            A list of the mappings. These must include a `source_field`, a
            `kg_field`, and optionally a `transform` callable and a
            `required` boolean. See docs for yext.etl.Mapping for more.
    """

    def __init__(
        self,
        entity_type: str,
        mappings: Optional[List[dict]],
        base_profile: Optional[dict] = {},
        **kwargs
    ):
        super().__init__(**kwargs)
        self.entity_type = entity_type
        self.mappings = mappings

    def fetch_source_profiles(self, func):
        """
        Decorator function for the user-defined function that fetches the
        entities from the source system.
        """
        self.fetch_source_profiles = func

    def on_error(self, func: Callable):
        """
        Callback decorator function for successful upload. Must take one argument
        for profile.
        """
        self.on_error = func

    def on_complete(self, func: Callable):
        """
        Callback decorator function for error handling. Must take one argument
        for profile and another for the exception.
        """
        self.on_complete = func

    def run(self):
        """
        Runs the ETL. No arguments currently.
        """
        source_profiles = self.fetch_source_profiles()
        for source_profile in source_profiles:
            transformed_profile = transform_profile(
                source_profile, self.mappings
            )
            try:
                self.upsert_entity(
                    profile=transformed_profile,
                    entity_type=self.entity_type,
                    format="html",
                    strip_unsupported_formats=True,
                )
                if self.on_complete:
                    self.on_complete(transformed_profile)
            except YextException as exc:
                if self.on_error:
                    self.on_error(profile=transformed_profile, exception=exc)
                else:
                    pass