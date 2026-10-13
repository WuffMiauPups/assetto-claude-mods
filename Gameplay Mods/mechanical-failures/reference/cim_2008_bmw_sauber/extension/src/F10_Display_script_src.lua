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

-- Draws background
function drawBackground()
	
	display.rect{pos= vec2 (0,0) , size = vec2(1000,1000),color = rgbm(0,0,0,0.87) }
	
	display.text{pos=vec2(397, 335), letter=vec2(232, 353), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	
	ui.beginRotation()
	display.text{pos=vec2(0, 0), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(260, 0), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(525, 0), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(780, 0), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(0.3,0.3,0.3,0.15)}
	ui.endRotation(270, vec2(0,0))
end

-- Draws the current gear
function drawGear()

    local gear = car.gear
	local x

    if gear == -1 then
        gear = "R"
		x = 0
    elseif gear == 0 then
        gear = "N"
		x = 0
	else
		x = 67
    end

	display.text{pos=vec2(330+x, 335), letter=vec2(232, 353), text=gear, font="36_big", color=rgbm(1,0,0,1)}
end

-- Draws the speed of the car in km/h
function drawSpeed()

	local speed = car.poweredWheelsSpeed
	
	if speed < 10 then
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", speed), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif speed >= 10 and speed < 100 then
		ui.beginRotation()
		display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", speed/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", speed%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif speed > 100 then
		ui.beginRotation()
		display.text{pos=vec2(260, 0), letter=vec2(200, 270), text=string.format("%0d", speed/100), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", (speed/10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", speed%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end	
end

-- Draws delta time
function drawDelta()

	local delta = math.round(car.performanceMeter, 2)

	if delta < 0 and delta > -10 then
        ui.beginRotation()
		display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="-", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", math.abs(delta)), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (math.abs(delta)*10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", (math.abs(delta)*100)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
    elseif delta > 0 and delta < 10 then
        ui.beginRotation()
		display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="+", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", delta), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (delta*10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", (delta*100)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif delta >= 10 then
		ui.beginRotation()
		display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="+", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif delta <= -10 then
		ui.beginRotation()
		display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="-", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
    else
        ui.beginRotation()
		display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="+", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="0", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
    end
end

-- Draws current battery level
function drawBattery()
	
	local battery = math.round(car.kersCharge*100,0)
	
	ui.beginRotation()	
	display.text{pos=vec2(45, 0), letter=vec2(200, 270), text="B", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	if battery < 10 then
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", battery), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif battery >= 10 and battery < 100 then
		ui.beginRotation()
		display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", battery/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", battery%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif battery >= 100 then
		ui.beginRotation()
		display.text{pos=vec2(260, 0), letter=vec2(200, 270), text=string.format("%0d", battery/100), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", (battery/10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", battery%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end	
	
end

-- Draws available energy this lap
function drawBatteryPerLap()
	
	local batteryPerLap = math.round(((1-car.kersLoad)*100),0)
	
	ui.beginRotation()	
	display.text{pos=vec2(40, 700), letter=vec2(200, 270), text="A", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	if batteryPerLap < 10 then
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", batteryPerLap), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif batteryPerLap >= 10 and batteryPerLap < 100 then
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", batteryPerLap/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", batteryPerLap%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif batteryPerLap >= 100 then
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", batteryPerLap/100), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (batteryPerLap/10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", batteryPerLap%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end
end

-- Draws the remaining fuel in liters
function drawFuelRemaining()
	
	local fuel = car.fuel
	
	ui.beginRotation()
	display.text{pos=vec2(40, 700), letter=vec2(200, 270), text="F", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	if fuel < 10 then
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", fuel), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif fuel >= 10 and fuel < 100 then
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", fuel/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", fuel%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif fuel >= 100 then
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", fuel/100), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (fuel/10)%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", fuel%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end
end

-- Draws temperature of water
function drawWaterTemp()
	
	local waterTemp = car.waterTemperature
	
	ui.beginRotation()
	display.text{pos=vec2(45, 0), letter=vec2(200, 270), text="W", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", waterTemp/10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", waterTemp%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
end

-- Draws temperature of oil
function drawOilTemp()
	
	local oilTemp = car.oilTemperature
	
	ui.beginRotation()
	display.text{pos=vec2(40, 700), letter=vec2(200, 270), text="O", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	if oilTemp < 100 then
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", oilTemp/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", oilTemp%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	elseif oilTemp >= 100 then
		ui.beginRotation()
		display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", oilTemp/100), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", oilTemp/10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", oilTemp%10), font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end
end

function drawLastLapTime()

	local lastLapTime = car.previousLapTimeMs
	
	ui.beginRotation()
	display.text{pos=vec2(0, 0), letter=vec2(200, 270), text=string.format("%0d", ((lastLapTime/1000)%60)/10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(260, 0), letter=vec2(200, 270), text=string.format("%0d", ((lastLapTime/1000)%60)%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(215, 10), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(525, 0), letter=vec2(200, 270), text=string.format("%0d", (lastLapTime%1000)/100), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(780, 0), letter=vec2(200, 270), text=string.format("%0d", ((lastLapTime%1000)/10)%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
end

local prevBestTime = 0
local newBestTime = 0

function drawEndLapDelta()

	if car.previousLapTimeMs > car.bestLapTimeMs then
		deltaNum = (car.previousLapTimeMs - car.bestLapTimeMs)/1000
		
		if (deltaNum) < 10 then
			ui.beginRotation()
			display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="+", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", deltaNum), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (deltaNum*10)%10), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", (deltaNum*100)%10), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
		elseif (deltaNum) >= 10 then
			ui.beginRotation()
			display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="+", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
		end
    else
		local lapTime = car.previousLapTimeMs

		if lapTime < newBestTime or newBestTime == 0 then
			prevBestTime = newBestTime
			newBestTime = lapTime
			
		end
		local lapTimeDelta = (newBestTime - prevBestTime)/1000
		
		if (lapTimeDelta) <= -10 then
			ui.beginRotation()
			display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="-", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(250, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(540, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(780, 700), letter=vec2(200, 270), text="9", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
		else
			ui.beginRotation()
			display.text{pos=vec2(0, 700), letter=vec2(200, 270), text="-", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", math.abs(lapTimeDelta)), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (math.abs(lapTimeDelta)*10)%10), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(780, 700), letter=vec2(200, 270), text=string.format("%0d", (math.abs(lapTimeDelta)*100)%10), font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
		end
	end
end

-- Draws speed and rpm for launch
function drawLaunch()

	local rpm = car.rpm

	ui.beginRotation()
	display.text{pos=vec2(0, 700), letter=vec2(200, 270), text=string.format("%0d", rpm/10000), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(250, 700), letter=vec2(200, 270), text=string.format("%0d", (rpm/1000)%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(205, 710), letter=vec2(130, 200), text=".", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(540, 700), letter=vec2(200, 270), text=string.format("%0d", (rpm/100)%10), font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
	
	ui.beginRotation()
	display.text{pos=vec2(827, 700), letter=vec2(200, 270), text="K", font="36_big", color=rgbm(1,0,0,1)}
	ui.endRotation(270, vec2(0,0))
end

-- Changes value of variable for extraD and extraE to change displays
local lastDisplayStateN = car.extraD
local lastDisplayStateP = car.extraE
local current_mode = 0

function getDisplayValue()

	local maxDisplayValue = 4

	if car.extraD ~= lastDisplayStateN then
		current_mode = current_mode + 1
	end
	if car.extraE ~= lastDisplayStateP then
		current_mode = current_mode - 1
	end
	lastDisplayStateN = car.extraD
	lastDisplayStateP = car.extraE
	
	if current_mode == maxDisplayValue then
		current_mode = 0
	end
	if current_mode == -1 then
		current_mode = maxDisplayValue - 1
	end
	
	return current_mode
end

-- Draws display for pits
function drawInPit()
	
	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		if (math.floor((ac.getSim().sessionTimeLeft) / 450) % 2) == 0 then
			drawSpeed()
			ui.beginRotation()
			display.text{pos=vec2(295, 715), letter=vec2(200, 270), text="P", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(585, 715), letter=vec2(200, 270), text="I", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
			
			ui.beginRotation()
			display.text{pos=vec2(830, 695), letter=vec2(200, 290), text="T", font="36_big", color=rgbm(1,0,0,1)}
			ui.endRotation(270, vec2(0,0))
		end
	end
end

-- Draws main display (#1) Speed and Delta
function drawSpeedDeltaDisplay()
	
	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		drawSpeed()
		drawDelta()
	end
end

-- Draws secondary display (#2) Battery and Battery per lap
function drawBatteryDisplay()
	
	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		drawBattery()
		drawBatteryPerLap()
	end
end

-- Draws secondary display (#3) Speed and Fuel
function drawSpeedFuelDisplay()

	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		drawSpeed()
		drawFuelRemaining()
	end
end

-- Draws secondary display (#4) Water and Oil temps
function drawWaterOilTempsDisplay()
	
	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		drawWaterTemp()
		drawOilTemp()
	end
end

-- Draws display at the end of lap
function drawEndLapDisplay()

	drawBackground()
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	elseif car.clutch == 0 and car.gear < 3 then
		drawLaunchDisplay()
	else
		drawLastLapTime()
		drawEndLapDelta()
	end
end

-- Draws launch display
function drawLaunchDisplay()
	
	drawGear()
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		drawAntiStallDisplay()
	else
		drawSpeed()
		drawLaunch()
	end
end

-- Draws antistall display
function drawAntiStallDisplay()
    
	if (math.floor((ac.getSim().sessionTimeLeft) / 450) % 2) == 0 then
		ui.beginRotation()	
		display.text{pos=vec2(42, -5), letter=vec2(200, 270), text="A", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(315, -5), letter=vec2(200, 270), text="N", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(575, -25), letter=vec2(200, 290), text="T", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(830, -5), letter=vec2(200, 270), text="I", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(40, 700), letter=vec2(200, 270), text="S", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(295, 680), letter=vec2(200, 290), text="T", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(585, 700), letter=vec2(200, 270), text="A", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
		
		ui.beginRotation()
		display.text{pos=vec2(815, 700), letter=vec2(200, 270), text="L", font="36_big", color=rgbm(1,0,0,1)}
		ui.endRotation(270, vec2(0,0))
	end
end