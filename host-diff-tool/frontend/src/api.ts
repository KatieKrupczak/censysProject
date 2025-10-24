export const API_BASE = import.meta.env.VITE_API_BASE || '';

export async function uploadSnapshot(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{ ok: true; ip: string; timestamp: string; path: string }>;
}

export async function getHosts() {
  const response = await fetch(`${API_BASE}/api/hosts`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{ hosts: string[] }>;
}

export async function getSnapshots(ip: string) {
  const response = await fetch(`${API_BASE}/api/snapshots/${encodeURIComponent(ip)}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{ip: string; timestamps: string[] }>;
}

export async function getDiff(ip: string, timestamp1: string, timestamp2: string) {
  const params = new URLSearchParams({
    ip,
    timestamp1,
    timestamp2,
  });
  const response = await fetch(`${API_BASE}/api/diff?${params}`);

  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<{ ip: string; timestamp1: string; timestamp2: string; diff: any }>;
}