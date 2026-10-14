-- Mechanische Ausfälle: Modul für CSP Extended Physics (script.lua im Datenordner des Autos).
-- Alle API-Namen gegen extension/internal/lua-sdk/ac_car_cphys (CSP 0.3.0-preview649) geprüft:
--   ac.accessCarPhysics()            Felder gas, brake, steer, rpm, requestedGearIndex, wheels[i].inflation
--   ac.setEngineLifeLeft(0)          engineLifeLeft selbst ist nur lesbar
--   ac.overrideEngineTorque(nm)      ersetzt die Kurve durch einen Punkt, deshalb jeden Schritt aus power.lut
--   ac.overrideTurboBoost(i, boost)  nil setzt zurück
--   ac.setTyreInflation(wheel, psi)  0 lässt den Reifen platzen
--   ac.overrideBrakesTorque(wheel, nm, handbrake)  einmal gerufen, bleibt die Originalbremse aus
--   ac.setBrakeBias(b), ac.setGearsGrinding(bool), ac.setWaterTemperature(t, disableOriginal)
--   ac.accessCarDamper(i)            Dämpferwerte schreibbar
--   ac.INIConfig.carData(idx, name)  :get(section, key, default), Abschnitte in .sections
--   car:skin()                       Methode, kein Feld
-- Nicht vorhanden in diesem SDK: SteerRatio als Physikwert, gearboxDamage schreibbar. Ersatz siehe unten.

local Failures = {}

local carPh = ac.accessCarPhysics()
local powerLut = ac.DataLUT11.carData(car.index, 'power.lut')
local brakesIni = ac.INIConfig.carData(car.index, 'brakes.ini')
local baseBrakeTorque = brakesIni:get('DATA', 'MAX_TORQUE', 4000)
local baseFrontShare = brakesIni:get('DATA', 'FRONT_SHARE', 0.6)

-- ---------- Konfiguration ----------
local RATE_KEYS = { 'ENGINE', 'POWER_LOSS', 'TURBO', 'GEARBOX', 'HYDRAULICS', 'ELECTRICS', 'BRAKES', 'PUNCTURE', 'SUSPENSION', 'COOLING' }

local cfg = {
  seed = 1, raceLengthMin = 90, multAll = 1.0, log = true, message = true,
  rates = {},
  driver = { ENGINE_MULT = 1, TURBO_MULT = 1, GEARBOX_MULT = 1, ENGINE_MILEAGE_KM = 0 },
  forceKind = nil, forceAt = 0,   -- [TEST] FORCE=ENGINE, FORCE_AT=20: Defekt fest auslösen, für Tests
}

local function loadConfig()
  local ini = ac.INIConfig.carData(car.index, 'failures.ini')
  if not ini or not ini.sections or not ini.sections['ERA'] then
    ac.warn('[failures] failures.ini fehlt oder hat keinen Abschnitt ERA, Script bleibt passiv')
    return false
  end
  local seedRaw = tostring(ini:get('GLOBAL', 'SEED', '1')):gsub('%D', '')
  cfg.seed = tonumber(seedRaw) or 1
  cfg.raceLengthMin = ini:get('GLOBAL', 'RACE_LENGTH_MIN', 90)
  cfg.multAll = ini:get('GLOBAL', 'MULT_ALL', 1.0)
  cfg.log = ini:get('GLOBAL', 'LOG', 1) == 1
  cfg.message = ini:get('GLOBAL', 'MESSAGE', 1) == 1
  for _, k in ipairs(RATE_KEYS) do cfg.rates[k] = ini:get('ERA', k, 0) end
  local section = 'DRIVER_' .. tostring(car:skin() or 'default')
  if not ini.sections[section] then section = 'DRIVER_default' end
  for k in pairs(cfg.driver) do cfg.driver[k] = ini:get(section, k, cfg.driver[k]) end
  if ini.sections['TEST'] then
    local kind = ini:get('TEST', 'FORCE', '')
    if kind ~= '' then cfg.forceKind, cfg.forceAt = kind, ini:get('TEST', 'FORCE_AT', 20) end
  end
  return true
end

-- ---------- Zufall, reproduzierbar pro Wochenende und Auto ----------
local rngState = 1
local function rng()
  rngState = (rngState * 1103515245 + 12345) % 2147483648
  return rngState / 2147483648
end

