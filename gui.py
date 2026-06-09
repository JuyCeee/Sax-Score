from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QPushButton
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sax Score")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        label = QLabel("Welcome to Sax Score!")
        button = QPushButton("Click me!")
        layout.addWidget(label)
        layout.addWidget(button)
        self.setLayout(layout)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()
    sys.exit(app.exec())