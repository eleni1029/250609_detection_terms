2025-06-11 多語言敏感詞檢測與替換系統 Version 2.3
-------------------------
1. 用户初步對比的 excel 統一為 phrase_comparison.xlsx
   在 tobemodified 時，才根據語言拆分多個 excel 文件。

2. 同步修改多語言生成的結果是橫向排列，方便用戶手動操作增減。

3. 根據目前 SaaS 中的方式讀取對應規格，使用者注意要根據這個邏輯匯入：

250609_detection_terms/
├── i18n_input/                          # 輸入目錄
│   ├── zh-TW/                           # 繁體中文
│   │   ├── zh-TW.json                   # JSON 檔案在語言根目錄
│   │   └── LC_MESSAGES/                 # PO 檔案在子目錄
│   │       └── messages.po
│   ├── en/                              # 英文
│   │   ├── en.json
│   │   └── LC_MESSAGES/
│   │       └── messages.po
│   └── ja/                              # 日文
│       ├── ja.json
│       └── LC_MESSAGES/
│           └── messages.po


2025-06-11 多語言敏感詞檢測與替換系統 Version 2.2
-------------------------
# 多語言敏感詞檢測與替換系統 v2.2

🌐 **支援多語言的敏感詞檢測與替換系統**

## ✨ v2.2 版本特色

- 🗂️ **多語言檔案組織**：支援 `i18n_input/{language}/` 目錄結構
- 🔄 **自動語言檢測**：自動掃描可用語言，無需手動配置
- 📊 **語言專屬對照表**：每個語言生成獨立的 `phrase_comparison_{language}.xlsx`
- 📁 **時間戳輸出目錄**：輸出到 `i18n_output/{language}_{timestamp}/`
- 🔒 **自動備份機制**：自動備份現有檔案，無需確認

## 📁 目錄結構

```
250609_detection_terms/
├── i18n_input/                          # 輸入目錄
│   ├── zh-TW/                           # 繁體中文
│   │   ├── messages.po                  # PO 檔案（可選）
│   │   └── zh-TW.json                   # JSON 檔案（可選，但至少要有一個）
│   ├── en/                              # 英文
│   │   ├── messages.po
│   │   └── en.json
│   └── ja/                              # 日文
│       ├── messages.po
│       └── ja.json
├── i18n_output/                         # 輸出目錄
│   ├── zh-TW_20241210_143022/           # 繁中輸出（含時間戳）
│   │   ├── messages_enterprises.po
│   │   ├── zh-TW_enterprises.json
│   │   ├── messages_public_sector.po
│   │   ├── zh-TW_public_sector.json
│   │   └── apply_fixes_20241210_143022.log
│   ├── en_20241210_143022/              # 英文輸出
│   │   ├── messages_enterprises.po
│   │   ├── en_enterprises.json
│   │   └── ...
│   └── ja_20241210_143022/              # 日文輸出
│       └── ...
├── phrase_comparison_zh-TW.xlsx         # 繁中對照表
├── phrase_comparison_en.xlsx            # 英文對照表
├── phrase_comparison_ja.xlsx            # 日文對照表
├── tobemodified_zh-TW.xlsx             # 繁中待修正清單
├── tobemodified_en.xlsx                # 英文待修正清單
├── backup/                             # 備份目錄
│   ├── phrase_comparison_zh-TW_20241210_143022.xlsx
│   └── ...
├── config.yaml                         # 系統配置
├── config_loader.py                    # 配置載入器
├── generate_phrase_comparison.py       # 生成對照表
├── script_01_generate_xlsx.py          # 生成待修正清單
└── script_02_apply_fixes.py            # 套用修正結果
```

## 🚀 極簡工作流程

### **3 步驟完成多語言處理**

