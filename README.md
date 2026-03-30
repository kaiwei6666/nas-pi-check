# NAS / 本地端 個資掃描工具 (PII Scanner)

## 專案簡介

本專案是一個以 Python 開發的個資掃描工具，可掃描本地端或透過 SMB 掛載的 NAS 檔案，偵測其中是否包含敏感個人資料（PII），並透過圖形化介面顯示結果。

本工具適用於：

* 內部資料盤點
* 個資外洩風險檢查
* 文件清理與管理前置作業

---

## 功能特色

* 掃描指定資料夾（支援多層目錄）
* 自動偵測個資內容：

  * 身分證字號
  * 手機號碼
  * Email
* 支援多種檔案格式：

  * .txt / .csv / .log
  * .docx
  * .xlsx
  * .pdf（文字型）
* 圖形化介面（PySide6）
* 掃描結果表格顯示
* 匯出 CSV 報表
* 背景執行（避免介面卡住）

---

## 使用技術

* Python 3
* PySide6（GUI）
* os / re（檔案掃描與正則表達式）
* python-docx（讀取 Word）
* openpyxl（讀取 Excel）
* pypdf（讀取 PDF）

---

## 專案結構

```
startup/
├─ gui_app.py        # GUI 主程式
├─ pii_core.py       # 掃描與個資偵測核心邏輯
├─ README.md
├─ requirements.txt
└─ .gitignore
```

---

## 安裝與執行

### 安裝套件

```
pip install -r requirements.txt
```

或手動安裝：

```
pip install PySide6 python-docx openpyxl pypdf
```

---

### 執行程式

```
python gui_app.py
```

---

## 使用說明

### 掃描路徑

可填入以下類型路徑：

本地端：

```
C:\Users\kevin\Desktop\test_folder
```

NAS（需先登入）：

```
\\192.168.1.132\startup
```

注意事項：

* 該路徑需能在 Windows 檔案總管正常開啟
* 若為 NAS，需先登入帳密

---

## 偵測規則（PII）

| 類型    | 規則             |
| ----- | -------------- |
| 身分證字號 | [A-Z][12]\d{8} |
| 手機號碼  | 09\d{8}        |
| Email | 一般 Email 格式    |

---

## 限制與注意事項

* PDF 僅支援可選取文字內容（不支援掃描型 PDF）
* 不支援：

  * .doc / .xls
  * 圖片檔（JPG / PNG）
* 目前僅提供偵測功能，不會修改或搬移檔案

---

## 安全設計

* 採用只讀掃描，不改動原始資料
* 不自動搬移或刪除檔案
* 所有結果需由使用者自行判斷與處理

---

## 未來擴充方向

* 檔案自動移動至 restricted 資料夾
* 權限控制（ACL）
* 個資風險分級
* OCR 支援（掃描 PDF / 圖片）
* 視覺化分析報表

---

## License

This project is for educational and internal use.
