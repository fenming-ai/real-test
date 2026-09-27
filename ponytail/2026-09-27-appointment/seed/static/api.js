export function account() { return sessionStorage.getItem('account') || 'north-organizer'; }
export async function request(path, params = {}) {
  const response = await fetch(path + '?' + new URLSearchParams(params), {
    headers: { Authorization: 'Bearer ' + account() }
  });
  if (!response.ok) throw new Error((await response.json()).error);
  return response;
}
export async function downloadCsv(path, params, filename) {
  const response = await request(path, params);
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement('a');
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
