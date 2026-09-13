import type { Results, Activity } from './types';
export const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : response.status === 422 ? 'Please check your dates, budget and group size.' : 'The concierge is unavailable. Check that the backend is running.');
  }
  return response.json();
}
export function sourceUrl(url: string) { return url.startsWith('/api/') ? API + url : url.startsWith('https://') ? url : '#'; }
export function money(value: number | null) { return value === null ? 'Unverified' : new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value); }
export function eventDate(value: string) { return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', weekday: 'short', timeZone: 'America/Los_Angeles' }).format(new Date(value)); }
export function eventTime(value: string) { return new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/Los_Angeles' }).format(new Date(value)); }
export type Job = { request_id: string; status: 'queued' | 'running' | 'complete' | 'failed'; activity: Activity[]; result?: Results; error?: string };
