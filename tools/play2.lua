-- play.lua: press START/CIRCLE every 60 vsyncs (START every 4th) from vsync 300 on, hold 10; dump RAM + screenshot every 900; quit at N
local STEP, N, n = 900, 9000, 0
local out = './play2/'
local ffi = require('ffi')
local pad = nil
pcall(function() pad = PCSX.SIO0.slots[1].pads[1] end)
local B = PCSX.CONSTS and PCSX.CONSTS.PAD and PCSX.CONSTS.PAD.BUTTON
listener = PCSX.Events.createEventListener('GPU::Vsync', function()
  n = n + 1
  if pad and B and n > 300 then
    local k = n % 60
    if k == 0 then pcall(pad.setOverride, (n % 240 == 0) and B.START or B.CIRCLE) end
    if k == 10 then pcall(pad.clearOverride, B.START); pcall(pad.clearOverride, B.CIRCLE) end
  end
  if n % STEP == 0 then
    local s = PCSX.GPU.takeScreenShot()
    local f = io.open(out .. 'shot' .. n .. '.raw', 'wb')
    f:write(tostring(s.width) .. ' ' .. tostring(s.height) .. ' ' .. tostring(s.bpp) .. '\n')
    f:write(tostring(s.data))
    f:close()
    f = io.open(out .. 'ram' .. n .. '.bin', 'wb')
    f:write(ffi.string(PCSX.getMemPtr(), 2 * 1024 * 1024))
    f:close()
  end
  if n >= N then PCSX.quit() end
end)
