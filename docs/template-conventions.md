# テンプレートの書き方

テンプレートは Zabbix 7.0 のエクスポート形式のYAML。編集後は`tools/normalize.py`で整える（冪等。項目の並びの統一、既定値の補完とコメントアウト、UUID重複チェック）。

## インポートで差分を出さない

Zabbixは既定値を省略してエクスポートするため、既定値をYAMLに書いたままだと、取り込むたびに差分が出る。既定値の行は`# delay: 1m`のようにコメントアウトして記載する（コメントはインポート時に無視される）。

| 項目 | 既定値 |
|---|---|
| `delay` | `1m` |
| `history` | `31d` |
| `trends` | `365d`（文字列・ログは`'0'`を明示） |
| `value_type` | `UNSIGNED`（`FLOAT`・`CHAR`・`LOG`は明示） |
| 前処理`CHECK_NOT_SUPPORTED`の`error_handler` | `DISCARD_VALUE` |

PyYAMLなどコメントを保持しない方法で書き直すとコメントが消えるので、編集後は`normalize.py`を実行する。

## YAMLの落とし穴

- 通常のグラフ（`graphs:`）は`zabbix_export`直下に置く。`graph_prototypes`はディスカバリルールの中。
- 単一アイテムだけを参照するトリガーは、そのアイテムの`triggers:`の中に書く。複数アイテムを参照するトリガーだけがテンプレート直下に残る。
- テンプレートの`macros`はマクロ名の昇順にする（Zabbixがその順でエクスポートする）。
- グラフに閾値の線を出すには、単一アイテムを定数と比べる単純な式のトリガーが要る。複合式のトリガーの閾値は描かれない。
- `drawtype`は`SINGLE_LINE`・`FILLED_REGION`・`BOLD_LINE`・`DOTTED_LINE`・`DASHED_LINE`・`GRADIENT_LINE`。
- 存在しない可能性があるOIDのアイテムには、前処理`CHECK_NOT_SUPPORTED`（`parameters: ['-1']`、`error_handler: DISCARD_VALUE`）を付ける。
- 値が小数になるアイテムは`value_type: FLOAT`を明示する。

## 値の方針

- 取得間隔: すぐ検知したい項目は`1m`、変更検知が不要な項目（`sysDescr`・`ifType`・`ifSpeed`など）は`1d`。
- ヒストリ: 数日前と比較したい項目は`31d`、異常値を残したいだけの項目は`7d`、文字列の情報項目は`365d`。
- トレンド: 数値は`365d`、文字列・ログは`'0'`。
- 取得間隔・ヒストリ・トレンドはマクロにせず、アイテムに直接書く。

## 項目の並び

[tools/normalize.py](../tools/normalize.py)の定数が正本。
