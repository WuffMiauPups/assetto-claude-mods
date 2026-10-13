-- Einstieg für Autos ohne eigenes Extended-Physics-Script (von install.py kopiert).
-- Autos mit eigenem script.lua bekommen stattdessen den Hook-Block am Dateiende.
local mod = require('failures')
function script.update(dt) mod.update(dt) end
function script.reset() mod.reset() end
