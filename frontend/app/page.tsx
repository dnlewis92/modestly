"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FilterSidebar, Filters } from "@/components/FilterSidebar";
import { ProductCard, Product } from "@/components/ProductCard";

const DEFAULT_FILTERS: Filters = {
  retailers: [],
  minDiscount: 0,
  maxPrice: 200,
  priceDropOnly: false,
  sortBy: "discount",
};

function buildQuery(filters: Filters, page: number): string {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("limit", "48");
  params.set("max_price", String(filters.maxPrice));
  params.set("sort_by", filters.sortBy);
  if (filters.minDiscount > 0) params.set("min_discount", String(filters.minDiscount));
  if (filters.priceDropOnly) params.set("price_dropped", "true");
  if (filters.retailers.length > 0)
    params.set("retailer", filters.retailers.join(","));
  return `/api/products?${params.toString()}`;
}

export default function Home() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<{
    total_items: number;
    on_sale: number;
    price_drops: number;
  } | null>(null);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  // Fetch stats once
  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then(setStats)
      .catch(() => {});
  }, []);

  const fetchProducts = useCallback(
    async (f: Filters, p: number) => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setLoading(true);
      try {
        const res = await fetch(buildQuery(f, p), {
          signal: controller.signal,
        });
        const data = await res.json();
        setProducts(data.items ?? []);
        setTotalPages(data.pages ?? 1);
        setTotal(data.total ?? 0);
      } catch (e: unknown) {
        if (e instanceof Error && e.name !== "AbortError") {
          setProducts([]);
        }
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Refetch when filters or page change
  useEffect(() => {
    fetchProducts(filters, page);
  }, [filters, page, fetchProducts]);

  const handleFiltersChange = (next: Filters) => {
    setFilters(next);
    setPage(1);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-white/95 backdrop-blur border-b border-stone-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-stone-900">
              Modestly
            </h1>
            <p className="text-xs text-stone-400 mt-0.5 hidden sm:block">
              Fashionable modest clothing &middot; best deals from top retailers
            </p>
          </div>

          {/* Mobile filter toggle */}
          <button
            className="lg:hidden text-sm font-medium text-stone-600 border border-stone-200 rounded-lg px-3 py-2 hover:bg-stone-50"
            onClick={() => setMobileFiltersOpen((v) => !v)}
          >
            {mobileFiltersOpen ? "Hide Filters" : "Filters"}
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 flex gap-8">
        {/* Sidebar */}
        <div
          className={`${
            mobileFiltersOpen ? "block" : "hidden"
          } lg:block fixed lg:static inset-0 lg:inset-auto z-10 lg:z-auto bg-white lg:bg-transparent pt-20 lg:pt-0 px-4 lg:px-0 overflow-y-auto lg:overflow-visible`}
        >
          <FilterSidebar
            filters={filters}
            onChange={handleFiltersChange}
            stats={stats ?? undefined}
          />
        </div>

        {/* Main */}
        <main className="flex-1 min-w-0">
          {/* Result count + loading */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-stone-500">
              {loading ? (
                "Loading..."
              ) : (
                <>
                  <span className="font-semibold text-stone-800">
                    {total.toLocaleString()}
                  </span>{" "}
                  items found
                </>
              )}
            </p>
          </div>

          {/* Empty state */}
          {!loading && products.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center gap-3">
              <p className="text-4xl">🧺</p>
              <p className="text-stone-600 font-medium">No items yet</p>
              <p className="text-stone-400 text-sm max-w-xs">
                Run the scraper to populate the database, or adjust your
                filters.
              </p>
              <button
                onClick={() =>
                  fetch("/api/scrape", { method: "POST" }).then(() =>
                    alert("Scrape started! Check back in a few minutes.")
                  )
                }
                className="mt-2 text-sm bg-stone-800 text-white px-4 py-2 rounded-lg hover:bg-stone-700 transition-colors"
              >
                Start scrape now
              </button>
            </div>
          )}

          {/* Product grid */}
          {products.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-4 py-2 text-sm rounded-lg border border-stone-200 disabled:opacity-40 hover:bg-stone-100 transition-colors"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-sm text-stone-600">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 text-sm rounded-lg border border-stone-200 disabled:opacity-40 hover:bg-stone-100 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
