---------------------------------Cimmerian F10 Steering Wheel Scriptable LEDs---------------------------------

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

local synced = false

function sync()
	synced = true
end

function update()
	LEDsize = 150
	local blueColor = rgbm(0,0.2,0.9,1)
	local redColor = rgbm(1,0,0,1)
	local greenColor = rgbm(0,1,0,1)
	local yellowColor = rgbm(1,0.8,0,1)
	
	-- Main LEDs for revs, cannot see 7 gear like real life
	if car.clutch > 0.05 then
		if car.gear <= 6 then
			if car.rpm >= 16500 then
				display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
				display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
				display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
				display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
				display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			end
			if car.rpm >= 16900 then
				display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
				display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
				display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
				display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
				display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			end
			if car.rpm >= 17400 then
				display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
				display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
				display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
				display.rect{pos= vec2 (600,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED13
				display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED14
			end
		end
	end

	-- Pitlane LEDs
	if car.isInPitlane == true and car.clutch > 0.05 and car.rpm > 1000 then
		display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
		display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED14
		
		if car.speedKmh >= 20 then
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (600,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED13
		end
		
		if car.speedKmh >= 30 then
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
		end
		
		if car.speedKmh >= 40 then
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
		end
		
		if car.speedKmh >= 50 then
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
		end
		
		if car.speedKmh >= 60 then
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
		end
		
		if car.speedKmh >= 70 then
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
		end
		
		if car.speedKmh >= 79 then
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
		end
		
		if car.speedKmh >= (car.speedLimiter - 1) then
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
		end
	end

	-- RPM launch lights
	if car.clutch == 0 and car.gear < 3 then
		if ac.getCar().gas > 0 and ac.getCar().gas < 0.1 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
		end
		
		if ac.getCar().gas >= 0.1 and ac.getCar().gas < 0.15 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
		end
		
		if ac.getCar().gas >= 0.15 and ac.getCar().gas < 0.2 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
		end

		if ac.getCar().gas >= 0.2 and ac.getCar().gas < 0.25 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
		end
		
		if ac.getCar().gas >= 0.25 and ac.getCar().gas < 0.35 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
		end

		if ac.getCar().gas >= 0.35 and ac.getCar().gas < 0.45 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
		end

		if ac.getCar().gas >= 0.45 and ac.getCar().gas < 0.55 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
		end
		
		if ac.getCar().gas >= 0.55 and ac.getCar().gas < 0.65 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
		end
		
		if ac.getCar().gas >= 0.65 and ac.getCar().gas < 0.75 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
		end
		
		if ac.getCar().gas >= 0.75 and ac.getCar().gas < 0.8 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
		end
		
		if ac.getCar().gas >= 0.8 and ac.getCar().gas < 0.85 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
			display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
		end
		
		if ac.getCar().gas >= 0.85 and ac.getCar().gas < 0.9 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
			display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
			display.rect{pos= vec2 (600,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED13
		end
		
		if ac.getCar().gas >= 0.9 and ac.getCar().gas <= 1 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
			display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
			display.rect{pos= vec2 (600,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED13
			display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED14
		end
	end
	
	-- Overtake mode active LED
	local batteryLeft = math.round(car.kersCharge*100, 0)
	local energyForLap = math.round((1-car.kersLoad)*100, 0)
	
	if car.kersButtonPressed and car.rpm > 1000 and car.clutch == 1 then
		if (math.floor((ac.getSim().sessionTimeLeft) / 400) % 2) == 0 then
			if batteryLeft == 0 or energyForLap == 0 then
				display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED14
			else
				display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED14
			end
		end
	end
	
	if car.clutch > 0.05 and car.gear ~= 0 and car.rpm < 1000 then
		if (math.floor((ac.getSim().sessionTimeLeft) / 450) % 2) == 0 then
			display.rect{pos= vec2 (100,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED0
			display.rect{pos= vec2 (500,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED2
			display.rect{pos= vec2 (700,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED4
			display.rect{pos= vec2 (300,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED6
			display.rect{pos= vec2 (600,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED8
			display.rect{pos= vec2 (100,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED10
			display.rect{pos= vec2 (500,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED12
			display.rect{pos= vec2 (700,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED14
		else
			display.rect{pos= vec2 (300,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED1
			display.rect{pos= vec2 (600,90) , size = vec2(LEDsize,LEDsize),color = greenColor } -- LED3
			display.rect{pos= vec2 (100,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED5
			display.rect{pos= vec2 (500,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED7
			display.rect{pos= vec2 (700,390) , size = vec2(LEDsize,LEDsize),color = redColor } -- LED9
			display.rect{pos= vec2 (300,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED11
			display.rect{pos= vec2 (600,790) , size = vec2(LEDsize,LEDsize),color = blueColor } -- LED13
		end
	end
	
	-- Syncs everything
	if not synced then 
		sync() 
	end
end