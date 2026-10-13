-- Reliability & Dirty Air (CSP Lua-App)
-- Wirkt über die physics.*-API auf jedes Auto im Feld, Spieler und KI, ohne data.acd anzufassen.
-- Geprüft gegen lua-sdk/ac_apps (CSP 0.3.0-preview649):
--   physics.setGripDecrease(car, wheels, 0..1)      Dirty Air, Modus "Grip" (invalidiert keine Runde)
--   physics.setAirDensityMultiplier(car, k)         Dirty Air, Modus "Luftdichte" (invalidiert die Runde)
--   physics.setCarEngineLife(car, life)             Motor-, Getriebe-, Hydraulik-, Elektrik-, Kühlungsausfall (Auto rollt aus)
--   physics.setCarRestrictor(car, pct)              Leistungsverlust, Turbo, Warnphasen
--   physics.blowTyres(car, wheels)                  Reifenschaden
--   physics.setSuspensionDamage(car, wheels, kmh)   Aufhängung
-- Nicht abbildbar über die App: Bremsdefekt (keine API), bleibt dem Auto-Script vorbehalten.

local S = ac.storage({
  enabled = true, dirtyAir = true, failures = true,
  strength = 0.4, aiStrength = 0.25, aeroShare = 0.5, mode = 0,   -- mode 0 = Grip, 1 = Luftdichte
  failMult = 1.0, seasonAuto = true, season = 2008, log = true, showCars = true,
}, 'reliability')

local function eraForYear(y)
  if y <= 1992 then return '1988_turbo' elseif y <= 1995 then return '1993_1994' elseif y <= 2004 then return '1996_2004'
  elseif y <= 2008 then return '2005_2008' elseif y <= 2013 then return '2009_2013' elseif y <= 2016 then return '2014_2016'
  elseif y <= 2021 then return '2017_2021' elseif y <= 2025 then return '2022_2025' else return '2026' end
end

local ROOT = ac.getFolder(ac.FolderID.ScriptOrigin)
local lutCache, profileCache = {}, {}

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

local function getLut(era)
  if lutCache[era] == nil then
    lutCache[era] = parseLut(io.load(ROOT .. '/data/dirty_air_' .. era .. '.lut')) or false
    if not lutCache[era] then ac.log('[reliability] Kennlinie fehlt: dirty_air_' .. era .. '.lut') end
  end
  return lutCache[era] or nil
end

local function lutLookup(t, d)
  if d <= t[1][1] then return t[1][2], t[1][3], t[1][4] end
  for i = 2, #t do
    if d <= t[i][1] then
      local a, b = t[i - 1], t[i]
      local f = (d - a[1]) / (b[1] - a[1])
      return a[2] + (b[2] - a[2]) * f, a[3] + (b[3] - a[3]) * f, a[4] + (b[4] - a[4]) * f
    end
  end
  return 0, 0, 0
end

local FAIL_KEYS = { 'ENGINE', 'POWER_LOSS', 'TURBO', 'GEARBOX', 'HYDRAULICS', 'ELECTRICS', 'BRAKES', 'PUNCTURE', 'SUSPENSION', 'COOLING' }

local function getProfile(season)
  season = math.max(1988, math.min(2025, season))
  if profileCache[season] == nil then
    local p = { season = season, raceLengthMin = 90, rates = {} }
    local ok, ini = pcall(ac.INIConfig.load, ROOT .. '/profiles/failures_' .. season .. '.ini')
    if ok and ini then
      p.raceLengthMin = ini:get('GLOBAL', 'RACE_LENGTH_MIN', 90)
      for _, k in ipairs(FAIL_KEYS) do p.rates[k] = ini:get('ERA', k, 0) end
    else
      ac.log('[reliability] Profil fehlt: failures_' .. season .. '.ini')
    end
    profileCache[season] = p
  end
  return profileCache[season]
end

-- ---------- Zustand pro Auto ----------
local cars = {}
local sessionId = 0
local logTimer = 0

