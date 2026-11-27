import json,re,sys,os
raw=open('bttest.log',encoding='utf-8',errors='replace').read()
try: raw2=open('bttest2.log',encoding='utf-8',errors='replace').read()
except Exception: raw2=''
try: allog=open('alllog.txt',encoding='utf-8',errors='replace').read()
except Exception: allog=''
def get(tag,src=None):
    m=re.findall(r'BTTEST\s*\(\s*\d+\):\s*'+tag+r':\s*(.*)',raw if src is None else src)
    if not m: return None
    v=m[-1].strip()
    try:
        v=json.loads(v)
        if isinstance(v,str):
            try: v=json.loads(v)
            except Exception: pass
    except Exception: pass
    return v
t1,t2,t3=get('t1'),get('t2'),get('t3')
out=['## Emulator-Test (echtes Android, Video p3ug4IRm_ic)','','start: %s'%get('start'),'t1 (nach ~25 s): %s'%t1,'t2 (nach Spulen auf 60 Prozent): %s'%t2,'t3 (nach Spulen auf 10 Prozent): %s'%t3,'']
ok=True
def need(c,msg):
    global ok
    out.append(('OK     ' if c else 'FEHLER ')+msg)
    if not c: ok=False
need(isinstance(t1,dict) and (t1.get('t') or 0)>2 and (t1.get('vw') or 0)>0 and not t1.get('p') and not t1.get('e'),'Video startet und laeuft')
need(isinstance(t2,dict) and t2.get('d') and t2['t']>=t2['d']*0.55 and t2['rs']>=2 and t2.get('vw',0)>0 and not t2.get('sk') and t2['t']-(t1 or {}).get('t',0)>=20 and not t2.get('e'),'Vorspulen funktioniert')
need(isinstance(t3,dict) and t3.get('d') and t3['d']*0.08<=t3['t']<=t3['d']*0.1+15 and t3['rs']>=2 and t3.get('vw',0)>0 and not t3.get('sk') and (t2 or {}).get('t',0)-t3['t']>=40 and not t3.get('e'),'Zurueckspulen funktioniert')
u1,u2,u3=get('t1',raw2),get('t2',raw2),get('t3',raw2)
need(isinstance(u1,dict) and (u1.get('t') or 0)>2 and (u1.get('vw') or 0)>0 and not u1.get('p') and not u1.get('e'),'Getrennte Spuren (MSE): startet und laeuft')
need(isinstance(u2,dict) and u2.get('d') and u2['t']>=u2['d']*0.55 and u2['rs']>=2 and u2.get('vw',0)>0 and not u2.get('sk') and not u2.get('e'),'Getrennte Spuren: Vorspulen')
need(isinstance(u3,dict) and u3.get('d') and u3['d']*0.08<=u3['t']<=u3['d']*0.1+15 and u3['rs']>=2 and u3.get('vw',0)>0 and not u3.get('sk') and not u3.get('e'),'Getrennte Spuren: Zurueckspulen')
out.append('')
out.append('Phase 2 (getrennte Spuren): t1=%s t2=%s t3=%s'%(u1,u2,u3))
out.append('Proxy-Status Phase 1: %s'%get('proxy'))
out.append('Proxy-Status Phase 2: %s'%get('proxy',raw2))
out.append('')
out.append('--- App/WebView-Meldungen (letzte) ---')
try: a1=open('alllog1.txt',encoding='utf-8',errors='replace').read()
except Exception: a1=''
out.append('--- Phase 1 Detail ---')
k1=[l for l in a1.splitlines() if not re.search(r'StrictMode|VideoCapture|MediaPlayerList|Choreographer|ActivityManager.*(PACKAGE|am_pss)|\bat [a-z]',l)]
out.append('\n'.join(k1[-90:])[-11000:])
out.append('--- Ende Phase 1 ---')
keep=[l for l in allog.splitlines() if re.search(r'chromium|BraveTube|BTTEST|AndroidRuntime|FATAL|cr_Media|Console',l)]
out.append('\n'.join(keep[-60:])[-7000:])
txt='\n'.join(out)
print(txt)
open(os.environ.get('GITHUB_STEP_SUMMARY','/dev/null'),'a').write(txt+'\n')
sys.exit(0 if ok else 1)
