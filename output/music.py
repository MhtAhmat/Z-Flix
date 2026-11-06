import numpy as np, wave
sr=44100; D=27.5; n=int(sr*D); t=np.arange(n)/sr
rng=np.random.default_rng(1)
chords=[(220.0,261.63,329.63),(174.61,220.0,261.63),(130.81,164.81,196.0),(196.0,246.94,293.66)]  # Am F C G
out=np.zeros(n); cl=6.0
for i in range(5):
    ch=chords[i%4]; s=int(i*cl*sr); e=min(n,int((i+1)*cl*sr+sr*1.5))
    tt=np.arange(e-s)/sr; env=np.minimum(1,tt/1.5)*np.minimum(1,(len(tt)/sr-tt)/1.5)
    for f in ch:
        for d in (-0.6,0.6):
            out[s:e]+=env*np.sin(2*np.pi*(f+d)*tt)*0.12
        out[s:e]+=env*np.sin(2*np.pi*f/2*tt)*0.10
# soft pulse arpeggio
step=0.5
for k in range(int(D/step)):
    ch=chords[int(k*step//cl)%4]; f=ch[k%3]*2; s=int(k*step*sr); L=int(0.6*sr)
    if s+L>n: break
    tt=np.arange(L)/sr; out[s:s+L]+=np.sin(2*np.pi*f*tt)*np.exp(-tt*6)*0.07
# gentle kick-less tech tick
out*=np.minimum(1,t/1.0)*np.minimum(1,(D-t)/1.5)
out/=np.abs(out).max()
st=np.stack([out,np.roll(out,200)],1)
w=wave.open('music.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((st*0.9*32767).astype('<i2').tobytes()); w.close()
