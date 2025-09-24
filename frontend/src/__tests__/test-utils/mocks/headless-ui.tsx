import React from 'react';
import { vi } from 'vitest';

vi.mock('@headlessui/react', () => {
  const DialogBase = ({ children, className }: any) => (
    <div data-testid="dialog" className={className}>
      {children}
    </div>
  );
  (DialogBase as any).Panel = ({ children }: any) => (
    <div data-testid="dialog-panel">{children}</div>
  );
  (DialogBase as any).Title = ({ children }: any) => (
    <h2 data-testid="dialog-title">{children}</h2>
  );
  (DialogBase as any).Description = ({ children }: any) => (
    <p data-testid="dialog-description">{children}</p>
  );
  return { Dialog: DialogBase };
});
