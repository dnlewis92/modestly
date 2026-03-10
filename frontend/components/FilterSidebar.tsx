"use client";

const ALL_RETAILERS = [
  "Abercrombie",
  "LOFT",
  "Madewell",
  "Banana Republic",
  "J.Crew",
  "ModCloth",
];

export interface Filters {
  retailers: string[];
  minDiscount: number;
  maxPrice: number;
  priceDropOnly: boolean;
  sortBy: string;
}

interface Props {
  filters: Filters;
  onChange: (filters: Filters) => void;
  stats?: { total_items: number; on_sale: number; price_drops: number };
}

export function FilterSidebar({ filters, onChange, stats }: Props) {
  const toggle = (retailer: string) => {
    const next = filters.retailers.includes(retailer)
      ? filters.retailers.filter((r) => r !== retailer)
      : [...filters.retailers, retailer];
    onChange({ ...filters, retailers: next });
  };

  return (
    <aside className="w-64 shrink-0 space-y-6">
      {/* Stats */}
      {stats && (
        <div className="bg-blush-50 border border-blush-100 rounded-2xl p-4 space-y-1">
          <p className="text-xs text-blush-600 font-semibold uppercase tracking-wide">
            Live inventory
          </p>
          <p className="text-2xl font-bold text-stone-800">
            {stats.total_items.toLocaleString()}
          </p>
          <p className="text-xs text-stone-500">
            modest items &middot;{" "}
            <span className="text-blush-600 font-medium">
              {stats.on_sale} on sale
            </span>{" "}
            &middot;{" "}
            <span className="text-amber-600 font-medium">
              {stats.price_drops} price drops
            </span>
          </p>
        </div>
      )}

      {/* Sort */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-2">
          Sort by
        </h3>
        <div className="space-y-1">
          {[
            { value: "discount", label: "Best Deal" },
            { value: "price_low", label: "Price: Low to High" },
            { value: "price_high", label: "Price: High to Low" },
            { value: "price_drop", label: "Recent Price Drops" },
            { value: "newest", label: "Newest" },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => onChange({ ...filters, sortBy: opt.value })}
              className={`w-full text-left text-sm px-3 py-2 rounded-lg transition-colors ${
                filters.sortBy === opt.value
                  ? "bg-stone-800 text-white font-medium"
                  : "text-stone-600 hover:bg-stone-100"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Deals filter */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-2">
          Deals
        </h3>
        <div className="space-y-1">
          {[
            { value: 0, label: "All items" },
            { value: 20, label: "20%+ off" },
            { value: 30, label: "30%+ off" },
            { value: 50, label: "50%+ off" },
          ].map((opt) => (
            <button
              key={opt.value}
              onClick={() => onChange({ ...filters, minDiscount: opt.value })}
              className={`w-full text-left text-sm px-3 py-2 rounded-lg transition-colors ${
                filters.minDiscount === opt.value
                  ? "bg-stone-800 text-white font-medium"
                  : "text-stone-600 hover:bg-stone-100"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <label className="flex items-center gap-2 mt-3 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.priceDropOnly}
            onChange={(e) =>
              onChange({ ...filters, priceDropOnly: e.target.checked })
            }
            className="rounded border-stone-300 text-blush-500 focus:ring-blush-400"
          />
          <span className="text-sm text-stone-600">Price drops only</span>
        </label>
      </div>

      {/* Max price */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-2">
          Max price: <span className="text-stone-800 font-bold">${filters.maxPrice}</span>
        </h3>
        <input
          type="range"
          min={10}
          max={200}
          step={5}
          value={filters.maxPrice}
          onChange={(e) =>
            onChange({ ...filters, maxPrice: parseInt(e.target.value) })
          }
          className="w-full accent-blush-500"
        />
        <div className="flex justify-between text-xs text-stone-400 mt-1">
          <span>$10</span>
          <span>$200</span>
        </div>
      </div>

      {/* Retailers */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-stone-500 mb-2">
          Retailers
        </h3>
        <div className="space-y-1">
          {ALL_RETAILERS.map((r) => (
            <label key={r} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.retailers.includes(r)}
                onChange={() => toggle(r)}
                className="rounded border-stone-300 text-blush-500 focus:ring-blush-400"
              />
              <span className="text-sm text-stone-700">{r}</span>
            </label>
          ))}
        </div>
        {filters.retailers.length > 0 && (
          <button
            onClick={() => onChange({ ...filters, retailers: [] })}
            className="mt-2 text-xs text-stone-400 hover:text-stone-600 underline"
          >
            Clear all
          </button>
        )}
      </div>
    </aside>
  );
}
