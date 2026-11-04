import './boot-theme'

import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from '@tanstack/react-router'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { queryClient } from './lib/query-client'
import { router } from './router'
import './styles.css'

if (window.location.hash === '' || window.location.hash === '#') {
  window.location.hash = '/'
}

const rootEl = document.getElementById('root')
if (rootEl === null) {
  throw new Error('missing #root')
}

createRoot(rootEl).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
)
