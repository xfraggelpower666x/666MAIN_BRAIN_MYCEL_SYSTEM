export async function requireComfyResponse(response: Response): Promise<void> {
  if (response.ok) return;
  const detail = response.status === 502 ? (await response.text()).slice(0, 500).trim() : '';
  throw new Error(`HTTP ${response.status}${detail ? `: ${detail}` : ''}`);
}
