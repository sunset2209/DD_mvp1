import { forwardRef, InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium mb-2 text-foreground">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'input',
            error && 'border-destructive-foreground focus:border-destructive-foreground',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-destructive-foreground">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }
