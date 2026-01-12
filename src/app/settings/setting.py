from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings derived from environment variables.

    This class handles the loading and validation of configuration parameters
    from a `.env` file or system environment variables. It defines strict types
    for the Visualization Engine.

    Attributes:
        mcp_app_name (str): The name of the MCP application. Defaults to "Viz Engine".
        mcp_app_version (str): The version of the application. Defaults to "0.1.0".
        mcp_app_port (int): The port the MCP server will listen on. Defaults to 3031
            (distinct from SQL MCP to allow parallel execution).
        mcp_env (str): The current environment (e.g., "development", "production").
            Defaults to "development".
        chart_dpi (int): The resolution (dots per inch) for generated images.
            Higher values mean better quality but larger payload sizes. Defaults to 150.
        chart_style (str): The default Seaborn style for plots. Defaults to "whitegrid".
    """

    mcp_app_name: str = "Viz Engine"
    mcp_app_version: str = "0.1.0"
    mcp_app_port: int = 3031
    mcp_env: str = "development"

    chart_dpi: int = 150
    chart_style: str = "whitegrid"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Retrieves a cached instance of the application settings.

    This function ensures that the settings are loaded and validated from the
    environment files only once to improve performance and maintain consistency
    throughout the application lifecycle.

    Returns:
        Settings: The initialized application configuration object.
    """
    return Settings()
