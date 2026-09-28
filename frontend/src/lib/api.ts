import {
  AreasResponse,
  AreasResponseSchema,
  ContactResponse,
  ContactResponseSchema,
  DemandCluster,
  MenuPlan,
  MenuPlanSchema,
  NegotiationResult,
  NegotiationResultSchema,
  OptimizeRequest,
  OptimizeResponse,
  OptimizeResponseSchema,
  Provider,
  ProviderMatch,
  ProviderOnboarding,
  ProviderSchema,
} from "./schemas"

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000/api/v1"

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message)
    this.name = "ApiError"
  }
}

async function handleResponse<T>(res: Response, parser: (data: unknown) => T): Promise<T> {
  if (!res.ok) {
    let errorCode = `HTTP_${res.status}`
    let errorMsg = `Request failed with status ${res.status}`
    try {
      const errorJson = await res.json()
      if (errorJson?.error) {
        errorCode = errorJson.error.code || errorCode
        errorMsg = errorJson.error.message || errorMsg
      }
    } catch {
      // Non-JSON error body
    }
    throw new ApiError(res.status, errorCode, errorMsg)
  }
  const json = await res.json()
  return parser(json)
}

export const api = {
  async getAreas(): Promise<AreasResponse> {
    const res = await fetch(`${BASE_URL}/areas`, { method: "GET" })
    return handleResponse(res, (data) => AreasResponseSchema.parse(data))
  },

  async match(payload: {
    area?: string
    cluster_id?: string
    diet?: string
    budget_max?: number
    radius_km?: number
    top_n?: number
  }): Promise<{ cluster: DemandCluster; matches: ProviderMatch[] }> {
    const res = await fetch(`${BASE_URL}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return handleResponse(res, (data) => data as { cluster: DemandCluster; matches: ProviderMatch[] })
  },

  async getProvider(id: string): Promise<Provider> {
    const res = await fetch(`${BASE_URL}/providers/${encodeURIComponent(id)}`, { method: "GET" })
    return handleResponse(res, (data) => ProviderSchema.parse(data))
  },

  async getMenu(providerId: string, clusterId: string): Promise<MenuPlan> {
    const res = await fetch(`${BASE_URL}/menu`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider_id: providerId, cluster_id: clusterId }),
    })
    return handleResponse(res, (data) => MenuPlanSchema.parse(data))
  },

  async negotiate(
    providerId: string,
    clusterId: string,
    maxRounds: number = 5
  ): Promise<NegotiationResult> {
    const res = await fetch(`${BASE_URL}/negotiate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider_id: providerId,
        cluster_id: clusterId,
        max_rounds: maxRounds,
      }),
    })
    return handleResponse(res, (data) => NegotiationResultSchema.parse(data))
  },

  async optimize(payload: OptimizeRequest): Promise<OptimizeResponse> {
    const res = await fetch(`${BASE_URL}/optimize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return handleResponse(res, (data) => OptimizeResponseSchema.parse(data))
  },

  async onboardProvider(
    payload: ProviderOnboarding
  ): Promise<{ id: string; status: string; message: string }> {
    const res = await fetch(`${BASE_URL}/providers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return handleResponse(res, (data) => data as { id: string; status: string; message: string })
  },

  async getContact(providerId: string): Promise<ContactResponse> {
    const res = await fetch(`${BASE_URL}/providers/${encodeURIComponent(providerId)}/contact`, {
      method: "GET",
    })
    return handleResponse(res, (data) => ContactResponseSchema.parse(data))
  },
}
