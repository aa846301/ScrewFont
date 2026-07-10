# ScrewFont

ScrewFont 是一套給 3D 列印螺絲抽屜標籤使用的字型。一般文字以 Noto Sans Black 為主體，螺絲與零件圖示放在 Unicode Private Use Area，可以搭配 `M3×6`、`M4×16` 這類文字做凸字或凹字標籤。

## 專案需求

- Python 3.11 或以上
- uv
- fontTools
- `third_party/noto/NotoSans-Black.ttf` 與 `third_party/noto/LICENSE.txt` 保留在專案內，作為一般文字的基礎字型與授權文件

## 建立環境與產生字型

```powershell
uv venv
uv sync
uv run python scripts/build_font.py
```

執行後會產生：

- `output/ScrewFont.ttf`
- `output/preview.html`
- `output/NotoSans-LICENSE.txt`

`scripts/build_font.py` 可以重複執行，會重新建立輸出檔案。

Noto Sans Black 依 SIL Open Font License 發布。本專案將基礎字型檔與授權文字保存在 `third_party/noto/`，避免 CI 或本機建置依賴上游網址；散布產物時會把授權文字複製成 `output/NotoSans-LICENSE.txt` 並放入 release zip。

## 發布 Release

`output/` 不進 git。發布新版時建立並推送 tag，GitHub Actions 會自動重建字型，並在 GitHub Release 上傳壓縮包：

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Release asset 會命名為 `ScrewFont-<tag>.zip`，zip 裡包含固定檔名的 `ScrewFont.ttf`、`preview.html` 與 `NotoSans-LICENSE.txt`。字型本身不寫入 tag 或版號，family name、full name、PostScript name 維持固定，方便在系統中覆蓋安裝。

## 字型規格

- Font name: `ScrewFont`
- `unitsPerEm = 1000`
- 一般文字來自 Noto Sans Black；螺絲圖示從 `U+E001` 起放在 Unicode Private Use Area
- Glyph 會依實際圖形寬度自動修剪 advance width，左右各保留 `20` units 邊距
- 橫式長版螺絲保留長版比例，但 advance width 不超過兩個直式螺絲字元寬度，並會自動修剪左右空白
- 輪廓為單色封閉向量
- 圖形以粗幾何造型為主，避免過細線條，適合 FDM 3D 列印

## 圖形硬性規則

- 內六角、十字、一字、Torx 工具孔一律使用外圓，內部再挖出對應孔形。
- 螺絲頭與牙身必須相接或重疊，不可留間隙。
- 所有螺絲的最寬處統一為 `540` units；直式看水平寬度，橫式看垂直高度。
- 一般機械牙不畫螺紋，用方塊代表；自攻牙不畫螺紋，用尖的長三角形代表。
- 止付螺絲是例外，必須畫出螺紋，內部不畫工具孔。
- 橫式短版螺絲必須嚴格維持直式圖案旋轉 90 度後的比例；橫式長版只延長牙身方向，頭型與最寬處不變。
- 圓頭螺絲用圓弧頭表示；杯頭螺絲用帶倒角且高度較高的方塊頭表示。
- 薄平頭螺絲另外成組，頭部為很扁的低平頭，不使用沉頭的錐形輪廓。
- 六角螺母外形為六角形，內孔為圓形。
- 熱熔螺母使用上下方框、中央縮腰、內部直向分格的輪廓。
- 鋁擠船型螺母使用長船型本體與中央圓孔。
- 墊片使用圓環；不標示為圓螺母。
- 圓形磁鐵使用實心圓本體，內部挖出大寫 `N`。

## UTF-8 符號對照

實際使用時請開啟 `output/preview.html`，按「複製」取得表格中的 Unicode Private Use Area 符號。這些符號會以 UTF-8 文字貼到建模軟體或其他文字欄位中；不要直接輸入 `H`、`S`、`B` 這類舊代號，舊代號只用於專案內部維護與查表。

### 工具符號

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `H` | `U+E001` | 內六角工具孔 |
| `P` | `U+E002` | 十字起子孔 |
| `L` | `U+E003` | 一字起子孔 |
| `T` | `U+E004` | Torx 星型孔 |
| `W` | `U+E005` | 外六角扳手/套筒 |

