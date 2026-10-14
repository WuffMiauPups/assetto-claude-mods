-- Dirty Air (CSP Extended Physics, Modul, aus script.lua mit DirtyAir.update(dt) aufrufen)
-- API gegen lua-sdk ac_car_cphys (0.3.0-preview649) geprüft:
--   ac.getCar(i)         aus dem Physik-Script erlaubt, Daten kommen aus dem Grafik-Thread (60 Hz), reicht mit Tiefpass
--   Felder               .isActive, .isInPitlane, .position, .look
--   ac.setWingGain(wingIndex, cdGain, clGain)   überschreibt CD_GAIN/CL_GAIN aus aero.ini
--   ac.INIConfig.carData(car.index, 'dirty_air.ini')  Kennlinie, von tools/install.py aus dem LUT erzeugt
--
-- Modell: Für jeden Vordermann innerhalb MAX_DIST wird der Abstand entlang seiner Fahrtrichtung und der
-- seitliche Versatz bestimmt. Verlust = Kennlinie(Abstand) * Gauss(Versatz / Breite(Abstand)). Mehrere Vordermänner
-- werden nicht addiert, es zählt der stärkste. Der Verlust wird geglättet und als CL-Gain auf die Flügel gesetzt.
-- Widerstand bleibt AC überlassen (Windschatten ist dort vorhanden).
--
-- dirty_air.ini:
--   [SETTINGS] MAX_DIST=80, HALF_WIDTH_10=1.1, SPREAD=0.06, SMOOTHING=6, FRONT_WINGS=1,2, REAR_WINGS=3
--   [LUT] POINT_0=5,0.45,0.30  (Abstand m, Verlust vorn, Verlust hinten), aufsteigend nummeriert

local DirtyAir = {}

local cfg = { maxDist = 80, halfWidth10 = 1.1, spread = 0.06, smoothing = 6.0, frontWings = {}, rearWings = {}, lut = nil }
local state = { front = 0, rear = 0 }
local enabled = false

local function parseList(s)
  local t = {}
  for v in tostring(s):gmatch('[^,%s]+') do t[#t + 1] = tonumber(v) end
  return t
end

function DirtyAir.init()
  local ini = ac.INIConfig.carData(car.index, 'dirty_air.ini')
  if not ini or not ini.sections or not ini.sections['LUT'] then
    ac.warn('[dirty air] dirty_air.ini fehlt, Modul bleibt passiv')
    return false
  end
  cfg.maxDist = ini:get('SETTINGS', 'MAX_DIST', 80)
  cfg.halfWidth10 = ini:get('SETTINGS', 'HALF_WIDTH_10', 1.1)
  cfg.spread = ini:get('SETTINGS', 'SPREAD', 0.06)
  cfg.smoothing = ini:get('SETTINGS', 'SMOOTHING', 6)
  cfg.frontWings = parseList(ini:get('SETTINGS', 'FRONT_WINGS', '1,2'))
  cfg.rearWings = parseList(ini:get('SETTINGS', 'REAR_WINGS', '3'))
  cfg.lut = {}
  local i = 0
  while true do
    local p = ini:get('LUT', 'POINT_' .. i, '')
    if p == '' then break end
    local v = parseList(p)
    cfg.lut[#cfg.lut + 1] = { v[1], v[2], v[3] }
    i = i + 1
  end
  enabled = #cfg.lut >= 2
  return enabled
end

local function lutLookup(d)
  local t = cfg.lut
  if d <= t[1][1] then return t[1][2], t[1][3] end
  for i = 2, #t do
    if d <= t[i][1] then
      local a, b = t[i - 1], t[i]
      local f = (d - a[1]) / (b[1] - a[1])
      return a[2] + (b[2] - a[2]) * f, a[3] + (b[3] - a[3]) * f
    end
  end
  return 0, 0
end

function DirtyAir.update(dt)
  if not enabled then return end
  local myPos = car.position
  local bestFront, bestRear = 0, 0
  for i = 0, sim.carsCount - 1 do
    if i ~= car.index then
      local other = ac.getCar(i)
      if other and other.isActive and not other.isInPitlane then
        local rel = myPos - other.position
        local fwd = other.look
        local along = -rel:dot(fwd)                             -- positiv, wenn wir hinter ihm sind
        if along > 1 and along < cfg.maxDist then
          local side = vec3(fwd.z, 0, -fwd.x)
          local lateral = math.abs(rel:dot(side))
          local w = math.max(0.6, cfg.halfWidth10 + cfg.spread * (along - 10))
          local lat = math.exp(-0.5 * (lateral / w) ^ 2)
          local fr, re = lutLookup(along)
          fr, re = fr * lat, re * lat
          if fr > bestFront then bestFront, bestRear = fr, re end
        end
      end
    end
  end
  local k = math.min(1, cfg.smoothing * dt)
  state.front = state.front + (bestFront - state.front) * k
  state.rear = state.rear + (bestRear - state.rear) * k
  for _, w in ipairs(cfg.frontWings) do ac.setWingGain(w, 1, 1 - state.front) end
  for _, w in ipairs(cfg.rearWings) do ac.setWingGain(w, 1, 1 - state.rear) end
  ac.debug('dirty air front', state.front)
  ac.debug('dirty air rear', state.rear)
end

return DirtyAir
