import type { Metadata } from 'next';
import './globals.css';
import { BRAND } from '@/lib/brand';
export const metadata: Metadata = { title: `${BRAND.name} — Go for the experience.`, description: 'Your personal Bay Area live-sports concierge. Discover, decide, and arrive prepared.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
