"""
ChessWithQuests – šachy s definovatelnou deskou, figurkami a kwesty.
Spuštění:  python main.py   (z kořenové složky projektu)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller.app_controller import AppController  # noqa: E402

if __name__ == "__main__":
    AppController().spust()
