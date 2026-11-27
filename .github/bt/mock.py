import os,re,subprocess,sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
F='/tmp/test.mp4'
if not os.path.exists(F):
    subprocess.check_call(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','testsrc2=size=640x360:rate=25','-f','lavfi','-i','sine=frequency=440','-t','240','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',F+'.tmp','-f','mp4'])
    os.replace(F+'.tmp',F)
SIZE=os.path.getsize(F)
print('Testvideo',SIZE,'Bytes',flush=True)
class H(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,fmt,*a):
        print('GET',self.path[:40],self.headers.get('Range'),self.headers.get('User-Agent','')[:40],flush=True)
    def do_GET(self):
        r=self.headers.get('Range')
        s,e=0,SIZE-1
        code=200
        if r:
            m=re.match(r'bytes=(\d*)-(\d*)',r)
            if m:
                if m.group(1)=='' and m.group(2)!='':
                    s=max(0,SIZE-int(m.group(2)))
                else:
                    s=int(m.group(1) or 0)
                    if m.group(2)!='': e=min(int(m.group(2)),SIZE-1)
                code=206
        if s>e or s>=SIZE:
            self.send_response(416);self.send_header('Content-Range','bytes */%d'%SIZE);self.send_header('Content-Length','0');self.end_headers();return
        self.send_response(code)
        self.send_header('Content-Type','video/mp4')
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(e-s+1))
        if code==206: self.send_header('Content-Range','bytes %d-%d/%d'%(s,e,SIZE))
        self.end_headers()
        try:
            with open(F,'rb') as f:
                f.seek(s);left=e-s+1
                while left>0:
                    b=f.read(min(65536,left))
                    if not b: break
                    self.wfile.write(b);left-=len(b)
        except Exception:
            pass
ThreadingHTTPServer(('0.0.0.0',8099),H).serve_forever()
