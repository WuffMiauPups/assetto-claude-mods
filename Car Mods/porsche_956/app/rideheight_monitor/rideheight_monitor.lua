-- Ride Height Monitor (CSP Lua App). Dateiname muss dem Ordnernamen entsprechen:
-- apps/lua/rideheight_monitor/rideheight_monitor.lua
--
-- Zeigt live: Geschwindigkeit, Bodenfreiheit vorn/hinten, Aero-Beiwerte (Cl*A vorn/hinten, Cd*A),
-- daraus gerechneten Abtrieb, Radlasten und Federweg. Sammelt zusätzlich je 10-km/h-Stufe den
-- zuletzt gesehenen Wert bei ruhiger Fahrt (wenig Gier, wenig Querbeschleunigung) und schreibt
-- alles auf Knopfdruck als CSV nach apps/lua/rideheight_monitor/logs/.
--
-- Felder laut lokalem lua-sdk (ac_apps/lib.lua, ac.StateCar): rideHeight[0..1] in m,
-- aeroLiftFront, aeroLiftRear, aeroDrag (Beiwerte, Fläche enthalten), wheels[i].load in N,
-- wheels[i].suspensionTravel in m, extendedPhysics.

local RHO = 1.225
local G = 9.81
local BIN = 10            -- km/h
local BIN_MAX = 360

local bins = {}           -- [kmh] = {hf, hr, clf, clr, cd, df_kg, bal, loads...}
local status = "Bereit"
local quietOnly = true    -- nur ruhige Geradeausfahrt in die Tabelle übernehmen
local minHf, minHr = 1, 1 -- bisheriges Minimum der Bodenfreiheit (Kuppen, Bremsen)

local function q(vKmh)
  local v = vKmh / 3.6
  return 0.5 * RHO * v * v
end

local function sample(car)
  local hf = car.rideHeight[0]
  local hr = car.rideHeight[1]
  local clf = -car.aeroLiftFront     -- CSP: negativ = Abtrieb, hier als positiver Abtrieb
  local clr = -car.aeroLiftRear
  local cd = car.aeroDrag
  local qd = q(car.speedKmh)
  local dfF = clf * qd / G
  local dfR = clr * qd / G
  local df = dfF + dfR
  local bal = df > 1 and dfF / df or 0
  return {
    kmh = car.speedKmh, hf = hf, hr = hr, clf = clf, clr = clr, cd = cd,
    df = df, dfF = dfF, dfR = dfR, bal = bal, drag = cd * qd / G,
    lf = car.wheels[0].load, rf = car.wheels[1].load, lr = car.wheels[2].load, rr = car.wheels[3].load,
    tf = (car.wheels[0].suspensionTravel + car.wheels[1].suspensionTravel) / 2,
    tr = (car.wheels[2].suspensionTravel + car.wheels[3].suspensionTravel) / 2,
  }
end

local function isQuiet(car)
  local yaw = math.abs(car.localAngularVelocity.y)
  local lat = math.abs(car.acceleration.x) / G
  return yaw < 0.05 and lat < 0.3 and car.brake < 0.05
end

function script.update(dt)
  local car = ac.getCar(0)
  if not car or car.speedKmh < 5 then return end
  local s = sample(car)
  if s.hf < minHf then minHf = s.hf end
  if s.hr < minHr then minHr = s.hr end
  if quietOnly and not isQuiet(car) then return end
  local k = math.floor(car.speedKmh / BIN + 0.5) * BIN
  if k >= BIN and k <= BIN_MAX then bins[k] = s end
end

local function exportCsv()
  local dir = ac.getFolder(ac.FolderID.ScriptOrigin) .. "/logs"
  io.createDir(dir)
  local car = ac.getCar(0)
  local name = car and ac.getCarID(0) or "car"
  local path = string.format("%s/%s_%s.csv", dir, name, os.date("%Y%m%d_%H%M%S"))
  local f = io.open(path, "w")
  if not f then status = "Konnte Datei nicht öffnen"; return end
  f:write("kmh,rh_front_mm,rh_rear_mm,cla_front,cla_rear,cda,downforce_kg,front_balance,drag_kg,load_lf,load_rf,load_lr,load_rr,travel_front_mm,travel_rear_mm\n")
  local n = 0
  for k = BIN, BIN_MAX, BIN do
    local s = bins[k]
    if s then
      f:write(string.format("%d,%.1f,%.1f,%.3f,%.3f,%.3f,%.0f,%.3f,%.0f,%.0f,%.0f,%.0f,%.0f,%.1f,%.1f\n",
        k, s.hf * 1000, s.hr * 1000, s.clf, s.clr, s.cd, s.df, s.bal, s.drag,
        s.lf, s.rf, s.lr, s.rr, s.tf * 1000, s.tr * 1000))
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

  ui.text(car.extendedPhysics and "Extended Physics: aktiv" or "Extended Physics: AUS (Aero Map wirkt nicht)")
  ui.separator()
  row("Geschwindigkeit", string.format("%.0f km/h", s.kmh))
  row("Bodenfreiheit vorn", string.format("%.1f mm  (min %.1f)", s.hf * 1000, minHf * 1000))
  row("Bodenfreiheit hinten", string.format("%.1f mm  (min %.1f)", s.hr * 1000, minHr * 1000))
  row("Rake (hinten - vorn)", string.format("%.1f mm", (s.hr - s.hf) * 1000))
  ui.separator()
  row("Cl*A vorn / hinten", string.format("%.3f / %.3f", s.clf, s.clr))
  row("Cl*A gesamt", string.format("%.3f", s.clf + s.clr))
  row("Cd*A", string.format("%.3f", s.cd))
  row("Abtrieb", string.format("%.0f kg  (vorn %.0f, hinten %.0f)", s.df, s.dfF, s.dfR))
  row("Balance vorn", string.format("%.1f %%", s.bal * 100))
  row("Widerstand", string.format("%.0f kg", s.drag))
  ui.separator()
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
  if ui.button("Min zurücksetzen") then minHf, minHr = 1, 1 end
  ui.textWrapped(status)

  ui.separator()
  ui.text("Tabelle (km/h: vorn / hinten mm, Abtrieb kg, Balance)")
  for k = BIN, BIN_MAX, BIN do
    local b = bins[k]
    if b then
      ui.text(string.format("%3d: %5.1f / %5.1f  %5.0f kg  %4.1f %%", k, b.hf * 1000, b.hr * 1000, b.df, b.bal * 100))
    end
  end
end
