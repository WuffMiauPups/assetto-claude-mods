-- Dirty Air: Abtriebsverlust im Nachlauf eines Vordermanns (CSP Extended Physics, Modul)
-- Geprüft gegen lua-sdk/ac_car_cphys, CSP 0.3.0-preview649:
--   ac.setWingGain(wingIndex, cdGain, clGain)   überschreibt CD_GAIN/CL_GAIN aus aero.ini
--   ac.getCar(i) -> ac.StateCar mit position, look, isActive, isInPitlane; sim.carsCount
--   ac.INIConfig.carData(car.index, 'aero.ini')  Flügelnamen für die Zuordnung vorn/hinten
--   io.load(ac.getFolder(ac.FolderID.ScriptOrigin) .. '/dirty_air.lut')  Kennlinie der Ära
--
-- Modell: Für jeden Vordermann innerhalb MAX_DIST wird der Abstand entlang seiner Fahrtrichtung und der
-- seitliche Versatz bestimmt. Verlust = LUT(Abstand) * Gauss(Versatz / Breite(Abstand)). Es zählt der
-- stärkste Vordermann, nicht die Summe. Der Verlust wird tiefpassgefiltert und als CL-Gain (1 - Verlust)
-- auf die Front- und Heckflügel gesetzt. CD-Gain bleibt 1: Windschatten (weniger Widerstand) hat AC selbst.
--
-- Konfiguration in failures.ini, Abschnitt [DIRTY_AIR]:
--   ENABLED=1  MAX_DIST=80  SMOOTHING=6  HALF_WIDTH_10M=1.1  WIDTH_SPREAD=0.06  LUT=dirty_air.lut
--   FRONT_WINGS=1,2  REAR_WINGS=3,4,7   (leer: automatisch aus den NAME-Einträgen in aero.ini)
--   EXCLUDE_WINGS=5,6                   (Flügel, die ein anderes Script des Autos selbst steuert)
--   DEBUG=1

local M = {}

local cfg = {
  enabled = true, maxDist = 80, smoothing = 6.0, halfWidth10 = 1.1, spread = 0.06,
  lutFile = 'dirty_air.lut', frontWings = {}, rearWings = {}, exclude = {}, debug = true,
}
local lut = nil                     -- {{d, total, front, rear}, ...}
local state = { front = 0, rear = 0, applied = false }

