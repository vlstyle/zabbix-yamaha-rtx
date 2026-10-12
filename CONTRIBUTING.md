# コントリビューション

IssueとPull Requestを歓迎します。

## Issue

不具合は、機種・ファームウェアのバージョン、Zabbixのバージョンと、`show log`の`zabbix_metrics:`の出力を添えてください。他機種への対応は、`show status packet-buffer`などの出力サンプルがあると助かります（ホスト名・IPアドレス・トークンは伏せてください）。

## Pull Request

1. forkしてブランチを作り、変更する。
2. テンプレートを変えたら整形する。

   ```bash
   python3 tools/normalize.py templates/yamaha_rtx_snmp.yaml
   python3 tools/normalize.py templates/yamaha_rtx_lua.yaml
   ```

   書き方は[docs/template-conventions.md](docs/template-conventions.md)。
3. PRを出す。CIで、テンプレートの整形とLuaの構文を確認する。

実機とZabbixでの動作確認ができていない場合は、PRにそう書いてください。

コントリビューションは、このリポジトリと同じ[AGPL-3.0](LICENSE)で公開されます。
