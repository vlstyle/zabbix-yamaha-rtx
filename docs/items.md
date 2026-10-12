# 取得項目とトリガー

## Yamaha RTX by Lua

Luaスクリプトが`history.push`で送るtrapper項目。

| キー | 内容 |
|---|---|
| `pktbuf.<small\|middle\|large\|huge>.usage` | `allocated`÷`max-buffer`の%（Luaで計算） |
| `pktbuf.<...>.allocated` / `.free` / `.fail` / `.chunks` | `show status packet-buffer`の各値 |
| `ping.external.loss` | 外部pingのロス率（%） |
| `ping.external.rtt.avg` / `.min` / `.max` | 外部pingの応答時間（ms）。全て無応答のときは`loss`だけ送る |

外部pingは宛先に`ping -c 3 -w 1`を実行する（約3秒で終わる）。ISPの輻輳確認を想定している。

| マクロ | 既定値 | 用途 |
|---|---|---|
| `{$PKTBUF.USAGE.WARN}` | 80 | パケットバッファ使用率の警告（5分超過） |
| `{$EXTPING.LOSS.CRIT}` | 50 | 外部pingロス率（%以上） |
| `{$EXTPING.RTT.CRIT}` | 100 | 外部ping最小応答時間（ms超を5分継続） |

トリガーは、`fail`の増加、`usage`の超過、5分間データなし、外部pingのロス・応答時間。

## Yamaha RTX by SNMP

公式の`Network Generic Device by SNMP`（7.0）を元にしたテンプレート。

- ICMP ping・ロス・応答時間（Zabbix serverから）
- `sysDescr`・`sysName`・`sysUpTime`など（SNMPv2-MIB）
- CPU・メモリ使用率とコア毎のCPU（ヤマハ独自MIB `1.3.6.1.4.1.1182.2.1`: `yrhCpuUtil1min`・`yrhMemoryUtil`・`yrhMultiCpuUtil1min`）
- インターフェースのディスカバリ（`ifDescr`）。64bitカウンタ（`ifHC*`）、エラー・破棄、速度、状態、種別
