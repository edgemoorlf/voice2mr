import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Chatbox from '../components/Chatbox';
import { sendMessage } from '../lib/api';

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MedAssistant',
  description: 'Personal Medical Record Management',
}

const handleSendMessage = async (message: string) => {
  const response = await sendMessage(message);
  console.log(response);
  // update the chatbox with the doctor's response
};

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