local function lcg(state)
  state.v = (state.v * 1103515245 + 12345) % 2147483648
  return state.v / 2147483648
end

local function currentSeason(carIdx)
  if S.seasonAuto then
    local c = ac.getCar(carIdx)
    local y = c and c.year or 0
    if y < 1950 then local p = ac.getCar(0); y = p and p.year or 2008 end
    if y < 1950 then y = 2008 end
    return y
  end
  return S.season
end

local function initCar(i)
  local season = currentSeason(i)
  cars[i] = {
    season = season, era = eraForYear(season), front = 0, rear = 0, total = 0, applied = false,
    rng = { v = (sessionId * 7919 + (i + 1) * 104729 + math.floor(os.clock() * 1000)) % 2147483648 },
    active = {}, done = {}, baseRestrictor = nil, nearest = 1e9, peak = 0,
  }
end

local function resetAll()
  for i, c in pairs(cars) do
    if c.applied then physics.setGripDecrease(i, ac.Wheel.All, 0); physics.setAirDensityMultiplier(i, 1) end
    if c.baseRestrictor then physics.setCarRestrictor(i, c.baseRestrictor) end
  end
  cars = {}
end

ac.onSessionStart(function() sessionId = sessionId + 1; resetAll() end)

-- ---------- Dirty Air ----------
local function aeroShare(speedKmh)
  local s = S.aeroShare * (speedKmh / 200) ^ 2
  return math.max(0, math.min(0.85, s))
end

local function updateDirtyAir(sim, dt)
  local n = sim.carsCount
  for i = 0, n - 1 do
    local me = ac.getCar(i)
    local c = cars[i]
    if me and c and me.physicsAvailable and not me.isInPitlane then
      local lut = getLut(c.era)
      local bestT, bestF, bestR, nearest = 0, 0, 0, 1e9
      if lut then
        for j = 0, n - 1 do
          if j ~= i then
            local o = ac.getCar(j)
            if o and o.isActive and not o.isInPitlane then
              local rel = me.position - o.position
              local fwd = o.look
              local along = -rel:dot(fwd)
              if along > 1 and along < 80 then
                if along < nearest then nearest = along end
                local side = vec3(fwd.z, 0, -fwd.x)
                local lateral = math.abs(rel:dot(side))
                local w = math.max(0.6, 1.1 + 0.06 * (along - 10))
                local lat = math.exp(-0.5 * (lateral / w) ^ 2)
                local t, f, r = lutLookup(lut, along)
                if f * lat > bestF then bestT, bestF, bestR = t * lat, f * lat, r * lat end
              end
            end
          end
        end
      end
      local scale = me.isAIControlled and S.aiStrength or S.strength
      if not S.dirtyAir then scale = 0 end
      local k = math.min(1, 6 * dt)
      c.front = c.front + (bestF * scale - c.front) * k
      c.rear = c.rear + (bestR * scale - c.rear) * k
      c.total = c.total + (bestT * scale - c.total) * k
      c.nearest = nearest
      if c.front > c.peak then c.peak = c.front end

      if c.front > 0.002 or c.rear > 0.002 then
        if S.mode == 0 then
          local share = aeroShare(me.speedKmh)
          physics.setGripDecrease(i, ac.Wheel.Front, c.front * share)
          physics.setGripDecrease(i, ac.Wheel.Rear, c.rear * share)
        else
          physics.setAirDensityMultiplier(i, 1 - c.total)
        end
        c.applied = true
      elseif c.applied then
        physics.setGripDecrease(i, ac.Wheel.All, 0)
        physics.setAirDensityMultiplier(i, 1)
        c.applied = false
      end
    end
  end
end

-- ---------- Ausfälle ----------
local function logEvent(i, text)
  local car = ac.getCar(i)
  local name = ac.getDriverName(i) or ('car ' .. i)
  ac.log(string.format('[reliability] %s (car %d, %s): %s', name, i, ac.getCarID(i), text))
  if car and not car.isAIControlled then ac.setMessage('Defekt', text, nil, 8) end
