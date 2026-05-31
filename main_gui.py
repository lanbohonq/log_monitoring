import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("1f310.ico"))
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
