# Data Validation Tool

## 系統需求

- Python 3.x
- 套件：
  - tkinter
  - google-generativeai
  - frictionless
  - pyyaml
  - csv
- 若使用 Google Gemini API 則需要網路連線
- 需準備檔案：
  - **資料檔案**（例如：`data.csv`）：第一列需為欄位名稱，其餘列為資料內容。
  - **欄位描述檔案**（例如：`description.csv`）：第一列為欄位名稱、第二列為欄位標題、第三列為欄位描述、第四列為欄位型別，欄位名稱需與資料檔案一致。

## 功能介紹與操作說明

### Generate Dataset Specification

此功能會根據使用者上傳的 CSV 資料檔案，利用 Frictionless 套件的 `Schema.describe()` 函式自動產生 YAML 格式的資料集規格檔（命名方式為 `<資料檔案名稱>.schema.yaml`）。

**操作步驟：**
- 在【Data File】中上傳資料檔案（例如：`data.csv`）。
- 在【Description File】中上傳欄位描述檔案（例如：`description.csv`）。
- 若需使用 Google Gemini AI 自動生成 constraints 值，勾選【Use Gemini AI】並填入有效的 Gemini API Key（免費版限制為每分鐘 15 次、每日 1500 次請求）。
- 按下【Submit】按鈕後，系統將依序：
  - 利用 Frictionless 生成 YAML 規格檔，並根據欄位描述檔補入每個欄位的 `title` 與 `description`。
  - 若啟用 Gemini AI，系統將針對數值型欄位（integer 或 number）向 API 詢問合理的最小值與最大值，並自動填入 `constraints` 屬性。【System Messege】區域會顯示進度與相關訊息，如：
    - `Create <yaml檔案> sucessfully`
    - `Detecting <欄位名稱> field...`
    - 如發生 API 資源問題或 API Key 錯誤，則會顯示錯誤訊息。

> **注意：** 若不需使用 Gemini AI，直接取消勾選【Use Gemini AI】，系統僅依據 Frictionless 生成基本規格檔案。

### Modify Dataset Specification

因自動產生的 YAML 規格檔案可能仍需調整修改，因此這個功能可以讓使用者修改各欄位的詳細屬性。

**操作步驟：**
- 在【YAML File】中選擇欲修改的 YAML 規格檔。
- 按下【Submit】，系統將依序將每個欄位的屬性（例如：`name`、`title`、`type`、`format`、`description`與 `constraints`）載入至各欄位中。
- 使用【<】與【>】按鈕瀏覽各個欄位內容，並修改所需資訊。
- 修改完成後，按下【Save】將變更儲存至原檔案。

**各屬性說明：**
- `name`：欄位名稱（不可重複，由系統自動填入，亦不可修改）。
- `title`：欄位顯示標題。
- `type`：欄位資料型別（例如：string、number、integer）。
- `format`：資料格式說明。
- `description`：欄位詳細描述。
- `constraints`：限制條件，包括 `required`、`unique` 以及數值或字串長度相關的限制等。

### Validate Dataset

在完成 YAML 規格檔準備後，可利用此功能對資料進行驗證，檢查資料內容是否符合規格要求。

**操作步驟：**
- 分別在【Data File】與【YAML File】欄位上傳資料檔案與其對應的 YAML 規格檔。
- 按下【Submit】後，系統會先驗證 YAML 規格檔本身，若格式正確，則再進行資料檔案的驗證。
- 驗證結果將在【Validation Results】中顯示：
  - 若資料完全符合規格，將顯示「There are no errors in the dataset.」。
  - 若有錯誤，系統會列出錯誤數量及錯誤資訊。

## 說明
- **Google Gemini API 使用限制**：免費版 Gemini API 每分鐘最多 15 次請求，若請求過快可能會出現 `ResourceExhausted` 錯誤，系統將自動等待並重試。
