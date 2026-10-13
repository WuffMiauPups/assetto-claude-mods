---------------------------------Cimmerian F10 Steering Wheel Scriptable Display---------------------------------

--This mod was based on Schmawlik (and SuzQ) code, but modified a lot by me (D3rza) for Cimmerian's F10
--https://www.racedepartment.com/downloads/rss-formula-hybrid-2022-s-scriptable-display.56397/
--Link for the original mod
--
----------My socials----------
--https://www.racedepartment.com/members/d3rza44.1871849/
--https://www.instagram.com/luka_derzic/
--Discord: d3rza (D3rza#9716) (feel free to contact me)
------------------------------
--
--PLEASE DO NOT SHARE OR MODIFY THE MOD WITHOUT ASKING ME
--IF YOU MAKE ANY ADJUSTMENTS OR MODIFY CODE IN ANY WAY PLEASE CREDIT Schmawlik and SuzQ BECAUSE THIS HAPPENED BECAUSE OF THEM
--Version 3.0 - 4-1-2025 - D3rza
--I will make more improvments and try to add new functions and features
-----------------------------------------------------------------------------------------------------------------

require 'src.F10_Display_script_src'

-- Draws displays
local function modeMainDisplay(dt)
	if car.isInPitlane == false then
		if car.splinePosition >= 0.998 or car.splinePosition <= 0.05 and car.lapCount+1 >= 3 then
			drawEndLapDisplay()
		elseif getDisplayValue() == 0 then
			drawSpeedDeltaDisplay()
		elseif getDisplayValue() == 1 then
			drawBatteryDisplay()
		elseif getDisplayValue() == 2 then
			drawSpeedFuelDisplay()
		elseif getDisplayValue() == 3 then
			drawWaterOilTempsDisplay()
		end
	else
		drawInPit()
	end
end

-- Draws brake bias change
local function modeBrakeBias(dt)

	local bbal = math.round(car.brakeBias*100, 1)
	
	drawBackground()
	drawGear()
	
	ui.beginRotation()	
	display.text{pos=vec2(45, 0), letter=vec2(200, 270), text="B", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(315, 0), letter=vec2(200, 270), text="B", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(580, 0), letter=vec2(200, 270), text="A", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(830, 0), letter=vec2(200, 270), text="L", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", bbal/10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", bbal%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(495, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", bbal*10%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
end


local listOfModes = {
    modeMainDisplay,
    modeBrakeBias,
}

local tempModeCount = 1
local currentMode = tonumber(ac.loadDisplayValue("displayMode", 1)) or 1

local lastBrakeBias = car.brakeBias
local lastExtraFState = car.extraF

local tempMode = 1
local timer = 0
local timerReset = 50

local function setDisplayMode()
    local _currentMode = currentMode
    if car.extraF ~= lastExtraFState then
        _currentMode = _currentMode + 1
        if _currentMode > #listOfModes - tempModeCount then
            _currentMode = 1
        end
        ac.saveDisplayValue("displayMode", _currentMode)
        currentMode = _currentMode
    end

    lastExtraFState = car.extraF

    if lastBrakeBias ~= car.brakeBias then
        lastBrakeBias = car.brakeBias
        timer = timerReset
        tempMode = 2
        return tempMode
    else
        if timer > 0 then
            timer = timer - 1
            return tempMode
        else
            return _currentMode
        end
    end
end

function script.update(dt)   
    local displayMode = setDisplayMode()

    listOfModes[displayMode](dt)
end