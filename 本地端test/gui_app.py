import sys
import csv
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView
)

from pii_core import run_scan


class ScanWorker(QObject):
    finished = Signal(list)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    @Slot()
    def run(self):
        try:
            results = run_scan(self.config, self.progress.emit)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("本地端個資掃描工具")
        self.resize(1100, 700)

        self.results = []
        self.thread = None
        self.worker = None

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # ===== 設定區 =====
        form_layout = QFormLayout()

        self.scan_root_edit = QLineEdit(r"C:\Users\kevin\Desktop\pii_test")
        self.restricted_root_edit = QLineEdit(r"C:\Users\kevin\Desktop\pii_test\_restricted")

        form_layout.addRow("掃描路徑", self.scan_root_edit)
        form_layout.addRow("Restricted 路徑", self.restricted_root_edit)

        main_layout.addLayout(form_layout)

        # ===== 按鈕區 =====
        btn_layout = QHBoxLayout()

        self.scan_btn = QPushButton("開始掃描")
        self.export_btn = QPushButton("匯出 CSV")
        self.clear_btn = QPushButton("清空結果")

        self.export_btn.setEnabled(False)

        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.clear_btn)

        main_layout.addLayout(btn_layout)

        # ===== 狀態區 =====
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("執行紀錄會顯示在這裡...")
        main_layout.addWidget(QLabel("執行紀錄"))
        main_layout.addWidget(self.log_text)

        # ===== 表格區 =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "檔名", "副檔名", "完整路徑", "大小(KB)", "個資類型", "處理結果"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(QLabel("掃描結果"))
        main_layout.addWidget(self.table)

        # ===== 事件綁定 =====
        self.scan_btn.clicked.connect(self.start_scan)
        self.export_btn.clicked.connect(self.export_csv)
        self.clear_btn.clicked.connect(self.clear_results)

    def append_log(self, message):
        self.log_text.append(message)

    def get_config(self):
        return {
            "scan_root": self.scan_root_edit.text().strip(),
            "restricted_root": self.restricted_root_edit.text().strip(),
        }

    def validate_inputs(self):
        config = self.get_config()
        required_fields = {
            "掃描路徑": config["scan_root"],
            "Restricted 路徑": config["restricted_root"],
        }

        for label, value in required_fields.items():
            if not value:
                QMessageBox.warning(self, "欄位未填", f"{label} 不能空白")
                return False
        return True

    @Slot()
    def start_scan(self):
        if not self.validate_inputs():
            return

        self.scan_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.append_log("開始掃描...")

        config = self.get_config()

        self.thread = QThread()
        self.worker = ScanWorker(config)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.append_log)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.error.connect(self.on_scan_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.start()

    @Slot(list)
    def on_scan_finished(self, results):
        self.results = results
        self.populate_table(results)
        self.append_log(f"掃描完成，共找到 {len(results)} 個含個資檔案")
        self.scan_btn.setEnabled(True)
        self.export_btn.setEnabled(len(results) > 0)

    @Slot(str)
    def on_scan_error(self, message):
        self.append_log(f"錯誤：{message}")
        self.scan_btn.setEnabled(True)
        QMessageBox.critical(self, "掃描失敗", message)

    def populate_table(self, results):
        self.table.setRowCount(0)

        for row_idx, item in enumerate(results):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("name", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("ext", ""))))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(item.get("path", ""))))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(item.get("size_kb", ""))))
            self.table.setItem(row_idx, 4, QTableWidgetItem("、".join(item.get("pii_types", []))))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(item.get("action_result", ""))))

    @Slot()
    def export_csv(self):
        if not self.results:
            QMessageBox.information(self, "沒有資料", "目前沒有可匯出的結果")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "儲存 CSV",
            "pii_report.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["檔名", "副檔名", "完整路徑", "大小(KB)", "個資類型", "處理結果"])
                for item in self.results:
                    writer.writerow([
                        item.get("name", ""),
                        item.get("ext", ""),
                        item.get("path", ""),
                        item.get("size_kb", ""),
                        "、".join(item.get("pii_types", [])),
                        item.get("action_result", "")
                    ])

            QMessageBox.information(self, "匯出成功", f"已匯出到：\n{file_path}")
            self.append_log(f"已匯出 CSV：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "匯出失敗", str(e))

    @Slot()
    def clear_results(self):
        self.results = []
        self.table.setRowCount(0)
        self.log_text.clear()
        self.export_btn.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())