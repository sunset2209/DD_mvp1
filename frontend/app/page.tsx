import { TopBar } from '@/components/layout/top-bar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Users, CheckCircle, Clock, TrendingUp } from 'lucide-react'

const stats = [
  { label: 'Всего учеников', value: '24', icon: Users, color: 'text-primary' },
  { label: 'Заданий выполнено', value: '156', icon: CheckCircle, color: 'text-success-foreground' },
  { label: 'Среднее время', value: '12 мин', icon: Clock, color: 'text-warning-foreground' },
  { label: 'Прогресс', value: '+18%', icon: TrendingUp, color: 'text-primary' },
]

const recentStudents = [
  { name: 'Миша К.', grade: 3, disability: 'Дислексия', progress: 75 },
  { name: 'Лена С.', grade: 4, disability: 'РАС', progress: 62 },
  { name: 'Артём В.', grade: 3, disability: 'СДВГ', progress: 88 },
  { name: 'Даша М.', grade: 2, disability: 'Дискалькулия', progress: 45 },
]

export default function DashboardPage() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <TopBar title="Дашборд" />
      
      <div className="flex-1 p-8 overflow-y-auto">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <Card key={stat.label}>
                <CardContent className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg bg-secondary ${stat.color}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Recent Students */}
          <Card>
            <CardHeader>
              <CardTitle>Активные ученики</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentStudents.map((student) => (
                  <div key={student.name} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                    <div>
                      <div className="font-medium">{student.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {student.grade} класс • {student.disability}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24 h-2 bg-secondary rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full" 
                          style={{ width: `${student.progress}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-10">{student.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Быстрые действия</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <a href="/generator" className="block p-4 border border-border rounded-lg hover:bg-secondary transition-colors">
                <div className="font-medium mb-1">Создать задание</div>
                <div className="text-sm text-muted-foreground">
                  Сгенерировать адаптивное задание с помощью ИИ
                </div>
              </a>
              <a href="/students" className="block p-4 border border-border rounded-lg hover:bg-secondary transition-colors">
                <div className="font-medium mb-1">Добавить ученика</div>
                <div className="text-sm text-muted-foreground">
                  Создать профиль нового ученика с ИОП
                </div>
              </a>
              <a href="/reports" className="block p-4 border border-border rounded-lg hover:bg-secondary transition-colors">
                <div className="font-medium mb-1">Отчёт по классу</div>
                <div className="text-sm text-muted-foreground">
                  Сформировать сводный отчёт успеваемости
                </div>
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
