import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import QTimer
import win32com.client

from engine import DiceEngine

CSV_DATEI = "dice.csv"


class Speaker:
    """Windows TTS (SAPI) asynchron, damit die GUI nicht blockiert."""
    def __init__(self):
        self._voice = None

    def _init(self):
        if self._voice is None:
            self._voice = win32com.client.Dispatch("SAPI.SpVoice")
            self._voice.Volume = 100
            self._voice.Rate = 0

    def speak_async(self, text: str):
        def run():
            self._init()
            self._voice.Speak(text)
        threading.Thread(target=run, daemon=True).start()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Würfelsimulator")

        self.speaker = Speaker()

        # Engine laden
        try:
            self.engine = DiceEngine(CSV_DATEI)
            self.startup_error = None
        except Exception as e:
            self.engine = None
            self.startup_error = str(e)

        # UI
        self.lbl_info = QLabel("Würfeln (Enter oder Leertaste)")
        self.btn_roll = QPushButton("Würfeln")
        self.btn_roll.setAccessibleName("Würfeln Schalter")
        self.btn_roll.clicked.connect(self.on_roll)

        # Button per Enter/Leertaste auslösen:
        # QPushButton macht das i.d.R. automatisch, aber wir setzen zusätzlich Default
        self.btn_roll.setDefault(True)
        self.btn_roll.setAutoDefault(True)

        self.out = QListWidget()
        self.out.setAccessibleName("Ausgabe Liste")

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.btn_roll)
        layout.addWidget(self.out)
        self.setLayout(layout)

        # Fokus auf Button (damit Enter/Space sofort funktionieren)
        self.btn_roll.setFocus()

        # Startup-Status anzeigen / sprechen
        QTimer.singleShot(0, self.after_show)

    def after_show(self):
        if self.startup_error:
            self.out.addItem(QListWidgetItem("Fehler beim Laden der CSV:"))
            self.out.addItem(QListWidgetItem(self.startup_error))
            QMessageBox.critical(self, "Fehler", f"CSV konnte nicht geladen werden:\n{self.startup_error}")
        else:
            sides_count = len(self.engine.sides)
            self.out.addItem(QListWidgetItem(f"CSV geladen: {sides_count} Seiten."))
            self.out.addItem(QListWidgetItem("Bereit zum Würfeln."))
            self.speaker.speak_async("Würfelsimulator gestartet. Bereit zum Würfeln.")

    def on_roll(self):
        if self.engine is None:
            QMessageBox.critical(self, "Fehler", f"CSV/Engine nicht geladen:\n{self.startup_error}")
            return

        try:
            result = self.engine.roll()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return

        # Ausgabe: oben das neueste Ergebnis
        self.out.insertItem(0, QListWidgetItem(f"Ergebnis: {result}"))
        self.out.setCurrentRow(0)

        # Ansage
        self.speaker.speak_async(f"{result}")

        # Fokus zurück auf Button, damit Enter/Space sofort wieder würfelt
        self.btn_roll.setFocus()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(520, 420)
    w.show()
    sys.exit(app.exec())
