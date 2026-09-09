import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Menu, Search, Settings, Images } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface AppHeaderProps {
  collapsed: boolean
  onToggle: () => void
  systemStatus: string
}

const STATUS_META: Record<string, { dot: string; label: string; tip: string }> = {
  healthy: { dot: 'bg-emerald-500', label: '运行正常', tip: '系统运行正常' },
  error: { dot: 'bg-red-500', label: '异常', tip: '系统存在错误，请检查服务' },
}

export default function AppHeader({ collapsed, onToggle, systemStatus }: AppHeaderProps) {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')

  const status = STATUS_META[systemStatus] ?? {
    dot: 'bg-amber-500',
    label: '检测中',
    tip: '系统状态未知',
  }

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const q = keyword.trim()
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`)
  }

  return (
    <header className="sticky top-0 z-30 flex h-[57px] items-center gap-3 border-b bg-card/85 px-4 backdrop-blur">
      {/* 折叠 */}
      <button
        type="button"
        onClick={onToggle}
        title={collapsed ? '展开侧栏' : '收起侧栏'}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
      >
        <Menu className="h-5 w-5" strokeWidth={1.8} />
      </button>

      {/* 品牌 */}
      <button
        type="button"
        onClick={() => navigate('/')}
        className="flex shrink-0 items-center gap-2"
        title="返回首页"
      >
        <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <Images className="h-[18px] w-[18px]" strokeWidth={1.9} />
        </span>
        <span className="font-serif text-lg font-semibold tracking-tight text-foreground">
          SmartImager
        </span>
      </button>

      {/* 搜索（视觉重心） */}
      <form onSubmit={onSearch} className="mx-auto w-full max-w-xl px-2">
        <div className="group flex h-9 items-center gap-2 rounded-md border border-input bg-background px-3 transition-colors focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/30">
          <Search className="h-4 w-4 shrink-0 text-muted-foreground" strokeWidth={2} />
          <input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="搜索图片：输入关键词，或去搜索页以图搜图…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="hidden shrink-0 rounded border bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground sm:inline">
            回车
          </kbd>
        </div>
      </form>

      {/* 右侧 */}
      <div className="flex shrink-0 items-center gap-3">
        <TooltipProvider delayDuration={200}>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={cn('h-2 w-2 rounded-full', status.dot)} />
                <span className="hidden md:inline">{status.label}</span>
              </span>
            </TooltipTrigger>
            <TooltipContent>{status.tip}</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <button
          type="button"
          onClick={() => navigate('/settings')}
          title="系统设置"
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <Settings className="h-[18px] w-[18px]" strokeWidth={1.8} />
        </button>
      </div>
    </header>
  )
}
