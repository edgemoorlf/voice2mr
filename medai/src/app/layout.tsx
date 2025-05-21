import './globals.css'
import { Toaster } from 'react-hot-toast'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'MedAI - Your AI Medical Assistant',
  description: 'AI-powered medical assistance platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta httpEquiv="Content-Security-Policy" content="script-src 'self' 'unsafe-eval' 'unsafe-inline';" />
        <link rel="manifest" href="/manifest.json" />
        {/* Apple touch icons */}
        <link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon-120x120.png" />
        <link rel="apple-touch-icon" sizes="152x152" href="/apple-touch-icon-152x152.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180x180.png" />
        {/* ...other head tags... */}
      </head>
      <body className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        {children}
      </body>
    </html>
  )
}
