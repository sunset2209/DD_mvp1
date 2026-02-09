'use client'

import { Bell, HelpCircle, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface TopBarProps {
  title: string
  breadcrumbs?: { label: string; href?: string }[]
}

export function TopBar({ title, breadcrumbs = [] }: TopBarProps) {
  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-8 shrink-0">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span>Главная</span>
        {breadcrumbs.map((crumb, i) => (
          <span key={i} className="flex items-center gap-2">
            <ChevronRight className="w-3.5 h-3.5" />
            <span className={i === breadcrumbs.length - 1 ? 'text-foreground font-medium' : ''}>
              {crumb.label}
            </span>
          </span>
        ))}
        {breadcrumbs.length === 0 && (
          <>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-foreground font-medium">{title}</span>
          </>
        )}
      </div>

      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm">
          <Bell className="w-5 h-5" />
        </Button>
        <Button variant="outline" size="sm">
          <HelpCircle className="w-4 h-4" />
          Справка
        </Button>
      </div>
    </header>
  )
}
