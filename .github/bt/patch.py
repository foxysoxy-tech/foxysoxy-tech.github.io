import os,re,sys
J='android/app/src/main/java/com/foxysoxy/bravetube/'
def rd(p): return open(p,encoding='utf-8').read()
def wr(p,s): open(p,'w',encoding='utf-8').write(s)

# MainActivity
p=J+'MainActivity.java'
s=rd(p)

# 1) Dateien mit Bild+Ton in einer Datei (itag 18, 22 ...) laden ohne Proxy direkt; Testhost 10.0.2.2 wie googlevideo behandeln
if 'isMuxedItag' not in s:
    a='h.endsWith(".googlevideo.com") && "GET".equals'
    assert s.count(a)==1, 'Stelle 1a nicht gefunden'
    s=s.replace(a,'(h.endsWith(".googlevideo.com") || (NativeAudio.testUrl != null && "10.0.2.2".equals(h))) && "GET".equals')
    a='&& !NativeAudio.streamUa.isEmpty() && (ref == null'
    assert s.count(a)==1, 'Stelle 1b nicht gefunden'
    s=s.replace(a,'&& !NativeAudio.streamUa.isEmpty() && !isMuxedItag(u.getQueryParameter("itag")) && (ref == null')
    i=s.rstrip().rfind('}')
    s=s[:i]+'''
    static boolean isMuxedItag(String t) {
        return "18".equals(t) || "22".equals(t) || "37".equals(t) || "38".equals(t) || "59".equals(t);
    }
}
'''

# 2) Selbsttest (nur mit Intent-Extra "selftest", sonst ohne Wirkung)
if 'selfTest(' not in s:
    k='        web.loadUrl(last);\n'
    assert s.count(k)==1, 'Stelle 2 nicht gefunden'
    s=s.replace(k,'        if (getIntent() != null && getIntent().getStringExtra("testurl") != null) { NativeAudio.testUrl = getIntent().getStringExtra("testurl"); web.getSettings().setMixedContentMode(android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW); }\n'+k+'        if (getIntent() != null && getIntent().getStringExtra("selftest") != null) selfTest(getIntent().getStringExtra("selftest"));\n')
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
        ui.postDelayed(() -> jsLog("t1", probe), 50000);
        ui.postDelayed(() -> jsLog("seek1", seek60), 51000);
        ui.postDelayed(() -> jsLog("t2", probe), 60000);
        ui.postDelayed(() -> jsLog("seek2", seek10), 61000);
        ui.postDelayed(() -> jsLog("t3", probe), 70000);
        ui.postDelayed(() -> jsLog("proxy", "(function(){return 'ende'})()"), 71000);
    }
}
'''
wr(p,s)

# NativeAudio: Testadresse statt YouTube (nur gesetzt, wenn der Selbsttest sie per Intent mitgibt)
p=J+'NativeAudio.java'
n=rd(p)
if 'testUrl' not in n:
    k='    static org.json.JSONObject streamJson(String videoId) {\n        org.json.JSONObject out = new org.json.JSONObject();\n        try {\n'
    assert n.count(k)==1, 'Stelle 3 nicht gefunden'
    n=n.replace(k,'    static volatile String testUrl = null;\n\n'+k+'            if (testUrl != null) { out.put("ok", true); out.put("url", testUrl); out.put("client", "TEST (nur Bild+Ton in einer Datei)"); streamUa = "BraveTube-Test"; return out; }\n')
    wr(p,n)

# Unverschluesselter Verkehr nur zum Emulator-Host 10.0.2.2 erlauben
mf='android/app/src/main/AndroidManifest.xml'
m=rd(mf)
if 'networkSecurityConfig' not in m:
    assert m.count('<application')==1, 'Manifest: application nicht eindeutig'
    wr(mf,m.replace('<application','<application android:networkSecurityConfig="@xml/bt_netsec"',1))
    os.makedirs('android/app/src/main/res/xml',exist_ok=True)
    wr('android/app/src/main/res/xml/bt_netsec.xml','<?xml version="1.0" encoding="utf-8"?>\n<network-security-config>\n  <domain-config cleartextTrafficPermitted="true"><domain includeSubdomains="false">10.0.2.2</domain></domain-config>\n</network-security-config>\n')
print('gepatcht')
