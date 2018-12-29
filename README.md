# Pocket_API

## 目的
以前作ったPocketerをLambda + API Gatewayで再実装(安いから)．

## API
### DELETE
Pocketに保存された複数タグを持つページから「twitter」タグを除去する.

### PICKUP
Pocketに保存されたページから「amazon_dash_button, conference, done, tool, twitter」タグ以外が付与されたものを一つ取得する.

### RESET
Pocketから「twitter」タグの付与されたものを3000件を削除する.

### SELECT
Pocketに保存されたQiitaのページからいいね数が100以上のものに対して，「twitter」タグを除去し，「selected_qiita」タグを付与する．
