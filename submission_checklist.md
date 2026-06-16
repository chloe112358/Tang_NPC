# 期末專題繳交清單

## 專案概覽

你的專案是 **Tang Dynasty Dialogue System**（唐代對話系統），一個以 Python 後端 + HTML 前端構成的教育互動遊戲，使用 Google Gemini API 驅動 NPC 對話。

---

## ✅ 必須繳交的檔案

這些是專案的核心程式碼和設定，缺一不可：

### 主程式 & 後端
| 檔案 | 說明 |
|------|------|
| [app.py](file:///c:/程式碼/system_prompt/app.py) | Web 伺服器主程式（HTTP handler） |
| [tang_dialogue_test.py](file:///c:/程式碼/system_prompt/tang_dialogue_test.py) | NPC 對話生成邏輯（被 app.py 匯入） |

### 前端
| 檔案 | 說明 |
|------|------|
| [final.html](file:///c:/程式碼/system_prompt/final.html) | 前端遊戲頁面（HTML/CSS/JS 一體） |
| `static/assets/` 整個目錄 (40 張圖片) | 遊戲使用的圖片素材 |

### 核心模組 (`src/`)
| 檔案 | 說明 |
|------|------|
| [src/\_\_init\_\_.py](file:///c:/程式碼/system_prompt/src/__init__.py) | 套件初始化 |
| [src/models.py](file:///c:/程式碼/system_prompt/src/models.py) | 資料模型定義 |
| [src/llm_client.py](file:///c:/程式碼/system_prompt/src/llm_client.py) | LLM API 呼叫封裝 |
| [src/prompt_manager.py](file:///c:/程式碼/system_prompt/src/prompt_manager.py) | Prompt 工程管理 |
| [src/response_generator.py](file:///c:/程式碼/system_prompt/src/response_generator.py) | 回應生成邏輯 |
| [src/state_manager.py](file:///c:/程式碼/system_prompt/src/state_manager.py) | 對話狀態管理 |
| [src/storage.py](file:///c:/程式碼/system_prompt/src/storage.py) | 資料持久化 |
| [src/knowledge_window_provider.py](file:///c:/程式碼/system_prompt/src/knowledge_window_provider.py) | 知識視窗內容提供 |

### 設定檔 (`config/`)
| 檔案 | 說明 |
|------|------|
| [config/\_\_init\_\_.py](file:///c:/程式碼/system_prompt/config/__init__.py) | 套件初始化 |
| [config/prompts.json](file:///c:/程式碼/system_prompt/config/prompts.json) | NPC 系統 prompt 設定 |
| [config/knowledge_windows.json](file:///c:/程式碼/system_prompt/config/knowledge_windows.json) | 知識視窗內容設定 |

### 專案設定 & 文件
| 檔案 | 說明 |
|------|------|
| [requirements.txt](file:///c:/程式碼/system_prompt/requirements.txt) | Python 相依套件清單 |
| [.env.example](file:///c:/程式碼/system_prompt/.env.example) | 環境變數範本（**不含真實金鑰**） |
| [README.md](file:///c:/程式碼/system_prompt/README.md) | 專案說明文件 |
| [.gitignore](file:///c:/程式碼/system_prompt/.gitignore) | Git 忽略規則 |
| [render.yaml](file:///c:/程式碼/system_prompt/render.yaml) | Render 部署設定 |
| [frontend/\_\_init\_\_.py](file:///c:/程式碼/system_prompt/frontend/__init__.py) | 前端套件初始化 |

---

## 📝 建議繳交的檔案

這些能展現你的專案品質和完整度：

### 測試程式 (`tests/`)
| 檔案 | 說明 |
|------|------|
| [tests/\_\_init\_\_.py](file:///c:/程式碼/system_prompt/tests/__init__.py) | 套件初始化 |
| [tests/test_models.py](file:///c:/程式碼/system_prompt/tests/test_models.py) | 資料模型測試 |
| [tests/test_llm_client.py](file:///c:/程式碼/system_prompt/tests/test_llm_client.py) | LLM 客戶端測試 |
| [tests/test_prompt_manager.py](file:///c:/程式碼/system_prompt/tests/test_prompt_manager.py) | Prompt 管理測試 |
| [tests/test_response_generator.py](file:///c:/程式碼/system_prompt/tests/test_response_generator.py) | 回應生成測試 |
| [tests/test_response_generator_integration.py](file:///c:/程式碼/system_prompt/tests/test_response_generator_integration.py) | 整合測試 |
| [tests/test_state_manager.py](file:///c:/程式碼/system_prompt/tests/test_state_manager.py) | 狀態管理測試 |
| [tests/test_storage.py](file:///c:/程式碼/system_prompt/tests/test_storage.py) | 儲存模組測試 |
| [tests/test_knowledge_window_provider.py](file:///c:/程式碼/system_prompt/tests/test_knowledge_window_provider.py) | 知識視窗測試 |
| [tests/test_npc_api_keys.py](file:///c:/程式碼/system_prompt/tests/test_npc_api_keys.py) | API 金鑰設定測試 |
| [tests/test_prompts_config.py](file:///c:/程式碼/system_prompt/tests/test_prompts_config.py) | Prompt 設定檔測試 |

### 知識文件 & 架構圖
| 檔案 | 說明 |
|------|------|
| [1_play.md](file:///c:/程式碼/system_prompt/1_play.md) | 遊玩主題知識文件 |
| [2_food.md](file:///c:/程式碼/system_prompt/2_food.md) | 飲食主題知識文件 |
| [3_live.md](file:///c:/程式碼/system_prompt/3_live.md) | 生活主題知識文件 |
| [output/three_layer_architecture.png](file:///c:/程式碼/system_prompt/output/three_layer_architecture.png) | 三層架構圖 |
| [output/three_layer_architecture.svg](file:///c:/程式碼/system_prompt/output/three_layer_architecture.svg) | 三層架構圖（向量） |
| [merge_docs.py](file:///c:/程式碼/system_prompt/merge_docs.py) | 文件合併工具 |

---

## 🚫 不應繳交的檔案

> [!CAUTION]
> 以下檔案**絕對不要**放進繳交內容中！

| 檔案/目錄 | 原因 |
|-----------|------|
| `.env` | ⚠️ **含有真實 API 金鑰，洩漏即被盜用** |
| `.venv/` / `venv/` | 虛擬環境，太大且可重建 |
| `__pycache__/` | Python 快取，自動產生 |
| `.pytest_cache/` | 測試快取，自動產生 |
| `.kiro/` | 開發工具設定 |
| `.git/` | 版本控制歷史（除非用 GitHub 繳交） |
| `唐代報告_定稿_final.docx` | 報告文件（另外繳交） |
| `期末報告_0605_已改好.docx` | 報告文件（另外繳交） |
| `期末報告_0605_已改好_合併版.docx` | 報告文件（另外繳交） |

---

## 📋 繳交前 Checklist

- [ ] **確認 `.env` 沒有被包含** — 真實 API 金鑰不能外流
- [ ] **確認 `.env.example` 已包含** — 讓老師知道需要哪些環境變數
- [ ] **確認 `README.md` 內容完整** — 含安裝步驟、啟動方法、部署說明
- [ ] **確認 `requirements.txt` 正確** — 老師能用它安裝所有相依套件
- [ ] **確認 `static/assets/` 圖片完整** — 共 40 張，遊戲畫面需要它們
- [ ] **測試過 `python app.py` 可正常啟動** — 繳交前跑一次確認沒壞

---

## 📦 建議繳交方式

### 方式一：壓縮成 ZIP（最簡單）
在專案目錄下排除不需要的檔案後，打包成 `.zip`。

### 方式二：使用 GitHub（最專業）
你的專案已有 `.git`，可以直接推到 GitHub：
```bash
git add .
git commit -m "期末專題繳交"
git push
```
> [!TIP]
> 你的 `.gitignore` 已經設定得很好，會自動排除 `.env`、`.venv/`、`__pycache__/`、`.docx` 等不該繳交的檔案。用 GitHub 繳交最方便也最安全。

### 方式三：Render 部署連結
你已有 [render.yaml](file:///c:/程式碼/system_prompt/render.yaml) 部署設定，如果已經部署上線，也可以附上線上網址讓老師直接試玩。

---

## 檔案數量摘要

| 類別 | 檔案數 |
|------|--------|
| 必須繳交 | ~22 個檔案 + 40 張圖片 |
| 建議繳交 | ~17 個檔案 |
| 不應繳交 | ~8 個項目 |
