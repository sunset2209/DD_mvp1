import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/layout/sidebar'

export const metadata: Metadata = {
  title: 'AdaptiveLearn - Адаптивное обучение',
  description: 'Генератор адаптивных заданий для детей с ОВЗ',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className="h-screen flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-direction-column overflow-hidden">
          {children}
        </main>
      </body>
    </html>
  )
}
