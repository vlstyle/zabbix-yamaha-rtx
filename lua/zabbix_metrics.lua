local TOKEN_FILE = "/lua/zabbix_token"

local function log(msg)
  rt.syslog("info", "zabbix_metrics: " .. msg)
end

local PING_COUNT = 3
local PING_WAIT = 1

local HOST, SERVER, PING_TARGET = arg[1], arg[2], arg[3]
if not HOST or not SERVER or not PING_TARGET then
  log("usage: zabbix_metrics.lua <zabbix host name> <zabbix server> <ping target ip>")
  return
end
if not PING_TARGET:match("^%d+%.%d+%.%d+%.%d+$") then
  log("invalid ping target: " .. PING_TARGET)
  return
end
local URL = "http://" .. SERVER .. "/api_jsonrpc.php"

local file = io.open(TOKEN_FILE, "r")
if not file then
  log("cannot open " .. TOKEN_FILE)
  return
end
local token = (file:read("*a") or ""):gsub("%s+", "")
file:close()
if token == "" then
  log("token is empty")
  return
end

local entries = {}
local function push(key, value)
  entries[#entries + 1] = string.format(
    '{"host":"%s","key":"%s","value":%s}', HOST, key, value)
end
local function add(group, name, value)
  push("pktbuf." .. group .. "." .. name, value)
end

local function idiv(a, b)
  return (a - a % b) / b
end

local function parse_pktbuf(out)
  local group, max
  for line in out:gmatch("[^\r\n]+") do
    local g = line:match("^(%a+) group:")
    if g then
      group, max = g, nil
    elseif group then
      local m = line:match("max%-buffer=(%d+)")
      if m then
        max = tonumber(m)
      end
      local free = line:match("^%s*(%d+) buffers? in free list")
      if free then
        add(group, "free", free)
      end
      local allocated, fail = line:match(
        "^%s*(%d+) buffers? %a+ allocated, req/succ/fail/rel = %d+/%d+/(%d+)/%d+")
      if allocated then
        add(group, "allocated", allocated)
        add(group, "fail", fail)
        if max and max > 0 then
          local hundredths = idiv(tonumber(allocated) * 10000 + idiv(max, 2), max)
          local fraction = hundredths % 100
          if fraction < 10 then
            fraction = "0" .. fraction
          end
          add(group, "usage", string.format("%d.%s", idiv(hundredths, 100), fraction))
        end
      end
      local chunks = line:match("^%s*(%d+) chunks? %a+ allocated,")
      if chunks then
        add(group, "chunks", chunks)
      end
    end
  end
end

local function micro(v)
  return string.format("%d.%03d", idiv(v, 1000), v % 1000)
end

local function collect_ping()
  local ok, out = rt.command(string.format(
    "ping -c %d -w %d %s", PING_COUNT, PING_WAIT, PING_TARGET), "off")
  if not ok or not out then
    log("ping failed")
    return
  end
  local sum, min, max, received = 0, nil, nil, 0
  for whole, frac in out:gmatch("ttl=%d+%D-(%d+)%.?(%d*)") do
    if received < PING_COUNT then
      local v = tonumber(whole) * 1000 + tonumber((frac .. "000"):sub(1, 3))
      sum = sum + v
      min = (not min or v < min) and v or min
      max = (not max or v > max) and v or max
      received = received + 1
    end
  end
  push("ping.external.loss", string.format("%d", idiv((PING_COUNT - received) * 100, PING_COUNT)))
  if received > 0 then
    push("ping.external.rtt.avg", micro(idiv(sum, received)))
    push("ping.external.rtt.min", micro(min))
    push("ping.external.rtt.max", micro(max))
  end
end

collect_ping()

local ok, out = rt.command("show status packet-buffer", "off")
if not ok or not out then
  log("show status packet-buffer failed")
else
  parse_pktbuf(out)
end

if #entries == 0 then
  log("no values parsed")
  return
end

local res = rt.httprequest({
  url = URL,
  method = "POST",
  auth_type = "bearer",
  auth_token = token,
  content_type = "application/json-rpc",
  post_text = '{"jsonrpc":"2.0","method":"history.push","params":['
    .. table.concat(entries, ",") .. '],"id":1}',
})

if not res.rtn1 then
  log("request failed: " .. tostring(res.err))
elseif res.code ~= 200 then
  log("http " .. tostring(res.code))
elseif res.body and res.body:find('"error"', 1, true) then
  log("api error: " .. res.body:sub(1, 180))
end
