import subprocess,glob,sys
U='/root/.claude/uploads/42051048-b252-5c7a-9f5d-b01420bfc70a/'
A=glob.glob(U+'de4e7955*.mp4')[0]; B=glob.glob(U+'f1b86e74*.mp4')[0]; V=glob.glob(U+'74c4c890*.mp3')[0]
LOGO=U+'e90ef8f9-image.png'
OUT=sys.argv[1]
TOTAL=30.7; CTA=26.57; OV=0.25
# src,start,dur,Z0,Z1,fx,fy,transition_into_this_shot
segs=[('B',15.0,1.4,1.9,1.75,.35,.22,''),
('B',16.4,1.36,1.3,1.4,.5,.3,'fade'),
('B',17.8,1.8,1.5,1.4,.45,.3,'smoothleft'),
('A',2.2,1.5,1.0,1.08,.5,.5,'fade'),
('B',19.7,1.89,1.9,1.8,.3,.25,'fade'),
('B',26.0,1.6,1.45,1.55,.5,.75,'smoothleft'),
('B',27.7,1.62,1.4,1.3,.6,.6,'fade'),
('B',10.0,2.4,1.55,1.62,.5,1.0,'fade'),
('B',14.4,1.9,1.4,1.3,1.0,.4,'fade'),
('B',5.0,2.4,1.6,1.7,1.0,.3,'smoothleft'),
('B',20.3,1.79,1.0,1.1,.5,.3,'fade'),
('B',21.7,2.1,1.0,1.1,.5,.3,'smoothleft'),
('B',23.9,2.09,1.2,1.1,.5,.3,'fade'),
('B',29.4,2.47,1.35,1.3,1.0,.3,'fade'),
('A',3.86,4.38,1.0,1.1,.5,.4,'smoothleft')]
n=len(segs); assert abs(sum(s[2] for s in segs)-TOTAL)<1e-6, sum(s[2] for s in segs)
inp=['-i',A,'-i',B,'-i',V,'-i','music2.wav','-loop','1','-i',LOGO,'-loop','1','-i','glow.png','-loop','1','-i','arrow_down.png']
fc=[];T=0;starts=[]
for i,(s,st,d,z0,z1,fx,fy,tr) in enumerate(segs):
    starts.append(T); idx=0 if s=='A' else 1
    pre='scale=1080:1920:flags=lanczos,unsharp=5:5:0.8,' if s=='A' else ''
    lead=OV/2 if i>0 else 0; tail=OV/2 if i<n-1 else 0
    L=d+lead+tail; r=(z1-z0)/L
    fc.append(f"[{idx}:v:0]trim=start={st-lead}:duration={L},setpts=PTS-STARTPTS,fps=30,{pre}"
      f"scale=w='1080*({z0}+{r}*t)':h=-2:eval=frame:flags=bicubic,crop=1080:1920:x='(iw-1080)*{fx}':y='(ih-1920)*{fy}',setsar=1,format=yuv420p[v{i}]")
    T+=d
cur='v0'
for i in range(1,n):
    fc.append(f"[{cur}][v{i}]xfade=transition={segs[i][7]}:duration={OV}:offset={starts[i]-OV/2}[x{i}]"); cur=f'x{i}'
fc.append(f"[{cur}]eq=contrast=1.1:saturation=1.05:gamma=0.98,colorbalance=bs=0.04:rs=-0.02,vignette=PI/6,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[vc]")
fc.append("[5:v]scale=520:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[gl]")
fc.append("[4:v]scale=380:-1,format=rgba,fade=t=in:st=0:d=0.6:alpha=1[lg]")
fc.append("[vc][gl]overlay=x=-47:y=-60:shortest=1[g1]")
fc.append("[g1][lg]overlay=x=17:y=10:shortest=1[g2]")
fc.append(f"[6:v]scale=150:-1,format=rgba,fade=t=in:st={CTA}:d=0.2:alpha=1,fade=t=out:st={TOTAL-0.5}:d=0.5:alpha=1[ar]")
fc.append(f"[g2][ar]overlay=x=(W-w)/2:y='1500+26*abs(sin(2*PI*1.5*(t-{CTA})))':enable='gte(t,{CTA})':shortest=1[vout]")
fc.append(f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asplit=2[vo][vsc]")
fc.append(f"[3:a]atrim=0:{TOTAL},volume=0.2,lowpass=f=5000,afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL-2.5}:d=2.5[mu]")
fc.append("[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[mud]")
fc.append("[vo][mud]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[aout]")
cmd=['ffmpeg','-y','-v','error']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-t',str(TOTAL),'-r','30',
 '-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart','-c:a','aac','-b:a','192k','-ar','44100',OUT]
print(subprocess.run(cmd).returncode)