```bash
# 步驟 1：生成各語言的對照表
python generate_phrase_comparison.py

# 步驟 2：編輯對照表並生成待修正清單
# (手動編輯各語言的 phrase_comparison_{language}.xlsx)
python script_01_generate_xlsx.py

# 步驟 3：套用修正結果
python script_02_apply_fixes.py

# 完成！🎉
```

## ⚙️ 環境設置

### **1. 安裝必要套件**

```bash
pip install openpyxl polib pyyaml
```

### **2. 準備檔案結構**

```bash
# 創建目錄結構
mkdir -p i18n_input/{zh-TW,en,ja}
mkdir -p i18n_output
mkdir -p backup

# 放置檔案到對應目錄
# i18n_input/zh-TW/messages.po
# i18n_input/zh-TW/zh-TW.json
# i18n_input/en/messages.po
# i18n_input/en/en.json
```

## 📋 詳細使用說明

### **1. 生成對照表**

```bash
# 為所有檢測到的語言生成對照表
python generate_phrase_comparison.py

# 只為特定語言生成
python generate_phrase_comparison.py --language zh-TW

# 測試敏感詞檢測
python generate_phrase_comparison.py --test
```

**功能**：
- 自動掃描 `i18n_input/` 中的語言目錄
- 檢測每個語言檔案中的敏感詞
- 生成 `phrase_comparison_{language}.xlsx`
- 自動備份現有檔案

### **2. 編輯對照表**

用任何 Excel 軟體編輯 `phrase_comparison_{language}.xlsx`：

| 敏感詞類型 | 敏感詞 | 對應方案(企業) | 對應方案(公部門) | 對應方案(培訓機構) |
|------------|--------|----------------|------------------|-------------------|
| 時間相關   | 年度   | 年度報告       | 年度總結         | 年度課程          |
| 時間相關   | 季度   | 季度報告       | 季度總結         | 季度課程          |

### **3. 生成待修正清單**

```bash
# 處理所有語言
python script_01_generate_xlsx.py

# 處理特定語言
python script_01_generate_xlsx.py --language zh-TW

# 列出可用語言
python script_01_generate_xlsx.py --list-languages
```

**輸出**：`tobemodified_{language}.xlsx`

### **4. 套用修正結果**

```bash
# 互動式選擇
python script_02_apply_fixes.py

# 指定語言和業態
python script_02_apply_fixes.py --language zh-TW --business-types enterprises

# 套用全部業態
python script_02_apply_fixes.py --business-types all

# 列出可用檔案
python script_02_apply_fixes.py --list-files
```

**輸出**：`i18n_output/{language}_{timestamp}/` 目錄

## 🔧 配置管理

### **業態配置**

在 `config.yaml` 中新增業態：

```yaml
business_types:
  healthcare:                           # 新業態
    suffix: "_healthcare"
    display_name: "醫療機構"
    description: "醫療保健機構適用方案"
```

### **檔案命名配置**

```yaml
file_patterns:
  po_file: "messages.po"
  json_file: "{language}.json"          # 支援 {language} 變數
  phrase_comparison: "phrase_comparison_{language}.xlsx"
  tobemodified: "tobemodified_{language}.xlsx"
  output_subdir: "{language}_{timestamp}"
```

### **目錄配置**

```yaml
directories:
  input_dir: "i18n_input"               # 可自訂輸入目錄
  output_dir: "i18n_output"             # 可自訂輸出目錄
  backup_dir: "backup"                  # 可自訂備份目錄
```

## 🌐 多語言支援

### **自動語言檢測**

系統會自動檢測 `i18n_input/` 中的語言目錄：

- ✅ **檢測條件**：目錄中至少有一個 `messages.po` 或 `{language}.json` 檔案
- ✅ **大小寫兼容**：支援檔案名大小寫不一致（如 `ZH-TW.json`）
- ✅ **靈活檔案**：可以只有 PO 檔案或只有 JSON 檔案

### **新增語言支援**

