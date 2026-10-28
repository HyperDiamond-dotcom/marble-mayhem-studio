"""Original generative electronic race soundtrack. Standard library only.
Usage: python soundtrack.py output.wav 4
"""
import math, wave, random, sys, os
from array import array
output=sys.argv[1] if len(sys.argv)>1 else 'soundtrack.wav'
duration=float(sys.argv[2]) if len(sys.argv)>2 else 70.0
sr=22050; beat=60.0/144.0
r=random.Random(952746)
notes=(55,43.65,65.4,49)
out=array('h')
for n in range(int(duration*sr)):
 t=n/sr; step=int(t/beat); phase=t-step*beat
 beat4=step%4
 k=0.0
 if beat4 in (0,2) and phase<.26:
  k=.56*math.sin(2*math.pi*(45*phase+118*(1-math.exp(-phase*23))/23))*math.exp(-phase*18)
 sn=0.0
 if beat4 in (1,3) and phase<.16:
  sn=(r.random()*2-1)*.27*math.exp(-phase*22)
 hat_phase=(t%(beat/2))
 hh=(r.random()*2-1)*.095*math.exp(-hat_phase*82)
 bassf=notes[(step//16)%4]
 bp=t%(beat*2)
 sub=.19*math.sin(2*math.pi*bassf*bp)*math.exp(-bp*2.7)
 lead=0
 if step%4==3 and phase<.20:
  lead=.055*math.sin(2*math.pi*bassf*4*phase)*math.exp(-phase*14)
 v=math.tanh((k+sn+hh+sub+lead)*1.4)*.7
 v*=min(1,t/.05,max(0,(duration-t)/.45))
 out.append(int(max(-1,min(1,v))*32767))
os.makedirs(os.path.dirname(os.path.abspath(output)),exist_ok=True)
with wave.open(output,'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(out.tobytes())
print('Generated', output, 'duration',duration)
