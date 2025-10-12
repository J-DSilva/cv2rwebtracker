-- fceux_poster.lua (mapping-driven)
-- Loads memoryToImageMap.json (from the same folder) and posts { darkened: [...] }
-- where true = darkened, false = lit. Supports per-entry "latch" and multi-bit ops.

-- Try to load optional modules. FCEUX builds sometimes lack luasocket or dkjson.
local has_socket_http, http = pcall(require, 'socket.http')
local has_ltn12, ltn12 = pcall(require, 'ltn12')
local has_json, json = pcall(require, 'dkjson')

-- Safe logging: prefer gui.addmessage if available, otherwise fall back to print
local function log(msg)
  if type(msg) ~= 'string' then msg = tostring(msg) end
  if type(gui) == 'table' and type(gui.addmessage) == 'function' then
    pcall(gui.addmessage, msg)
  else
    print(msg)
  end
end

if not has_json then
  log('fceux_poster.lua: warning: dkjson not found; using minimal JSON encoder for payloads. Mapping JSON must still be parseable by dkjson or provided as Lua table.')
end

-- Configuration: which URL to POST updates to.
-- If you run the server in the Docker container (as shown earlier), the default
-- of 127.0.0.1:3000 will work because the container published port 3000 to the host.
-- If you need to reach the host from inside another container or a special network,
-- you can set this to 'http://host.docker.internal:3000/update' instead.
local SERVER_URL = 'http://127.0.0.1:3000/update'

-- Helper: read file
local function read_file(path)
  local f = io.open(path, 'r')
  if not f then return nil end
  local s = f:read('*a')
  f:close()
  return s
end

-- Parse hex string like "0x0091" or decimal number
local function parse_addr(a)
  if type(a) == 'number' then return a end
  if string.sub(a,1,2) == '0x' then
    return tonumber(string.sub(a,3),16)
  end
  return tonumber(a)
end

-- Load mapping
-- Embedded mapping table (inlined so this script is self-contained for FCEUX)
-- Embedded mapping table (inlined so this script is self-contained for FCEUX)
-- Special-case: entries that omit a `bit` field are treated as whole-byte checks.
-- For those entries the byte is read; 0x00 => darkened (default), any non-zero value => lit.
-- Laurel and Garlic are monitored as whole bytes per your request:
--   The Laurel -> address 0x004C (byte check)
--   Garlic      -> address 0x004D (byte check)
local mapping = {
  { alt = "White Crystal", addr = "0x0091", bit = 5, when = "set", latch = true },
  { alt = "Blue Crystal", addr = "0x0091", bit = 6, when = "set", latch = true },
  { alt = "Red Crystal", addr = "0x0091", bit = {5,6}, when = "set", op = "and" },
  { alt = "Holy Water", addr = "0x004A", bit = 3, when = "set" },
  { alt = "The Cross", addr = "0x0092", bit = 1, when = "set" },
  { alt = "The Rib", addr = "0x0091", bit = 0, when = "set" },
  { alt = "The Nail", addr = "0x0091", bit = 3, when = "set" },
  { alt = "The Eyeball", addr = "0x0091", bit = 2, when = "set" },
  { alt = "The Heart", addr = "0x0091", bit = 1, when = "set" },
  { alt = "The Ring", addr = "0x0091", bit = 4, when = "set" },
  -- Garlic: monitor full byte at 0x004D; any non-zero -> lit
  { alt = "Garlic", addr = "0x004D", when = "set" },
  { alt = "Sacred Flame", addr = "0x004A", bit = 5, when = "set" },
  { alt = "Silk Bag", addr = "0x0092", bit = 0, when = "set" },
  { alt = "The Diamond", addr = "0x004A", bit = 0, when = "set" },
  -- The Laurel: monitor full byte at 0x004C; any non-zero -> lit
  { alt = "The Laurel", addr = "0x004C", when = "set" },
  { alt = "The Oak Stake", addr = "0x004A", bit = 6, when = "set" },
  { alt = "The Dagger", addr = "0x004A", bit = 0, when = "set" },
  { alt = "The Silver Knife", addr = "0x004A", bit = 1, when = "set" },
  { alt = "The Gold Knife", addr = "0x004A", bit = 2, when = "set" },
}

-- Normalize mapping entries
for i,entry in ipairs(mapping) do
  entry.addr_n = parse_addr(entry.addr)
  entry.bit = entry.bit -- could be number or array
  entry.op = entry.op or 'or' -- default OR for multi-bit
  entry.when = entry.when or 'set'
  entry.latch = entry.latch or false
  entry._latched = false
end

-- Build list of addresses to read (unique)
local addrs_set = {}
local addrs = {}
for _,e in ipairs(mapping) do
  if not addrs_set[e.addr_n] then
    addrs_set[e.addr_n] = true
    table.insert(addrs, e.addr_n)
  end
