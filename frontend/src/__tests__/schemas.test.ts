import { describe, it, expect } from "vitest"
import {
  DietSchema,
  DishSchema,
  ProviderSchema,
  ProviderMatchSchema,
  DemandClusterSchema,
  MenuPlanSchema,
  NegotiationResultSchema,
  TraceStepSchema,
  OptimizeRequestSchema,
  OptimizeResponseSchema,
  ProviderOnboardingSchema,
} from "@/lib/schemas"

describe("Zod Domain Schemas", () => {
  describe("DietSchema", () => {
    it("accepts valid diets", () => {
      expect(DietSchema.parse("veg")).toBe("veg")
      expect(DietSchema.parse("non_veg")).toBe("non_veg")
      expect(DietSchema.parse("egg")).toBe("egg")
    })

    it("rejects unknown diet strings", () => {
      expect(() => DietSchema.parse("vegan_keto")).toThrow()
    })
  })

  describe("DishSchema", () => {
    it("validates a complete dish", () => {
      const raw = {
        id: "d101",
        name: "Paneer Butter Masala",
        slot: "lunch",
        diet: "veg",
        cuisine: "North Indian",
        main_item: "paneer",
        cost_tier: 2,
      }
      const parsed = DishSchema.parse(raw)
      expect(parsed.name).toBe("Paneer Butter Masala")
      expect(parsed.cost_tier).toBe(2)
    })

    it("rejects invalid slot or cost tier", () => {
      expect(() =>
        DishSchema.parse({
          id: "d102",
          name: "Invalid Slot",
          slot: "breakfast",
          diet: "veg",
          cuisine: "North Indian",
          main_item: "poha",
          cost_tier: 1,
        })
      ).toThrow()

      expect(() =>
        DishSchema.parse({
          id: "d103",
          name: "Invalid Tier",
          slot: "dinner",
          diet: "veg",
          cuisine: "North Indian",
          main_item: "dal",
          cost_tier: 5,
        })
      ).toThrow()
    })
  })

  describe("ProviderSchema", () => {
    it("validates a full provider with defaults", () => {
      const raw = {
        id: "p1",
        name: "Annapurna Kitchen",
        town: "Kota",
        area: "Vigyan Nagar",
        lat: 25.132,
        lon: 75.845,
        cuisines: ["North Indian", "Rajasthani"],
        diet_types: ["veg"],
        capacity_total: 60,
        capacity_available: 25,
        list_price_monthly: 3200,
        cost_per_meal: 45,
        min_margin: 0.15,
        flexibility: 0.7,
        rating: 4.6,
      }
      const parsed = ProviderSchema.parse(raw)
      expect(parsed.name).toBe("Annapurna Kitchen")
      expect(parsed.status).toBe("approved")
      expect(parsed.dishes).toEqual([])
    })
  })

  describe("ProviderMatchSchema", () => {
    it("validates multi-factor match result", () => {
      const raw = {
        provider_id: "p1",
        score: 0.88,
        factors: {
          distance: 0.95,
          cuisine_fit: 0.8,
          price_fit: 0.9,
          capacity_fit: 1.0,
          rating: 0.92,
        },
        distance_km: 1.2,
        reason: "Excellent proximity (1.2km) and great North Indian cuisine fit",
      }
      const parsed = ProviderMatchSchema.parse(raw)
      expect(parsed.score).toBe(0.88)
      expect(parsed.factors.distance).toBe(0.95)
    })
  })

  describe("DemandClusterSchema", () => {
    it("validates student demand cluster data", () => {
      const raw = {
        id: "c1",
        town: "Kota",
        area: "Mahaveer Nagar",
        lat: 25.14,
        lon: 75.85,
        headcount: 35,
        budget_ceiling_monthly: 3500,
        cuisine_weights: { "North Indian": 0.7, "South Indian": 0.3 },
        diet_split: { veg: 0.8, non_veg: 0.2 },
        flexibility: 0.6,
      }
      const parsed = DemandClusterSchema.parse(raw)
      expect(parsed.headcount).toBe(35)
      expect(parsed.cuisine_weights["North Indian"]).toBe(0.7)
    })
  })

  describe("MenuPlanSchema", () => {
    it("validates 7-day meal plan with llm or fallback source", () => {
      const raw = {
        provider_id: "p1",
        cluster_id: "c1",
        source: "fallback",
        rationale: "Rotating homestyle selection with balanced protein",
        days: [
          {
            day: 1,
            lunch: { dish_id: "d1", name: "Dal Tadka" },
            dinner: { dish_id: "d2", name: "Aloo Gobhi" },
          },
        ],
      }
      const parsed = MenuPlanSchema.parse(raw)
      expect(parsed.source).toBe("fallback")
      expect(parsed.days[0].lunch.name).toBe("Dal Tadka")
    })
  })

  describe("NegotiationResultSchema", () => {
    it("validates deal outcome with monotonic rounds", () => {
      const raw = {
        status: "deal",
        final_price: 3100,
        floor: 2800,
        ceiling: 3400,
        volume_discount: 0.1,
        rounds: [
          { round: 1, provider_ask: 3400, cluster_bid: 2720 },
          { round: 2, provider_ask: 3250, cluster_bid: 2950 },
          { round: 3, provider_ask: 3100, cluster_bid: 3100 },
        ],
        note: "Volume agreement reached at ₹3,100/mo",
      }
      const parsed = NegotiationResultSchema.parse(raw)
      expect(parsed.status).toBe("deal")
      expect(parsed.rounds.length).toBe(3)
      expect(parsed.final_price).toBe(3100)
    })

    it("allows final_price to be null when status is no_deal", () => {
      const raw = {
        status: "no_deal",
        final_price: null,
        floor: 3800,
        ceiling: 3200,
        volume_discount: 0.05,
        rounds: [{ round: 1, provider_ask: 3800, cluster_bid: 2560 }],
        note: "Budget ceiling lower than provider minimum floor",
      }
      const parsed = NegotiationResultSchema.parse(raw)
      expect(parsed.status).toBe("no_deal")
      expect(parsed.final_price).toBeNull()
    })
  })

  describe("TraceStepSchema & OptimizeResponseSchema", () => {
    it("validates trace step metrics", () => {
      const step = {
        agent: "menu",
        started_ms: 100,
        duration_ms: 320,
        used_llm: true,
        fallback_used: false,
        error: null,
      }
      const parsed = TraceStepSchema.parse(step)
      expect(parsed.agent).toBe("menu")
      expect(parsed.used_llm).toBe(true)
      expect(parsed.fallback_used).toBe(false)
    })

    it("validates end-to-end optimize response shape", () => {
      const response = {
        cluster: null,
        matches: [],
        top_provider: null,
        menu: null,
        negotiation: null,
        trace: [
          {
            agent: "demand",
            started_ms: 10,
            duration_ms: 45,
            used_llm: false,
            fallback_used: false,
          },
        ],
        errors: [],
      }
      const parsed = OptimizeResponseSchema.parse(response)
      expect(parsed.trace.length).toBe(1)
      expect(parsed.errors).toEqual([])
    })

    it("validates optimize request shape", () => {
      const req = {
        area: "Vigyan Nagar",
        diet: "veg" as const,
        budget_max: 3500,
        cuisines: ["North Indian"],
        radius_km: 5.0,
        top_n: 5,
      }
      const parsed = OptimizeRequestSchema.parse(req)
      expect(parsed.area).toBe("Vigyan Nagar")
      expect(parsed.budget_max).toBe(3500)
    })
  })

  describe("ProviderOnboardingSchema", () => {
    const validPayload = {
      name: "Radhe Shyam Tiffin",
      town: "Manipal",
      area: "Eshwar Nagar",
      lat: 13.35,
      lon: 74.78,
      cuisines: ["South Indian", "North Indian"],
      diet_types: ["veg", "egg"],
      capacity_total: 50,
      capacity_available: 20,
      list_price_monthly: 3200,
      cost_per_meal: 40,
      min_margin: 0.15,
      flexibility: 0.5,
      phone: "+91 9876543210",
      consent_given: true,
    }

    it("accepts valid onboarding payload", () => {
      const parsed = ProviderOnboardingSchema.parse(validPayload)
      expect(parsed.consent_given).toBe(true)
      expect(parsed.name).toBe("Radhe Shyam Tiffin")
    })

    it("fails when consent_given is false", () => {
      expect(() =>
        ProviderOnboardingSchema.parse({
          ...validPayload,
          consent_given: false,
        })
      ).toThrow("You must consent")
    })

    it("fails when phone is too short or fields are negative", () => {
      expect(() =>
        ProviderOnboardingSchema.parse({
          ...validPayload,
          phone: "123",
        })
      ).toThrow()

      expect(() =>
        ProviderOnboardingSchema.parse({
          ...validPayload,
          capacity_total: -10,
        })
      ).toThrow()
    })
  })
})
