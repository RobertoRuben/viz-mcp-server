import asyncio
import io
import platform
import sys

import matplotlib
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
from settings import Settings

from ..interface import IVizService


class VizServiceImpl(IVizService):
    """Implementation of IVizService using Polars and Matplotlib/Seaborn.

    This class handles the safe execution of plotting code and manages the
    rendering context to ensure images are generated in memory without
    filesystem side effects.

    Attributes:
        settings (Settings): Application configuration settings.
        _lock (asyncio.Lock): Mutex to prevent race conditions on the global
            Matplotlib state machine.
    """

    def __init__(self, settings: Settings):
        """Initializes the service with configuration and threading safety.

        Args:
            settings (Settings): The injected application settings.
        """
        self.settings = settings
        self._lock = asyncio.Lock()

        plt.switch_backend("Agg")
        sns.set_theme(style=self.settings.chart_style)

    async def generate_chart(self, data: list[dict[str, object]], code: str) -> bytes:
        """Generates a chart image from data and execution code.

        It uses an asyncio Lock to ensure exclusive access to the Matplotlib
        pyplot state machine during the rendering process.

        Args:
            data (list[dict[str, object]]): The source data.
            code (str): The Python plotting code.

        Returns:
            bytes: The PNG image data.

        Raises:
            ValueError: If data parsing fails or code execution errors occur.
        """
        try:
            df = pl.DataFrame(data)
            if df.is_empty():
                raise ValueError("The provided dataset is empty.")
        except Exception as e:
            raise ValueError(f"Failed to parse data into Polars DataFrame: {e}")

        async with self._lock:
            try:
                plt.clf()
                plt.figure(figsize=(10, 6))

                local_context = {"df": df, "pl": pl, "plt": plt, "sns": sns}

                exec(code, {}, local_context)

                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png", dpi=self.settings.chart_dpi)

                plt.close()
                buffer.seek(0)

                return buffer.read()

            except Exception as e:
                plt.close()
                raise ValueError(f"Error executing plotting code: {e}")

    async def inspect_data(self, data: list[dict[str, object]]) -> str:
        """Generates a statistical summary of the provided data using Polars."""
        try:
            df = pl.DataFrame(data)
            if df.is_empty():
                return "Dataset is empty."

            info = []
            info.append("--- DATA STRUCTURE ---")
            info.append(f"Rows: {df.height}, Columns: {df.width}")

            info.append("\n--- COLUMNS & TYPES ---")
            info.append(str(df.schema))

            info.append("\n--- STATISTICAL SUMMARY ---")
            info.append(str(df.describe()))

            return "\n".join(info)

        except Exception as e:
            raise ValueError(f"Failed to inspect data: {e}")

    async def get_system_info(self) -> dict[str, str]:
        return {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "polars_version": pl.__version__,
            "matplotlib_version": matplotlib.__version__,
            "seaborn_version": sns.__version__,
            "backend": matplotlib.get_backend(),
        }
