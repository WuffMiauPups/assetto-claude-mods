-- Minimales Physik-Script für Autos ohne eigenes script.lua.
-- Hat das Auto bereits ein script.lua, fügt tools/install.py stattdessen den Block aus script/hook.lua an.
local Failures = require('failures')

function script.update(dt)
  Failures.update(dt)
end
