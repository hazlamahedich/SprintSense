export type WebSocketHandler = (data: any) => void

export class WebSocketService {
  private static instance: WebSocketService
  private ws: WebSocket | null = null
  private handlers: Set<WebSocketHandler> = new Set()
  private subscriptions: Map<string, Set<WebSocketHandler>> = new Map()
  private messageQueue: Set<string> = new Set()
  private connecting: boolean = false
  private connected: boolean = false
  private reconnectHandlers: Set<() => void> = new Set()

  private constructor() {}

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService()
    }
    return WebSocketService.instance
  }

  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return
    if (this.connecting) return

    this.connecting = true
    this.ws = new WebSocket(process.env.WS_URL || 'ws://localhost:8080')

    this.ws.onopen = () => {
      this.connecting = false
      this.connected = true
      this.reconnectHandlers.forEach((handler) => handler())
    }

    this.ws.onclose = () => {
      this.connecting = false
      this.connected = false
      setTimeout(() => this.connect(), 1000) // Reconnect after 1 second
    }

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      // First notify type-specific handlers
      if (message.type && this.subscriptions.has(message.type)) {
        const handlers = this.subscriptions.get(message.type)
        handlers?.forEach((handler) => handler(message))
      }
      // Then notify generic handlers
      this.handlers.forEach((handler) => handler(message))
    }
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.connecting = false
      this.connected = false
    }
  }

  public isConnecting(): boolean {
    return this.connecting
  }

  public isConnected(): boolean {
    return this.connected
  }

  public subscribe(type: string, handler: WebSocketHandler): void {
    if (!this.subscriptions.has(type)) {
      this.subscriptions.set(type, new Set())
    }
    this.subscriptions.get(type)?.add(handler)
  }

  public unsubscribe(type: string, handler: WebSocketHandler): void {
    this.subscriptions.get(type)?.delete(handler)
    if (this.subscriptions.get(type)?.size === 0) {
      this.subscriptions.delete(type)
    }
  }

  public emit(type: string, data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, message queued')
      this.messageQueue.add(JSON.stringify({ type, data }))
      return
    }

    // Support message deduplication
    if (data.messageId) {
      if (this.messageQueue.has(data.messageId)) {
        return // Skip duplicate message
      }
      this.messageQueue.add(data.messageId)
      // Cleanup old messages after 5 minutes
      setTimeout(() => this.messageQueue.delete(data.messageId), 5 * 60 * 1000)
    }

    this.ws.send(JSON.stringify({ type, data }))
  }

  public addHandler(handler: WebSocketHandler): () => void {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }

  public onReconnect(handler: () => void): void {
    this.reconnectHandlers.add(handler)
  }

  public offReconnect(handler: () => void): void {
    this.reconnectHandlers.delete(handler)
  }
}

export default WebSocketService.getInstance()
