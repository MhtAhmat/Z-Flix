import subprocess,glob,sys
U='/root/.claude/uploads/42051048-b252-5c7a-9f5d-b01420bfc70a/'
A=glob.glob(U+'8d9cb6ac*.mp4')[0]; B=glob.glob(U+'9f771297*.mp4')[0]; V=glob.glob(U+'47e59918*.mp3')[0]
LOGO=U+'ac50bfda-image.png'
OUT=sys.argv[1] if len(sys.argv)>1 else 'laptop-stand-ad-FINAL.mp4'
TOTAL=27.5; VOICE_END=26.16; CTA=23.61; OV=0.3
# src,start,dur,Z0,Z1,fx,fy
segs=[('A',2.2,2.0,1.0,1.06,.5,.5),
('B',10.0,2.65,1.55,1.62,.5,1.0),
('B',15.0,2.4,1.35,1.45,.45,.30),
('B',20.0,2.5,1.35,1.45,.45,.30),
('B',24.0,6.75,1.28,1.42,.45,.32),
('B',5.0,3.0,1.6,1.7,1.0,.30),
('B',17.4,2.6,1.35,1.45,1.0,.30),
('B',22.55,1.65,1.2,1.3,.5,.3),
('A',4.28,3.95,1.0,1.08,.5,.40)]
n=len(segs)
assert abs(sum(s[2] for s in segs)-TOTAL)<1e-6
inp=['-i',A,'-i',B,'-i',V,'-i','music.wav','-loop','1','-i',LOGO,'-loop','1','-i','glow.png','-loop','1','-i','arrow_down.png']
fc=[]; T=0; starts=[]
for i,(s,st,d,z0,z1,fx,fy) in enumerate(segs):
    starts.append(T)
    idx=0 if s=='A' else 1
    pre='scale=1080:1920:flags=lanczos,unsharp=5:5:0.8,' if s=='A' else ''
    lead=OV/2 if i>0 else 0; tail=OV/2 if i<n-1 else 0
    L=d+lead+tail; r=(z1-z0)/L
    fc.append(f"[{idx}:v:0]trim=start={st-lead}:duration={L},setpts=PTS-STARTPTS,fps=30,{pre}"
      f"scale=w='1080*({z0}+{r}*t)':h=-2:eval=frame:flags=bicubic,crop=1080:1920:x='(iw-1080)*{fx}':y='(ih-1920)*{fy}',setsar=1,format=yuv420p[v{i}]")
    T+=d
cur='v0'
for i in range(1,n):
    fc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={OV}:offset={starts[i]-OV/2}[x{i}]"); cur=f'x{i}'
fc.append(f"[{cur}]eq=contrast=1.06:saturation=1.1:gamma=1.02,fade=t=out:st={TOTAL-0.5}:d=0.5,format=yuv420p[vc]")
# logo (exact pixels, only scaled uniformly) + soft light plate behind it; fade-in
fc.append("[5:v]scale=520:-1,format=rgba,fade=t=in:st=0:d=0.8:alpha=1[gl]")
fc.append("[4:v]scale=340:-1,format=rgba,fade=t=in:st=0.2:d=0.8:alpha=1[lg]")
fc.append("[vc][gl]overlay=x=280:y=-28:shortest=1[g1]")   # plate centre (540,232)
fc.append("[g1][lg]overlay=x=370:y=63:shortest=1[g2]")
# arrow (pointing down): appears exactly when CTA starts, gentle bounce, fades with video end
fc.append(f"[6:v]scale=150:-1,format=rgba,fade=t=in:st={CTA}:d=0.2:alpha=1,fade=t=out:st={TOTAL-0.5}:d=0.5:alpha=1[ar]")
fc.append(f"[g2][ar]overlay=x=(W-w)/2:y='1500+26*abs(sin(2*PI*1.5*(t-{CTA})))':enable='gte(t,{CTA})':shortest=1[vout]")
# audio: full voiceover, untouched length, padded with silence to final length; no fade on voice
fc.append(f"[2:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7,apad=whole_dur={TOTAL},atrim=0:{TOTAL},asplit=2[vo][vsc]")
fc.append(f"[3:a]atrim=0:{TOTAL},volume=0.2,lowpass=f=5000,afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL-2.2}:d=2.2[mu]")
fc.append("[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[mud]")
fc.append("[vo][mud]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[aout]")
cmd=['ffmpeg','-y','-v','error']+inp+['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-t',str(TOTAL),'-r','30',
 '-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart','-c:a','aac','-b:a','192k','-ar','44100',OUT]
print(subprocess.run(cmd).returncode)