```bash
# 1. 創建語言目錄
mkdir i18n_input/fr

# 2. 放置檔案
# i18n_input/fr/messages.po
# i18n_input/fr/fr.json

# 3. 自動檢測並處理
python generate_phrase_comparison.py
python script_01_generate_xlsx.py
```

### **語言檔案要求**

| 檔案類型 | 檔案名稱 | 是否必須 | 說明 |
|----------|----------|----------|------|
| PO 檔案 | `messages.po` | 可選 | GNU gettext 格式 |
| JSON 檔案 | `{language}.json` | 可選 | 必須與目錄名稱一致 |

**注意**：每個語言目錄至少需要一個檔案。

## 📊 Excel 檔案說明

### **phrase_comparison_{language}.xlsx**

每個語言的對照表，包含：

- **敏感詞類型**：分類名稱
- **敏感詞**：要檢測的詞彙
- **對應方案(業態)**：各業態的替換方案

### **tobemodified_{language}.xlsx**

待修正清單，包含：

- **source**：來源檔案類型（po/json）
- **key**：原始鍵值
- **value**：原始內容
- **敏感詞**：檢測到的敏感詞
- **修正方案(業態)**：建議的修正方案
- **修正結果(業態)**：修正後的內容

## 🔄 工作流程詳解

### **完整流程圖**

```
i18n_input/                           generate_phrase_comparison.py
├── zh-TW/                           ────────────────────────────────►
│   ├── messages.po                   phrase_comparison_zh-TW.xlsx
│   └── zh-TW.json                               │
├── en/                                          │ (手動編輯)
│   └── en.json                                  ▼
└── ja/                               script_01_generate_xlsx.py
    └── messages.po                  ────────────────────────────────►
                                      tobemodified_zh-TW.xlsx
                                                  │
                                                  ▼
                                      script_02_apply_fixes.py
                                     ────────────────────────────────►
                                      i18n_output/zh-TW_20241210_143022/
                                      ├── messages_enterprises.po
                                      ├── zh-TW_enterprises.json
                                      └── ...
```

### **處理邏輯**

1. **語言檢測**：掃描 `i18n_input/` 目錄
2. **敏感詞檢測**：從檔案內容中識別敏感詞
3. **對照表生成**：創建語言專屬的 Excel 對照表
4. **手動編輯**：使用者編輯替換方案
5. **清單生成**：掃描檔案並生成待修正清單
6. **修正套用**：將修正結果寫入新檔案

## 🛠️ 進階功能

### **批量處理**

```bash
# 處理所有語言的完整流程
for step in generate_phrase_comparison script_01_generate_xlsx script_02_apply_fixes; do
    python $step.py
done
```

### **單語言處理**

```bash
# 只處理英文
python generate_phrase_comparison.py --language en
python script_01_generate_xlsx.py --language en
python script_02_apply_fixes.py --language en --business-types all
```

### **檢查和驗證**

```bash
# 檢查配置
python config_loader.py

# 檢測可用語言
python script_01_generate_xlsx.py --list-languages

# 檢查待修正檔案
python script_02_apply_fixes.py --list-files
```

## 📈 輸出結構

### **時間戳目錄**

每次執行 `script_02_apply_fixes.py` 都會創建新的時間戳目錄：

```
i18n_output/
├── zh-TW_20241210_143022/    # 第一次執行
├── zh-TW_20241210_150030/    # 第二次執行
└── en_20241210_143022/       # 英文處理結果
```

### **檔案命名規則**

- **PO 檔案**：`{原檔名}_{業態後綴}.po`
  - 範例：`messages_enterprises.po`
- **JSON 檔案**：`{原檔名}_{業態後綴}.json`
  - 範例：`zh-TW_enterprises.json`

## 🔍 故障排除

### **常見問題**

**Q: 找不到語言目錄**
```bash
❌ 在 i18n_input 中沒有檢測到任何有效的語言目錄
```
**A**: 確認目錄結構正確，每個語言目錄至少有一個檔案

