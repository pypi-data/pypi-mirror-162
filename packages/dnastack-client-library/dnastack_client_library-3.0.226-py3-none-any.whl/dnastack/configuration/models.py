from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from dnastack.client.models import ServiceEndpoint as Endpoint

DEFAULT_CONTEXT = 'default'


class Context(BaseModel):
    model_version: float = 1.0

    # This is the short-type-to-service-id map.
    defaults: Dict[str, str] = Field(default_factory=lambda: dict())

    endpoints: List[Endpoint] = Field(default_factory=lambda: list())


class Configuration(BaseModel):
    """
    Configuration

    Please note that "defaults" and "endpoints" are for backward compatibility. They are ignored in version 4 onward.
    """
    version: float = 4

    #############
    # Version 4 #
    #############
    current_context: str = Field(default_factory=lambda: DEFAULT_CONTEXT)
    contexts: Dict[str, Context] = Field(default_factory=lambda: dict())

    ###############################################################
    # Version 3 (for object migration and backward compatibility) #
    ###############################################################
    defaults: Optional[Dict[str, str]]
    endpoints: Optional[List[Endpoint]]