### 直式螺絲本體

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `S` | `U+E006` | 直式圓頭機械牙螺絲 |
| `B` | `U+E007` | 直式杯頭機械牙螺絲 |
| `F` | `U+E008` | 直式沉頭機械牙螺絲 |
| `I` | `U+E009` | 直式薄平頭機械牙螺絲 |
| `s` | `U+E00A` | 直式圓頭自攻螺絲 |
| `b` | `U+E00B` | 直式杯頭自攻螺絲 |
| `f` | `U+E00C` | 直式沉頭自攻螺絲 |
| `i` | `U+E00D` | 直式薄平頭自攻螺絲 |

### 橫式短版螺絲本體

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `A` | `U+E00E` | 橫式短版圓頭機械牙螺絲 |
| `C` | `U+E00F` | 橫式短版杯頭機械牙螺絲 |
| `E` | `U+E010` | 橫式短版沉頭機械牙螺絲 |
| `K` | `U+E011` | 橫式短版薄平頭機械牙螺絲 |
| `a` | `U+E012` | 橫式短版圓頭自攻螺絲 |
| `c` | `U+E013` | 橫式短版杯頭自攻螺絲 |
| `e` | `U+E014` | 橫式短版沉頭自攻螺絲 |
| `k` | `U+E015` | 橫式短版薄平頭自攻螺絲 |

### 橫式長版螺絲本體

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `Q` | `U+E016` | 橫式長版圓頭機械牙螺絲 |
| `G` | `U+E017` | 橫式長版杯頭機械牙螺絲 |
| `J` | `U+E018` | 橫式長版沉頭機械牙螺絲 |
| `Y` | `U+E019` | 橫式長版薄平頭機械牙螺絲 |
| `q` | `U+E01A` | 橫式長版圓頭自攻螺絲 |
| `g` | `U+E01B` | 橫式長版杯頭自攻螺絲 |
| `j` | `U+E01C` | 橫式長版沉頭自攻螺絲 |
| `y` | `U+E01D` | 橫式長版薄平頭自攻螺絲 |

### 止付螺絲

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `Z` | `U+E01E` | 直式止付螺絲 |
| `z` | `U+E01F` | 橫式止付螺絲 |

### 非螺絲零件

| 舊代號 | UTF-8/Unicode | 說明 |
| --- | --- | --- |
| `N` | `U+E020` | 六角螺母 |
| `R` | `U+E021` | 墊片 |
| `D` | `U+E022` | 圓形磁鐵 |
| `O` | `U+E023` | 方形螺母 |
| `U` | `U+E024` | 熱熔螺母 |
| `V` | `U+E025` | 鋁擠船型螺母 |

## 安裝字型

在 Windows 上可直接開啟 `output/ScrewFont.ttf`，按「安裝」。也可以在字型檔上按右鍵，選擇「安裝」或「為所有使用者安裝」。

安裝後，在支援系統字型的軟體中選擇 `ScrewFont`，貼上 `preview.html` 複製出的 UTF-8/Private Use Area 符號即可得到圖示。

## 在 3D 建模軟體中使用

1. 安裝 `output/ScrewFont.ttf`。
2. 在建模軟體的文字工具中選擇字型 `ScrewFont`。
3. 開啟 `output/preview.html`，按「複製」取得需要的 UTF-8 圖示符號。
4. 在文字工具中貼上圖示符號並輸入尺寸文字，例如「內六角圖示 + 圓頭螺絲圖示 + `M4×16`」。
5. 將文字轉為曲線、輪廓或實體後，再做凸字或凹字布林運算。

長版橫式螺絲的 UTF-8 符號保留長版比例，但寬度控制在兩個直式螺絲字元以內；所有 glyph 的 advance width 會依圖形實際寬度自動修剪左右空白。

## 預覽

用瀏覽器開啟：

```text
output/preview.html
```

預覽頁會載入同目錄的 `ScrewFont.ttf`，並顯示完整 glyph 對照表、UTF-8/Unicode 碼位、複製按鈕與標籤範例。