**Q: Excel 檔案缺少欄位**
```bash
❌ Excel 缺少必要欄位：['對應方案(企業)']
```
**A**: 重新執行 `generate_phrase_comparison.py` 生成標準格式

**Q: JSON 檔案名稱不匹配**
```bash
⚠️ 語言目錄 'zh-TW' 中沒有找到有效檔案
```
**A**: 確認 JSON 檔案名稱與目錄名稱一致（支援大小寫不敏感）

### **除錯工具**

```bash
# 檢查系統配置
python -c "from config_loader import get_config; get_config().print_config_summary()"

# 測試敏感詞檢測
python generate_phrase_comparison.py --test

# 檢查檔案結構
find i18n_input -type f -name "*.po" -o -name "*.json" | sort
```

## 📝 開發和自訂

### **自訂敏感詞類別**

編輯 `generate_phrase_comparison.py` 中的 `BASE_SENSITIVE_WORDS`：

```python
BASE_SENSITIVE_WORDS = {
    "新分類": ["詞彙1", "詞彙2", "詞彙3"],
    "時間相關": ["年度", "季度", "月份"],
    # ...
}
```

### **自訂業態**

在 `config.yaml` 中新增：

```yaml
business_types:
  custom_domain:
    suffix: "_custom"
    display_name: "自訂領域"
    description: "自訂領域專用方案"
```

### **自訂檔案格式**

```yaml
file_patterns:
  po_file: "custom.po"                    # 自訂 PO 檔案名
  json_file: "custom_{language}.json"    # 自訂 JSON 檔案名
```

## 🎯 最佳實踐

### **檔案組織**

1. **一致的命名**：確保 JSON 檔案名與語言代碼一致
2. **完整的檔案**：盡量提供 PO 和 JSON 兩種格式
3. **定期備份**：系統會自動備份，但建議額外保存重要版本

### **編輯對照表**

1. **段階式填寫**：先填寫常用詞彙的替換方案
2. **一致性檢查**：確保同類詞彙的替換邏輯一致
3. **測試驗證**：處理小批量檔案先測試效果

### **版本控制**

```bash
# 將重要檔案加入版本控制
git add config.yaml
git add phrase_comparison_*.xlsx
git commit -m "Update translation mappings"

# 忽略臨時檔案
echo "tobemodified_*.xlsx" >> .gitignore
echo "i18n_output/" >> .gitignore
echo "backup/" >> .gitignore
```

## ✨ 總結

多語言版本提供了：

- 🌐 **真正的多語言支援**：每個語言獨立處理
- 🚀 **極簡工作流程**：3 個步驟完成所有處理
- 🔒 **安全的檔案管理**：自動備份和時間戳目錄
- 🎯 **精確的對應關係**：語言專屬的對照表
- 📈 **可擴展的架構**：輕鬆新增語言和業態

從複雜的多檔案系統簡化為：

**準備檔案 → 生成對照表 → 編輯方案 → 生成清單 → 套用修正**

就這麼簡單！🎉

---

**版本**: v2.2.0 (多語言版本)  
**更新日期**: 2024-12-10  
**系統類型**: Multi-language Excel-based


2025-06-10 詞彙檢測與替換專案 Version 2.0
-------------------------

一個支援多語言和可配置業態的敏感詞檢測與替換系統。

## 🆕 v2.0 更新內容

- ✅ **多語言支援**：可處理不同語言的翻譯檔案
- ✅ **可配置業態**：支援任意數量的業態類型
- ✅ **配置檔案驅動**：透過 `config.yaml` 集中管理設定
- ✅ **自動檢測**：智能檢測語言和檔案類型
- ✅ **向下相容**：保持與 v1.0 的相容性

## 📁 檔案結構

