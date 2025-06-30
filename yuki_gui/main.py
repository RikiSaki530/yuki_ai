from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

app = QApplication([])

window = QWidget()
layout = QVBoxLayout()

label = QLabel("こんにちは、riki！")
layout.addWidget(label)

window.setLayout(layout)
window.setWindowTitle("雪ちゃんの部屋")
window.resize(300, 200)
window.show()

app.exec()