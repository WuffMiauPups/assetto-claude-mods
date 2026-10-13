# Fast Lane Recorder App

Installation: Ordner `fastlane_recorder` nach `assettocorsa/apps/lua/` kopieren. Content Manager erkennt die App nach einem Neustart, dann im Spiel über die App-Leiste aktivieren.

Bedienung: Aufnahme starten, drei bis fünf saubere Runden fahren, Aufnahme stoppen. Die CSV liegt in `apps/lua/fastlane_recorder/logs/`.

Hinweise: Die Spline-Position braucht eine vorhandene `fast_lane.ai` der Strecke, bei Kunos-Strecken ist das immer gegeben. Die Seitenabstände werden nur gefüllt, wenn die CSP-Version die entsprechende Funktion anbietet, sonst stehen dort -1 und das Build-Skript nutzt die Referenz-Linie.
