import { vi } from 'vitest'

// Module state to ensure it's shared across all instances
const state = {
  handlers: {} as { [key: string]: Array<(data: any) => void> },
  connected: false,
  connecting: false,
  // Track seen messageIds for deduplication
  seen: new Set<string>(),
  // Map original subscriber handlers to wrapped handlers that perform per-subscriber deduplication
  wrapperMap: new Map<Function, Function>(),
}

const mockWebSocketService = {
  isConnected: vi.fn().mockImplementation(() => state.connected),
  isConnecting: vi.fn().mockImplementation(() => state.connecting),
  connect: vi.fn().mockImplementation(() => {
    state.connecting = false
    state.connected = true
    // trigger reconnect handlers if any
    if (state.handlers['reconnect']) {
      state.handlers['reconnect'].forEach((h) => h())
    }
  }),
  disconnect: vi.fn().mockImplementation(() => {
    state.connected = false
    state.connecting = true // simulate reconnecting state
  }),
  subscribe: vi
    .fn()
    .mockImplementation((type: string, handler: (data: any) => void) => {
      if (!state.handlers[type]) {
        state.handlers[type] = []
      }
      // Wrap the handler to add per-subscriber messageId deduplication
      if (!state.wrapperMap.has(handler)) {
        const seen = new Set<string>()
        const wrapped = (data: any) => {
          const messageId = data?.messageId
          if (messageId) {
            const key = `${type}:${messageId}`
            if (seen.has(key)) return
            seen.add(key)
          }
          handler(data)
        }
        state.wrapperMap.set(handler, wrapped)
      }
      const wrappedHandler = state.wrapperMap.get(handler) as (
        data: any
      ) => void
      state.handlers[type].push(wrappedHandler)
    }),
  unsubscribe: vi
    .fn()
    .mockImplementation((type: string, handler: (data: any) => void) => {
      if (state.handlers[type]) {
        const wrapped =
          (state.wrapperMap.get(handler) as (data: any) => void) || handler
        const index = state.handlers[type].indexOf(wrapped)
        if (index !== -1) {
          state.handlers[type].splice(index, 1)
        }
        // Clean up wrapper map to avoid memory leaks
        if (state.wrapperMap.has(handler)) {
          state.wrapperMap.delete(handler)
        }
      }
    }),
  emit: vi.fn().mockImplementation((type: string, data: any) => {
    // Deduplicate by messageId if present
    const messageId = data?.messageId
    if (messageId) {
      const key = `${type}:${messageId}`
      console.log('WS emit:', {
        type,
        messageId,
        key,
        seen: Array.from(state.seen),
      })
      if (state.seen.has(key)) {
        console.log('Skipping duplicate message:', key)
        return
      }
      state.seen.add(key)
      console.log('Added key to seen:', key)
    } else {
      console.log('WS emit (no messageId):', { type, data })
    }

    if (state.handlers[type]) {
      state.handlers[type].forEach((handler) => handler(data))
      console.log('Called handlers for:', type)
    }
  }),
  onReconnect: vi.fn().mockImplementation((handler: () => void) => {
    if (!state.handlers['reconnect']) {
      state.handlers['reconnect'] = []
    }
    state.handlers['reconnect'].push(handler)
  }),
  offReconnect: vi.fn().mockImplementation((handler: () => void) => {
    if (state.handlers['reconnect']) {
      const index = state.handlers['reconnect'].indexOf(handler)
      if (index !== -1) {
        state.handlers['reconnect'].splice(index, 1)
      }
    }
  }),
}

class MockWebSocketService {
  private static instance: MockWebSocketService
  private constructor() {}

  public static getInstance(): MockWebSocketService {
    if (!MockWebSocketService.instance) {
      MockWebSocketService.instance = new MockWebSocketService()
    }
    return MockWebSocketService.instance
  }

  public isConnected(): boolean {
    return state.connected
  }

  public isConnecting(): boolean {
    return state.connecting
  }

  public connect(): void {
    state.connecting = false
    state.connected = true
    // trigger reconnect handlers if any
    if (state.handlers['reconnect']) {
      state.handlers['reconnect'].forEach((h) => h())
    }
  }

  public disconnect(): void {
    state.connected = false
    state.connecting = true
  }

  public subscribe(type: string, handler: (data: any) => void): void {
    if (!state.handlers[type]) {
      state.handlers[type] = []
    }
    // Wrap the handler to add per-subscriber messageId deduplication
    if (!state.wrapperMap.has(handler)) {
      const seen = new Set<string>()
      const wrapped = (data: any) => {
        const messageId = data?.messageId
        if (messageId) {
          const key = `${type}:${messageId}`
          if (seen.has(key)) return
          seen.add(key)
        }
        handler(data)
      }
      state.wrapperMap.set(handler, wrapped)
    }
    const wrappedHandler = state.wrapperMap.get(handler) as (data: any) => void
    state.handlers[type].push(wrappedHandler)
  }

  public unsubscribe(type: string, handler: (data: any) => void): void {
    if (state.handlers[type]) {
      const wrapped =
        (state.wrapperMap.get(handler) as (data: any) => void) || handler
      const index = state.handlers[type].indexOf(wrapped)
      if (index !== -1) {
        state.handlers[type].splice(index, 1)
      }
      // Clean up wrapper map to avoid memory leaks
      if (state.wrapperMap.has(handler)) {
        state.wrapperMap.delete(handler)
      }
    }
  }

  public emit(type: string, data: any): void {
    // Deduplicate by messageId if present (global across service)
    const messageId = data?.messageId
    if (messageId) {
      const key = `${type}:${messageId}`
      if (state.seen.has(key)) {
        return // Skip duplicate message
      }
      state.seen.add(key)
    }

    if (state.handlers[type]) {
      state.handlers[type].forEach((handler) => handler(data))
    }
  }

  public onReconnect(handler: () => void): void {
    if (!state.handlers['reconnect']) {
      state.handlers['reconnect'] = []
    }
    state.handlers['reconnect'].push(handler)
  }

  public offReconnect(handler: () => void): void {
    if (state.handlers['reconnect']) {
      const index = state.handlers['reconnect'].indexOf(handler)
      if (index !== -1) {
        state.handlers['reconnect'].splice(index, 1)
      }
    }
  }

  // For tests to reset state
  public static resetState(): void {
    state.connected = false
    state.connecting = false
    state.handlers = {}
    state.seen.clear()
    state.wrapperMap.clear()
  }
}

export { MockWebSocketService as WebSocketService, mockWebSocketService }
