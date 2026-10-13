-- Mechanische Ausfälle (CSP Extended Physics, Modul im Datenordner des Autos)
-- Eingebunden über script.lua (Autos ohne eigenes Script) oder per Hook am Ende des vorhandenen script.lua.
-- Geprüft gegen lua-sdk/ac_car_cphys, CSP 0.3.0-preview649: ac.accessCarPhysics() (gas, requestedGearIndex
-- beschreibbar), ac.overrideEngineTorque, ac.overrideGasInput, ac.setPhysicsValue, ac.setEngineLifeLeft,
-- ac.setTyreInflation(ac.Wheel.*, 0..1), ac.INIConfig.carData, ac.getCarSkinID.
-- Noch offen: Feld für Getriebeschaden ist in ac.StateCarPhysics nur lesbar (gearboxDamage), Setter fehlt.

local M = {}
local DirtyAir = require('dirty_air')
local carPh = ac.accessCarPhysics()

-- ---------- Konfiguration ----------
local cfg = {
  seed = 1, raceLengthMin = 90, multAll = 1.0, log = true,
  rates = { ENGINE = 4, POWER_LOSS = 6, TURBO = 2, GEARBOX = 3, HYDRAULICS = 2, ELECTRICS = 3, BRAKES = 1, PUNCTURE = 5 },
  driver = { ENGINE_MULT = 1, TURBO_MULT = 1, GEARBOX_MULT = 1, ENGINE_MILEAGE_KM = 0 },
}

local function loadConfig()
  local ok, ini = pcall(ac.INIConfig.carData, car.index, 'failures.ini')
  if not ok or not ini then ac.log('[failures] failures.ini nicht lesbar'); return nil end
  cfg.seed = tonumber((ini:get('GLOBAL', 'SEED', '1'):gsub('%D', ''))) or 1
  cfg.raceLengthMin = ini:get('GLOBAL', 'RACE_LENGTH_MIN', 90)
  cfg.multAll = ini:get('GLOBAL', 'MULT_ALL', 1.0)
  cfg.log = ini:get('GLOBAL', 'LOG', 1) == 1
  for k in pairs(cfg.rates) do cfg.rates[k] = ini:get('ERA', k, cfg.rates[k]) end
  local section = 'DRIVER_' .. tostring(ac.getCarSkinID(car.index) or 'default')
  if ini:get(section, 'ENGINE_MULT', -1) == -1 then section = 'DRIVER_default' end
  for k in pairs(cfg.driver) do cfg.driver[k] = ini:get(section, k, cfg.driver[k]) end
  return ini
end

-- ---------- Zufall, reproduzierbar pro Wochenende und Auto ----------
local rngState
local function rng()
  rngState = (rngState * 1103515245 + 12345) % 2147483648
  return rngState / 2147483648
end

-- ---------- Zustand ----------
local state = { active = {}, elapsed = 0, warned = {}, logged = {} }

local function perSecondProbability(ratePercentPerRace, mult)
  local p = ratePercentPerRace / 100 * mult * cfg.multAll
  return p / (cfg.raceLengthMin * 60)
end

local function mileageMult()
  local km = cfg.driver.ENGINE_MILEAGE_KM or 0
  return 1 + math.max(0, km - 800) / 800   -- ab 800 km steigt die Motorrate, bei 1600 km doppelt
end

local function logEvent(kind)
  if cfg.log and not state.logged[kind] then
    state.logged[kind] = true
    ac.log(string.format('[failures] car %d skin %s: %s at %.0fs', car.index, tostring(ac.getCarSkinID(car.index)), kind, state.elapsed))
  end
end

-- ---------- Defekte: jeder hat Warnphase, Verschlechterung, Ausfall ----------
local failures = {}

failures.ENGINE = { mult = function() return cfg.driver.ENGINE_MULT * mileageMult() end,
  apply = function(f, dt)
    f.t = f.t + dt
    if f.t < 20 then                       -- Warnphase: leichter Leistungsverlust, Temperatur steigt
      ac.overrideEngineTorque(carPh.engineTorque and carPh.engineTorque * 0.92 or nil)
    elseif f.t < 45 then                   -- Verschlechterung: Aussetzer
      if math.floor(f.t * 4) % 3 == 0 then carPh.gas = 0 end
    else                                   -- Ausfall
      ac.setEngineLifeLeft(0)
      logEvent('ENGINE')
    end
  end }

