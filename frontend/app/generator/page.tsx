'use client'

import { useState } from 'react'
import { TopBar } from '@/components/layout/top-bar'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { 
  Sliders, Sparkles, Volume2, Eye, Lightbulb, 
  CheckCircle2, RotateCcw, Edit3, Send 
} from 'lucide-react'
import { cn } from '@/lib/utils'

const subjects = [
  { value: 'math', label: 'Математика' },
  { value: 'russian', label: 'Русский язык' },
  { value: 'reading', label: 'Чтение' },
  { value: 'natural_science', label: 'Окружающий мир' },
]

const students = [
  { value: '1', label: 'Миша К. (Дислексия, 3 класс)' },
  { value: '2', label: 'Лена С. (РАС, 4 класс)' },
  { value: '3', label: 'Артём В. (СДВГ, 3 класс)' },
]

const adaptations = [
  { id: 'large_font', label: 'Крупный шрифт' },
  { id: 'no_distractions', label: 'Без отвлекающих деталей' },
  { id: 'visual_hints', label: 'Визуальные подсказки' },
  { id: 'audio', label: 'Аудио-дублирование' },
  { id: 'timer', label: 'Таймер активности' },
]

const formats = [
  { id: 'interactive', label: 'Интерактив' },
  { id: 'pdf', label: 'PDF для печати' },
]

const history = [
  { title: 'Сложение до 20', time: '2 минуты назад', type: 'СДВГ' },
  { title: 'Окружающий мир: Лес', time: '1 час назад', type: 'РАС' },
]

