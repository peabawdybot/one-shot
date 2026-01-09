import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { VibeKanbanWebCompanion } from 'vibe-kanban-web-companion'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <VibeKanbanWebCompanion />
    <App />
  </StrictMode>,
)
