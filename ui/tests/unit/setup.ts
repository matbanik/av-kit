/// <reference types="@testing-library/jest-dom/vitest" />

const OriginalResponse = globalThis.Response

class ResponseAllowEmpty extends OriginalResponse {
  constructor(body?: BodyInit | null, init?: ResponseInit) {
    const status = init?.status
    if (status === 204 || status === 205 || status === 304) {
      super(null, init)
      return
    }
    super(body, init)
  }
}

globalThis.Response = ResponseAllowEmpty as typeof OriginalResponse