end

local function restrictor(i, pct)
  local c = cars[i]
  if not c.baseRestrictor then local car = ac.getCar(i); c.baseRestrictor = car and car.restrictor or 0 end
  physics.setCarRestrictor(i, math.max(c.baseRestrictor, pct))
end

local WHEELS = { ac.Wheel.FrontLeft, ac.Wheel.FrontRight, ac.Wheel.RearLeft, ac.Wheel.RearRight }

local FAIL = {}
-- Jeder Defekt: apply(i, f, dt), f.t läuft mit. Terminale Defekte setzen das Motorleben auf 0, das Auto rollt aus.
FAIL.ENGINE = function(i, f, dt)
  if f.t < 20 then restrictor(i, 12)
  elseif f.t < 45 then restrictor(i, f.t % 2 < 0.4 and 60 or 20)
  elseif not f.done then physics.setCarEngineLife(i, 0); f.done = true; logEvent(i, 'Motorschaden') end
end
FAIL.POWER_LOSS = function(i, f, dt)
  if not f.pct then f.pct = 15 + math.floor(lcg(cars[i].rng) * 15) end
  restrictor(i, f.t < 10 and 5 or f.pct)
  if f.t >= 10 and not f.done then f.done = true; logEvent(i, string.format('Leistungsverlust, Restriktor %d%%', f.pct)) end
end
FAIL.TURBO = function(i, f, dt)
  local car = ac.getCar(i)
  if car and car.turboCount == 0 then f.done = true; return end
  restrictor(i, f.t < 15 and 10 or 30)
  if f.t >= 15 and not f.done then f.done = true; logEvent(i, 'Turbo defekt, Ladedruck weg') end
end
local function terminal(name, warnSec, warnPct)
  return function(i, f, dt)
    if f.t < warnSec then
      if warnPct > 0 then restrictor(i, warnPct) end
    elseif not f.done then
      physics.setCarEngineLife(i, 0); f.done = true; logEvent(i, name)
    end
  end
end
FAIL.GEARBOX = terminal('Getriebeschaden', 15, 0)
FAIL.HYDRAULICS = terminal('Hydraulikausfall', 25, 8)
FAIL.ELECTRICS = terminal('Elektrikdefekt', 30, 15)
FAIL.COOLING = terminal('Kühlung, Motor überhitzt', 60, 10)
FAIL.PUNCTURE = function(i, f, dt)
  if not f.done then
    physics.blowTyres(i, WHEELS[1 + math.floor(lcg(cars[i].rng) * 4)]); f.done = true; logEvent(i, 'Reifenschaden')
  end
end
FAIL.SUSPENSION = function(i, f, dt)
  if not f.done then
    physics.setSuspensionDamage(i, WHEELS[1 + math.floor(lcg(cars[i].rng) * 4)], 70); f.done = true; logEvent(i, 'Aufhängung beschädigt')
  end
end
-- FAIL.BRAKES: keine API in der App, nur über das Auto-Script

local function updateFailures(sim, dt)
  local sessionMult = sim.raceSessionType == ac.SessionType.Race and 1.0 or 0.5
  for i = 0, sim.carsCount - 1 do
    local car, c = ac.getCar(i), cars[i]
    if car and c and car.physicsAvailable and car.speedKmh > 30 then
      local p = getProfile(c.season)
      if S.failures then
        for _, k in ipairs(FAIL_KEYS) do
          if FAIL[k] and not c.active[k] and not c.done[k] then
            local perSec = (p.rates[k] or 0) / 100 * S.failMult * sessionMult / (p.raceLengthMin * 60)
            if lcg(c.rng) < perSec * dt then c.active[k] = { t = 0 }; c.done[k] = true end
          end
        end
      end
      for k, f in pairs(c.active) do
        f.t = f.t + dt
        FAIL[k](i, f, dt)
      end
    end
  end
