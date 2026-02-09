'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Users,
  Wand2,
  Library,
  BarChart2,
  FileText,
  Settings,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { label: 'Меню', items: [
    { href: '/', icon: LayoutDashboard, label: 'Дашборд' },
    { href: '/students', icon: Users, label: 'Мои ученики' },
    { href: '/generator', icon: Wand2, label: 'Генератор' },
    { href: '/library', icon: Library, label: 'Библиотека' },
  ]},
  { label: 'Аналитика', items: [
    { href: '/progress', icon: BarChart2, label: 'Успеваемость' },
    { href: '/reports', icon: FileText, label: 'Отчеты ИОП' },
  ]},
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-[280px] bg-card border-r border-border flex flex-col p-6 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 pb-6 border-b border-border mb-6">
        <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <span className="text-lg font-bold text-foreground">AdaptiveLearn</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-6">
        {navItems.map((group) => (
          <div key={group.label} className="space-y-1">
            <div className="text-[11px] uppercase text-muted-foreground font-semibold px-3 mb-2 tracking-wide">
              {group.label}
            </div>
            {group.items.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn('nav-item', isActive && 'active')}
                >
                  <Icon className="w-[18px] h-[18px]" />
                  {item.label}
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      {/* User Profile */}
      <div className="flex items-center gap-3 pt-4 border-t border-border">
        <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center text-sm font-medium">
          АП
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-foreground truncate">
            Анна Петрова
          </div>
          <div className="text-xs text-muted-foreground">
            Тьютор 3-Б
          </div>
        </div>
        <button className="p-2 text-muted-foreground hover:text-foreground transition-colors">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </aside>
  )
}
