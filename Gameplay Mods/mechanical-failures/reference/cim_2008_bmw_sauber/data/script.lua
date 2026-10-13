local lastAState = car.extraA
local lastBState = car.extraB
local bmig = 0.02
local bmigMin = 0.00
local bmigMax = 0.09
local bmigRamp = 0.30



local function brakeMigration(data,dataCphys)
    if lastAState ~= car.extraA then
        if bmig == bmigMax then
            bmig = bmigMin
        else
            bmig = math.clamp(bmig+0.01,bmigMin,bmigMax)
        end
        lastAState = car.extraA
    end

    if lastBState ~= car.extraB then
        if bmig == bmigMin then
            bmig = bmigMax
        else
            bmig = math.clamp(bmig-0.01,bmigMin,bmigMax)
        end
        lastBState = car.extraB
    end

    local brakeBiasBase = car.brakeBias
    local brakeBiasTotal = brakeBiasBase + ((math.clamp(data.brake-bmigRamp,0,1)/(1-bmigRamp)) * bmig * brakeBiasBase)
    local bmigCalc = math.round((brakeBiasTotal - brakeBiasBase) / brakeBiasBase * 100,0)
    local torqueFront = dataCphys.wheels[0].brakeTorque + dataCphys.wheels[1].brakeTorque
    local torqueRear = dataCphys.wheels[2].brakeTorque + dataCphys.wheels[3].brakeTorque
    local torqueTotal = torqueFront + torqueRear
    local brakeBiasActual = torqueFront/torqueTotal
    local bbdiff = brakeBiasTotal-brakeBiasActual

    ac.debug('bba',brakeBiasActual)
    ac.debug('bmigCalc',bmigCalc)
    ac.debug('bbdiff',bbdiff)
    ac.debug('bbb',brakeBiasBase)
    ac.debug('bbt',brakeBiasTotal)
    ac.debug('torqueTotal',torqueTotal)
    ac.debug('bmig',bmig * 100)

    data.controllerInputs[0] = brakeBiasTotal
    data.controllerInputs[1] = bmig * 100
end

local lastCState = car.extraC
local lastDState = car.extraD
local lastEState = car.extraE

local DifferentialModes = {
    ENTRY = 0,
    MID = 1,
    HISPD = 2
}

local diffMode = DifferentialModes.MID
local step = 0.01
local entryDiff = 0.10
local midDiff = 0.25
local hispdDiff = 0.60

local function midDiffSwitch(data)
    return data.speedKmh < 200 and true or false
end

local function differential(data)

    if lastCState ~= car.extraC then
        if diffMode == DifferentialModes.HISPD then
            diffMode = DifferentialModes.ENTRY
        else
            diffMode = diffMode + 1
            --ac.setMessage('diffMode',diffMode)
        end
        lastCState = car.extraC
    end

    local diffValue = 0
    
    if diffMode == DifferentialModes.ENTRY then
        diffValue = entryDiff
    elseif diffMode == DifferentialModes.MID then
        diffValue = midDiff
    else
        diffValue = hispdDiff
    end

    if lastDState ~= car.extraD then
        if diffValue == 1 then
            diffValue = 0
        else
            diffValue = math.clamp(diffValue+step,0,1)
        end
        lastDState = car.extraD
    end

    if lastEState ~= car.extraE then
        if diffValue == 0 then
            diffValue = 1
        else
            diffValue = math.clamp(diffValue-step,0,1)
        end
        lastEState = car.extraE
    end

    if diffMode == DifferentialModes.ENTRY then
        entryDiff = diffValue
    elseif diffMode == DifferentialModes.MID then
        midDiff = diffValue
    else
        hispdDiff = diffValue
    end

    ac.debug('e',car.extraE)

    local exitDiff = 0
    if midDiffSwitch(data) then
        exitDiff = midDiff
    else
        exitDiff = hispdDiff
    end

    ac.debug('driver',ac.getDriverName(car.index))
    ac.debug('diffMode',diffMode)
    ac.debug('entryDiff',entryDiff)
    ac.debug('midDiff',midDiff)
    ac.debug('lastmidDiff',lastmidDiff)
    ac.debug('hispdDiff',hispdDiff)
    ac.debug('exitDiff',exitDiff)
    ac.debug('speed',data.speedKmh)

    --ac.setMessage('exitDiff',exitDiff)

    data.controllerInputs[2] = exitDiff
    data.controllerInputs[3] = entryDiff
    data.controllerInputs[4] = midDiff
    data.controllerInputs[5] = hispdDiff
    data.controllerInputs[6] = diffMode
end


local lastbmig = bmig
local lastentryDiff = entryDiff
local lastmidDiff = midDiff
local lasthispdDiff = hispdDiff
local lastdiffMode = diffMode

