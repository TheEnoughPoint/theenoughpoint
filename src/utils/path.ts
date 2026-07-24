const base = import.meta.env.BASE_URL.replace(/\/$/, '');

export function url(path: string = '/'): string {
  if (!path) return base || '/';
  let p = path.startsWith('/') ? path : `/${path}`;

  // Append a trailing slash to page routes so they resolve on hosts that
  // require it (e.g. /about -> /about/) — but never to asset files
  // (/img/logo.png), query strings, or hash fragments.
  const [pathOnly] = p.split(/[?#]/);
  const hasExtension = /\.[a-zA-Z0-9]+$/.test(pathOnly);
  if (!p.endsWith('/') && !hasExtension && !/[?#]/.test(p)) {
    p += '/';
  }

  return `${base}${p}`;
}
