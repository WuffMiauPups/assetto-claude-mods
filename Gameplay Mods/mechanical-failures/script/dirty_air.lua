-- Dirty Air (CSP Extended Physics, Teil von script.lua oder als Modul eingebunden)
-- Entwurf. Vor dem Test gegen das lokale lua-sdk prüfen: Zugriff auf andere Autos aus dem Physik-Thread,
-- Funktionsname für Flügel-Gain, alternativ ac.addForce an der Vorderachse.
--
-- Modell: Für jeden Vordermann innerhalb MAX_DIST wird der Abstand entlang seiner Fahrtrichtung und der
-- seitliche Versatz bestimmt. Verlust = LUT(Abstand) * Gauss(Versatz / Breite(Abstand)). Mehrere Vordermänner
-- werden nicht addiert, es zählt der stärkste. Der Verlust wird mit einem Tiefpass geglättet und als
-- Gain auf Front- und Heckflügel gesetzt. Widerstand bleibt AC überlassen (Windschatten ist dort vorhanden).

local DirtyAir = {}

local cfg = {
  maxDist = 80,
  lut = nil,               -- {{d, total, front, rear}, ...} aus dirty_air_<era>.lut
  halfWidth10 = 1.1, spread = 0.06,
  smoothing = 6.0,         -- 1/s, Reaktionszeit des Verlusts
  frontWing = 1, rearWing = 2,   -- Flügel-Indizes laut aero.ini des Autos
  tyreHeatGain = 0.0,      -- optional: zusätzliche Reifenerwärmung vorn pro Verlustanteil, Feld prüfen
}

local function loadLut(path)
  local t = {}
  for line in io.lines(path) do
    if not line:match('^;') then
      local d, tot, fr, re = line:match('^([%d%.]+)|([%d%.]+)|([%d%.]+)|([%d%.]+)')
      if d then t[#t + 1] = { tonumber(d), tonumber(tot), tonumber(fr), tonumber(re) } end
    end
  end
  return t
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

local state = { front = 0, rear = 0 }

function DirtyAir.init(era)
  local dataDir = ac.getFolder(ac.FolderID.CarData)     -- Funktionsname prüfen
  cfg.lut = loadLut(dataDir .. '/dirty_air_' .. era .. '.lut')
end

function DirtyAir.update(dt)
  if not cfg.lut then return end
  local me = car
  local myPos = me.position
  local bestFront, bestRear = 0, 0
  for i = 0, sim.carsCount - 1 do
    if i ~= me.index then
      local other = ac.getCar(i)
      if other and other.isActive and not other.isInPitlane then
        local rel = myPos - other.position
        local fwd = other.look                                  -- Fahrtrichtung des Vordermanns
        local along = -rel:dot(fwd)                             -- positiv, wenn wir hinter ihm sind
        if along > 1 and along < cfg.maxDist then
          local side = vec3(fwd.z, 0, -fwd.x)
          local lateral = math.abs(rel:dot(side))
          local w = math.max(0.6, cfg.halfWidth10 + cfg.spread * (along - 10))
          local lat = math.exp(-0.5 * (lateral / w) ^ 2)
          local fr, re = lutLookup(cfg.lut, along)
          fr, re = fr * lat, re * lat
          if fr > bestFront then bestFront, bestRear = fr, re end
        end
      end
    end
  end
  local k = math.min(1, cfg.smoothing * dt)
  state.front = state.front + (bestFront - state.front) * k
  state.rear = state.rear + (bestRear - state.rear) * k

  -- Flügel-Gain setzen (Feature seit CSP 0.1.78, Funktionsname im lokalen SDK nachschlagen):
  -- ac.setWingGain(cfg.frontWing, 1 - state.front); ac.setWingGain(cfg.rearWing, 1 - state.rear)
  -- Fallback ohne Flügel-Gain: nach oben gerichtete Kraft an der Vorderachse, proportional zum verlorenen Abtrieb.
  ac.debug('dirty air front', state.front)
  ac.debug('dirty air rear', state.rear)
end

return DirtyAir
