// Mock for Framer Motion
vi.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    span: 'span',
    tr: 'tr',
    td: 'td',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
}))
