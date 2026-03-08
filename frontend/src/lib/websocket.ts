const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/v1/agent/ws";

export type WSMessageHandler = (data: unknown) => void;
export type WSErrorHandler = (error: Event) => void;
export type WSCloseHandler = () => void;

export class AgentWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private onMessageHandlers: WSMessageHandler[] = [];
  private onErrorHandlers: WSErrorHandler[] = [];
  private onCloseHandlers: WSCloseHandler[] = [];
  private onOpenHandlers: (() => void)[] = [];
  private sessionId?: number;

  connect(sessionId?: number) {
    this.sessionId = sessionId;
    const token = localStorage.getItem("access_token");
    const url = new URL(WS_BASE_URL);
    if (token) url.searchParams.set("token", token);
    if (sessionId) url.searchParams.set("session_id", String(sessionId));

    this.ws = new WebSocket(url.toString());

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.onOpenHandlers.forEach((h) => h());
    };

    this.ws.onmessage = (event) => {
      let data: unknown;
      try {
        data = JSON.parse(event.data as string);
      } catch {
        data = event.data;
      }
      this.onMessageHandlers.forEach((h) => h(data));
    };

    this.ws.onerror = (error) => {
      this.onErrorHandlers.forEach((h) => h(error));
    };

    this.ws.onclose = () => {
      this.onCloseHandlers.forEach((h) => h());
      this.attemptReconnect();
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    this.reconnectAttempts++;
    setTimeout(() => {
      this.connect(this.sessionId);
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  send(message: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  onMessage(handler: WSMessageHandler) {
    this.onMessageHandlers.push(handler);
    return () => {
      this.onMessageHandlers = this.onMessageHandlers.filter((h) => h !== handler);
    };
  }

  onError(handler: WSErrorHandler) {
    this.onErrorHandlers.push(handler);
    return () => {
      this.onErrorHandlers = this.onErrorHandlers.filter((h) => h !== handler);
    };
  }

  onClose(handler: WSCloseHandler) {
    this.onCloseHandlers.push(handler);
    return () => {
      this.onCloseHandlers = this.onCloseHandlers.filter((h) => h !== handler);
    };
  }

  onOpen(handler: () => void) {
    this.onOpenHandlers.push(handler);
    return () => {
      this.onOpenHandlers = this.onOpenHandlers.filter((h) => h !== handler);
    };
  }

  disconnect() {
    this.maxReconnectAttempts = 0;
    this.ws?.close();
    this.ws = null;
  }

  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}
