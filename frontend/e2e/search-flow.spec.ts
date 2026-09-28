import { test, expect } from "@playwright/test"

test.describe("Search to Results Flow", () => {
  test("smoke test: user selects area, searches, and views matches with trace panel", async ({
    page,
  }) => {
    // 1. Mock API /api/v1/areas
    await page.route("**/api/v1/areas", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          areas: [
            {
              id: "c-kota-1",
              town: "Kota",
              area: "Vigyan Nagar",
              cluster_id: "c-kota-1",
              lat: 25.132,
              lon: 75.845,
              headcount: 40,
            },
            {
              id: "c-manipal-1",
              town: "Manipal",
              area: "Eshwar Nagar",
              cluster_id: "c-manipal-1",
              lat: 13.35,
              lon: 74.78,
              headcount: 35,
            },
          ],
          towns: ["Kota", "Manipal"],
        }),
      })
    })

    // 2. Mock API /api/v1/optimize
    await page.route("**/api/v1/optimize", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          cluster: {
            id: "c-kota-1",
            town: "Kota",
            area: "Vigyan Nagar",
            lat: 25.132,
            lon: 75.845,
            headcount: 40,
            budget_ceiling_monthly: 3600,
            cuisine_weights: { "North Indian": 0.8, Rajasthani: 0.2 },
            diet_split: { veg: 0.9, non_veg: 0.1 },
            flexibility: 0.7,
          },
          matches: [
            {
              provider_id: "p-annapurna",
              score: 0.92,
              factors: {
                distance: 0.96,
                cuisine_fit: 0.9,
                price_fit: 0.88,
                capacity_fit: 1.0,
                rating: 0.92,
              },
              distance_km: 0.8,
              reason: "Outstanding proximity (0.8km) and high North Indian cuisine fit",
            },
          ],
          top_provider: {
            id: "p-annapurna",
            name: "Annapurna Shudh Shakahari Bhojanalaya",
            town: "Kota",
            area: "Vigyan Nagar",
            lat: 25.135,
            lon: 75.848,
            cuisines: ["North Indian", "Rajasthani"],
            diet_types: ["veg"],
            capacity_total: 80,
            capacity_available: 30,
            list_price_monthly: 3200,
            cost_per_meal: 45,
            min_margin: 0.15,
            flexibility: 0.6,
            rating: 4.8,
            dishes: [],
            status: "approved",
          },
          menu: {
            provider_id: "p-annapurna",
            cluster_id: "c-kota-1",
            source: "llm",
            rationale: "Wholesome 7-day rotating vegetarian thali rotation.",
            days: [
              {
                day: 1,
                lunch: { dish_id: "d1", name: "Dal Makhani & Roti" },
                dinner: { dish_id: "d2", name: "Paneer Bhurji & Paratha" },
              },
            ],
          },
          negotiation: {
            status: "deal",
            final_price: 2950,
            floor: 2700,
            ceiling: 3200,
            volume_discount: 0.1,
            rounds: [
              { round: 1, provider_ask: 3200, cluster_bid: 2560 },
              { round: 2, provider_ask: 3050, cluster_bid: 2800 },
              { round: 3, provider_ask: 2950, cluster_bid: 2950 },
            ],
            note: "10% group discount agreed for 40 students.",
          },
          trace: [
            {
              agent: "demand",
              started_ms: 100,
              duration_ms: 35,
              used_llm: false,
              fallback_used: false,
            },
            {
              agent: "match",
              started_ms: 135,
              duration_ms: 45,
              used_llm: false,
              fallback_used: false,
            },
            {
              agent: "menu",
              started_ms: 180,
              duration_ms: 420,
              used_llm: true,
              fallback_used: false,
            },
            {
              agent: "deal",
              started_ms: 600,
              duration_ms: 30,
              used_llm: false,
              fallback_used: false,
            },
          ],
          errors: [],
        }),
      })
    })

    // Navigate to homepage
    await page.goto("/")

    // Verify title and search form
    await expect(page).toHaveTitle(/MessMate/i)
    await expect(page.getByText(/Reliable Daily Tiffin Matches/i)).toBeVisible()

    // Select town/area or click search
    const searchBtn = page.getByRole("button", { name: /Search & Optimize Tiffin Matches/i })
    await expect(searchBtn).toBeVisible()
    await searchBtn.click()

    // Should navigate to /results
    await page.waitForURL(/\/results/)

    // Verify results page content
    await expect(page.getByText(/Ranked Tiffin Providers/i)).toBeVisible()
    await expect(
      page.getByText(/Annapurna Shudh Shakahari Bhojanalaya/i)
    ).toBeVisible()

    // Verify score badge and reason
    await expect(page.getByText("92%")).toBeVisible()
    await expect(
      page.getByText(/Outstanding proximity \(0\.8km\)/i)
    ).toBeVisible()

    // Verify AgentTracePanel is visible
    await expect(
      page.getByText(/LangGraph Agent Observability Trace/i)
    ).toBeVisible()
    await expect(page.getByText(/4 steps/i)).toBeVisible()

    // Verify pricing disclaimer is present
    await expect(
      page.getByText(/Important Pricing Disclaimer/i)
    ).toBeVisible()
  })
})
