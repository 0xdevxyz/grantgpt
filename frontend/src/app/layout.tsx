import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { ToastProvider } from '@/components/Toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'FörderScout AI - Intelligente Fördermittelsuche',
  description: 'KI-gestützte Fördermittelsuche und Antragsassistenz für deutsche Unternehmen',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className={inter.className}>
        <ToastProvider>
          <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">{children}</main>
            <Footer />
          </div>
        </ToastProvider>
      </body>
    </html>
  );
}

