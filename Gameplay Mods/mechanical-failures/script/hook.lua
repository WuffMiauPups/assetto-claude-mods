
-- >>> mechanical-failures (von tools/install.py angefügt, nicht von Hand ändern)
local __failures = require('failures')
local __originalUpdate = script.update
function script.update(dt)
  if __originalUpdate then __originalUpdate(dt) end
  __failures.update(dt)
end
-- <<< mechanical-failures
