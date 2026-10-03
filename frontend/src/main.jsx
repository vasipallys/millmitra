import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import App from './App.jsx'
import { I18nProvider } from './i18n/I18nContext.jsx'
import { clearDevServiceWorkers } from './utils/pwaRuntime.js'
import './index.css'

const queryClient = new QueryClient()

function renderApp() {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true
          }}
        >
          <I18nProvider>
            <App />
          </I18nProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>,
  )
}

clearDevServiceWorkers()
  .then((shouldReload) => {
    if (shouldReload) {
      window.location.reload()
      return
    }
    renderApp()
  })
  .catch(() => {
    renderApp()
  })
