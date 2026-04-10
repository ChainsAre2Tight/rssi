import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './app/App.tsx'

import "./styles/tokens.css"
import "./styles/themes.css"
import "./styles/global.css"
import "./styles/panel.css"

document.documentElement.dataset.theme = "light"

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
