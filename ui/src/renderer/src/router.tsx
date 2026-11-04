import {
  createHashHistory,
  createRootRoute,
  createRoute,
  createRouter,
  lazyRouteComponent,
  Outlet,
} from '@tanstack/react-router'

import { AppShell } from './components/layout/AppShell'
import { ModuleSkeleton } from './components/ModuleSkeleton'
import { DownloaderPage } from './features/downloader/DownloaderPage'
import { SettingsPage } from './features/settings/SettingsPage'
import { TranscriptPage } from './features/transcript/TranscriptPage'
import { TTSPage } from './features/tts/TTSPage'

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
  component: TTSPage,
})

const convertRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/convert',
  pendingComponent: ModuleSkeleton,
  component: lazyRouteComponent(() => import('./features/converter/ConvertPage'), 'ConvertPage'),
})

const captureRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/capture',
  pendingComponent: ModuleSkeleton,
  component: lazyRouteComponent(() => import('./features/capture/CapturePage'), 'CapturePage'),
})

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: SettingsPage,
})

const routeTree = rootRoute.addChildren([
  homeRoute,
  transcriptRoute,
  ttsRoute,
  convertRoute,
  captureRoute,
  settingsRoute,
])

export const router = createRouter({
  routeTree,
  history: hashHistory,
  defaultPreload: 'intent',
})