-- ---------- Zustand ----------
local state = { active = {}, elapsed = 0, logged = {}, terminal = false }

local function perSecondProbability(ratePercentPerRace, mult)
  return ratePercentPerRace / 100 * mult * cfg.multAll / (cfg.raceLengthMin * 60)
end

local function mileageMult()
  local km = cfg.driver.ENGINE_MILEAGE_KM or 0
  return 1 + math.max(0, km - 800) / 800   -- ab 800 km steigt die Motorrate, bei 1600 km doppelt
end

local function announce(kind, text)
  if state.logged[kind] then return end
  state.logged[kind] = true
  if cfg.log then
    ac.log(string.format('[failures] car %d skin %s: %s at %.0fs', car.index, tostring(car:skin()), kind, state.elapsed))
  end
  if cfg.message and car.index == sim.focusedCar then ac.setMessage('Defekt: ' .. kind, text or '') end
end

local function torqueFactor(factor)
  ac.overrideEngineTorque(powerLut:get(carPh.rpm) * factor)
end

local function killEngine(kind)
  ac.overrideEngineTorque(0 / 0)   -- Override aufheben, dann Motor sterben lassen
  ac.setEngineLifeLeft(0)
  state.terminal = true
  announce(kind, 'Motor aus')
end

-- ---------- Defekte: Warnphase, Verschlechterung, Ausfall ----------
local failures = {}

failures.ENGINE = { mult = function() return cfg.driver.ENGINE_MULT * mileageMult() end,
  apply = function(f, dt)
    if f.t < 20 then torqueFactor(0.92)                                   -- Warnphase: leichter Leistungsverlust
    elseif f.t < 45 then                                                  -- Verschlechterung: Aussetzer
      torqueFactor(0.85)
      if math.floor(f.t * 4) % 3 == 0 then carPh.gas = 0 end
    else killEngine('ENGINE') end
  end }

failures.POWER_LOSS = { mult = function() return cfg.driver.ENGINE_MULT end,
  apply = function(f, dt)
    if not f.factor then f.factor = 0.70 + 0.15 * rng() end               -- bleibt bei 70 bis 85 Prozent
    torqueFactor(f.t < 10 and 0.95 or f.factor)
    if f.t > 10 then announce('POWER_LOSS', string.format('Leistung %.0f %%', f.factor * 100)) end
  end }

failures.TURBO = { mult = function() return cfg.driver.TURBO_MULT end,
  apply = function(f, dt)
    local cap = f.t < 15 and 0.85 or 0.55
    if car.turboCount and car.turboCount > 0 then
      for i = 0, car.turboCount - 1 do ac.overrideTurboBoost(i, car.turboBoosts and car.turboBoosts[i] * cap or 0) end
    else
      ac.overrideGasInput(math.min(carPh.gas, cap))                       -- Saugmotor: Gas begrenzen
    end
    if f.t > 15 then announce('TURBO', 'Ladedruck weg') end
  end }

failures.GEARBOX = { mult = function() return cfg.driver.GEARBOX_MULT end,
  apply = function(f, dt)
    if not f.deadGear then f.deadGear = 3 + math.floor(rng() * 4) end     -- Index 3 bis 6 = 2. bis 5. Gang
    if f.t > 120 then                                                     -- Ausfall: nur noch Neutral
      carPh.requestedGearIndex = 1
      ac.setGearsGrinding(true)
      state.terminal = true
      announce('GEARBOX', 'Getriebe fest')
    elseif f.t > 10 and carPh.requestedGearIndex == f.deadGear then       -- ein Gang fällt aus
      carPh.requestedGearIndex = 1
      ac.setGearsGrinding(true)
      announce('GEARBOX', string.format('%d. Gang fehlt', f.deadGear - 1))
    else
      ac.setGearsGrinding(false)
    end
  end }

-- Kein SteerRatio-Zugriff im SDK: Lenkeingabe wird gedämpft, wirkt für Spieler und KI
failures.HYDRAULICS = { mult = function() return 1 end,
  apply = function(f, dt)
    local factor = f.t < 20 and 0.9 or 0.65
    carPh.steer = carPh.steer * factor
    if f.t > 20 then announce('HYDRAULICS', 'Servolenkung ausgefallen') end
  end }

