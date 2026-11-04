import {
  createHashHistory,
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from '@tanstack/react-router'
import { lazy } from 'react'

import { AppShell } from './components/layout/AppShell'
import { ModuleSkeleton } from './components/ModuleSkeleton'
import { DownloaderPage } from './features/downloader/DownloaderPage'
import { SettingsChrome } from './features/settings/SettingsChrome'
import { TranscriptPage } from './features/transcript/TranscriptPage'

const LazyPlaceholder = lazy(async () => {
  const mod = await import('./features/shell/LazyPlaceholder')
  return { default: mod.LazyPlaceholder }
})

const hashHistory = createHashHistory()

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
  pendingComponent: ModuleSkeleton,
})

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: DownloaderPage,
})

const transcriptRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/transcript',
  component: TranscriptPage,
})

const ttsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/tts',
  component: LazyPlaceholder,
})

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: SettingsChrome,
})

const routeTree = rootRoute.addChildren([homeRoute, transcriptRoute, ttsRoute, settingsRoute])

export const router = createRouter({
  routeTree,
  history: hashHistory,
  defaultPreload: 'intent',
})