```
250609_detection_terms/
├── config.yaml                          # 系統配置檔案
├── config_loader.py                     # 配置載入器
├── detection_terms.py                   # 基礎敏感詞字典
├── detection_terms_enterprises.py       # 企業方案字典
├── detection_terms_public_sector.py     # 公部門方案字典
├── detection_terms_training_institutions.py  # 培訓機構方案字典
├── phrase_update.py                     # Excel → Python 字典轉換
├── phrase_comparison.py                 # 生成對照 Excel
├── script_01_generate_xlsx.py           # 掃描翻譯檔案生成問題列表
├── script_02_apply_fixes.py             # 套用修正結果
├── messages.po                          # PO 翻譯檔案
├── zh-TW.json                          # JSON 翻譯檔案
├── phrase_comparison.xlsx               # 敏感詞對照表
├── tobemodified_zh-TW.xlsx             # 待修正項目列表
└── backup/                             # 備份目錄
    ├── apply_fixes_YYYYMMDD_HHMMSS.log
    └── ...
```

## ⚙️ 配置說明

### config.yaml 結構

```yaml
# 語言配置
languages:
  zh-TW:
    po_file: "messages.po"
    json_file: "zh-TW.json"
    description: "繁體中文"
  # 可添加更多語言...

# 業態配置 (可擴充)
business_types:
  enterprises:
    suffix: "_enterprises"
    display_name: "企業"
    description: "企業客戶適用的敏感詞解決方案"
  
  public_sector:
    suffix: "_public_sector"
    display_name: "公部門"
    description: "政府機關與公部門適用的敏感詞解決方案"
  
  training_institutions:
    suffix: "_training_institutions"
    display_name: "培訓機構"
    description: "教育訓練機構適用的敏感詞解決方案"
  
  # 可添加更多業態...
```

### 新增語言

1. 在 `config.yaml` 的 `languages` 區段添加新語言：
```yaml
languages:
  en:
    po_file: "messages_en.po"
    json_file: "en.json"
    description: "English"
```

2. 準備對應的翻譯檔案：
   - `messages_en.po`
   - `en.json`

### 新增業態

1. 在 `config.yaml` 的 `business_types` 區段添加新業態：
```yaml
business_types:
  healthcare:
    suffix: "_healthcare"
    display_name: "醫療機構"
    description: "醫療保健機構適用的敏感詞解決方案"
```

2. 系統會自動生成對應的檔案：
   - `detection_terms_healthcare.py`

## 🚀 使用流程

### 1. 建立敏感詞對照表

```bash
python phrase_comparison.py
```

**功能**：
- 讀取所有 `detection_terms_*.py` 檔案
- 生成 `phrase_comparison.xlsx` 對照表
- 顯示敏感詞與各業態解決方案的對應關係

### 2. 更新敏感詞字典

編輯 `phrase_comparison.xlsx` 後：

```bash
python phrase_update.py
```

**功能**：
- 讀取修改後的 `phrase_comparison.xlsx`
- 重新生成所有 `detection_terms_*.py` 檔案
- 自動備份原始檔案到 `backup/`

### 3. 掃描翻譯檔案

```bash
# 掃描預設語言 (zh-TW)
python script_01_generate_xlsx.py

# 掃描指定語言
python script_01_generate_xlsx.py --language en

# 顯示說明
python script_01_generate_xlsx.py --help
```

**功能**：
- 掃描指定語言的 PO 和 JSON 檔案
- 偵測敏感詞並生成修正建議
- 輸出 `tobemodified_語言.xlsx`

### 4. 套用修正結果

```bash
# 互動式選擇
python script_02_apply_fixes.py

# 指定語言和業態
python script_02_apply_fixes.py --language zh-TW --business-types enterprises public_sector

# 套用全部業態
python script_02_apply_fixes.py --business-types all

# 顯示說明
python script_02_apply_fixes.py --help
```

**功能**：
- 讀取 `tobemodified_*.xlsx` 中的修正結果
- 生成各業態的翻譯檔案
- 自動備份原始檔案到 `backup/`

## 📊 檔案命名規則

