import re,sys
p='android/app/src/main/java/com/foxysoxy/bravetube/MainActivity.java'
s=open(p,encoding='utf-8').read()

# 1) Dateien mit Bild+Ton in einer Datei (itag 18, 22 ...) laden ohne Proxy direkt
a='&& !NativeAudio.streamUa.isEmpty() && (ref == null'
b='&& !NativeAudio.streamUa.isEmpty() && !isMuxedItag(u.getQueryParameter("itag")) && (ref == null'
if 'isMuxedItag' not in s:
    assert s.count(a)==1, 'Stelle 1 nicht gefunden'
    s=s.replace(a,b)
    i=s.rstrip().rfind('}')
    s=s[:i]+'''
    static boolean isMuxedItag(String t) {
        return "18".equals(t) || "22".equals(t) || "37".equals(t) || "38".equals(t) || "59".equals(t);
    }
}
'''

# 2) Selbsttest: nur mit Intent-Extra "selftest" (Emulator), sonst ohne Wirkung
if 'selfTest(' not in s:
    k='        web.loadUrl(last);\n'
    assert s.count(k)==1, 'Stelle 2 nicht gefunden'
    s=s.replace(k,k+'        if (getIntent() != null && getIntent().getStringExtra("selftest") != null) selfTest(getIntent().getStringExtra("selftest"));\n')
    i=s.rstrip().rfind('}')
    s=s[:i]+'''
    private void jsLog(final String tag, final String js) {
        ui.post(() -> web.evaluateJavascript(js, r -> android.util.Log.i("BTTEST", tag + ": " + r)));
    }

    private void selfTest(final String id) {
        final String probe = "(function(){var v=document.getElementById('ownV');var o={};try{o.am=String(typeof appMode!=='undefined'&&appMode);o.cur=(typeof cur!=='undefined'&&cur)?cur.id:null;o.own=(typeof own!=='undefined')?{on:own.on,w:own.waiting,bad:own.bad,nerr:own.nerr,fmt:own.fmt,cl:own.client,q:own.q,retry:own.retry}:null;var tt=document.getElementById('toast');o.toast=tt?tt.textContent.slice(0,200):null;var w=document.getElementById('why');o.why=w?w.textContent.slice(0,200):null;o.url=location.href.slice(0,60)}catch(e){o.ex=String(e)}if(v){o.t=v.currentTime;o.d=v.duration;o.rs=v.readyState;o.p=v.paused;o.e=v.error?v.error.code+':'+(v.error.message||''):null;o.s=(v.currentSrc||'').slice(0,50)}else o.v='kein ownV';return JSON.stringify(o)})()";
        final String seek60 = "(function(){var v=document.getElementById('ownV');if(v&&v.duration>0){v.currentTime=v.duration*0.6}return 'seek60'})()";
        final String seek10 = "(function(){var v=document.getElementById('ownV');if(v&&v.duration>0){v.currentTime=v.duration*0.1}return 'seek10'})()";
        ui.postDelayed(() -> jsLog("start", "(function(){try{play({id:'" + id + "',title:'selftest'});return 'play ok'}catch(e){return 'play fehler '+e}})()"), 30000);
        ui.postDelayed(() -> jsLog("t1", probe), 55000);
        ui.postDelayed(() -> jsLog("seek1", seek60), 56000);
        ui.postDelayed(() -> jsLog("t2", probe), 66000);
        ui.postDelayed(() -> jsLog("seek2", seek10), 67000);
        ui.postDelayed(() -> jsLog("t3", probe), 77000);
        ui.postDelayed(() -> android.util.Log.i("BTTEST", "ende"), 78000);
    }
}
'''
open(p,'w',encoding='utf-8').write(s)
print('MainActivity gepatcht')
