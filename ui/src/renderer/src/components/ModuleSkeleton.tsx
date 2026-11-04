type ModuleSkeletonProps = {
  label?: string
}

export function ModuleSkeleton({ label = 'Connecting to backend…' }: ModuleSkeletonProps) {
  return (
    <div className="bg-bg text-fg p-6" data-testid="module-skeleton">
      {label}
    </div>
  )
}