### 字典檔案
- 基礎敏感詞：`detection_terms.py`
- 業態方案：`detection_terms_{業態後綴}.py`

### 翻譯檔案
- 原始檔案：`messages.po`、`zh-TW.json`
- 業態檔案：`messages_{業態後綴}.po`、`zh-TW_{業態後綴}.json`

### Excel 檔案
- 對照表：`phrase_comparison.xlsx`
- 待修正列表：`tobemodified_{語言}.xlsx`

### 備份檔案
- 位置：`backup/` 目錄
- 格式：`檔名_{時間戳}.副檔名`
- 日誌：`apply_fixes_{時間戳}.log`

## 📋 Excel 檔案格式

### phrase_comparison.xlsx
| 敏感詞類型 | 敏感詞 | 對應方案(企業) | 一對多校驗(企業) | 對應方案(公部門) | 一對多校驗(公部門) | 對應方案(培訓機構) | 一對多校驗(培訓機構) |
|------------|--------|----------------|------------------|------------------|-------------------|-------------------|---------------------|
| 時間相關   | 年度   | 年度報告       |                  | 年度總結         |                   | 年度課程          |                     |

### tobemodified_{語言}.xlsx
| source | key | value | 敏感詞 | 修正方案(企業) | 修正結果(企業) | 修正方案(公部門) | 修正結果(公部門) | 修正方案(培訓機構) | 修正結果(培訓機構) |
|--------|-----|-------|--------|----------------|----------------|------------------|------------------|-------------------|-------------------|
| po     | ... | ...   | 年度   | 年度→年度報告  | ...年度報告... | 年度→年度總結    | ...年度總結...   | 年度→年度課程     | ...年度課程...    |

## 🔧 開發指南

### 新增支援的檔案類型

1. 修改 `script_01_generate_xlsx.py` 中的檔案讀取函數
2. 添加對應的檔案解析邏輯
3. 更新 `script_02_apply_fixes.py` 中的檔案寫入函數

### 擴展檢測邏輯

1. 修改 `script_01_generate_xlsx.py` 中的 `find_keywords()` 函數
2. 調整正則表達式或檢測算法
3. 更新關鍵字匹配邏輯

### 自定義業態邏輯

1. 在 `config.yaml` 中定義新的業態
2. 系統會自動處理檔案生成和映射
3. 可在各腳本中添加特定業態的處理邏輯

## 🐛 故障排除

### 常見問題

**Q: `❌ 找不到配置文件：config.yaml`**
A: 確保 `config.yaml` 檔案存在於執行目錄中

**Q: `❌ 載入 detection_terms_*.py 失敗`**
A: 檢查 Python 檔案語法是否正確，確保包含 `DETECTION_TERMS` 變數

**Q: `❌ Excel 缺少必要欄位`**
A: 確保 Excel 檔案包含所有必要的欄位，可重新生成檔案

**Q: `❌ JSON 格式錯誤`**
A: 檢查 JSON 檔案語法，使用 JSON 驗證工具確認格式正確

### 日誌檢查

詳細的操作日誌儲存在 `backup/apply_fixes_*.log`：
```bash
# 查看最新日誌
ls -la backup/apply_fixes_*.log | tail -1
cat backup/apply_fixes_YYYYMMDD_HHMMSS.log
```

### 備份恢復

如需恢復備份檔案：
```bash
# 查看備份檔案
ls backup/

# 恢復檔案 (範例)
cp backup/detection_terms_20241210_143000.py detection_terms.py
```

## 📚 API 參考

### config_loader.py

```python
from config_loader import get_config

config = get_config()

# 獲取語言配置
languages = config.get_languages()
default_lang = config.get_default_language()
lang_files = config.get_language_files('zh-TW')

# 獲取業態配置
business_types = config.get_business_types()
choices = config.get_business_type_choices()

# 獲取檔案路徑
detection_files = config.get_detection_terms_files()
output_files = config.get_output_files('zh-TW')
```

