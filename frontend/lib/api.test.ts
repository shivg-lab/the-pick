import { describe,it,expect } from 'vitest';
import { eventDate,eventTime,money,sourceUrl } from './api';
describe('visitor-facing data formatting',()=>{
 it('uses the venue timezone instead of UTC',()=>{expect(eventDate('2026-09-20T01:05:00Z')).toContain('Sep 19');expect(eventTime('2026-09-20T01:05:00Z')).toBe('6:05 PM');});
 it('never converts a missing price into free admission',()=>{expect(money(null)).toBe('Unverified');expect(money(0)).toBe('$0');});
 it('handles fixture citations and rejects unsafe external URLs',()=>{expect(sourceUrl('/api/demo/fixtures/49ers')).toContain('/api/demo/fixtures/49ers');expect(sourceUrl('javascript:alert(1)')).toBe('#');expect(sourceUrl('https://calbears.com')).toBe('https://calbears.com');});
});
