import { describe, it, expect } from 'vitest'
import { baseTheme } from './index'

describe('Theme Configuration', () => {
  it('should have correct primary color', () => {
    expect(baseTheme.palette.primary.main).toBe('#1976d2')
    expect(baseTheme.palette.primary.light).toBe('#42a5f5')
    expect(baseTheme.palette.primary.dark).toBe('#1565c0')
  })

  it('should have correct secondary color', () => {
    expect(baseTheme.palette.secondary.main).toBe('#dc004e')
    expect(baseTheme.palette.secondary.light).toBe('#ff5983')
    expect(baseTheme.palette.secondary.dark).toBe('#9a0036')
  })

  it('should have correct background colors', () => {
    expect(baseTheme.palette.background.default).toBe('#f5f5f5')
    expect(baseTheme.palette.background.paper).toBe('#ffffff')
  })

  it('should have correct border radius', () => {
    expect(baseTheme.shape.borderRadius).toBe(8)
  })

  it('should have correct typography settings', () => {
    expect(baseTheme.typography.fontFamily).toBe('"Roboto", "Helvetica", "Arial", sans-serif')
    expect(baseTheme.typography.h4?.fontWeight).toBe(600)
    expect(baseTheme.typography.h5?.fontWeight).toBe(500)
  })

  it('should have button text transform disabled', () => {
    const buttonStyles = baseTheme.components?.MuiButton?.styleOverrides?.root as Record<string, unknown>
    expect(buttonStyles?.textTransform).toBe('none')
  })
})