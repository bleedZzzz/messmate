import { z } from "zod"

export const DietSchema = z.enum(["veg", "non_veg", "egg"])
export type Diet = z.infer<typeof DietSchema>

export const DishSchema = z.object({
  id: z.string(),
  name: z.string(),
  slot: z.enum(["lunch", "dinner"]),
  diet: DietSchema,
  cuisine: z.string(),
  main_item: z.string(),
  cost_tier: z.union([z.literal(1), z.literal(2), z.literal(3)]),
})
export type Dish = z.infer<typeof DishSchema>

export const ProviderSchema = z.object({
  id: z.string(),
  name: z.string(),
  town: z.string(),
  area: z.string(),
  lat: z.number(),
  lon: z.number(),
  cuisines: z.array(z.string()),
  diet_types: z.array(DietSchema),
  capacity_total: z.number(),
  capacity_available: z.number(),
  list_price_monthly: z.number(),
  cost_per_meal: z.number(),
  min_margin: z.number(),
  flexibility: z.number(),
  rating: z.number(),
  dishes: z.array(DishSchema).default([]),
  phone: z.string().nullable().optional(),
  status: z.enum(["pending", "approved", "rejected"]).default("approved"),
})
export type Provider = z.infer<typeof ProviderSchema>

export const ProviderMatchSchema = z.object({
  provider_id: z.string(),
  score: z.number(),
  factors: z.record(z.string(), z.number()),
  distance_km: z.number(),
  reason: z.string(),
})
export type ProviderMatch = z.infer<typeof ProviderMatchSchema>

export const DemandClusterSchema = z.object({
  id: z.string(),
  town: z.string(),
  area: z.string(),
  lat: z.number(),
  lon: z.number(),
  headcount: z.number(),
  budget_ceiling_monthly: z.number(),
  cuisine_weights: z.record(z.string(), z.number()),
  diet_split: z.record(z.string(), z.number()),
  flexibility: z.number(),
})
export type DemandCluster = z.infer<typeof DemandClusterSchema>

export const MealPickSchema = z.object({
  dish_id: z.string(),
  name: z.string(),
})
export type MealPick = z.infer<typeof MealPickSchema>

export const DayPlanSchema = z.object({
  day: z.number(),
  lunch: MealPickSchema,
  dinner: MealPickSchema,
})
export type DayPlan = z.infer<typeof DayPlanSchema>

export const MenuPlanSchema = z.object({
  provider_id: z.string(),
  cluster_id: z.string(),
  days: z.array(DayPlanSchema),
  source: z.enum(["llm", "fallback"]),
  rationale: z.string(),
})
export type MenuPlan = z.infer<typeof MenuPlanSchema>

export const NegotiationRoundSchema = z.object({
  round: z.number(),
  provider_ask: z.number(),
  cluster_bid: z.number(),
})
export type NegotiationRound = z.infer<typeof NegotiationRoundSchema>

export const NegotiationResultSchema = z.object({
  status: z.enum(["deal", "compromise", "no_deal"]),
  final_price: z.number().nullable(),
  floor: z.number(),
  ceiling: z.number(),
  volume_discount: z.number(),
  rounds: z.array(NegotiationRoundSchema),
  note: z.string(),
})
export type NegotiationResult = z.infer<typeof NegotiationResultSchema>

export const TraceStepSchema = z.object({
  agent: z.string(),
  started_ms: z.number(),
  duration_ms: z.number(),
  used_llm: z.boolean(),
  fallback_used: z.boolean(),
  error: z.string().nullable().optional(),
})
export type TraceStep = z.infer<typeof TraceStepSchema>

export const OptimizeRequestSchema = z.object({
  area_id: z.string().optional(),
  area: z.string().optional(),
  cluster_id: z.string().optional(),
  lat: z.number().optional(),
  lon: z.number().optional(),
  diet: DietSchema.optional(),
  budget_max: z.number().optional(),
  cuisines: z.array(z.string()).default([]),
  radius_km: z.number().default(5.0),
  top_n: z.number().default(5),
})
export type OptimizeRequest = z.infer<typeof OptimizeRequestSchema>

export const OptimizeResponseSchema = z.object({
  cluster: DemandClusterSchema.nullable().optional(),
  matches: z.array(ProviderMatchSchema).default([]),
  top_provider: ProviderSchema.nullable().optional(),
  menu: MenuPlanSchema.nullable().optional(),
  negotiation: NegotiationResultSchema.nullable().optional(),
  trace: z.array(TraceStepSchema).default([]),
  errors: z.array(z.string()).default([]),
})
export type OptimizeResponse = z.infer<typeof OptimizeResponseSchema>

export const AreaItemSchema = z.object({
  id: z.string(),
  town: z.string(),
  area: z.string(),
  cluster_id: z.string(),
  lat: z.number(),
  lon: z.number(),
  headcount: z.number(),
})
export type AreaItem = z.infer<typeof AreaItemSchema>

export const AreasResponseSchema = z.object({
  areas: z.array(AreaItemSchema),
  towns: z.array(z.string()),
})
export type AreasResponse = z.infer<typeof AreasResponseSchema>

export const ContactResponseSchema = z.object({
  provider_id: z.string(),
  whatsapp_url: z.string(),
})
export type ContactResponse = z.infer<typeof ContactResponseSchema>

export const ProviderOnboardingSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  town: z.string().min(2, "Town must be at least 2 characters"),
  area: z.string().min(2, "Area must be at least 2 characters"),
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
  cuisines: z.array(z.string()).min(1, "Select at least one cuisine"),
  diet_types: z.array(DietSchema).min(1, "Select at least one diet option"),
  capacity_total: z.number().positive("Capacity must be positive"),
  capacity_available: z.number().nonnegative("Available capacity cannot be negative"),
  list_price_monthly: z.number().positive("Price must be positive"),
  cost_per_meal: z.number().positive("Cost per meal must be positive"),
  min_margin: z.number().min(0).max(1),
  flexibility: z.number().min(0).max(1),
  phone: z.string().min(8, "Phone must have at least 8 digits"),
  consent_given: z.boolean().refine((val) => val === true, {
    message: "You must consent to provider registration and contact terms",
  }),
})
export type ProviderOnboarding = z.infer<typeof ProviderOnboardingSchema>
