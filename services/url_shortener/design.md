# URL Shortener — 設計決策

## 資料庫：DynamoDB

### 存取模式

這個服務有兩種主要讀取模式與一種寫入模式：

| 操作 | 使用的 Key | 頻率 |
|------|-----------|------|
| Redirect：查詢原始 URL | `short_url`（PK） | 高（讀寫比 100:1） |
| 去重：檢查原始 URL 是否已縮短過 | `original_url`（GSI） | 每次寫入都會執行 |
| 寫入新 URL 對應關係 | — | 低 |

兩種讀取都是純粹的 key lookup，沒有 range query、join 或 aggregate 運算，符合 DynamoDB key-value 存取模型。

### Why DynamoDB

**vs. 關聯式資料庫（PostgreSQL / MySQL）**  
加上適當的 index，關聯式資料庫也能支撐這個讀取量，但在 100M DAU 的規模下需要仔細調整 connection pool，最終可能需要水平 sharding。而這個 schema 沒有任何關聯結構，不值得承擔這些額外的維運複雜度。

**vs. Redis**  
Redis 的延遲比 DynamoDB 更低，因此已規劃作為 cache 層使用（見 `rpc/redirect.py` 中的 `# TODO: query Redis cache before hitting DB`）。但 Redis 不適合作為主要儲存，因為將 3 年份的 URL 對應關係全部放在記憶體中，成本過高。

**vs. MongoDB**  
Document model 對於只有兩個欄位的 key-value 紀錄來說，並沒有使用到 MonogDB 的彈性優勢。

**DynamoDB 在此的具體優勢：**

- **PK 查詢 O(1)**，延遲為個位數毫秒 — 讀取路徑（`GET /{short_url}`）直接命中 PK。
- **`original_url` 的 GSI (Global Secondary Index)** 讓 de-dup query 也能快速查詢，不需要 full table scan。
- **內建水平擴展**，無需手動 sharding 即可應對寫入吞吐量的成長。
- **TTL 支援**，可直接在儲存層強制執行 3 年資料保留期，應用層不需要額外實作。

---

## HASH：MD5，取前 8 個十六進位字元

### 運作方式

```python
# rpc/generate_url.py
def _hash(original_url: str, attempt: int = 0) -> str:
    salted = f"{original_url}{attempt}"
    return hashlib.md5(salted.encode()).hexdigest()[:8]
```

MD5 產生 128-bit 的摘要，以 32 個十六進位字元表示。取前 8 個字元作為短網址的 key，字母表為 16 個字元（0–9、a–f）。

### 為何選擇 MD5

MD5 的密碼學弱點（Collision 攻擊、preimage 抵抗力不足）在這個場景不造成影響，因為這裡的雜湊用途是內容定址，而非安全保護。
關鍵在於速度：MD5 是標準函式庫中最快的通用雜湊函數之一，適合可能頻繁執行的寫入路徑。

### 為何取 8 個字元

8 個十六進位字元可產生 **16⁸ = 4,294,967,296（約 42.9 億）個唯一值**。

對照規格的試算（100M DAU、讀寫比 100:1、資料保留 3 年）：

- 估計寫入量：100M DAU × 1% 寫入比例 ≈ 每天 100 萬筆新 URL
- 3 年累計：約 10 億筆 URL

42.9 億個 slot 遠高於 3 年累積的 10 億筆預估，提供了極佳的空間緩衝。即使考慮到「生日論」(Birthday Paradox) 導致的碰撞機率，在這種佔用率下（約 25%），重試次數會保持在極低水準。此外：

1. **去重機制吸收重複寫入** — 相同的原始 URL 永遠對應到同一個短網址，實際的唯一寫入率通常遠低於原始寫入率。
2. **碰撞重試機制** — slot 被佔用時，`attempt` 遞增並重新計算雜湊，這作為保險手段確保 100% 寫入成功。

若日後超出 8 個字元的上限，解法是改用 9 個字元，或改用 Base62 編碼（7 碼即可提供 3.5 兆個組合）。

### 為什麼不採用 Auto-increment ID？

雖然 auto-increment ID 具備完全消除 collision 的優點，但其「連續性」與「可預測性」會讓其他人能藉此推測出系統的使用量與增長速度，也有可能發生短網址被猜中的風險。

相較之下，雜湊 (Hash) 方案能產生不透明 (Opaque) 且非連續的 ID，能有效隱藏資料規模，避免上述風險。
