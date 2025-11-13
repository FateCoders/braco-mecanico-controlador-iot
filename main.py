import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton,
    QTextEdit, QStatusBar
)
from PySide6.QtCore import Slot

class RobotControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painel de Controle - Braço Robótico")
        self.setGeometry(100, 100, 400, 500) 

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        coord_layout = QFormLayout()
        self.x_input = QLineEdit("0.0")
        self.y_input = QLineEdit("0.0")
        self.z_input = QLineEdit("0.0")
        
        coord_layout.addRow("Posição X:", self.x_input)
        coord_layout.addRow("Posição Y:", self.y_input)
        coord_layout.addRow("Posição Z:", self.z_input)
        
        main_layout.addLayout(coord_layout)

        action_layout = QHBoxLayout()
        self.gripper_button = QPushButton("Abrir/Fechar Garra")
        self.calibrate_button = QPushButton("Calibrar Posição")
        
        action_layout.addWidget(self.gripper_button)
        action_layout.addWidget(self.calibrate_button)
        
        main_layout.addLayout(action_layout)

        main_layout.addWidget(QLabel("Log de Comandos:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        self.setStatusBar(QStatusBar(self))
        self.update_status("Desconectado")

        self.gripper_button.clicked.connect(self.on_toggle_gripper)
        self.calibrate_button.clicked.connect(self.on_calibrate)
        
        self.connect_to_hardware()

    @Slot()
    def on_toggle_gripper(self):
        self_x = self.x_input.text() 
        self.log_to_console("Comando: Acionar Garra")

    @Slot()
    def on_calibrate(self):
        self.log_to_console("Iniciando calibração...")
        

    def connect_to_hardware(self):

        self.update_status("Falha na conexão")
        self.log_to_console("Erro: Não foi possível encontrar o hardware.")

    def update_status(self, message):
        """Atualiza a mensagem na barra de status."""
        self.statusBar().showMessage(message)

    def log_to_console(self, message):
        """Adiciona uma mensagem à área de log."""
        self.log_area.append(message) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotControlWindow()
    window.show()
    sys.exit(app.exec())