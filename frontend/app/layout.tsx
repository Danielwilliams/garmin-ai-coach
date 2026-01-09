import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Garmin AI Coach',
  description: 'AI-powered triathlon coaching platform with Garmin Connect integration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}