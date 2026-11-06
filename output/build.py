import subprocess
U='/root/.claude/uploads/42051048-b252-5c7a-9f5d-b01420bfc70a/'
import glob
A=glob.glob(U+'8d9cb6ac*.mp4')[0]; B=glob.glob(U+'9f771297*.mp4')[0]; V=glob.glob(U+'47e59918*.mp3')[0]
# src,start,dur,Z0,Z1,fx,fy
segs=[('A',2.6,2.0,1.0,1.06,.5,.5),
('B',15.0,2.65,1.35,1.45,.45,.30),
('B',19.0,4.9,1.30,1.42,.45,.30),
('B',24.0,3.4,1.30,1.40,.45,.32),
('B',28.0,3.35,1.35,1.28,.45,.35),
('B',29.4,3.0,1.0,1.08,.5,.5),
('B',20.0,4.1,1.0,1.1,.5,.3),
('A',5.0,3.2,1.0,1.1,.5,.55)]
inputs=['-i',A,'-i',B,'-i',V,'-i','music.wav']
fc=[]
for i,(s,st,d,z0,z1,fx,fy) in enumerate(segs):
    idx=0 if s=='A' else 1
    pre='scale=1080:1920:flags=lanczos,unsharp=5:5:0.8,' if s=='A' else ''
    r=(z1-z0)/d
    fc.append(f"[{idx}:v:0]trim=start={st}:duration={d},setpts=PTS-STARTPTS,fps=30,{pre}"
      f"scale=w='1080*({z0}+{r}*t)':h=-2:eval=frame:flags=bicubic,crop=1080:1920:x='(iw-1080)*{fx}':y='(ih-1920)*{fy}',setsar=1[v{i}]")
n=len(segs)
fc.append(''.join(f'[v{i}]' for i in range(n))+f"concat=n={n}:v=1:a=0,"
 "eq=contrast=1.06:saturation=1.1:gamma=1.02,fade=t=out:st=26.1:d=0.5,format=yuv420p[vc]")
F="/usr/share/fonts/opentype/inter/Inter-Bold.otf"
texts=[("Plus de confort au quotidien",0.5,4.1),("Refroidissement intégré",5.0,9.2),("Hauteur réglable",10.0,15.8),("Un design élégant et pratique",16.6,22.8)]
cur='vc'
for j,(tx,a,b) in enumerate(texts):
    nxt=f'vt{j}'
    al=f"if(lt(t,{a}+0.25),(t-{a})/0.25,if(gt(t,{b}-0.25),({b}-t)/0.25,1))"
    fc.append(f"[{cur}]drawtext=fontfile={F}:text='{tx}':fontsize=62:fontcolor=white:alpha='{al}':x=(w-text_w)/2:y=1380:"
              f"box=1:boxcolor=black@0.38:boxborderw=26:shadowcolor=black@0.6:shadowx=2:shadowy=2:enable='between(t,{a},{b})'[{nxt}]")
    cur=nxt
fc.append(f"[{cur}]null[vout]")
fc.append("[2:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=7,asplit=2[vo][vsc]")
fc.append("[3:a]volume=0.22,lowpass=f=5000[mu]")
fc.append("[mu][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[mud]")
fc.append("[vo][mud]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=26.0:d=0.6,alimiter=limit=0.95[aout]")
cmd=['ffmpeg','-y','-v','error']+inputs+['-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]',
 '-t','26.6','-r','30','-c:v','libx264','-preset','slow','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart',
 '-c:a','aac','-b:a','192k','-ar','44100','/home/user/Z-Flix/output/laptop-stand-ad-1080x1920.mp4']
print(subprocess.run(cmd).returncode)
