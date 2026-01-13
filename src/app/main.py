import json
from typing import Any

from fastmcp import FastMCP, Context
from settings import get_settings
from service.dependencies import get_viz_service

settings = get_settings()
mcp = FastMCP(
    name=settings.mcp_app_name,
    version=settings.mcp_app_version,
    port=settings.mcp_app_port,
)


@mcp.tool(
    name="generate_chart",
    description="Generates a visualization and saves it to the server disk. Returns a FILENAME reference to be used with the Telegram tool.",
    tags={"visualization", "chart", "python", "plotting", "file"},
)
async def generate_chart(data: str, code: str, ctx: Context) -> str:
    """Executes Python plotting code and saves the result to the shared volume.

    Args:
        data (str): A JSON string representing the dataset.
        code (str): The Python script to execute.
        ctx (Context): The execution context.

    Returns:
        str: A message containing the filename reference (e.g., 'chart_xyz.png').
    """
    ctx.info("Received request to generate chart.")
    service = get_viz_service()

    try:
        try:
            parsed_data: list[dict[str, Any]] = json.loads(data)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format in 'data' argument. {str(e)}"

        filename = await service.generate_chart(parsed_data, code)

        ctx.info(f"Chart generated and saved to {filename}")

        return (
            f"SUCCESS: Chart generated and saved as '{filename}'.\n"
            f"Please pass this exact filename '{filename}' to the 'send_chart_from_disk' tool "
            f"in the Telegram server to send it."
        )

    except ValueError as e:
        ctx.error(f"Validation error: {e}")
        return f"Error generating chart: {str(e)}"
    except Exception as e:
        ctx.error(f"Unexpected error: {e}")
        return f"Critical error: {str(e)}"


@mcp.tool(
    name="inspect_data",
    description="Analyzes dataset structure, schema, and statistics.",
    tags={"data-analysis", "statistics", "schema", "inspection"},
)
async def inspect_data(data: str, ctx: Context) -> str:
    ctx.info("Inspecting data structure.")
    service = get_viz_service()
    try:
        parsed_data: list[dict[str, Any]] = json.loads(data)
        report = await service.inspect_data(parsed_data)
        return report
    except json.JSONDecodeError:
        return "Error: Invalid JSON format."
    except Exception as e:
        return f"Error inspecting data: {str(e)}"


@mcp.tool(
    name="get_environment_info",
    description="Returns installed library versions.",
    tags={"system", "debug", "version", "environment"},
)
async def get_environment_info() -> str:
    service = get_viz_service()
    info = await service.get_system_info()
    return f"Python: {info['python_version']}, Polars: {info['polars_version']}, Matplotlib: {info['matplotlib_version']}"


if __name__ == "__main__":
    mcp.run()
