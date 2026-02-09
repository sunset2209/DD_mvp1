'use client'

import { useState } from 'react'
import { TopBar } from '@/components/layout/top-bar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Plus, Search, MoreVertical, 
  User, GraduationCap, Brain, TrendingUp 
} from 'lucide-react'
import { cn } from '@/lib/utils'

const studentsData = [
  { 
    id: 1, 
    name: 'Миша К.', 
    grade: 3, 
    disabilities: ['Дислексия'], 
    progress: 75,
    tasksCompleted: 45,
    avgScore: 82,
    scaffolding: 2,
  },
  { 
    id: 2, 
    name: 'Лена С.', 
    grade: 4, 
    disabilities: ['РАС'], 
    progress: 62,
    tasksCompleted: 38,
    avgScore: 78,
    scaffolding: 3,
  },
  { 
    id: 3, 
    name: 'Артём В.', 
    grade: 3, 
    disabilities: ['СДВГ'], 
    progress: 88,
    tasksCompleted: 67,
    avgScore: 91,
    scaffolding: 4,
  },
  { 
    id: 4, 
    name: 'Даша М.', 
    grade: 2, 
    disabilities: ['Дискалькулия'], 
    progress: 45,
    tasksCompleted: 23,
    avgScore: 65,
    scaffolding: 2,
  },
  { 
    id: 5, 
    name: 'Саша П.', 
    grade: 3, 
    disabilities: ['СДВГ', 'Дислексия'], 
    progress: 58,
    tasksCompleted: 34,
    avgScore: 72,
    scaffolding: 2,
  },
]

const scaffoldingLabels: Record<number, string> = {
  1: 'Полная поддержка',
  2: 'Высокая',
  3: 'Средняя',
  4: 'Минимальная',
  5: 'Самостоятельно',
}

export default function StudentsPage() {
  const [search, setSearch] = useState('')
  const [selectedStudent, setSelectedStudent] = useState<number | null>(null)

  const filteredStudents = studentsData.filter(s => 
    s.name.toLowerCase().includes(search.toLowerCase())
  )

  const selected = studentsData.find(s => s.id === selectedStudent)

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <TopBar title="Мои ученики" />
      
      <div className="flex-1 p-8 overflow-y-auto flex gap-6">
        {/* Students List */}
        <div className="w-[400px] shrink-0 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input 
                placeholder="Поиск учеников..." 
                className="pl-10"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button>
              <Plus className="w-4 h-4" />
              Добавить
            </Button>
          </div>

          <div className="space-y-2">
            {filteredStudents.map((student) => (
              <div
                key={student.id}
                onClick={() => setSelectedStudent(student.id)}
                className={cn(
                  'p-4 bg-card border rounded-lg cursor-pointer transition-all',
                  selectedStudent === student.id 
                    ? 'border-primary shadow-sm' 
                    : 'border-border hover:border-primary/50'
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-semibold">{student.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {student.grade} класс
                    </div>
                  </div>
                  <button className="p-1 text-muted-foreground hover:text-foreground">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {student.disabilities.map((d) => (
                    <span key={d} className="px-2 py-0.5 bg-accent text-accent-foreground rounded text-xs font-medium">
                      {d}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full transition-all" 
                      style={{ width: `${student.progress}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-muted-foreground w-10">
                    {student.progress}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Student Details */}
        {selected ? (
          <div className="flex-1 space-y-6">
            {/* Header */}
            <Card>
              <CardContent className="flex items-center gap-6">
                <div className="w-20 h-20 bg-secondary rounded-full flex items-center justify-center text-2xl font-bold text-muted-foreground">
                  {selected.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold mb-1">{selected.name}</h2>
                  <div className="flex gap-4 text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <GraduationCap className="w-4 h-4" />
                      {selected.grade} класс
                    </span>
                    <span className="flex items-center gap-1">
                      <Brain className="w-4 h-4" />
                      {selected.disabilities.join(', ')}
                    </span>
                  </div>
                </div>
                <Button variant="outline">Редактировать профиль</Button>
              </CardContent>
            </Card>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
              <Card>
                <CardContent>
                  <div className="text-2xl font-bold">{selected.tasksCompleted}</div>
                  <div className="text-sm text-muted-foreground">Заданий выполнено</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent>
                  <div className="text-2xl font-bold">{selected.avgScore}%</div>
                  <div className="text-sm text-muted-foreground">Средний балл</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent>
                  <div className="text-2xl font-bold">{selected.progress}%</div>
                  <div className="text-sm text-muted-foreground">Прогресс ИОП</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent>
                  <div className="text-2xl font-bold">{scaffoldingLabels[selected.scaffolding]}</div>
                  <div className="text-sm text-muted-foreground">Уровень поддержки</div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Последние задания</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { title: 'Сложение дробей', score: 85, date: 'Сегодня' },
                    { title: 'Сравнение дробей', score: 90, date: 'Вчера' },
                    { title: 'Деление с остатком', score: 75, date: '2 дня назад' },
                  ].map((task, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <div>
                        <div className="font-medium">{task.title}</div>
                        <div className="text-xs text-muted-foreground">{task.date}</div>
                      </div>
                      <div className={cn(
                        'px-2 py-1 rounded text-sm font-medium',
                        task.score >= 80 ? 'bg-success text-success-foreground' : 'bg-warning text-warning-foreground'
                      )}>
                        {task.score}%
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Рекомендации</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 bg-accent/50 rounded-lg">
                    <div className="flex items-center gap-2 text-sm font-medium mb-1">
                      <TrendingUp className="w-4 h-4 text-primary" />
                      Повысить сложность
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Ученик показывает хорошие результаты. Рекомендуется увеличить сложность на 1 уровень.
                    </p>
                  </div>
                  <div className="p-3 bg-secondary rounded-lg">
                    <div className="text-sm font-medium mb-1">Слабые темы</div>
                    <p className="text-xs text-muted-foreground">
                      Требуется дополнительная практика: Деление с остатком
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <User className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Выберите ученика из списка</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
