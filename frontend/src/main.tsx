import { createRoot } from 'react-dom/client'
import App from './App.tsx'

// 去掉严格模式以避免 findDOMNode 警告
createRoot(document.getElementById('root')!).render(
  <App />
)
