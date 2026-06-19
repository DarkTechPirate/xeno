/**
 * Root layout for Next.js App Router
 */

'use client';

import type { Metadata } from 'next';
import { ReactNode } from 'react';
import '@/styles/globals.css';
import { Toaster } from 'react-hot-toast';

export const metadata: Metadata = {
  title: 'TransactIQ - Enterprise Transaction Validation Platform',
  description: 'Validate, clean, correct, and analyze transaction datasets with enterprise-grade accuracy.',
  viewport: 'width=device-width, initial-scale=1',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#000000" />
      </head>
      <body className="antialiased">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