failures.POWER_LOSS = { mult = function() return cfg.driver.ENGINE_MULT end,
  apply = function(f, dt)
    f.t = f.t + dt
    local factor = f.t < 10 and 0.95 or (0.70 + 0.15 * rng() * 0)   -- bleibt bei 70 bis 85 Prozent
    if not f.factor then f.factor = 0.70 + 0.15 * rng() end
    if f.t >= 10 then factor = f.factor end
    if carPh.engineTorque then ac.overrideEngineTorque(carPh.engineTorque * factor) end
    if f.t > 10 then logEvent('POWER_LOSS') end
  end }

failures.TURBO = { mult = function() return cfg.driver.TURBO_MULT end,
  apply = function(f, dt)
    f.t = f.t + dt
    local cap = f.t < 15 and 0.85 or 0.55
    ac.overrideGasInput(math.min(carPh.gas, cap))
    if f.t > 15 then logEvent('TURBO') end
  end }

failures.GEARBOX = { mult = function() return cfg.driver.GEARBOX_MULT end,
  apply = function(f, dt)
    f.t = f.t + dt
    if not f.deadGear then f.deadGear = 2 + math.floor(rng() * 5) end   -- ein Gang zwischen 1 und 5 fällt aus
    if f.t > 10 and carPh.requestedGearIndex == f.deadGear then
      carPh.requestedGearIndex = 1                                     -- Neutral statt des defekten Gangs
      logEvent('GEARBOX')
    end
    -- gearboxDamage ist in ac.StateCarPhysics nur lesbar; dauerhafter Ausfall über Neutral-Zwang ab 120 s
    if f.t > 120 then carPh.requestedGearIndex = 1 end
  end }

failures.HYDRAULICS = { mult = function() return 1 end,
  apply = function(f, dt)
    f.t = f.t + dt
    local ratio = f.t < 20 and 1.1 or 1.6
    if ac.CarPhysicsValueID and ac.CarPhysicsValueID.SteerRatio then
      ac.setPhysicsValue(ac.CarPhysicsValueID.SteerRatio, (f.baseRatio or 12) * ratio)   -- Basiswert aus car.ini lesen
    end
    if f.t > 20 then logEvent('HYDRAULICS') end
  end }

failures.ELECTRICS = { mult = function() return 1 end,
  apply = function(f, dt)
    f.t = f.t + dt
    local period = f.t < 30 and 6 or 2
    if (f.t % period) < 0.15 then carPh.gas = 0 end
    if f.t > 90 then ac.setEngineLifeLeft(0); logEvent('ELECTRICS') end
  end }

failures.BRAKES = { mult = function() return 1 end,
  apply = function(f, dt)
    f.t = f.t + dt
    if ac.CarPhysicsValueID and ac.CarPhysicsValueID.BrakeTorque then
      local factor = f.t < 30 and 0.85 or 0.6
      ac.setPhysicsValue(ac.CarPhysicsValueID.BrakeTorque, (f.baseTorque or 4000) * factor)   -- Basiswert aus brakes.ini
      ac.setPhysicsValue(ac.CarPhysicsValueID.BrakeFrontBias, (f.baseBias or 0.6) + 0.08)
    end
    if f.t > 30 then logEvent('BRAKES') end
  end }

failures.PUNCTURE = { mult = function() return 1 end,
  apply = function(f, dt)
    f.t = f.t + dt
    if not f.wheel then f.wheel = math.floor(rng() * 4) end           -- 0..3 = ac.Wheel.FrontLeft..RearRight
    ac.setTyreInflation(f.wheel, f.t < 8 and 0.6 or 0)                 -- 8 s Druckverlust, dann geplatzt
    if f.t > 8 then logEvent('PUNCTURE') end
  end }

-- ---------- Hauptschleife ----------
local initialized = false
local function init()
  local ini = loadConfig()
  DirtyAir.init(ini)
  rngState = (cfg.seed * 7919 + (car.index + 1) * 104729) % 2147483648
  initialized = true
end

function M.update(dt)
  if not initialized then init() end
  if sim and sim.isReplayActive then return end
  DirtyAir.update(dt)
  state.elapsed = state.elapsed + dt

  -- nur im Rennen und nach dem Start würfeln; im Training und Quali mit halber Rate
  local sessionMult = 1.0
  if sim and sim.raceSessionType ~= ac.SessionType.Race then sessionMult = 0.5 end

  for name, def in pairs(failures) do
    if not state.active[name] then
      local p = perSecondProbability(cfg.rates[name] or 0, def.mult() * sessionMult) * dt
      if rng() < p then state.active[name] = { t = 0 } end
    end
  end
  for name, f in pairs(state.active) do failures[name].apply(f, dt) end
end

function M.reset()
  state = { active = {}, elapsed = 0, warned = {}, logged = {} }
  initialized = false
  DirtyAir.reset()
end

return M
