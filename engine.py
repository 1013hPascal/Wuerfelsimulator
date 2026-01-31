import csv
import random
import sys, os
from pathlib import Path
from typing import List, Optional

def resource_path(rel_path: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / rel_path

class DiceEngine:
    """
    Lädt Würfelseiten aus einer CSV-Datei (eine Seite pro Zeile) und würfelt zufällig.
    """

    def __init__(self, csv_path: Optional[str] = None):
        # Wenn nichts angegeben ist: dice.csv neben der engine.py bzw. in _MEIPASS (bei EXE)
        self.csv_path = Path(csv_path) if csv_path else resource_path("dice.csv")
        self.sides: List[str] = []
        self.load_sides()

    def load_sides(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV-Datei nicht gefunden: {self.csv_path}")

        sides: List[str] = []
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                value = str(row[0]).strip()
                if value:
                    sides.append(value)

        if len(sides) < 2:
            raise ValueError("Die CSV muss mindestens 2 Seiten enthalten (eine pro Zeile).")

        self.sides = sides

    def roll(self) -> str:
        if not self.sides:
            raise RuntimeError("Keine Würfelseiten geladen.")
        return random.choice(self.sides)
