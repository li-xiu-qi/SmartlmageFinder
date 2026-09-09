import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import AppHeader from './AppHeader'
import AppSidebar from './AppSidebar'
import { useSystemStatus } from '@/hooks/useSystemStatus'

/**
 * 应用外壳：暖白画廊风整体布局
 * 顶栏（搜索为重心） + 侧边导航 + 主内容区
 */
export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const { systemStatus } = useSystemStatus()

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <AppHeader
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
        systemStatus={systemStatus}
      />
      <div className="flex flex-1">
        <AppSidebar collapsed={collapsed} />
        <main className="min-w-0 flex-1 px-6 py-6 lg:px-8">
          <div className="mx-auto w-full max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
