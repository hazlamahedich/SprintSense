// Temporary implementation using Material UI while we build the complete UI system
import React from 'react'
import {
  Button as MuiButton,
  Card as MuiCard,
  CardHeader as MuiCardHeader,
  CardContent as MuiCardContent,
  TextField as MuiTextField,
  Chip as MuiChip,
  Alert as MuiAlert,
  Dialog as MuiDialog,
  DialogTitle as MuiDialogTitle,
  DialogContent as MuiDialogContent,
  DialogActions as MuiDialogActions,
  Select as MuiSelect,
  MenuItem as MuiMenuItem,
  FormControl as MuiFormControl,
  Box,
  Typography,
} from '@mui/material'
import type { ButtonProps as MuiButtonProps } from '@mui/material/Button'
import type { CardProps as MuiCardProps } from '@mui/material/Card'
import type { TextFieldProps as MuiTextFieldProps } from '@mui/material/TextField'
import type { ChipProps as MuiChipProps } from '@mui/material/Chip'
import type { AlertProps as MuiAlertProps } from '@mui/material/Alert'

// Button component
export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?:
    | 'default'
    | 'destructive'
    | 'outline'
    | 'secondary'
    | 'ghost'
    | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'default', size = 'default', ...props }, ref) => {
    const getVariant = () => {
      switch (variant) {
        case 'outline':
          return 'outlined'
        case 'secondary':
          return 'text'
        case 'ghost':
          return 'text'
        case 'link':
          return 'text'
        default:
          return 'contained'
      }
    }

    const getSize = () => {
      switch (size) {
        case 'sm':
          return 'small'
        case 'lg':
          return 'large'
        default:
          return 'medium'
      }
    }

    return (
      <MuiButton
        ref={ref}
        variant={getVariant()}
        size={getSize()}
        color={variant === 'destructive' ? 'error' : 'primary'}
        {...props}
      />
    )
  }
)

// Card components
export const Card = React.forwardRef<HTMLDivElement, MuiCardProps>(
  (props, ref) => <MuiCard ref={ref} {...props} />
)

interface CardHeaderProps {
  className?: string
  children?: React.ReactNode
  [key: string]: unknown
}

export const CardHeader = ({ children, ...props }: CardHeaderProps) => (
  <MuiCardHeader title={children} {...props} />
)

export const CardContent = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<typeof MuiCardContent>
>((props, ref) => <MuiCardContent ref={ref} {...props} />)

interface CardFooterProps {
  children?: React.ReactNode
  className?: string
  [key: string]: unknown
}

export const CardFooter = ({
  children,
  className,
  ...props
}: CardFooterProps) => (
  <Box sx={{ p: 2, pt: 0 }} className={className} {...props}>
    {children}
  </Box>
)

// Input component
export const Input = React.forwardRef<HTMLInputElement, MuiTextFieldProps>(
  (props, ref) => (
    <MuiTextField
      ref={ref}
      variant="outlined"
      size="small"
      fullWidth
      {...props}
    />
  )
)

// Label component (simplified)
interface LabelProps {
  children?: React.ReactNode
  htmlFor?: string
  [key: string]: unknown
}

export const Label = ({ children, htmlFor, ...props }: LabelProps) => (
  <Typography variant="body2" component="label" htmlFor={htmlFor} {...props}>
    {children}
  </Typography>
)

// Textarea component
interface TextareaProps extends Omit<MuiTextFieldProps, 'multiline'> {
  rows?: number
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ rows = 3, ...props }, ref) => (
    <MuiTextField
      ref={ref}
      variant="outlined"
      multiline
      rows={rows}
      fullWidth
      {...props}
    />
  )
)

// Badge component
export const Badge = React.forwardRef<
  HTMLDivElement,
  MuiChipProps & { variant?: string; children?: React.ReactNode }
>(({ variant, children, ...props }, ref) => (
  <MuiChip
    ref={ref}
    size="small"
    color={variant === 'secondary' ? 'default' : 'primary'}
    label={children}
    {...props}
  />
))

// Alert components
export const Alert = React.forwardRef<
  HTMLDivElement,
  MuiAlertProps & { variant?: string }
>(({ variant, ...props }, ref) => (
  <MuiAlert
    ref={ref}
    severity={variant === 'destructive' ? 'error' : 'info'}
    {...props}
  />
))

interface AlertDescriptionProps {
  children?: React.ReactNode
  [key: string]: unknown
}

export const AlertDescription = ({
  children,
  ...props
}: AlertDescriptionProps) => <div {...props}>{children}</div>

