import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SmartImager',
  description: 'AI 驱动的智能图片管理系统',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-background font-sans antialiased">{children}</body>
    </html>
  )
}
