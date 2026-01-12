import json
import base64
from typing import Any

from mcp.types import ImageContent
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
    description="Generates a static PNG visualization from raw data using Python. Requires data as a JSON string and plotting code.",
    tags={"visualization", "chart", "python", "plotting", "image"},
)
async def generate_chart(data: str, code: str, ctx: Context) -> list[Any] | str:
    """Executes Python plotting code to generate a chart from provided data.

    Args:
        data (str): A JSON string representing the dataset (list of dicts).
        code (str): The Python script to execute. Must reference `df`.
        ctx (Context): The execution context for server-side logging.

    Returns:
        list[ImageContent] | str: A list containing the image content for Claude to render,
            or an error string.
    """
    ctx.info("Received request to generate chart.")
    service = get_viz_service()

    try:
        try:
            parsed_data: list[dict[str, Any]] = json.loads(data)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format in 'data' argument. {str(e)}"

        image_bytes = await service.generate_chart(parsed_data, code)

        ctx.info("Chart generated successfully.")

        base64_data = base64.b64encode(image_bytes).decode("utf-8")

        return [ImageContent(type="image", data=base64_data, mimeType="image/png")]

    except ValueError as e:
        ctx.error(f"Validation error: {e}")
        return f"Error generating chart: {str(e)}"
    except Exception as e:
        ctx.error(f"Unexpected error: {e}")
        return f"Critical error: {str(e)}"


@mcp.tool(
    name="inspect_data",
    description="Analyzes dataset structure, schema, and statistics. MANDATORY step before generating charts.",
    tags={"data-analysis", "statistics", "schema", "inspection"},
)
async def inspect_data(data: str, ctx: Context) -> str:
    """Generates a statistical summary and schema report for a dataset."""
    ctx.info("Inspecting data structure.")
    service = get_viz_service()

    try:
        parsed_data: list[dict[str, Any]] = json.loads(data)
        report = await service.inspect_data(parsed_data)
        return report

    except json.JSONDecodeError:
        return "Error: Invalid JSON format. Please provide a valid JSON string."
    except Exception as e:
        return f"Error inspecting data: {str(e)}"


@mcp.tool(
    name="get_environment_info",
    description="Returns installed library versions (Python, Polars, Matplotlib). Use for syntax validation.",
    tags={"system", "debug", "version", "environment"},
)
async def get_environment_info() -> str:
    """Retrieves runtime environment details for code compatibility."""
    service = get_viz_service()
    info = await service.get_system_info()

    return (
        f"--- RUNTIME ENVIRONMENT ---\n"
        f"Python: {info['python_version']}\n"
        f"OS: {info['platform']}\n"
        f"--- LIBRARIES ---\n"
        f"Polars: {info['polars_version']}\n"
        f"Matplotlib: {info['matplotlib_version']} (Backend: {info['backend']})\n"
        f"Seaborn: {info['seaborn_version']}"
    )


if __name__ == "__main__":
    mcp.run()
