-- Ride Height Monitor (CSP Lua App). Dateiname muss dem Ordnernamen entsprechen:
-- apps/lua/rideheight_monitor/rideheight_monitor.lua
--
-- Zeigt live: Geschwindigkeit, Bodenfreiheit vorn/hinten, Radlasten, daraus gerechneten Abtrieb
-- (Summe der Radlasten minus statische Last) und Federweg. Sammelt zusaetzlich je 10-km/h-Stufe
-- den Mittelwert bei ruhiger Fahrt (wenig Gier, wenig Querbeschleunigung, keine Bremse) und
-- schreibt alles auf Knopfdruck als CSV nach apps/lua/rideheight_monitor/logs/.
--
-- Felder laut lokalem lua-sdk (ac_apps/lib.lua, ac.StateCar): rideHeight[0..1] in m,
-- wheels[i].load in N, wheels[i].suspensionTravel in m, extendedPhysics.
-- Hinweis: car.aeroLiftFront/Rear/aeroDrag liefern im App-Kontext 0 (getestet 2026-10-13),
-- deshalb wird der Abtrieb aus den Radlasten gerechnet.

local G = 9.81
local BIN = 10            -- km/h
local BIN_MAX = 360

local bins = {}           -- [kmh] = {n=..., Summen der Messgroessen}
local status = "Bereit"
local quietOnly = true
local minHf, minHr = 1, 1
local staticLoad = nil    -- Summe der Radlasten im Stand (N), Referenz fuer den Abtrieb
local staticFront = nil   -- Anteil vorn im Stand
local lastKmh, lastRateHr = 0, 0

local FIELDS = { "hf", "hr", "lf", "rf", "lr", "rr", "tf", "tr" }

local function sample(car)
  local w = car.wheels
  return {
    hf = car.rideHeight[0], hr = car.rideHeight[1],
    lf = w[0].load, rf = w[1].load, lr = w[2].load, rr = w[3].load,
    tf = (w[0].suspensionTravel + w[1].suspensionTravel) / 2,
    tr = (w[2].suspensionTravel + w[3].suspensionTravel) / 2,
  }
end

local function downforce(s)
  if not staticLoad then return 0, 0, 0 end
  local front = (s.lf + s.rf - staticLoad * staticFront) / G
  local rear = (s.lr + s.rr - staticLoad * (1 - staticFront)) / G
  return front + rear, front, rear
end

local function isQuiet(car)
  local yaw = math.abs(car.localAngularVelocity.y)
  local lat = math.abs(car.acceleration.x) / G
  return yaw < 0.05 and lat < 0.3 and car.brake < 0.05
end

function script.update(dt)
  local car = ac.getCar(0)
  if not car then return end
  local s = sample(car)

  -- statische Referenz im Stand (einmal, oder nach Reset)
  if car.speedKmh < 1 and (not staticLoad or math.abs(s.lf + s.rf + s.lr + s.rr - staticLoad) > 500) then
    staticLoad = s.lf + s.rf + s.lr + s.rr
    staticFront = (s.lf + s.rf) / staticLoad
  end
  if car.speedKmh < 5 then return end

  if s.hf < minHf then minHf = s.hf end
  if s.hr < minHr then minHr = s.hr end
  if quietOnly and not isQuiet(car) then return end
  local k = math.floor(car.speedKmh / BIN + 0.5) * BIN
  if k < BIN or k > BIN_MAX then return end
  local b = bins[k]
  if not b then
    b = { n = 0 }
    for _, f in ipairs(FIELDS) do b[f] = 0 end
    bins[k] = b
  end
  b.n = b.n + 1
  for _, f in ipairs(FIELDS) do b[f] = b[f] + s[f] end
end

local function binMean(k)
  local b = bins[k]
  if not b or b.n == 0 then return nil end
  local m = {}
  for _, f in ipairs(FIELDS) do m[f] = b[f] / b.n end
  m.n = b.n
  m.df, m.dfF, m.dfR = downforce(m)
  m.bal = m.df > 20 and m.dfF / m.df or 0
  return m
end

