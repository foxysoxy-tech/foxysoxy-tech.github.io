import os,re,sys
J='android/app/src/main/java/com/foxysoxy/bravetube/'
def rd(p): return open(p,encoding='utf-8').read()
def wr(p,s): open(p,'w',encoding='utf-8').write(s)

# MainActivity
p=J+'MainActivity.java'
s=rd(p)

# 1) Dateien mit Bild+Ton in einer Datei (itag 18, 22 ...) laden ohne Proxy direkt
if 'isMuxedItag' not in s:
    a='&& !NativeAudio.streamUa.isEmpty() && (ref == null'
    assert s.count(a)==1, 'Stelle 1 nicht gefunden'
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
    s=s.replace(k,'        if (getIntent() != null && getIntent().getStringExtra("testurl") != null) NativeAudio.testUrl = getIntent().getStringExtra("testurl");\n        web.loadUrl(getIntent() != null && getIntent().getStringExtra("selftest") != null ? SITE + "BraveTube3.20.html" : last);\n'+'        if (getIntent() != null && getIntent().getStringExtra("selftest") != null) selfTest(getIntent().getStringExtra("selftest"));\n')
    i=s.rstrip().rfind('}')
    s=s[:i]+'''
    private void jsLog(final String tag, final String js) {
        ui.post(() -> web.evaluateJavascript(js, r -> android.util.Log.i("BTTEST", tag + ": " + r)));
    }

    private void selfTest(final String id) {
        final String probe = "(function(){var v=document.getElementById('ownV');var o={};try{o.am=String(typeof appMode!=='undefined'&&appMode);o.cur=(typeof cur!=='undefined'&&cur)?cur.id:null;o.own=(typeof own!=='undefined')?{on:own.on,w:own.waiting,bad:own.bad,nerr:own.nerr,fmt:own.fmt,cl:own.client,q:own.q,retry:own.retry}:null;var tt=document.getElementById('toast');o.toast=tt?tt.textContent.slice(0,200):null;var w=document.getElementById('why');o.why=w?w.textContent.slice(0,200):null;o.url=location.href.slice(0,60)}catch(e){o.ex=String(e)}if(v){o.t=v.currentTime;o.d=v.duration;o.rs=v.readyState;o.vw=v.videoWidth;o.sk=v.seeking;o.bf=v.buffered.length?v.buffered.end(v.buffered.length-1):0;o.p=v.paused;o.e=v.error?v.error.code+':'+(v.error.message||''):null;o.s=(v.currentSrc||'').slice(0,50)}else o.v='kein ownV';return JSON.stringify(o)})()";
        final String seek60 = "(function(){var v=document.getElementById('ownV');if(v&&v.duration>0){v.currentTime=v.duration*0.6}return 'seek60'})()";
        final String seek10 = "(function(){var v=document.getElementById('ownV');if(v&&v.duration>0){v.currentTime=v.duration*0.1}return 'seek10'})()";
        ui.postDelayed(() -> jsLog("start", "(function(){try{play({id:'" + id + "',title:'selftest'});return 'play ok'}catch(e){return 'play fehler '+e}})()"), 30000);
        ui.postDelayed(() -> jsLog("t1", probe), 50000);
        ui.postDelayed(() -> jsLog("seek1", seek60), 51000);
        ui.postDelayed(() -> jsLog("t2", probe), 60000);
        ui.postDelayed(() -> jsLog("seek2", seek10), 61000);
        ui.postDelayed(() -> jsLog("t3", probe), 70000);
        ui.postDelayed(() -> android.util.Log.i("BTTEST", "proxy: " + android.text.TextUtils.htmlEncode(StreamProxy.last) + " n=" + StreamProxy.count), 71000);
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
    n=n.replace(k,'    static volatile String testUrl = null;\n\n'+k+'            if ("AD".equals(testUrl)) { java.net.HttpURLConnection hc = (java.net.HttpURLConnection) new java.net.URL("https://foxysoxy-tech.github.io/bt-test/ad.json").openConnection(); java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream(); java.io.InputStream is = hc.getInputStream(); byte[] bf = new byte[8192]; int rn; while ((rn = is.read(bf)) > 0) bo.write(bf, 0, rn); is.close(); String js = bo.toString("UTF-8").replace("itag=137", "itag=137&pot=t").replace("itag=140", "itag=140&pot=t"); out.put("ok", true); out.put("ad", new org.json.JSONObject(js)); out.put("client", "TEST (getrennte Spuren)"); streamUa = "BraveTube-Test"; return out; }\n            if (testUrl != null) { out.put("ok", true); out.put("url", testUrl); out.put("client", "TEST (nur Bild+Ton in einer Datei)"); streamUa = "BraveTube-Test"; return out; }\n')
    wr(p,n)

# StreamProxy: im Testmodus zeigt test.googlevideo.com auf das Testvideo auf der GitHub-Seite
p=J+'StreamProxy.java'
n=rd(p)
if 'testMap(' not in n:
    for sig in ['static WebResourceResponse fetch(String url, Map<String, String> reqHeaders, String ua) {\n',
                'private static HttpURLConnection open(String url, String ua, long a, long b) throws IOException {\n',
                'static WebResourceResponse fetchSingle(String url, Map<String, String> reqHeaders, String ua) {\n']:
        assert n.count(sig)==1, 'StreamProxy: '+sig[:40]
        n=n.replace(sig,sig+'        url = testMap(url);\n')
    k='    static volatile String last = "noch nichts geladen";\n'
    assert n.count(k)==1, 'StreamProxy: last nicht gefunden'
    n=n.replace(k,k+'''
    static String testMap(String url) {
        if (NativeAudio.testUrl != null && url != null && url.startsWith("https://test.googlevideo.com/"))
            return url.contains("/bt-v") ? "https://foxysoxy-tech.github.io/bt-test/v.mp4" : url.contains("/bt-a") ? "https://foxysoxy-tech.github.io/bt-test/a.mp4" : "https://foxysoxy-tech.github.io/bt-test/test.mp4";
        return url;
    }
''')
    wr(p,n)
# YtFetcher.rangeFetch: Testadresse umbiegen
p=J+'YtFetcher.java'
n=rd(p)
if 'testMap(' not in n:
    k='            c = (HttpURLConnection) new URL(url).openConnection();\n            c.setRequestMethod("GET");\n            c.setConnectTimeout(12000);\n'
    assert n.count(k)==1, 'YtFetcher: Stelle nicht gefunden'
    n=n.replace(k,'            url = StreamProxy.testMap(url);\n'+k)
    wr(p,n)
print('gepatcht')
