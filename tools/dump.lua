-- dump.lua: every STEP vsyncs save a screenshot (shot<n>.raw) and the 2 MB main RAM (ram<n>.bin), quit after N
local STEP, N, n = 900, 9000, 0
local out = './'
local ffi = require('ffi')
listener = PCSX.Events.createEventListener('GPU::Vsync', function()
  n = n + 1
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
