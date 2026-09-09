import type { Metadata } from 'next';
import { Archivo_Narrow, Libre_Franklin } from 'next/font/google';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

const franklin = Libre_Franklin({ variable: '--font-franklin', subsets: ['latin'] });
const archivo = Archivo_Narrow({ variable: '--font-archivo', subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Networking Tracker',
  description: 'A private list of the people you want to stay connected with at Berkeley.',
};

// The direction contract, kept as an HTML comment in the emitted markup so it survives the production build.
const CONTRACT = `<!-- impeccable direction contract 9bae0f3a
THESIS: Your contacts are a private edition of the Berkeley class directory, and the priority filter is the book's thumb index. It refuses the sidebar-and-data-table CRM shell.
OWN-WORLD: Berkeley Blue cloth chrome with gold stamping on the band and the thumb index only; bright white uncoated listing stock with black hanging-indent entries and hairline rules; Libre Franklin for listing and controls, Archivo Narrow condensed caps for running heads and tabs; square corners.
STORY: I sign in through the cover, see my own edition with a live count, scan entries by priority through the thumb index, and add or edit an entry in seconds.
FIRST VIEWPORT: Blue band with the gold-stamped title and the owner's inscription; white running head with live counts, search, and the one solid Add contact button; entries below in directory grammar; a vertical gold-and-blue thumb index on the right edge.
FORM: The Class Directory, candidate 5 of 7, seed 9bae0f3a, code-led.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
-->`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${franklin.variable} ${archivo.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <div hidden dangerouslySetInnerHTML={{ __html: CONTRACT }} />
        {children}
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
