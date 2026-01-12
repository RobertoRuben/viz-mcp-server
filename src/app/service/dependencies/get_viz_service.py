from functools import lru_cache

from settings import get_settings

from ..impl import VizServiceImpl
from ..interface import IVizService


@lru_cache
def get_viz_service() -> IVizService:
    """Provides a singleton instance of the Visualization Service.

    We use @lru_cache to ensure only one instance of the service exists
    throughout the application lifecycle. This is critical because the
    service manages an asyncio.Lock for the global Matplotlib state.

    Returns:
        IVizService: The active visualization service instance.
    """
    settings = get_settings()
    return VizServiceImpl(settings)
