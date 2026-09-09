'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Activity,
  SlidersHorizontal,
  RefreshCw,
  Settings2,
  Database,
  Cloud,
  Server,
  Clock,
  Boxes,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Info,
  HardDrive,
  Cpu,
  FileImage,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import AppShell from '@/components/layout/AppShell'
import { systemService } from '@/services/api'
import { cn } from '@/lib/utils'

// 轮询间隔：旧前端每秒拉一次运行时信息，但那套接口未迁移；
// 这里每次拉取都会触发远端推理服务健康检查（5s 超时），1 秒轮询会打爆推理服务，故放宽到 10 秒。
const POLL_INTERVAL_MS = 10_000
const TOAST_DURATION_MS = 3_000

// 模型配置：配置读写接口（getSystemConfig / updateSystemConfig）尚未迁移，
// 这两个值是当前部署的实际取值，待接口到位后改为从接口读取。
const CURRENT_VISION_MODEL = 'glm-4.6v-flash'
const CURRENT_EMBEDDING_MODEL = 'jina-embeddings-v4'

// /api/v1/system 当前实际返回的字段
interface SystemStatusData {
  status?: string
  image_count?: number
  inference_service?: string
  backend?: string
}

type ToastState = { type: 'success' | 'error'; text: string } | null
type TabKey = 'status' | 'config'

// 状态文案与配色映射（旧前端 getStatusBadge）
function statusText(status?: string): string {
  const map: Record<string, string> = {
    healthy: '正常',
    connected: '已连接',
    available: '可用',
    enabled: '已启用',
    warning: '警告',
    disconnected: '未连接',
    missing: '缺失',
    error: '错误',
    disabled: '已禁用',
  }
  return (status && map[status]) || status || '暂无数据'
}

function statusTone(status?: string): string {
  const ok = ['healthy', 'connected', 'available', 'enabled', 'ok']
  const bad = ['warning', 'disconnected', 'missing', 'error', 'unavailable']
  if (status && ok.includes(status)) return 'text-emerald-600'
  if (status && bad.includes(status)) return 'text-destructive'
  return 'text-muted-foreground'
}

function StatusBadge({ status }: { status?: string }) {
  const tone = statusTone(status)
  const Icon = tone === 'text-emerald-600' ? CheckCircle2 : tone === 'text-destructive' ? XCircle : Info
  return (
    <span className={cn('inline-flex items-center gap-1.5 font-medium', tone)}>
      <Icon className="h-3.5 w-3.5" strokeWidth={2} />
      {statusText(status)}
    </span>
  )
}