local function exportCsv()
  local dir = ac.getFolder(ac.FolderID.ScriptOrigin) .. "/logs"
  io.createDir(dir)
  local path = string.format("%s/%s_%s.csv", dir, ac.getCarID(0) or "car", os.date("%Y%m%d_%H%M%S"))
  local f = io.open(path, "w")
  if not f then status = "Konnte Datei nicht öffnen"; return end
  f:write(string.format("# static_load_N=%.0f static_front_share=%.3f\n", staticLoad or 0, staticFront or 0))
  f:write("kmh,samples,rh_front_mm,rh_rear_mm,downforce_kg,downforce_front_kg,downforce_rear_kg,front_balance,load_lf,load_rf,load_lr,load_rr,travel_front_mm,travel_rear_mm\n")
  local n = 0
  for k = BIN, BIN_MAX, BIN do
    local m = binMean(k)
    if m then
      f:write(string.format("%d,%d,%.1f,%.1f,%.0f,%.0f,%.0f,%.3f,%.0f,%.0f,%.0f,%.0f,%.1f,%.1f\n",
        k, m.n, m.hf * 1000, m.hr * 1000, m.df, m.dfF, m.dfR, m.bal,
        m.lf, m.rf, m.lr, m.rr, m.tf * 1000, m.tr * 1000))
      n = n + 1
    end
  end
  f:close()
  status = string.format("%d Stufen gespeichert: %s", n, path)
end

local function row(label, value)
  ui.text(label)
  ui.sameLine(170)
  ui.text(value)
end

function windowMain(dt)
  local car = ac.getCar(0)
  if not car then ui.text("Kein Auto"); return end
  local s = sample(car)
  local df, dfF, dfR = downforce(s)

  ui.text(car.extendedPhysics and "Extended Physics: aktiv" or "Extended Physics: AUS (Aero Map wirkt nicht)")
  ui.text(staticLoad and string.format("Statische Last: %.0f kg, vorn %.0f %%", staticLoad / G, staticFront * 100)
                    or "Statische Last: noch nicht gemessen (kurz anhalten)")
  ui.separator()
  row("Geschwindigkeit", string.format("%.0f km/h", car.speedKmh))
  row("Bodenfreiheit vorn", string.format("%.1f mm  (min %.1f)", s.hf * 1000, minHf * 1000))
  row("Bodenfreiheit hinten", string.format("%.1f mm  (min %.1f)", s.hr * 1000, minHr * 1000))
  row("Rake (hinten - vorn)", string.format("%.1f mm", (s.hr - s.hf) * 1000))
  ui.separator()
  row("Abtrieb", string.format("%.0f kg  (vorn %.0f, hinten %.0f)", df, dfF, dfR))
  row("Balance vorn", string.format("%.1f %%", df > 20 and dfF / df * 100 or 0))
  row("Radlast VL / VR", string.format("%.0f / %.0f N", s.lf, s.rf))
  row("Radlast HL / HR", string.format("%.0f / %.0f N", s.lr, s.rr))
  row("Federweg vorn / hinten", string.format("%.1f / %.1f mm", s.tf * 1000, s.tr * 1000))
  ui.separator()

  if ui.checkbox("Nur ruhige Geradeausfahrt sammeln", quietOnly) then quietOnly = not quietOnly end
  local n = 0
  for _ in pairs(bins) do n = n + 1 end
  ui.text(string.format("Gesammelte Stufen: %d", n))
  if ui.button("CSV speichern") then exportCsv() end
  ui.sameLine()
  if ui.button("Tabelle leeren") then bins = {}; minHf, minHr = 1, 1; status = "Geleert" end
  ui.sameLine()
  if ui.button("Statik neu messen") then staticLoad = nil end
  ui.textWrapped(status)

  ui.separator()
  ui.text("Mittelwerte (km/h: vorn / hinten mm, Abtrieb kg, Balance, n)")
  for k = BIN, BIN_MAX, BIN do
    local m = binMean(k)
    if m then
      ui.text(string.format("%3d: %5.1f / %5.1f  %5.0f kg  %4.1f %%  %d", k, m.hf * 1000, m.hr * 1000, m.df, m.bal * 100, m.n))
    end
  end
end
