from abc import ABC, abstractmethod


class IVizService(ABC):
    """Abstract base class defining the contract for the Visualization Service.

    This interface outlines the core capabilities required for generating charts
    from raw data and Python code, ensuring decoupling between the MCP controller
    and the execution logic.
    """

    @abstractmethod
    async def generate_chart(self, data: list[dict[str, object]], code: str) -> str:
        """Generates a chart image from data and execution code.

        Args:
            data (list[dict[str, object]]): The source data as a list of dictionaries.
            code (str): The Python code snippet (matplotlib/seaborn) to execute.

        Returns:
            str: The filename of the saved chart (e.g., 'chart_a1b2c3d4.png').

        Raises:
            ValueError: If the data is empty or the code execution fails.
        """
        pass

    @abstractmethod
    async def inspect_data(self, data: list[dict[str, any]]) -> str:
        """Generates a statistical summary of the provided data.

        Args:
            data (list[dict[str, any]]): The source data to analyze.
        Returns:
            str: A text summary (e.g., DataFrame.describe()) of the dataset.
        """
        pass

    @abstractmethod
    async def get_system_info(self) -> dict[str, str]:
        """Retrieves runtime environment details.

        Returns:
            dict[str, str]: Key-value pairs of library versions (Python, Polars, etc.)
                            to help the LLM generate compatible code.
        """
        pass
