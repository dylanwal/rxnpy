from pathlib import Path

__all__ = ["elements_data"]

main_path = Path(__file__).parent
elements_data = (main_path / Path(r"elements.txt")).resolve()


