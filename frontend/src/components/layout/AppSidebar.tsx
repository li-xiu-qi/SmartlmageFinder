import { NavLink, useNavigate } from 'react-router-dom'
import {
  Home,
  Images,
  UploadCloud,
  Search,
  Tags,
  Settings,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: '首页', icon: Home },
  { to: '/images', label: '图片库', icon: Images },
  { to: '/upload', label: '上传图片', icon: UploadCloud },
  { to: '/search', label: '搜索', icon: Search },
  { to: '/tags', label: '标签', icon: Tags },
  { to: '/settings', label: '设置', icon: Settings },
]

interface AppSidebarProps {
  collapsed: boolean
}

/**
 * 侧边导航：暖白画廊风，纯 Tailwind + shadcn 气质
 */
export default function AppSidebar({ collapsed }: AppSidebarProps) {
  const navigate = useNavigate()

  return (
    <aside
      className={cn(
        'sticky top-[57px] z-20 flex h-[calc(100vh-57px)] shrink-0 flex-col border-r bg-card transition-[width] duration-200',
        collapsed ? 'w-[68px]' : 'w-56'
      )}
    >
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            title={label}
            className={({ isActive }) =>
              cn(
                'group flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium transition-colors',
                collapsed && 'justify-center px-0',
                isActive
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )
            }
          >
            <Icon className="h-[18px] w-[18px] shrink-0" strokeWidth={1.8} />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <button
          type="button"
          onClick={() => navigate('/upload')}
          className="m-3 flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90"
        >
          <UploadCloud className="h-4 w-4" strokeWidth={2} />
          上传图片
        </button>
      )}
    </aside>
  )
}
