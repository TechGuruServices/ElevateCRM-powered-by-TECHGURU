import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
  placeholder?: string;
  label?: string;
}

export function Select({ 
  children, 
  className, 
  placeholder, 
  label,
  ...props 
}: SelectProps) {
  return (
    <div className="relative">
      <select
        className={cn(
          "w-full h-12 px-3 pr-10 bg-white/50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-md focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-slate-900 dark:text-slate-100 appearance-none",
          className
        )}
        aria-label={label || placeholder}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {children}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
    </div>
  )
}