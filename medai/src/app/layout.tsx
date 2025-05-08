import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MedAI - Free Medical AI Assistant",
  description: "Your accessible AI medical assistant for remote healthcare support",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm">
            <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="flex h-16 justify-between items-center">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-2xl font-bold text-blue-600">MedAI</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <a href="/" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900">
                    Home
                  </a>
                  <a href="/about" className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-900">
                    About
                  </a>
                </div>
              </div>
            </nav>
          </header>
          <main>
            {children}
          </main>
          <footer className="bg-white mt-auto">
            <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
              <p className="text-center text-sm text-gray-500">
                © {new Date().getFullYear()} MedAI. Free medical AI assistance for everyone.
              </p>
            </div>
          </footer>
        </div>
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
