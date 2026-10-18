"""raw2png.py <in.raw> <out.png>: PCSX-Redux takeScreenShot dump ('w h bpp' line + pixels) -> PNG via ffmpeg"""
import subprocess, sys
b = open(sys.argv[1], 'rb').read()
i = b.index(10); hd = b[:i].split(); w, h, bpp = hd[0], hd[1], hd[-1]
w, h = int(w), int(h); px = b[i + 1:]
fmt = "rgb24" if bpp == b"1" else "bgr555le"   # PCSX-Redux enum: 0 = BPP_16 (PSX 5:5:5, red in low bits), 1 = BPP_24
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', fmt, '-s', '%dx%d' % (w, h),
                '-i', '-', '-frames:v', '1', sys.argv[2]], input=px[:w * h * (3 if fmt == 'rgb24' else 2)], check=True)
print(w, h, bpp.decode(), fmt)
