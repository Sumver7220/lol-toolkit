# lol-toolkit

透過本機的 **LCU API**（League Client Update API）讀取《英雄聯盟》客戶端資料的小工具箱。

目前提供的功能：

| 子命令 | 功能 |
|---|---|
| `all` | 產生完整頁面（預設，雙擊 exe 即為此模式） |
| `skins` | 只產生造型收藏 |
| `loot` | 只產生造型碎片 |
| `challenges` | 只產生挑戰進度 |
| `matches` | 只產生最近對戰 |
| `ranked` | 只產生排位戰績 |

## 為什麼需要它

Riot 的官方公開 API 拿不到帳號的 inventory（你擁有哪些英雄與造型），這些資料只存在於客戶端在本機開的 LCU 介面。這個工具去把它讀出來。

## 使用方式

1. 開啟《英雄聯盟》客戶端並**完全登入**（進到大廳）
2. 執行工具
3. 輸出檔會產生在程式（或 `.exe`）所在的資料夾

### 從原始碼執行

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python -m loltk all
```

### 打包成執行檔

```bash
pip install pyinstaller
pyinstaller loltk.spec
```

產物位於 `dist/loltk.exe`，雙擊即可執行，輸出檔會落在 exe 所在的資料夾。

### CLI

```
loltk <all|skins|loot|challenges|matches|ranked> [--output DIR] [--json-only | --html-only] [--no-open] [--quiet]
```

| 參數 | 說明 |
|---|---|
| `--output DIR` | 輸出目錄，預設為程式所在資料夾 |
| `--json-only` | 只產生 JSON |
| `--html-only` | 只產生 HTML |
| `--no-open` | 不自動開啟瀏覽器 |
| `--quiet` | 只輸出錯誤，適合指令稿串接 |

## 運作原理

1. 掃描系統進程找到 `LeagueClientUx.exe`，從命令列參數解析出 `--app-port` 與 `--remoting-auth-token`
2. 以 HTTP Basic Auth（帳號固定為 `riot`、密碼為上述 token）連線 `https://127.0.0.1:{port}`
3. 呼叫對應的 LCU endpoint 取得資料

LCU 使用自我簽署憑證，所以程式會關閉憑證驗證——連線目標是 `127.0.0.1`，不經過網路。

每次啟動客戶端，port 與 token 都會變動，因此必須在客戶端執行中才能使用。

## 注意事項

- 僅在 Windows 上測試過
- 所有操作皆為唯讀，不會對帳號做任何修改
- 若客戶端以系統管理員權限執行，本工具也需要以相同權限執行才讀得到進程參數
- 對戰紀錄僅能取得最近數場，客戶端不保留完整歷史

## 致謝

最初的構想與 LCU 連線做法參考自 [jason871012/lol-owned-skins-fetcher](https://github.com/jason871012/lol-owned-skins-fetcher)。本專案為重新實作，程式碼、架構與輸出格式均為獨立撰寫。

## 授權

[MIT](LICENSE)
