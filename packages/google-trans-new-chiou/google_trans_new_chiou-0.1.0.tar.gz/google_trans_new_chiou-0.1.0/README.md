## 文字翻譯
### 安裝
```
pip install google_trans_new_chiou
```
### 含入模組
```
from google_trans_new_chiou import google_translator
```
### 使用
```
translator=google_translator()
word=translator.translate("今天天氣真好",lang_src="zh-TW",lang_tgt="ja",pronounce=True)
```
傳回值：
```
['今日は良い天気 ', 'Jīntiān tiānqì zhēn hǎo', 'Kyō wa yoi tenki']
```