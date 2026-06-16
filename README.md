# 史料未及：請勿對古人劇透！

一款以唐朝長安城為背景的教育互動對話遊戲。玩家扮演穿越到唐朝的現代人，透過與三位唐代 NPC 的自由對話，在趣味互動中學習古代科學與人文知識。

遊戲網址：https://tang-dialogue-game.onrender.com

## 遊戲內容

玩家可在長安城地圖上選擇三條探索路線，每條路線包含 3 回合對話：

| 路線 | NPC | 地點 | 對話主題 |
|------|-----|------|----------|
| 🎭 育樂 | 雷班主（舞台總監） | 大明宮教坊 | 陶甕擴音 → 軟裝吸音 → 拍板指揮 |
| 🍜 食衣 | 安掌櫃（酒樓布莊老闆） | 西市 | 食物保鮮 → 服飾材質 → 品色服制度 |
| 🏯 住行 | 裴掌櫃（商行總管） | 東市 | 車輿減震 → 倉儲防火 → 榫卯預製 |

每回合結束後會彈出科普視窗，將古代工藝與現代科學原理對照解說。三條路線全部完成後，進入尾聲收束畫面。

## 技術架構

```
前端 (final.html)                     後端 (app.py)
┌─────────────────────┐    POST      ┌─────────────────────────┐
│  HTML / CSS / JS     │──────────→  │  Python HTTP Server      │
│  遊戲畫面 & 互動邏輯  │  /api/     │                          │
│  預設選項 A/B 回覆    │  dialogue  │  tang_dialogue_test.py   │
│  (不需呼叫後端)       │ ←──────────│  ├ 9 組 System Prompt     │
└─────────────────────┘   JSON      │  ├ 服色禁忌偵測 & 校正     │
                                    │  ├ 收束知識點驗證          │
                                    │  └ Gemini API 呼叫        │
                                    └─────────────────────────┘
```

- **前端**：`final.html` 為單一 HTML 檔案，包含所有 CSS、HTML 場景和 JavaScript 邏輯。玩家選擇預設選項 A/B 時，直接使用前端內建的回覆，不需呼叫後端。
- **後端**：`app.py` 啟動一個 Python HTTP Server，負責提供 `final.html` 與靜態圖片，並處理 `POST /api/dialogue` 請求。
- **對話引擎**：`tang_dialogue_test.py` 包含 9 組 NPC System Prompt、服色禁忌校正邏輯、收束知識點驗證，以及 Google Gemini API 的呼叫封裝。當玩家使用自由輸入時，後端呼叫 Gemini 生成 NPC 回覆。

## 專案結構

```
.
├── app.py                     # Web 伺服器（HTTP handler，提供前端頁面與 API）
├── tang_dialogue_test.py      # 對話引擎（System Prompt、Gemini API、服色校正）
├── final.html                 # 前端遊戲（HTML/CSS/JS 單一檔案）
├── static/assets/             # 遊戲圖片素材（場景、NPC、科普插圖等 40 張）
├── requirements.txt           # Python 相依套件
├── .env.example               # 環境變數範本
├── render.yaml                # Render 部署設定
└── README.md                  # 本文件
```

## 環境設定與啟動

### 1. 建立虛擬環境並安裝套件

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 為 `.env`，填入 Google Gemini API Key：

```bash
cp .env.example .env
```

```env
# 每個 NPC 分支使用獨立的 API Key（必填至少一組）
GEMINI_API_KEY_THEATER=你的_API_Key
GEMINI_API_KEY_FOOD=你的_API_Key
GEMINI_API_KEY_TBD=你的_API_Key

# 或設定一個共用的 fallback key
# GEMINI_API_KEY=你的_fallback_API_Key
```

### 3. 啟動伺服器

```bash
python app.py
```

開啟瀏覽器前往 `http://localhost:8000` 即可遊玩。

## 部署

本專案已部署至 Render，設定檔為 `render.yaml`。

部署至其他平台（Railway、Fly.io、Cloud Run 等）的基本設定：

| 項目 | 值 |
|------|---|
| Build command | `pip install -r requirements.txt` |
| Start command | `python app.py` |
| 必要環境變數 | `GEMINI_API_KEY_THEATER`、`GEMINI_API_KEY_FOOD`、`GEMINI_API_KEY_TBD` |
| 選用環境變數 | `GEMINI_MODEL`（預設 `gemini-3.1-flash-lite`）、`PORT`（預設 `8000`） |

## API 說明

### `POST /api/dialogue`

前端自由輸入時呼叫此 API，由後端透過 Gemini 生成 NPC 回覆。

**Request Body：**
```json
{
  "branch": "theater",
  "turn": 1,
  "user_input": "舞台地板下面到底藏了什麼？"
}
```

**Response（成功）：**
```json
{
  "npc_response": "哈哈，非也非也！這木板底下大有乾坤...",
  "is_fallback": false
}
```

**Response（Gemini 不可用時的 fallback）：**
```json
{
  "npc_response": "回覆額度用盡，請選既有選項",
  "is_fallback": true
}
```

當 API 回傳 `is_fallback: true` 時，前端會保留預設選項 A/B 供玩家繼續遊戲。

## 對話設計機制

- **收束目標**：每回合的 System Prompt 都設定了強制收束的知識點（如「陶甕擴音」「拍板指揮」），無論玩家問什麼，NPC 都必須帶到該知識點。
- **服色禁忌校正**：若玩家提到想穿黃色、紫色、緋色等唐代禁色衣物，系統會在 user message 中注入校正指令，確保 NPC 先勸阻再轉回主題。
- **收束驗證**：後端會檢查 Gemini 回覆是否包含核心關鍵詞，若缺漏則自動替換為預設的收束回覆。
- **輸出清理**：自動移除 Gemini 回覆中的 Markdown 格式符號（`**`、`*` 等），並處理重複的轉場用語。
