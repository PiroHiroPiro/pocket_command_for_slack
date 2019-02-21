# Pocket_API

## 目的
以前作ったPocketerをLambda + API Gatewayで再実装．

## API
### CLEAN
Pocketに保存されたアイテムから，Twitterへのリンクを持つアイテムを削除する．
Pocketに保存された複数タグを持つアイテムから「twitter」タグを除去する.
現在使われていない．

### PICKUP
Pocketに保存されたページから「amazon_dash_button, conference, done, tool, twitter」タグ以外が付与されたアイテムを一つ取得する.

### RESET
Pocketから「twitter」タグの付与されたアイテムを3000件を削除する.
現在使われていない．

### SELECT
Pocketに保存されたQiitaのページからいいね数が100以上のアイテムに対して，「twitter」タグを除去し，「selected_qiita」タグを付与する．
現在使われていない．

### STREAMING
1分以内にPocketに保存されたアイテムを取得する．