export default function GeneratorPage() {
  const [topic, setTopic] = useState('Простые дроби: сравнение')
  const [selectedAdaptations, setSelectedAdaptations] = useState(['large_font', 'no_distractions', 'visual_hints'])
  const [selectedFormat, setSelectedFormat] = useState('interactive')
  const [difficulty, setDifficulty] = useState(60)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedTask, setGeneratedTask] = useState(true) // Show preview by default

  const toggleAdaptation = (id: string) => {
    setSelectedAdaptations(prev =>
      prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]
    )
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setGeneratedTask(true)
    setIsGenerating(false)
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <TopBar title="Генератор заданий" />
      
      <div className="flex-1 p-8 overflow-y-auto flex gap-6">
        {/* Configuration Panel */}
        <div className="w-[400px] shrink-0 space-y-6">
          <Card>
            <CardHeader>
              <Sliders className="w-5 h-5 text-primary" />
              <CardTitle>Параметры генерации</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Subject & Topic */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Предмет и Тема</label>
                <div className="flex gap-2">
                  <Select options={subjects} className="w-32" />
                  <Input 
                    value={topic} 
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="Введите тему"
                  />
                </div>
              </div>

              {/* Student */}
              <Select label="Ученик или Группа" options={students} />

              {/* Difficulty Slider */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Уровень сложности</label>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">Базовый</span>
                  <div className="flex-1 relative h-1.5 bg-secondary rounded-full">
                    <div 
                      className="absolute left-0 top-0 h-full bg-primary rounded-full"
                      style={{ width: `${difficulty}%` }}
                    />
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={difficulty}
                      onChange={(e) => setDifficulty(Number(e.target.value))}
                      className="absolute inset-0 w-full opacity-0 cursor-pointer"
                    />
                    <div 
                      className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-primary rounded-full shadow-sm"
                      style={{ left: `calc(${difficulty}% - 8px)` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">Продвинутый</span>
                </div>
              </div>

              {/* Adaptations */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Особенности адаптации (ИОП)</label>
                <div className="flex flex-wrap gap-2">
                  {adaptations.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => toggleAdaptation(item.id)}
                      className={cn('tag', selectedAdaptations.includes(item.id) && 'selected')}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Format */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Формат вывода</label>
                <div className="flex gap-2">
                  {formats.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setSelectedFormat(item.id)}
                      className={cn('tag', selectedFormat === item.id && 'selected')}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button */}
              <Button 
                className="w-full h-12"
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Sparkles className="w-5 h-5" />
                )}
                {isGenerating ? 'Генерация...' : 'Сгенерировать задание'}
              </Button>
            </CardContent>
          </Card>

          {/* History */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">История генераций</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {history.map((item, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <div>
                    <div className="text-sm font-medium">{item.title}</div>
                    <div className="text-xs text-muted-foreground">{item.time} • {item.type}</div>
                  </div>
                  <button className="p-1 text-muted-foreground hover:text-foreground">
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Preview Panel */}
        <div className="flex-1 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-semibold">Предпросмотр</h2>
              <span className="px-2 py-1 bg-secondary rounded text-xs text-muted-foreground">
                Версия 1.0
              </span>
            </div>
            <div className="flex bg-secondary p-1 rounded-md">
              <button className="px-3 py-1.5 text-sm text-muted-foreground rounded-sm">
                Учитель
              </button>
              <button className="px-3 py-1.5 text-sm bg-card text-foreground rounded-sm shadow-sm">
                Ученик (Дислексия)
              </button>
            </div>
          </div>

          {generatedTask ? (
            <>
              <div className="flex-1 bg-card border border-border rounded-lg p-10 relative overflow-y-auto">
                {/* Accessibility Badge */}
                <div className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 bg-white/90 backdrop-blur border border-border rounded-full text-xs font-semibold text-primary">
                  <Eye className="w-3.5 h-3.5" />
                  Режим высокой читаемости
                </div>

                <div className="max-w-[600px] mx-auto">
                  {/* Task Header */}
                  <div className="flex gap-4 mb-6 pb-6 border-b-2 border-dashed border-border">
                    <div className="w-10 h-10 bg-accent text-primary rounded-full flex items-center justify-center text-lg font-bold shrink-0">
                      1
                    </div>
                    <div className="flex-1">
                      <h2 className="text-2xl font-semibold mb-2" style={{ letterSpacing: '0.5px' }}>
                        Какая часть пиццы осталась?
                      </h2>
                      <p className="text-muted-foreground">
                        Посмотри на картинку. Выбери дробь, которая показывает оставшуюся часть.
                      </p>
                    </div>
                    <button className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center shrink-0">
                      <Volume2 className="w-[18px] h-[18px]" />
                    </button>
                  </div>

                  {/* Visual Aid */}
                  <div className="w-full h-[200px] bg-secondary rounded-lg mb-6 flex items-center justify-center text-muted-foreground">
                    <span>Изображение пиццы с 3/4 кусками</span>
                  </div>

                  {/* Answer Options */}
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { value: '1/4', correct: false },
                      { value: '3/4', correct: true },
                      { value: '1/2', correct: false },
                      { value: '2/3', correct: false },
                    ].map((option) => (
                      <div 
                        key={option.value}
                        className={cn(
                          'border-2 rounded-md p-4 cursor-pointer flex items-center gap-3 transition-all',
                          option.correct 
                            ? 'border-primary bg-accent' 
                            : 'border-border hover:border-primary hover:bg-accent'
                        )}
                      >
                        <div className="w-10 h-10 bg-white rounded flex items-center justify-center text-xl font-medium">
                          {option.value}
                        </div>
                        <span className="text-base font-medium">{option.value}</span>
                        {option.correct && (
                          <CheckCircle2 className="w-5 h-5 text-primary ml-auto" />
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Scaffolding Hint */}
                  <div className="mt-6 p-4 bg-success border border-green-200 rounded-md flex gap-3 text-success-foreground">
                    <Lightbulb className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                      <strong>Подсказка:</strong> Посчитай, сколько всего кусков было сначала (4). 
                      А сколько лежит на тарелке сейчас (3)?
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 justify-end">
                <Button variant="outline">
                  <Edit3 className="w-4 h-4" />
                  Редактировать вручную
                </Button>
                <Button>
                  <Send className="w-4 h-4" />
                  Назначить Мише К.
                </Button>
              </div>
            </>
          ) : (
            <div className="flex-1 bg-card border border-border rounded-lg flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Настройте параметры и нажмите "Сгенерировать задание"</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