// Dialog components
export const Dialog = MuiDialog
export const DialogContent = MuiDialogContent
interface DialogHeaderProps {
  children?: React.ReactNode
  [key: string]: unknown
}

export const DialogHeader = ({ children, ...props }: DialogHeaderProps) => (
  <Box {...props}>{children}</Box>
)
export const DialogTitle = MuiDialogTitle
export const DialogFooter = MuiDialogActions

// Select components (simplified implementation)
interface SelectProps {
  children?: React.ReactNode
  onValueChange?: (value: string) => void
  value?: string
  disabled?: boolean
  [key: string]: unknown
}

export const Select = ({
  children,
  onValueChange,
  value,
  disabled,
  ...props
}: SelectProps) => (
  <MuiFormControl fullWidth size="small">
    <MuiSelect
      value={value || ''}
      onChange={(e) => onValueChange?.(e.target.value as string)}
      disabled={disabled}
      {...props}
    >
      {children}
    </MuiSelect>
  </MuiFormControl>
)

interface SelectContentProps {
  children?: React.ReactNode
}
export const SelectContent = ({ children }: SelectContentProps) => (
  <>{children}</>
)

interface SelectItemProps {
  value: string
  children?: React.ReactNode
}
export const SelectItem = ({ value, children }: SelectItemProps) => (
  <MuiMenuItem value={value}>{children}</MuiMenuItem>
)

interface SelectTriggerProps {
  children?: React.ReactNode
}
export const SelectTrigger = ({ children }: SelectTriggerProps) => (
  <>{children}</>
)

export const SelectValue = () => null

// Dropdown menu components (placeholder)
interface DropdownMenuProps {
  children?: React.ReactNode
}
export const DropdownMenu = ({ children }: DropdownMenuProps) => <>{children}</>

interface DropdownMenuTriggerProps {
  children?: React.ReactNode
}
export const DropdownMenuTrigger = ({ children }: DropdownMenuTriggerProps) => (
  <>{children}</>
)

interface DropdownMenuContentProps {
  children?: React.ReactNode
}
export const DropdownMenuContent = ({ children }: DropdownMenuContentProps) => (
  <>{children}</>
)

interface DropdownMenuLabelProps {
  children?: React.ReactNode
}
export const DropdownMenuLabel = ({ children }: DropdownMenuLabelProps) => (
  <Typography variant="subtitle2">{children}</Typography>
)

export const DropdownMenuSeparator = () => <hr />

interface DropdownMenuCheckboxItemProps {
  children?: React.ReactNode
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}
export const DropdownMenuCheckboxItem = ({
  children,
  checked,
  onCheckedChange,
}: DropdownMenuCheckboxItemProps) => (
  <MuiMenuItem onClick={() => onCheckedChange?.(!checked)}>
    <input type="checkbox" checked={checked} readOnly />
    {children}
  </MuiMenuItem>
)

interface DropdownMenuRadioGroupProps {
  children: React.ReactElement
  onValueChange?: (value: string) => void
}
export const DropdownMenuRadioGroup = ({
  children,
  onValueChange,
}: DropdownMenuRadioGroupProps) =>
  React.cloneElement(children, { onValueChange })

interface DropdownMenuRadioItemProps {
  children?: React.ReactNode
  value: string
  onSelect?: (value: string) => void
}
export const DropdownMenuRadioItem = ({
  children,
  value,
  onSelect,
}: DropdownMenuRadioItemProps) => (
  <MuiMenuItem onClick={() => onSelect?.(value)}>{children}</MuiMenuItem>
)

// Toggle group components (placeholder)
interface ToggleGroupProps {
  children: React.ReactNode
  onValueChange?: (value: string) => void
  value?: string
}
export const ToggleGroup = ({
  children,
  onValueChange,
  value,
}: ToggleGroupProps) => (
  <Box sx={{ display: 'flex', gap: 1 }}>
    {React.Children.map(children, (child) => {
      if (React.isValidElement(child)) {
        return React.cloneElement(child, {
          selected: child.props.value === value,
          onClick: () => onValueChange?.(child.props.value),
        } as Record<string, unknown>)
      }
      return child
    })}
  </Box>
)

interface ToggleGroupItemProps {
  children?: React.ReactNode
  selected?: boolean
  onClick?: () => void
  className?: string
}
export const ToggleGroupItem = ({
  children,
  selected,
  onClick,
  className,
}: ToggleGroupItemProps) => (
  <MuiButton
    variant={selected ? 'contained' : 'outlined'}
    size="small"
    onClick={onClick}
    className={className}
  >
    {children}
  </MuiButton>
)