### 命令列參數

#### script_01_generate_xlsx.py
```bash
python script_01_generate_xlsx.py [選項]

選項:
  -l, --language {zh-TW,en,...}  指定要處理的語言
  -h, --help                     顯示說明並退出
```

#### script_02_apply_fixes.py
```bash
python script_02_apply_fixes.py [選項]

選項:
  -l, --language {zh-TW,en,...}           指定要處理的語言
  -b, --business-types {業態1,業態2,all}  指定要處理的業態
  -h, --help                              顯示說明並退出
```

## 📈 效能優化

### 大型檔案處理
- 對於大型翻譯檔案，考慮分批處理
- 使用 `--business-types` 參數只處理必要的業態

### 記憶體使用
- 系統會將整個檔案載入記憶體
- 對於非常大的檔案，可能需要修改為串流處理

### 處理速度
- Excel 檔案操作是瓶頸
- 考慮使用 pandas 替代 openpyxl 處理大型資料

## 🔐 安全注意事項

- 備份檔案包含敏感資料，注意存取權限
- 配置檔案可能包含路徑資訊，避免暴露
- 日誌檔案記錄詳細操作，定期清理

## 📄 授權

本專案遵循 MIT 授權條款。

## 🤝 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📞 技術支援

如有問題或建議，請：
1. 查看本 README 的故障排除區段
2. 檢查 GitHub Issues
3. 創建新的 Issue 描述問題

---

**版本**: v2.0  
**更新日期**: 2024-12-10  
**維護者**: [您的名稱]






2025-06-10 Version 1.0
-------------------------
資料夾：
1. Ori: 手動備份文件，在專案中不會用到。
2. backup：在更新 py, po, json 時，會保存 backup 文件在裡頭，並加上時間戳。
3. __pycache__：我也不知道是啥，Claude 很開心寫的。

檔案，此處僅引用繁體中文的版本：
1. zh-TW.json - 前端文件（內部稱呼）
2. messages.po - 後端文件（內部稱呼）

-
操作流程：
這個專案包含兩套操作，
  1. 敏感詞彙的確認與調整
    1-1. 用戶編輯 phrase_comparison.xlsx，確認後保存。
    1-2. 執行 “phrase_update.py”，會輸入 phrase_comparison.xlsx,
      存在變更時會先備份原本的py文件，然後將新的內容分別寫入
      detection_terms.py,（教育機構）
      detection_terms_enterprises.py,（企業）
      detection_terms_public_sector.py,（公部門）
      detection_terms_training_institutions.py.(培訓機構）
 （*備註：
    這個步驟是可逆的，如果四個py是另外生成的，也可以根據py的內容生成phrase_comparison.xlsx：
    在已經存在這幾個py的情況下，執行"phrase_comparison.py",即可生成 phrase_comparison.xlsx。）

  2. 具體替換敏感詞彙並確認寫入，生成新版本的 json 與 po 文件。
    2-1. 執行整體比對，執行 "script_01_generate_xlsx.py"
      輸出 tobemodified.xlsx 內容會包含如下 
      對比 messages.po, zh-TW.json, 列出內容包含敏感詞彙的 key 與 value
      並且展示對應在企業、公部門、培訓機構的 value 對照，並顯示替換後的 value 值。
    2-2. 用戶確認是否調整（不調整可以將內容改為空），或是整體用另外的方式修改。
      用戶調整完成後，執行 "script_02_apply_fixes.py"
      會將有修改的文件保存到 bakcup 中，並且生成新的對應 po 與 json 文件：
      zh-TW.json
      zh-TW_enterprises.json
      zh-TW_public_sector.json
      zh-TW_training_institutions.json
      messages.po
      messages_enterprises.po
      messages_public_sector.po
      messages_training_institutions.po

  3. 截至 2025-06-10，目前尚未加入其他語言或是其他前後端文件的功能。
