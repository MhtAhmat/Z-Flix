import subprocess,glob,sys
U='/root/.claude/uploads/42051048-b252-5c7a-9f5d-b01420bfc70a/'
C=[glob.glob(U+p+'*.mp4')[0] for p in ('26d6b8e2','dbf471e6','f841e8bb','26accbf6')]  # C1..C4
V=glob.glob(U+'a247909f*.mp3')[0]; LOGO=U+'db1d53d8-image.png'
OUT=sys.argv[1]
TOTAL=32.5; CTA=28.33; OV=0.2
# clip(1-4),start,dur,Z0,Z1,fx,fy
segs=[(4,0.0,1.6,1.2,1.28,.5,.5),(1,1.0,1.65,1.15,1.22,.5,.5),
(3,0.0,1.85,1.5,1.55,.5,.85),(2,6.0,2.7,1.35,1.42,0,0),
(4,3.3,1.75,1.2,1.12,.5,.5),(1,6.0,1.75,1.15,1.22,.5,.5),
(3,8.6,1.55,1.5,1.55,.5,.85),(2,1.0,1.55,1.35,1.42,0,0),
(4,10.0,2.0,1.2,1.12,.5,.5),(3,2.0,2.1,1.5,1.55,.5,.85),
(2,8.7,2.4,1.35,1.42,0,0),(4,7.2,2.3,1.2,1.28,.5,.5),
(4,5.0,1.5,1.2,1.25,.5,.5),(2,10.7,1.3,1.35,1.42,0,0),
(4,8.7,2.2,1.2,1.12,.5,.5),(1,12.1,4.3,1.1,1.2,.5,.5)]
n=len(segs); assert abs(sum(s[2] for s in segs)-TOTAL)<1e-6, sum(s[2] for s in segs)
inp=[]
for c in C: inp+=['-i',c]
inp+=['-i',V,'-i','music3.wav','-loop','1','-i',LOGO,'-loop','1','-i','glow.png','-loop','1','-i','arrow_down.png']
fc=[];T=0;starts=[]
for i,(c,st,d,z0,z1,fx,fy) in enumerate(segs):
    starts.append(T)
    pre='crop=702:1248:9:16,' if c==1 else ''
    lead=OV/2 if i>0 else 0; tail=OV/2 if i<n-1 else 0
    L=d+lead+tail; r=(z1-z0)/L
    fc.append(f"[{c-1}:v:0]trim=start={max(0,st-lead)}:duration={L},setpts=PTS-STARTPTS,fps=30,{pre}scale=1080:1920:flags=lanczos,unsharp=5:5:0.7,"
      f"scale=w='1080*({z0}+{r}*t)':h=-2:eval=frame:flags=bicubic,crop=1080:1920:x='(iw-1080)*{fx}':y='(ih-1920)*{fy}',setsar=1,format=yuv420p[v{i}]")
    T+=d
cur='v0'
for i in range(1,n):
    fc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={OV}:offset={starts[i]-OV/2}[x{i}]"); cur=f'x{i}'
fc.append(f"[{cur}]eq=contrast=1.05:saturation=1.08,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[vc]")
fc.append("[7:v]scale=520:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[gl]")
fc.append("[6:v]scale=380:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[lg]")
fc.append("[vc][gl]overlay=x=-47:y=-60:shortest=1[g1]")
fc.append("[g1][lg]overlay=x=17:y=10:shortest=1[g2]")
fc.append(f"[8:v]scale=150:-1,format=rgba,fade=t=in:st={CTA}:d=0.2:alpha=1,fade=t=out:st={TOTAL-0.5}:d=0.5:alpha=1[ar]")
fc.append(f"[g2][ar]overlay=x=(W-w)/2:y='1500+26*abs(sin(2*PI*1.5*(t-{CTA})))':enable='gte(t,{CTA})':shortest=1[vout]")
fc.append(f"[4:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asplit=2[vo][vsc]")
fc.append(f"[5:a]atrim=0:{TOTAL},volume=0.2,lowpass=f=5000,afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL-2.5}:d=2.5[mu]")
fc.append("[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[mud]")
fc.append("[vo][mud]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[aout]")
cmd=['ffmpeg','-y','-v','error']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-t',str(TOTAL),'-r','30',
 '-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart','-c:a','aac','-b:a','192k','-ar','44100',OUT]
print(subprocess.run(cmd).returncode)