local function parseList(s)
  local t = {}
  for n in tostring(s or ''):gmatch('%-?%d+') do t[#t + 1] = tonumber(n) end
  return t
end

local function parseLut(text)
  local t = {}
  for line in tostring(text or ''):gmatch('[^\r\n]+') do
    if not line:match('^%s*;') then
      local d, tot, fr, re = line:match('^%s*([%d%.]+)%s*|%s*([%d%.]+)%s*|%s*([%d%.]+)%s*|%s*([%d%.]+)')
      if d then t[#t + 1] = { tonumber(d), tonumber(tot), tonumber(fr), tonumber(re) } end
    end
  end
  table.sort(t, function(a, b) return a[1] < b[1] end)
  return #t > 0 and t or nil
end

local function lutLookup(t, d)
  if d <= t[1][1] then return t[1][3], t[1][4] end
  for i = 2, #t do
    if d <= t[i][1] then
      local a, b = t[i - 1], t[i]
      local f = (d - a[1]) / (b[1] - a[1])
      return a[3] + (b[3] - a[3]) * f, a[4] + (b[4] - a[4]) * f
    end
  end
  return 0, 0
end

-- Flügel anhand der NAME-Einträge in aero.ini zuordnen (nur wenn nichts konfiguriert ist)
local function classifyWings()
  local ok, aero = pcall(ac.INIConfig.carData, car.index, 'aero.ini')
  if not ok or not aero then return end
  for i = 0, 63 do
    local name = aero:get('WING_' .. i, 'NAME', '')
    if name == '' then break end
    local u = name:upper()
    if u:find('FRONT') or u:find('SPLITTER') then
      cfg.frontWings[#cfg.frontWings + 1] = i
    elseif u:find('REAR') or u:find('DIFF') or u:find('MONKEY') or u:find('BEAM') then
      cfg.rearWings[#cfg.rearWings + 1] = i
    end
  end
end

local function removeExcluded(list)
  local out = {}
  for _, i in ipairs(list) do
    local skip = false
    for _, e in ipairs(cfg.exclude) do if e == i then skip = true end end
    if not skip then out[#out + 1] = i end
  end
  return out
end

---@param ini ac.INIConfig? failures.ini des Autos (optional)
function M.init(ini)
  if ini then
    cfg.enabled = ini:get('DIRTY_AIR', 'ENABLED', 1) == 1
    cfg.maxDist = ini:get('DIRTY_AIR', 'MAX_DIST', cfg.maxDist)
    cfg.smoothing = ini:get('DIRTY_AIR', 'SMOOTHING', cfg.smoothing)
    cfg.halfWidth10 = ini:get('DIRTY_AIR', 'HALF_WIDTH_10M', cfg.halfWidth10)
    cfg.spread = ini:get('DIRTY_AIR', 'WIDTH_SPREAD', cfg.spread)
    cfg.lutFile = ini:get('DIRTY_AIR', 'LUT', cfg.lutFile)
    cfg.debug = ini:get('DIRTY_AIR', 'DEBUG', 1) == 1
    cfg.frontWings = parseList(ini:get('DIRTY_AIR', 'FRONT_WINGS', ''))
    cfg.rearWings = parseList(ini:get('DIRTY_AIR', 'REAR_WINGS', ''))
    cfg.exclude = parseList(ini:get('DIRTY_AIR', 'EXCLUDE_WINGS', ''))
  end
  if not cfg.enabled then return end

  local path = ac.getFolder(ac.FolderID.ScriptOrigin) .. '/' .. cfg.lutFile
  lut = parseLut(io.load(path))
  if not lut then
    ac.log('[dirty_air] Kennlinie fehlt oder leer: ' .. path .. ', Dirty Air aus')
    cfg.enabled = false
    return
  end
  if #cfg.frontWings == 0 and #cfg.rearWings == 0 then classifyWings() end
  cfg.frontWings = removeExcluded(cfg.frontWings)
  cfg.rearWings = removeExcluded(cfg.rearWings)
  ac.log(string.format('[dirty_air] car %d: %d Punkte in %s, vorn {%s} hinten {%s}', car.index, #lut, cfg.lutFile,
    table.concat(cfg.frontWings, ','), table.concat(cfg.rearWings, ',')))
end

local function applyGains(front, rear)
  for _, i in ipairs(cfg.frontWings) do ac.setWingGain(i, 1, 1 - front) end
  for _, i in ipairs(cfg.rearWings) do ac.setWingGain(i, 1, 1 - rear) end
end

function M.update(dt)
  if not cfg.enabled or not lut then return end
  local myPos = car.position
  local bestFront, bestRear = 0, 0
  for i = 0, sim.carsCount - 1 do
    if i ~= car.index then
      local other = ac.getCar(i)
      if other and other.isActive and not other.isInPitlane then
        local rel = myPos - other.position
        local fwd = other.look
        local along = -rel:dot(fwd)                 -- positiv, wenn wir hinter dem anderen sind
        if along > 1 and along < cfg.maxDist then
          local side = vec3(fwd.z, 0, -fwd.x)
          local lateral = math.abs(rel:dot(side))
          local w = math.max(0.6, cfg.halfWidth10 + cfg.spread * (along - 10))
          local lat = math.exp(-0.5 * (lateral / w) ^ 2)
          local fr, re = lutLookup(lut, along)
          fr, re = fr * lat, re * lat
          if fr > bestFront then bestFront, bestRear = fr, re end
        end
      end
    end
  end

  local k = math.min(1, cfg.smoothing * dt)
  state.front = state.front + (bestFront - state.front) * k
  state.rear = state.rear + (bestRear - state.rear) * k

  if state.front > 0.001 or state.rear > 0.001 then
    applyGains(state.front, state.rear)
    state.applied = true
  elseif state.applied then
    applyGains(0, 0)                               -- einmal zurücksetzen, danach nicht mehr eingreifen
    state.applied = false
  end

  if cfg.debug then
    ac.debug('dirty air front', state.front)
    ac.debug('dirty air rear', state.rear)
  end
end

function M.reset()
  state.front, state.rear = 0, 0
  if state.applied then applyGains(0, 0); state.applied = false end
end

return M
