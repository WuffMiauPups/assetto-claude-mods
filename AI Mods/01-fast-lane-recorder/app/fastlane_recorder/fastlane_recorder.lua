-- Fast Lane Recorder (CSP Lua App). Dateiname muss dem Ordnernamen entsprechen: apps/lua/fastlane_recorder/fastlane_recorder.lua
-- Schreibt pro Frame eine Zeile: t, lap, spline, x, y, z, speed, gas, brake, steer, yaw_rate, track_left, track_right
-- Ausgabe: apps/lua/fastlane_recorder/logs/<track>_<datum>.csv

local recording = false
local file = nil
local rows = 0
local startTime = 0
local lastLap = -1
local status = "Bereit"

local function logPath()
  local sim = ac.getSim()
  local track = ac.getTrackID() or "track"
  local layout = ac.getTrackLayout and ac.getTrackLayout() or ""
  if layout ~= "" then track = track .. "_" .. layout end
  local stamp = os.date("%Y%m%d_%H%M%S")
  local dir = ac.getFolder(ac.FolderID.ScriptOrigin) .. "/logs"
  io.createDir(dir)
  return string.format("%s/%s_%s.csv", dir, track, stamp)
end

local function startRecording()
  local path = logPath()
  file = io.open(path, "w")
  if not file then status = "Konnte Datei nicht öffnen"; return end
  file:write("t,lap,spline,x,y,z,speed,gas,brake,steer,yaw_rate,track_left,track_right\n")
  rows = 0
  startTime = os.clock()
  lastLap = -1
  recording = true
  status = "Aufnahme: " .. path
end

local function stopRecording()
  if file then file:close(); file = nil end
  recording = false
  status = string.format("Gestoppt, %d Zeilen", rows)
end

-- Abstand zu den Streckenrändern über die AI-Spline-Seitenangaben
local function trackSides(car)
  local sides = ac.getTrackAISplineSides and ac.getTrackAISplineSides(car.splinePosition)
  if sides then return sides.x, sides.y end
  return -1, -1
end

function script.update(dt)
  if not recording or not file then return end
  local car = ac.getCar(0)
  if not car then return end
  local p = car.position
  local v = car.velocity
  local yawRate = car.angularVelocity and car.angularVelocity.y or 0
  local left, right = trackSides(car)
  local lap = car.lapCount or 0
  if lap ~= lastLap then lastLap = lap end
  file:write(string.format("%.4f,%d,%.6f,%.3f,%.3f,%.3f,%.2f,%.3f,%.3f,%.4f,%.4f,%.2f,%.2f\n",
    os.clock() - startTime, lap, car.splinePosition, p.x, p.y, p.z,
    v:length() * 3.6, car.gas, car.brake, car.steer, yawRate, left, right))
  rows = rows + 1
  if rows % 600 == 0 then file:flush() end
end

function windowMain(dt)
  ui.text(status)
  ui.text(string.format("Zeilen: %d", rows))
  local car = ac.getCar(0)
  if car then
    ui.text(string.format("Runde %d  Spline %.3f  %.0f km/h", car.lapCount or 0, car.splinePosition, car.speedKmh))
  end
  ui.separator()
  if not recording then
    if ui.button("Aufnahme starten", vec2(140, 30)) then startRecording() end
  else
    if ui.button("Aufnahme stoppen", vec2(140, 30)) then stopRecording() end
  end
  ui.sameLine()
  ui.text("Fahre 3 bis 5 saubere Runden.")
end
