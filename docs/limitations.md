# 制約

## SNMP

- 機種ごとにMIBが違う。RTX830は`ifName`・`ifAlias`（IF-MIB）、`EtherLike-MIB`、`HOST-RESOURCES-MIB`に未対応のため、ディスカバリは`ifDescr`で行う。
- 64bitカウンタ（`ifHC*`）はRTX830で使える。RTX1220・NVR700W・NVR510は未対応。
- パケットバッファはMIBにないため、SNMPでは取れない（Luaで取得する）。
- 他機種で使う場合は、各機種のMIB一覧と照合する。

## Lua

- RTXのLuaでは浮動小数点の`string.format`が使えない。使用率や応答時間は整数演算で計算して文字列に組み立てている。
- `ping`の出力は日本語表示でも応答時間を取れるよう、`ttl=<n>`に続く数値を拾っている。
- APIトークンはルーター上のファイルに平文で置く。書き込み権限をtrapper項目だけに絞った専用ユーザーのトークンを使うこと。
