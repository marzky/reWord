from PyQt5 import QtWidgets
import ctypes
from ctypes import wintypes

class Core():

    def set_title_bar_color(hwnd):
        dwmapi = ctypes.windll.dwmapi
        DWMWA_CAPTION_COLOR = 35
        color = wintypes.DWORD(0x00050505)
        hwnd = wintypes.HWND(hwnd)
        dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(color), ctypes.sizeof(color))

    @staticmethod
    def create_warning_box(title, desc):
        box = QtWidgets.QMessageBox()
        box.setWindowTitle(title)
        box.setText(desc)
        box.setIcon(QtWidgets.QMessageBox.Warning)
        box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        box.setStyleSheet("""
            QMessageBox {
                background-color: #111;
                border: none;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #222;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF2C55;
                color: black;
            }
        """)
        box.exec_()