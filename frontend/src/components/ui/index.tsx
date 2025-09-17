// Temporary implementation using Material UI while we build the complete UI system
import React from 'react';
import {
  Button as MuiButton,
  Card as MuiCard,
  CardHeader as MuiCardHeader,
  CardContent as MuiCardContent,
  TextField as MuiTextField,
  Chip as MuiChip,
  Alert as MuiAlert,
  AlertTitle as MuiAlertTitle,
  Dialog as MuiDialog,
  DialogTitle as MuiDialogTitle,
  DialogContent as MuiDialogContent,
  DialogActions as MuiDialogActions,
  Select as MuiSelect,
  MenuItem as MuiMenuItem,
  FormControl as MuiFormControl,
  InputLabel as MuiInputLabel,
  Box,
  Typography
} from '@mui/material';
import type { ButtonProps as MuiButtonProps } from '@mui/material/Button';
import type { CardProps as MuiCardProps } from '@mui/material/Card';
import type { TextFieldProps as MuiTextFieldProps } from '@mui/material/TextField';
import type { ChipProps as MuiChipProps } from '@mui/material/Chip';
import type { AlertProps as MuiAlertProps } from '@mui/material/Alert';
import type { DialogProps as MuiDialogProps } from '@mui/material/Dialog';

// Button component
export interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'default', size = 'default', ...props }, ref) => {
    const getVariant = () => {
      switch (variant) {
        case 'outline': return 'outlined';
        case 'secondary': return 'text';
        case 'ghost': return 'text';
        case 'link': return 'text';
        default: return 'contained';
      }
    };

    const getSize = () => {
      switch (size) {
        case 'sm': return 'small';
        case 'lg': return 'large';
        default: return 'medium';
      }
    };

    return (
      <MuiButton
        ref={ref}
        variant={getVariant()}
        size={getSize()}
        color={variant === 'destructive' ? 'error' : 'primary'}
        {...props}
      />
    );
  }
);

// Card components
export const Card = React.forwardRef<HTMLDivElement, MuiCardProps>((props, ref) => (
  <MuiCard ref={ref} {...props} />
));

export const CardHeader = ({ className, children, ...props }: any) => (
  <MuiCardHeader title={children} {...props} />
);

export const CardContent = React.forwardRef<HTMLDivElement, any>((props, ref) => (
  <MuiCardContent ref={ref} {...props} />
));

export const CardFooter = ({ children, className, ...props }: any) => (
  <Box sx={{ p: 2, pt: 0 }} className={className} {...props}>
    {children}
  </Box>
);

// Input component
export const Input = React.forwardRef<HTMLInputElement, MuiTextFieldProps>((props, ref) => (
  <MuiTextField
    ref={ref}
    variant="outlined"
    size="small"
    fullWidth
    {...props}
  />
));

// Label component (simplified)
export const Label = ({ children, htmlFor, ...props }: any) => (
  <Typography variant="body2" component="label" htmlFor={htmlFor} {...props}>
    {children}
  </Typography>
);

// Textarea component
export const Textarea = React.forwardRef<HTMLTextAreaElement, any>(({ rows = 3, ...props }, ref) => (
  <MuiTextField
    ref={ref}
    variant="outlined"
    multiline
    rows={rows}
    fullWidth
    {...props}
  />
));

// Badge component
export const Badge = React.forwardRef<HTMLDivElement, MuiChipProps & { variant?: string; children?: React.ReactNode }>(
  ({ variant, children, ...props }, ref) => (
    <MuiChip
      ref={ref}
      size="small"
      color={variant === 'secondary' ? 'default' : 'primary'}
      label={children}
      {...props}
    />
  )
);

// Alert components
export const Alert = React.forwardRef<HTMLDivElement, MuiAlertProps & { variant?: string }>(
  ({ variant, ...props }, ref) => (
    <MuiAlert
      ref={ref}
      severity={variant === 'destructive' ? 'error' : 'info'}
      {...props}
    />
  )
);

export const AlertDescription = ({ children, ...props }: any) => (
  <div {...props}>{children}</div>
);

// Dialog components
export const Dialog = MuiDialog;
export const DialogContent = MuiDialogContent;
export const DialogHeader = ({ children, ...props }: any) => (
  <Box {...props}>{children}</Box>
);
export const DialogTitle = MuiDialogTitle;
export const DialogFooter = MuiDialogActions;

// Select components (simplified implementation)
export const Select = ({ children, onValueChange, value, disabled, ...props }: any) => (
  <MuiFormControl fullWidth size="small">
    <MuiSelect
      value={value || ''}
      onChange={(e) => onValueChange?.(e.target.value)}
      disabled={disabled}
      {...props}
    >
      {children}
    </MuiSelect>
  </MuiFormControl>
);

export const SelectContent = ({ children }: any) => <>{children}</>;
export const SelectItem = ({ value, children }: any) => (
  <MuiMenuItem value={value}>{children}</MuiMenuItem>
);
export const SelectTrigger = ({ children }: any) => <>{children}</>;
export const SelectValue = () => null;

// Dropdown menu components (placeholder)
export const DropdownMenu = ({ children }: any) => <>{children}</>;
export const DropdownMenuTrigger = ({ children }: any) => <>{children}</>;
export const DropdownMenuContent = ({ children }: any) => <>{children}</>;
export const DropdownMenuLabel = ({ children }: any) => <Typography variant="subtitle2">{children}</Typography>;
export const DropdownMenuSeparator = () => <hr />;
export const DropdownMenuCheckboxItem = ({ children, checked, onCheckedChange }: any) => (
  <MuiMenuItem onClick={() => onCheckedChange?.(!checked)}>
    <input type="checkbox" checked={checked} readOnly />
    {children}
  </MuiMenuItem>
);
export const DropdownMenuRadioGroup = ({ children, onValueChange }: any) =>
  React.cloneElement(children, { onValueChange });
export const DropdownMenuRadioItem = ({ children, value, onSelect }: any) => (
  <MuiMenuItem onClick={() => onSelect?.(value)}>{children}</MuiMenuItem>
);

// Toggle group components (placeholder)
export const ToggleGroup = ({ children, onValueChange, value }: any) => (
  <Box sx={{ display: 'flex', gap: 1 }}>
    {React.Children.map(children, (child: any) =>
      React.cloneElement(child, {
        selected: child.props.value === value,
        onClick: () => onValueChange?.(child.props.value)
      })
    )}
  </Box>
);

export const ToggleGroupItem = ({ children, selected, onClick, className }: any) => (
  <MuiButton
    variant={selected ? 'contained' : 'outlined'}
    size="small"
    onClick={onClick}
    className={className}
  >
    {children}
  </MuiButton>
);