failures.ELECTRICS = { mult = function() return 1 end,
  apply = function(f, dt)
    local period = f.t < 30 and 6 or 2
    if (f.t % period) < 0.15 then carPh.gas = 0 end
    if f.t > 90 then killEngine('ELECTRICS') end
  end }

failures.BRAKES = { mult = function() return 1 end,
  apply = function(f, dt)
    local factor = f.t < 30 and 0.85 or 0.6
    local bias = math.min(0.9, (car.brakeBias > 0 and car.brakeBias or baseFrontShare) + 0.08)
    local total = baseBrakeTorque * carPh.brake * factor
    ac.overrideBrakesTorque(0, total * bias, 0); ac.overrideBrakesTorque(1, total * bias, 0)
    ac.overrideBrakesTorque(2, total * (1 - bias), 0); ac.overrideBrakesTorque(3, total * (1 - bias), 0)
    ac.setBrakeBias(bias)                                                 -- greift auch, falls das Auto die neue Bremse nutzt
    if f.t > 30 then announce('BRAKES', 'Bremsleistung sinkt') end
  end }

failures.PUNCTURE = { mult = function() return 1 end,
  apply = function(f, dt)
    if not f.wheel then
      f.wheel = math.floor(rng() * 4)
      f.basePressure = carPh.wheels[f.wheel].inflation
    end
    if f.t < 8 then
      ac.setTyreInflation(f.wheel, f.basePressure * (1 - 0.05 * f.t))     -- schleichender Druckverlust
    else
      ac.setTyreInflation(f.wheel, 0)
      announce('PUNCTURE', 'Reifen geplatzt')
    end
  end }

-- Ein Dämpfer verliert seine Wirkung, die Ecke wird unruhig
failures.SUSPENSION = { mult = function() return 1 end,
  apply = function(f, dt)
    if not f.wheel then f.wheel = math.floor(rng() * 4) end
    local d = ac.accessCarDamper(f.wheel)
    local factor = f.t < 15 and 0.6 or 0.1
    if not f.base then f.base = { d.reboundSlow, d.reboundFast, d.bumpSlow, d.bumpFast } end
    d.reboundSlow, d.reboundFast = f.base[1] * factor, f.base[2] * factor
    d.bumpSlow, d.bumpFast = f.base[3] * factor, f.base[4] * factor
    if f.t > 15 then announce('SUSPENSION', 'Dämpfer defekt') end
  end }

-- Wassertemperatur steigt, Motor stirbt nach drei Minuten
failures.COOLING = { mult = function() return 1 end,
  apply = function(f, dt)
    if not f.base then f.base = carPh.waterTemperature end
    ac.setWaterTemperature(f.base + f.t * 0.3, true)                      -- plus 18 Grad pro Minute
    if f.t > 60 then torqueFactor(0.9) end
    if f.t > 180 then killEngine('COOLING') end
  end }

-- ---------- Hauptschleife ----------
local initialized, enabled = false, false

function Failures.init()
  enabled = loadConfig()
  rngState = (cfg.seed * 7919 + (car.index + 1) * 104729) % 2147483648
  state = { active = {}, elapsed = 0, logged = {}, terminal = false }
  initialized = true
end

function Failures.reset() initialized = false end

function Failures.update(dt)
  if not initialized then Failures.init() end
  if not enabled or sim.isReplayActive then return end
  state.elapsed = state.elapsed + dt

  local sessionMult = sim.raceSessionType == ac.SessionType.Race and 1.0 or 0.5
  if not state.terminal then
    for _, name in ipairs(RATE_KEYS) do
      local def = failures[name]
      if def and not state.active[name] then
        local p = perSecondProbability(cfg.rates[name] or 0, def.mult() * sessionMult) * dt
        if rng() < p then state.active[name] = { t = 0 } end
      end
    end
    if cfg.forceKind and failures[cfg.forceKind] and not state.active[cfg.forceKind] and state.elapsed >= cfg.forceAt then
      state.active[cfg.forceKind] = { t = 0 }
      ac.log('[failures] TEST: ' .. cfg.forceKind .. ' erzwungen')
    end
  end
  for name, f in pairs(state.active) do
    f.t = f.t + dt
    failures[name].apply(f, dt)
  end
  ac.debug('failures active', next(state.active) and table.concat((function()
    local t = {}; for k in pairs(state.active) do t[#t + 1] = k end; return t end)(), ',') or 'none')
end

return Failures
