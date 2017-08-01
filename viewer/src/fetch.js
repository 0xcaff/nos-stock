// Makes a request returning the cached version instantly and returning the
// server sent version as it becomes available.
export default async function ffetch(request, cb) {
  const isSecure = window.location.protocol === 'https:';

  if (isSecure) {
    // try resolving from cache
    var cache = await caches.open(name);
    const cacheResp = await cache.match(request);

    if (cacheResp) {
      cb(cacheResp);
    }
  }

  // continue to fetch from network
  const liveResp = await fetch(request);
  const toCacheResp = liveResp.clone();
  cb(liveResp);

  if (!liveResp.ok) {
    return;
  }

  if (isSecure) {
    // update cache if respnse successful
    await cache.put(request, toCacheResp);
  }
}

// The name of the cache which holds our data.
const name ="sw-precache-v3-sw-precache-webpack-plugin-https://nos-stock.drone.lan/";

