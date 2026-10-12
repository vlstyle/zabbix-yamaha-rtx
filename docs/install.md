# 導入手順

## 1. テンプレートのインポート

Zabbix UIの「データ収集 > テンプレート > インポート」で、`templates/`の2つのYAMLを取り込む。

## 2. ホストの設定

- インターフェースにSNMP（v2c）を設定する。コミュニティ名は`{$SNMP_COMMUNITY}`のようなグローバルマクロで参照すると、コミュニティ名をホスト定義に書かずに済む。
- `Yamaha RTX by SNMP`と`Yamaha RTX by Lua`を紐付ける。
- 監視するインターフェースは`{$NET.IF.IFDESCR.MATCHES}`で絞る（例: `^(LAN1|LAN2|LAN1/1)$`）。RTXは`ifName`・`ifAlias`を返さないため、ディスカバリは`ifDescr`（`{#IFDESCR}`）を使う。

## 3. RTX側のSNMP設定

```
snmpv2c community read-only <コミュニティ名>
snmpv2c host <Zabbix serverの送信元>
save
```

## 4. Luaスクリプトの設置

1. Zabbixに、ホストのtrapper項目への書き込み権限だけを持つ専用ユーザーを作り、APIトークンを発行する。
2. ルーターのRTFSに`lua/zabbix_metrics.lua`を`/lua/zabbix_metrics.lua`として置く（TFTPなど）。
3. トークン文字列だけを書いたファイルを`/lua/zabbix_token`として置く。トークンはリポジトリや`show config`に置かない。
4. 毎分実行するスケジュールを設定する。

```
schedule at 2 */* *:* * lua /lua/zabbix_metrics.lua <Zabbixのホスト名> <Zabbix APIの送信先> <pingの宛先IP>
save
```

引数は順に、Zabbixに登録したホスト名、Zabbix APIの送信先（`http://<値>/api_jsonrpc.php`として使う）、外部pingの宛先IPv4アドレス。

## 失敗の確認

`show log`で`zabbix_metrics:`から始まるSYSLOG（INFO）を見る。成功時はログを出さない。

| ログ | 原因 |
|---|---|
| `usage: ...` | 引数が足りない |
| `invalid ping target` | 宛先がIPv4アドレスの形式でない |
| `cannot open /lua/zabbix_token` / `token is empty` | トークンファイルがない・空 |
| `ping failed` / `show status packet-buffer failed` | コマンドの実行に失敗 |
| `no values parsed` | 出力のパースで値が1件も取れなかった |
| `request failed` / `http <code>` / `api error` | Zabbix APIへの送信に失敗 |
