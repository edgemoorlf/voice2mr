import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MedAssistant',
  description: 'Personal Medical Record Management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50`}>
        <main className="max-w-md mx-auto min-h-screen bg-white shadow-sm">
          {children}
        </main>
      </body>
    </html>
  )
}
