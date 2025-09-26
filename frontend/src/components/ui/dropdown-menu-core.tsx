import React, { createContext, useContext, useRef, useEffect, useState } from 'react';
import { ChevronRight } from 'lucide-react';

interface DropdownMenuContextValue {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const DropdownMenuContext = createContext<DropdownMenuContextValue>({
  isOpen: false,
  setIsOpen: () => {},
});

interface DropdownMenuProps extends React.HTMLAttributes<HTMLDivElement> {
  trigger: React.ReactNode;
}

const DropdownMenu = React.forwardRef<HTMLDivElement, DropdownMenuProps>(
  ({ className, trigger, children, ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
          setIsOpen(false);
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
      <DropdownMenuContext.Provider value={{ isOpen, setIsOpen }}>
        <div ref={dropdownRef} className={`relative inline-block ${className || ''}`} {...props}>
          <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
          {isOpen && (
            <div className="absolute z-50 mt-2 min-w-[8rem] overflow-hidden rounded-md border bg-white shadow-md">
              {children}
            </div>
          )}
        </div>
      </DropdownMenuContext.Provider>
    );
  }
);

interface DropdownMenuItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode;
  inset?: boolean;
}

const DropdownMenuItem = React.forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
  ({ className, children, icon, inset, ...props }, ref) => (
    <button
      ref={ref}
      className={`relative flex w-full cursor-pointer select-none items-center px-2 py-1.5 text-sm outline-none hover:bg-gray-100 ${
        inset ? 'pl-8' : ''
      } ${className || ''}`}
      {...props}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  )
);

interface DropdownMenuSubMenuProps extends React.HTMLAttributes<HTMLDivElement> {
  trigger: React.ReactNode;
}

const DropdownMenuSubMenu = React.forwardRef<HTMLDivElement, DropdownMenuSubMenuProps>(
  ({ className, trigger, children, ...props }, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const subMenuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (subMenuRef.current && !subMenuRef.current.contains(event.target as Node)) {
          setIsOpen(false);
        }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
      <div ref={subMenuRef} className="relative" {...props}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex w-full items-center justify-between px-2 py-1.5 text-sm hover:bg-gray-100"
        >
          {trigger}
          <ChevronRight className="ml-auto h-4 w-4" />
        </button>
        {isOpen && (
          <div className="absolute left-full top-0 ml-1 min-w-[8rem] overflow-hidden rounded-md border bg-white shadow-md">
            {children}
          </div>
        )}
      </div>
    );
  }
);

DropdownMenu.displayName = 'DropdownMenu';
DropdownMenuItem.displayName = 'DropdownMenuItem';
DropdownMenuSubMenu.displayName = 'DropdownMenuSubMenu';

export { DropdownMenu, DropdownMenuItem, DropdownMenuSubMenu };