end

-- ---------- Hauptschleife ----------
function script.update(dt)
  local sim = ac.getSim()
  if not S.enabled or sim.isReplayActive then return end
  for i = 0, sim.carsCount - 1 do if not cars[i] then initCar(i) end end
  updateDirtyAir(sim, dt)
  updateFailures(sim, dt)

  if S.log then
    logTimer = logTimer + dt
    if logTimer >= 10 then
      logTimer = 0
      local c = cars[0]
      if c then
        ac.log(string.format('[reliability] car 0: Aera %s, Vordermann %.0f m, Verlust vorn %.2f hinten %.2f, Spitze %.2f',
          c.era, c.nearest < 1e8 and c.nearest or -1, c.front, c.rear, c.peak))
        c.peak = 0
      end
    end
  end
end

-- ---------- Fenster ----------
local MODES = { 'Grip (Reifen vorn/hinten, Runde bleibt gültig)', 'Luftdichte (Abtrieb und Widerstand, Runde ungültig)' }

function script.windowMain(dt)
  if ui.checkbox('Aktiv', S.enabled) then S.enabled = not S.enabled; if not S.enabled then resetAll() end end
  ui.sameLine(); if ui.checkbox('Dirty Air', S.dirtyAir) then S.dirtyAir = not S.dirtyAir end
  ui.sameLine(); if ui.checkbox('Ausfälle', S.failures) then S.failures = not S.failures end
  ui.sameLine(); if ui.checkbox('Log', S.log) then S.log = not S.log end

  ui.separator(); ui.header('Saison')
  if ui.checkbox('Automatisch aus Baujahr des Autos', S.seasonAuto) then S.seasonAuto = not S.seasonAuto; resetAll() end
  if not S.seasonAuto then
    local v, changed = ui.slider('##season', S.season, 1988, 2026, 'Saison %.0f', true)
    if changed then S.season = math.floor(v + 0.5); resetAll() end
  end
  local c0 = cars[0]
  if c0 then ui.text(string.format('Spielerauto: Saison %d, Dirty-Air-Kennlinie %s', c0.season, c0.era)) end

  ui.separator(); ui.header('Dirty Air')
  S.strength = ui.slider('##str', S.strength, 0, 1, 'Stärke Spieler %.2f')
  S.aiStrength = ui.slider('##aistr', S.aiStrength, 0, 1, 'Stärke KI %.2f')
  local m, mc = ui.combo('Modus', S.mode + 1, ui.ComboFlags.None, MODES)
  if mc then S.mode = m - 1; resetAll() end
  if S.mode == 0 then S.aeroShare = ui.slider('##share', S.aeroShare, 0.1, 0.9, 'Abtriebsanteil an der Radlast bei 200 km/h %.2f') end

  ui.separator(); ui.header('Ausfälle')
  S.failMult = ui.slider('##fm', S.failMult, 0, 20, 'Rate x %.1f', 2)
  if c0 then
    local p = getProfile(c0.season)
    local sum = 0
    for _, k in ipairs(FAIL_KEYS) do if FAIL[k] then sum = sum + (p.rates[k] or 0) end end
    ui.text(string.format('Profil %d: %.1f %% pro Auto und Rennen (x %.1f)', p.season, sum, S.failMult))
  end

  ui.separator()
  if ui.checkbox('Autos anzeigen', S.showCars) then S.showCars = not S.showCars end
  if S.showCars then
    local sim = ac.getSim()
    for i = 0, sim.carsCount - 1 do
      local c, car = cars[i], ac.getCar(i)
      if c and car then
        local fails = {}
        for k in pairs(c.active) do fails[#fails + 1] = k end
        ui.text(string.format('%2d %-18s %3.0f km/h  DA %.2f/%.2f  %s', i, tostring(ac.getDriverName(i)):sub(1, 18), car.speedKmh,
          c.front, c.rear, #fails > 0 and table.concat(fails, ',') or ''))
      end
    end
  end
end