-- Porpoising settings
local porpoiseConfig = {
    heightThresholdf = 0.055,
    heightThresholdr = 0.075,
    speedThreshold = 265,      -- The speed at which porpoising occurs (km/h)
    speedPorpoiseMax = 300,  -- Porpoise maximum effect speed (km/h)
    porpoiseDuration = 0.1,    -- Time when downforce increases（sec）
    porpoiseInterval = 0.15,   -- Porpoise period time (sec)
    wingGain_DIFFUSER_RL = 0.0,       -- Maximum CL wingGainDIFFUSER_RL
    wingGain_DIFFUSER_RR = 0.0,        -- Maximum CL wingGainDIFFUSER_RR
    normalWingGain = 1,        -- Normal CL magnification
    maxSteerAngle = 14 * math.pi / 180,  -- Steering Angle Threshold (Convert degrees to radians. Do not change the value of 180.)
    minThrottle = 0.05         -- -- Throttle threshold (when the throttle is pressed down more than x (%)
}

-- Porpising control variables
local porpoise = false
local porpoiseTimer = 0
local porpoiseActive = false
local porpoiseTimeLeft = porpoiseConfig.porpoiseDuration

-- A function to reset downforce to normal state
local function resetPorpoisingEffect()
    ac.setWingGain(5, 1, porpoiseConfig.normalWingGain)
    ac.setWingGain(6, 1, porpoiseConfig.normalWingGain)
    porpoiseActive = false
    porpoiseTimeLeft = porpoiseConfig.porpoiseDuration  -- reset time
end

-- A function to porpise process
local function porpoiseEffect(data, dt, datacar)
    if porpoise == true and 
       data.speedKmh >= porpoiseConfig.speedThreshold and 
       data.gas >= porpoiseConfig.minThrottle and  
       math.abs(data.steer) < porpoiseConfig.maxSteerAngle and
       datacar.rideHeight[0] < porpoiseConfig.heightThresholdf and
       datacar.rideHeight[1] < porpoiseConfig.heightThresholdr then
       
        porpoiseTimer = porpoiseTimer + dt

        -- Porpoise strength calculation according to speed.
        local speedRange = porpoiseConfig.speedPorpoiseMax - porpoiseConfig.speedThreshold
        local speedFactor = math.clamp((data.speedKmh - porpoiseConfig.speedThreshold) / speedRange, 0, 1)

        -- Linear approach to maximum CL value
        local currentWingGainRL = 1 + (porpoiseConfig.wingGain_DIFFUSER_RL - 1) * speedFactor
        local currentWingGainRR = 1 + (porpoiseConfig.wingGain_DIFFUSER_RR - 1) * speedFactor

        -- Porpoise execution timing management
        if porpoiseTimer >= porpoiseConfig.porpoiseInterval then
            porpoiseActive = true
            porpoiseTimer = 0
        end

        -- ポーポイジング中
        if porpoiseActive then
            ac.setWingGain(5, 1, currentWingGainRL)  -- DIFFUSER_RL
            ac.setWingGain(6, 1, currentWingGainRR)  -- DIFFUSER_RR
            porpoiseTimeLeft = porpoiseTimeLeft - dt

            if porpoiseTimeLeft <= 0 then
                resetPorpoisingEffect()
            end
        end
    else
        resetPorpoisingEffect()
        porpoiseTimer = 0
    end
end


function script.update(dt)
    local data = ac.accessCarPhysics()
    local dataCphys = ac.getCarPhysics(car.index)
    local datacar = ac.getCar(car.index)
    
    brakeMigration(data,dataCphys)
    differential(data)
    porpoiseEffect(data, dt, datacar)

    if lastbmig ~= bmig then
        lastbmig = bmig 
        ac.setMessage('BMIG',bmig*100)
    end

    if lastentryDiff ~= entryDiff then  
        lastentryDiff = entryDiff
        ac.setMessage('DIFF ENTRY',entryDiff*100)
    end
    
    if lastmidDiff ~= midDiff then
        lastmidDiff = midDiff
        ac.setMessage('DIFF MID',midDiff*100)
    end

    if lasthispdDiff ~= hispdDiff then
        lasthispdDiff = hispdDiff
        ac.setMessage('DIFF HISPD',hispdDiff*100)
    end

    if lastdiffMode ~= diffMode then
        lastdiffMode = diffMode
        if diffMode == 0 then
            ac.setMessage('DIFF MODE','ENTRY') 
        end
        if diffMode == 1 then
            ac.setMessage('DIFF MODE','MID') 
        end
        if diffMode == 2 then
            ac.setMessage('DIFF MODE','HISPD') 
        end
    end

end