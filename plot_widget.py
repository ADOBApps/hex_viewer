"""
Author: Acxel Orozco
Date: 20/01/2026 (Started)
Last modification: 01/02/2026
Hexadecimal/Binary Viewer inspired by Kate Morley web tool - Quantum Analysis Helper (QHA)

QAH is a python software for plot and analyze Quantum Espresso DOS, 
PDOS and Bands structures with a friendly GUI and extensive plugins.

This file is part of QHA.
QHA is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

QHA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) [2026] Acxel David Orozco Baldomero
"""

import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QLabel, QFileDialog, QStyle,
                              QScrollArea, QTextEdit, QFrame, QApplication)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

class HexViewerWidget(QWidget):
    def __init__(self, plugin_instance=None):
        super().__init__()
        self.plugin = plugin_instance
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header Area
        header_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        select_btn = QPushButton("Select Binary File")
        select_btn.setIcon(
            QApplication.style().standardIcon(QStyle.SP_DriveHDIcon)
        )
        select_btn.clicked.connect(self.open_file)
        
        header_layout.addWidget(select_btn)
        header_layout.addWidget(self.file_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Hex Display Area
        # Using a monospace font is critical for alignment, similar to the reference page
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setFont(QFont("Courier New", 10))
        self.display.setLineWrapMode(QTextEdit.NoWrap)
        
        layout.addWidget(self.display)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Binary File", "")
        if file_path:
            self.file_label.setText(file_path.split('/')[-1])
            self.load_hex_data(file_path)

    def load_hex_data(self, file_path):
        """Processes the file locally and formats it into hex/ASCII columns."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(4096000000) # Reading first 4GB to maintain performance
                
            output = []
            # Header Row
            output.append("Offset    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  Decoded Text")
            output.append("-" * 75)

            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                
                # 1. Offset Column
                offset = f"{i:08x}  "
                
                # 2. Hex Bytes Column
                hex_values = " ".join(f"{b:02x}" for b in chunk)
                # Padding for short rows at the end of the file
                hex_values = hex_values.ljust(47)
                
                # 3. ASCII/Decoded Text Column
                # Non-printable characters are replaced with '.'
                ascii_text = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                
                output.append(f"{offset} {hex_values}  {ascii_text}")

            self.display.setPlainText("\n".join(output))
            
            if len(data) == 4096:
                self.display.append("\n... [File truncated to 4GB for preview] ...")
                
        except Exception as e:
            self.display.setPlainText(f"Error reading file: {str(e)}")