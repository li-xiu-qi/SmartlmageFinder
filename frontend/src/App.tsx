import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import AppShell from '@/components/layout/AppShell';
import { TooltipProvider } from '@/components/ui/tooltip';

// 路由页面按需代码分割
const HomePage = lazy(() => import('@/pages/home'));
const ImagesPage = lazy(() => import('@/pages/images/ImagePage'));
const UploadPage = lazy(() => import('@/pages/upload'));
const SearchPage = lazy(() => import('@/pages/search'));
const TagsPage = lazy(() => import('@/pages/tags'));
const SettingsPage = lazy(() => import('@/pages/settings'));
const NotFoundPage = lazy(() => import('@/pages/404'));

// 全局组件
import GlobalAIFloatButton from '@/components/GlobalAIFloatButton';

function PageLoading() {
  return (
    <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
      加载中…
    </div>
  );
}

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          // 暖白画廊主题：赭石主色，与 shadcn 变量对齐
          colorPrimary: '#b1502c',
          colorInfo: '#b1502c',
          colorLink: '#b1502c',
          colorBgLayout: '#f5f1e9',
          colorBgContainer: '#fdfbf7',
          colorBorder: '#e3dccd',
          colorBorderSecondary: '#ece7db',
          borderRadius: 8,
          fontFamily:
            '"PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        },
        components: {
          Card: { borderRadiusLG: 10 },
          Button: { borderRadius: 8 },
        },
      }}
    >
      <AntdApp>
        <TooltipProvider delayDuration={200}>
          <BrowserRouter>
            <Suspense fallback={<PageLoading />}>
              <Routes>
                <Route element={<AppShell />}>
                  <Route path="/" element={<HomePage />} />
                  <Route path="images" element={<ImagesPage />} />
                  <Route path="upload" element={<UploadPage />} />
                  <Route path="search" element={<SearchPage />} />
                  <Route path="tags" element={<TagsPage />} />
                  <Route path="settings" element={<SettingsPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </Suspense>

            {/* 全局AI悬浮按钮 */}
            <GlobalAIFloatButton />
          </BrowserRouter>
        </TooltipProvider>
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