// 单条信息行：dl/dt/dd 结构，比 antd Descriptions 轻
function InfoRow({ label, children, tone }: { label: string; children?: React.ReactNode; tone?: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-1.5">
      <dt className="shrink-0 text-sm text-muted-foreground">{label}</dt>
      <dd className={cn('min-w-0 break-all text-right text-sm font-medium', tone || 'text-foreground')}>
        {children ?? <span className="font-normal text-muted-foreground">暂无数据</span>}
      </dd>
    </div>
  )
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('status')
  const [systemStatus, setSystemStatus] = useState<SystemStatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  // 运行时监控（旧 SystemRuntime 的迁移）
  const [responseTime, setResponseTime] = useState<number | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [errorCount, setErrorCount] = useState(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const [toast, setToast] = useState<ToastState>(null)

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), TOAST_DURATION_MS)
    return () => clearTimeout(t)
  }, [toast])

  const fetchStatus = useCallback(async () => {
    const start = Date.now()
    try {
      const res = await systemService.getStatus()
      const latency = Date.now() - start
      setResponseTime(latency)
      if (res.data) {
        setSystemStatus(res.data)
        setLastUpdate(new Date())
        setLoadError(null)
        setErrorCount(0)
      } else {
        setErrorCount((c) => c + 1)
      }
    } catch (e) {
      setResponseTime(Date.now() - start)
      setErrorCount((c) => c + 1)
      setLoadError(e instanceof Error ? e.message : '未知错误')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    timerRef.current = setInterval(fetchStatus, POLL_INTERVAL_MS)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [fetchStatus])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchStatus()
    setToast({ type: 'success', text: '系统状态已更新' })
  }

  const online: 'online' | 'warning' | 'offline' =
    errorCount >= 3 ? 'offline' : errorCount >= 1 ? 'warning' : 'online'

  const perf =
    responseTime === null
      ? null
      : responseTime < 300
        ? { text: '良好', percent: 20 }
        : responseTime < 800
          ? { text: '正常', percent: 50 }
          : responseTime < 1500
            ? { text: '较慢', percent: 75 }
            : { text: '较差', percent: 95 }

  const timeSince = lastUpdate
    ? `${Math.floor((Date.now() - lastUpdate.getTime()) / 1000)} 秒前`
    : '暂无数据'

  const navItems: Array<{ key: TabKey; label: string; icon: typeof Activity }> = [
    { key: 'status', label: '系统状态', icon: Activity },
    { key: 'config', label: '当前配置', icon: SlidersHorizontal },
  ]

  return (
    <AppShell>
      <div className="space-y-6">
        {/* 标题区 */}
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1">
            <h1 className="font-serif text-2xl font-semibold tracking-tight text-foreground">系统设置</h1>
            <p className="text-sm text-muted-foreground">
              查看运行状态与当前配置。配置在线修改接口尚未迁移，暂只读展示。
            </p>
          </div>
          <button
            type="button"
            onClick={handleRefresh}
            disabled={refreshing}
            className="inline-flex h-9 items-center gap-2 rounded-md border border-input bg-card px-4 text-sm font-medium text-secondary-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground disabled:opacity-60"
          >
            <RefreshCw className={cn('h-4 w-4', refreshing && 'animate-spin')} strokeWidth={1.9} />
            刷新状态
          </button>
        </div>

        {/* 固定位置 toast */}
        {toast && (
          <div
            className={cn(
              'fixed left-1/2 top-6 z-50 -translate-x-1/2 rounded-md px-4 py-2.5 text-sm font-medium shadow-lg',
              toast.type === 'success'
                ? 'bg-emerald-600 text-white'
                : 'bg-destructive text-destructive-foreground'
            )}
          >
            {toast.text}
          </div>
        )}

        <div className="flex flex-col gap-6 md:flex-row">
          {/* 左侧分段导航 */}
          <nav className="flex shrink-0 gap-1 overflow-x-auto md:w-44 md:flex-col">
            {navItems.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                type="button"
                onClick={() => setActiveTab(key)}
                className={cn(
                  'flex h-10 shrink-0 items-center gap-2.5 rounded-md px-3.5 text-sm font-medium transition-colors',
                  activeTab === key
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-[18px] w-[18px]" strokeWidth={1.8} />
                {label}
              </button>
            ))}
          </nav>

          <div className="min-w-0 flex-1">
            {activeTab === 'status' && (
              <div className="space-y-4">
                {/* 系统运行状态监控 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      系统运行状态监控
                      <span className="text-xs font-normal text-muted-foreground">每 10 秒自动刷新</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {loading && !systemStatus ? (
                      <div className="space-y-3">
                        <Skeleton className="h-6 w-40" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-16 w-full" />
                      </div>
                    ) : online === 'offline' ? (
                      <div className="flex items-start gap-3 rounded-md border border-destructive/40 bg-destructive/5 p-4">
                        <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
                        <div className="space-y-1">
                          <p className="text-sm font-medium text-destructive">系统离线</p>
                          <p className="text-sm text-muted-foreground">
                            无法连接到系统后端服务{loadError ? `：${loadError}` : ''}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="flex flex-wrap items-center gap-3">
                          <span
                            className={cn(
                              'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
                              online === 'online'
                                ? 'bg-emerald-600/10 text-emerald-600'
                                : 'bg-amber-500/10 text-amber-600'
                            )}
                          >
                            {online === 'online' ? (
                              <CheckCircle2 className="h-3.5 w-3.5" />
                            ) : (
                              <AlertTriangle className="h-3.5 w-3.5" />
                            )}
                            {online === 'online' ? '系统在线' : '响应异常'}
                          </span>
                          {responseTime !== null && (
                            <span className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
                              响应时间：{responseTime} ms
                            </span>
                          )}
                          <span className="text-xs text-muted-foreground">最后更新：{timeSince}</span>
                        </div>

                        {perf && (
                          <div className="space-y-1.5">
                            <p className="text-sm text-muted-foreground">系统响应性能：{perf.text}</p>
                            <Progress value={perf.percent} />
                          </div>
                        )}

                        <div className="grid gap-4 sm:grid-cols-2">
                          <div className="rounded-md border p-4">
                            <p className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Clock className="h-3.5 w-3.5" /> 应用运行时间
                            </p>
                            <p className="mt-1 text-lg font-semibold text-foreground">暂无数据</p>
                            <p className="mt-1 text-xs text-muted-foreground">运行时接口未迁移</p>
                          </div>
                          <div className="rounded-md border p-4">
                            <p className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Clock className="h-3.5 w-3.5" /> 系统时间
                            </p>
                            <p className="mt-1 text-lg font-semibold text-foreground">暂无数据</p>
                            <p className="mt-1 text-xs text-muted-foreground">运行时接口未迁移</p>
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* 三栏信息板块 */}
                <div className="grid gap-4 lg:grid-cols-3">
                  {/* 系统 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Server className="h-4 w-4 text-muted-foreground" /> 系统
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <dl>
                        <InfoRow label="版本" />
                        <InfoRow label="状态">
                          <StatusBadge status={systemStatus?.status} />
                        </InfoRow>
                        <InfoRow label="后端" tone="text-foreground">
                          {systemStatus?.backend ?? '暂无数据'}
                        </InfoRow>
                        <InfoRow label="平台" />
                        <InfoRow label="应用运行时间" />
                        <InfoRow label="服务器地址" />
                      </dl>
                    </CardContent>
                  </Card>

                  {/* 数据库与推理服务 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Database className="h-4 w-4 text-muted-foreground" /> 数据库与推理服务
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <dl>
                        <InfoRow label="数据库状态" />
                        <InfoRow label="数据库类型" />
                        <InfoRow label="数据库版本" />
                        <InfoRow label="向量状态" />
                        <InfoRow label="向量驱动" />
                        <InfoRow label="推理服务状态">
                          <StatusBadge status={systemStatus?.inference_service} />
                        </InfoRow>
                        <InfoRow label="多模态 API" />
                        <InfoRow label="当前 AI 分析模型">{CURRENT_VISION_MODEL}</InfoRow>
                        <InfoRow label="Embedding 模型">{CURRENT_EMBEDDING_MODEL}</InfoRow>
                        <InfoRow label="Embedding 维度" />
                      </dl>
                    </CardContent>
                  </Card>

                  {/* 存储 */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Cloud className="h-4 w-4 text-muted-foreground" /> 存储
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-3">
                        <div className="rounded-md border p-3">
                          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <FileImage className="h-3.5 w-3.5" /> 图片总数
                          </p>
                          <p className="mt-1 text-xl font-semibold text-foreground">
                            {systemStatus?.image_count ?? 0}
                            <span className="ml-1 text-xs font-normal text-muted-foreground">张</span>
                          </p>
                        </div>
                        <div className="rounded-md border p-3">
                          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <Boxes className="h-3.5 w-3.5" /> 标签总数
                          </p>
                          <p className="mt-1 text-xl font-semibold text-foreground">暂无数据</p>
                        </div>
                      </div>
                      <dl>
                        <InfoRow label="数据库路径" />
                        <InfoRow label="图片目录" />
                        <InfoRow label="存储总大小" />
                        <InfoRow label="缓存大小" />
                        <InfoRow label="统计时间" />
                      </dl>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {activeTab === 'config' && (
              <div className="space-y-4">
                <div className="flex items-start gap-3 rounded-md border border-amber-500/40 bg-amber-500/5 p-4">
                  <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
                  <div className="space-y-1 text-sm">
                    <p className="font-medium text-amber-700">配置读写接口尚未迁移</p>
                    <p className="text-muted-foreground">
                      旧设置页的保存、重置、清除缓存操作依赖 getSystemConfig / updateSystemConfig / clearCache 等接口，
                      这些接口在 next-app 中还没有实现，本页暂只展示当前生效的配置，不支持在线修改。
                    </p>
                  </div>
                </div>

                {/* 模型配置 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Cpu className="h-4 w-4 text-muted-foreground" /> 模型配置
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl>
                      <InfoRow label="AI 分析模型">{CURRENT_VISION_MODEL}</InfoRow>
                      <InfoRow label="Embedding 模型">{CURRENT_EMBEDDING_MODEL}</InfoRow>
                      <InfoRow label="Embedding 维度" />
                      <InfoRow label="可用视觉模型列表" />
                      <InfoRow label="语义搜索状态">
                        <StatusBadge status={systemStatus?.inference_service === 'ok' ? 'available' : undefined} />
                      </InfoRow>
                    </dl>
                  </CardContent>
                </Card>

                {/* 存储配置 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <HardDrive className="h-4 w-4 text-muted-foreground" /> 存储配置
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl>
                      <InfoRow label="存储根目录" />
                      <InfoRow label="缓存目录" />
                      <InfoRow label="最大缓存大小" />
                      <InfoRow label="当前缓存大小" />
                      <InfoRow label="图片总数" tone="text-foreground">
                        {systemStatus?.image_count ?? 0} 张
                      </InfoRow>
                    </dl>
                  </CardContent>
                </Card>

                {/* 向量数据库配置 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Database className="h-4 w-4 text-muted-foreground" /> 向量数据库配置
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <dl>
                      <InfoRow label="sqlite-vec 驱动状态" />
                      <InfoRow label="驱动路径" />
                      <InfoRow label="title 向量条目数" />
                      <InfoRow label="description 向量条目数" />
                      <InfoRow label="image 向量条目数" />
                    </dl>
                  </CardContent>
                </Card>

                {/* API 配置 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Settings2 className="h-4 w-4 text-muted-foreground" /> API 配置
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-start gap-3 rounded-md border border-amber-500/40 bg-amber-500/5 p-3">
                      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                      <p className="text-sm text-muted-foreground">
                        API 密钥是敏感信息，仅保存在服务器端配置文件中，本页不展示密钥内容。
                      </p>
                    </div>
                    <dl>
                      <InfoRow label="API 密钥" />
                      <InfoRow label="API 基础 URL" />
                    </dl>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  )
}