end

-- Read all configured addresses into a table {addr -> value}
local function read_addrs()
  local out = {}
  for _,a in ipairs(addrs) do
    -- Use the appropriate memory-read API depending on emulator build
    local value = nil
    if type(mainmemory) == 'table' then
      if type(mainmemory.read_u8) == 'function' then
        value = mainmemory.read_u8(a)
      elseif type(mainmemory.readbyte) == 'function' then
        value = mainmemory.readbyte(a)
      end
    end
    if value == nil and type(memory) == 'table' then
      if type(memory.readbyte) == 'function' then
        value = memory.readbyte(a)
      elseif type(memory.read_u8) == 'function' then
        value = memory.read_u8(a)
      end
    end
    if value == nil then
      -- No known memory API found; abort with a helpful message
      log('fceux_poster.lua: no supported memory.read API found (tried mainmemory, memory). Ensure you run this in FCEUX or a compatible emulator build.')
      return nil
    end
    out[a] = value
  end
  return out
end

local function eval_entry(e, vals)
  local byte = vals[e.addr_n]
  if byte == nil then return false end

    local function check_bit(bit)
      -- Support multiple Lua environments: prefer bit, then bit32, else arithmetic
      if type(bit) ~= 'number' then return false end
      if _G.bit and type(_G.bit.band) == 'function' and type(_G.bit.lshift) == 'function' then
        return _G.bit.band(byte, _G.bit.lshift(1, bit)) ~= 0
      end
      if _G.bit32 and type(_G.bit32.band) == 'function' then
        return _G.bit32.band(byte, 2 ^ bit) ~= 0
      end
      -- Fallback arithmetic approach
      local mask = 2 ^ bit
      return math.floor(byte / mask) % 2 ~= 0
    end

  local ok = false
  if type(e.bit) == 'number' then
    ok = check_bit(e.bit)
  elseif type(e.bit) == 'table' then
    if e.op == 'and' then
      ok = true
      for _,b in ipairs(e.bit) do ok = ok and check_bit(b) end
    else -- 'or'
      ok = false
      for _,b in ipairs(e.bit) do ok = ok or check_bit(b) end
    end
  else
    -- no bit provided: treat non-zero byte as set
    ok = (byte ~= 0)
  end

  if e.when == 'set' then
    return ok
  else -- when == 'clear'
    return not ok
  end
end

local function build_states(vals)
  local states = {}
  for i,e in ipairs(mapping) do
    local is_lit = eval_entry(e, vals)
    -- handle latch: once lit, remains lit
    if e.latch then
      if is_lit then e._latched = true end
      is_lit = e._latched or is_lit
    end
    -- darkened = not lit
    states[i] = not is_lit
  end
  return states
end

local function simple_encode_payload(states)
  local parts = {}
  for i,v in ipairs(states) do parts[#parts+1] = v and 'true' or 'false' end
  return '{"darkened":[' .. table.concat(parts, ',') .. ']}'
end

local function post_state(states)
  local payload
  if has_json then
    payload = json.encode({ darkened = states })
  else
    payload = simple_encode_payload(states)
  end

  -- Preferred method: use luasocket/http if available
  if has_socket_http and has_ltn12 then
    local response_body = {}
    local res, code, headers = http.request{
      url = SERVER_URL,
      method = 'POST',
      headers = {
        ['Content-Type'] = 'application/json',
        ['Content-Length'] = tostring(#payload),
      },
      source = ltn12.source.string(payload),
      sink = ltn12.sink.table(response_body),
    }
    if code ~= 200 then
      log('FCEUX POST failed (socket.http): '..tostring(code))
    end
    return
  end

  -- Fallback: use curl via os.execute (macOS has curl). Write to temp file and POST
  local tmp = os.tmpname()
  local f = io.open(tmp, 'w')
  if f then
    f:write(payload)
    f:close()
    local cmd = string.format('curl -s -o /dev/null -w "%%{http_code}" -X POST -H "Content-Type: application/json" --data-binary @%s %s', tmp, SERVER_URL)
    local ok = os.execute(cmd)
    if not ok then gui.addmessage('FCEUX POST failed (curl fallback)') end
    os.remove(tmp)
  else
    log('FCEUX POST failed: cannot write temp file')
  end
end

-- Main loop
local function states_key(states)
  -- deterministic compact string representation for change detection
  local parts = {}
  for i,v in ipairs(states) do parts[#parts+1] = v and '1' or '0' end
  return table.concat(parts, ',')
end

local last_key = nil
while true do
  local vals = read_addrs()
  if not vals then return end -- aborted due to missing memory API
  local states = build_states(vals)
  local key = states_key(states)
  if key ~= last_key then
    post_state(states)
    last_key = key
  end
  emu.frameadvance()
end
