/**
 * REST_OBSERVER: an independent HTTP client on the live API using the GUI token. It never goes
 * through the MCP server, so an observable and the MCP result come from two different paths.
 */

export type RestResponse = { status: number; json: unknown; text: string };

export class RestObserver {
  constructor(
    private readonly apiBase: string,
    private readonly token: string,
    private readonly timeoutMs = 60_000,
  ) {}

  /** `scheme://host:port` of the API (for `/openapi.json`). */
  origin(): string {
    return new URL(this.apiBase).origin;
  }

  private async request(method: string, url: string, body?: unknown): Promise<Response> {
    return fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${this.token}`,
        ...(body === undefined ? {} : { "content-type": "application/json" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
  }

  private static async parse(res: Response): Promise<RestResponse> {
    const text = await res.text();
    let json: unknown = null;
    if (text) {
      try {
        json = JSON.parse(text);
      } catch {
        json = null;
      }
    }
    return { status: res.status, json, text };
  }

  /** GET `path` relative to the API base (`/downloads`). */
  async get(path: string): Promise<RestResponse> {
    return RestObserver.parse(await this.request("GET", `${this.apiBase}${path}`));
  }

  /** Any method relative to the API base. */
  async send(method: string, path: string, body?: unknown): Promise<RestResponse> {
    return RestObserver.parse(await this.request(method, `${this.apiBase}${path}`, body));
  }

  /** GET an absolute path on the API origin (`/openapi.json`). */
  async getOrigin(path: string): Promise<RestResponse> {
    return RestObserver.parse(await this.request("GET", `${this.origin()}${path}`));
  }

  /** Raw bytes (capture images). */
  async bytes(path: string): Promise<{ status: number; bytes: Uint8Array }> {
    const res = await this.request("GET", `${this.apiBase}${path}`);
    return { status: res.status, bytes: new Uint8Array(await res.arrayBuffer()) };
  }
}
