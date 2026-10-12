# zabbix-yamaha-rtx

ヤマハ RTX ルーターを Zabbix で監視するための、Luaスクリプトとテンプレート。

| ファイル | 置き場所 | 内容 |
|---|---|---|
| [templates/yamaha_rtx_snmp.yaml](templates/yamaha_rtx_snmp.yaml) | Zabbix | `Yamaha RTX by SNMP`。CPU・メモリ・インターフェース・ICMP監視 |
| [templates/yamaha_rtx_lua.yaml](templates/yamaha_rtx_lua.yaml) | Zabbix | `Yamaha RTX by Lua`。パケットバッファ・外部pingのtrapper項目 |
| [lua/zabbix_metrics.lua](lua/zabbix_metrics.lua) | RTX | SNMPのMIBにない値を取得し、Zabbix APIの`history.push`で送る |

## 動作確認済みの環境

| 項目 | バージョン |
|---|---|
| 機種 | RTX830 |
| Zabbix | 7.0 |

## 導入の流れ

1. Zabbixに2つのテンプレートをインポートする。
2. ホストにテンプレートを紐付ける（SNMPインターフェースが必要）。
3. RTXにLuaスクリプトとAPIトークンを置き、`schedule`で毎分実行する。

詳細は [docs/install.md](docs/install.md)。取得項目とトリガーは [docs/items.md](docs/items.md)、RTXのLuaの制約は [docs/limitations.md](docs/limitations.md)。

## 開発

テンプレートは Zabbix 7.0 のエクスポート形式。編集後は整形する。

```bash
python3 tools/normalize.py templates/yamaha_rtx_snmp.yaml
python3 tools/normalize.py templates/yamaha_rtx_lua.yaml
```

項目の並び順と既定値の扱いは [docs/template-conventions.md](docs/template-conventions.md)。
