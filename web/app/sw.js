// PintarAI v2.1 — demo app shell offline cache. Never cache API or sensitive requests.
const CACHE = 'pintarai-app-v2.1-1';
const SHELL = ['/app/','/app/index.html','/app/manifest.webmanifest','/app/icons/icon-192.png','/app/icons/icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(names=>Promise.all(names.filter(n=>n.startsWith('pintarai-app-')&&n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 const url=new URL(e.request.url);
 if(e.request.method!=='GET' || url.origin!==self.location.origin || url.pathname.startsWith('/api/')) return;
 if(url.pathname.startsWith('/app/')){
  e.respondWith(fetch(e.request).then(res=>{if(res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));}return res;}).catch(()=>caches.match(e.request).then(res=>res||caches.match('/app/index.html'))));
 }
});
