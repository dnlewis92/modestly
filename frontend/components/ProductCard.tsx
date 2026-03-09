"use client";

import Image from "next/image";

export interface Product {
  id: number;
  retailer: string;
  name: string;
  url: string;
  image_url: string | null;
  current_price: number | null;
  original_price: number | null;
  discount_pct: number | null;
  currency: string;
  modest_length: string | null;
  price_dropped: boolean;
  scraped_at: string;
  price_changed_at: string | null;
}

const RETAILER_COLORS: Record<string, string> = {
  ASOS: "bg-stone-800 text-white",
  "H&M": "bg-red-600 text-white",
  Zara: "bg-black text-white",
  "Nordstrom Rack": "bg-blue-800 text-white",
  "Bloomingdale's": "bg-orange-700 text-white",
  Anthropologie: "bg-emerald-700 text-white",
  Abercrombie: "bg-stone-600 text-white",
};

const LENGTH_LABELS: Record<string, string> = {
  knee: "Knee Length",
  midi: "Midi",
  maxi: "Maxi",
};

export function ProductCard({ product }: { product: Product }) {
  const discount = product.discount_pct;
  const isBigSale = discount !== null && discount >= 20;
  const retailerColor =
    RETAILER_COLORS[product.retailer] ?? "bg-stone-500 text-white";
  const lengthLabel = product.modest_length
    ? LENGTH_LABELS[product.modest_length] ?? null
    : null;

  return (
    <a
      href={product.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex flex-col bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200 border border-stone-100"
    >
      {/* Image */}
      <div className="relative aspect-[3/4] bg-stone-100 overflow-hidden">
        {product.image_url ? (
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            unoptimized
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-stone-300 text-sm">
            No image
          </div>
        )}

        {/* Badges — top left */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          {discount !== null && discount >= 20 && (
            <span className="text-xs font-bold bg-blush-500 text-white px-2 py-0.5 rounded-full">
              {Math.round(discount)}% OFF
            </span>
          )}
          {product.price_dropped && (
            <span className="text-xs font-semibold bg-amber-400 text-amber-900 px-2 py-0.5 rounded-full">
              Price Drop
            </span>
          )}
        </div>

        {/* Length badge — top right */}
        {lengthLabel && (
          <span className="absolute top-2 right-2 text-xs bg-white/90 text-stone-600 px-2 py-0.5 rounded-full font-medium">
            {lengthLabel}
          </span>
        )}
      </div>

      {/* Info */}
      <div className="flex flex-col gap-1.5 p-3">
        {/* Retailer pill */}
        <span
          className={`self-start text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full ${retailerColor}`}
        >
          {product.retailer}
        </span>

        {/* Name */}
        <p className="text-sm font-medium text-stone-800 line-clamp-2 leading-snug">
          {product.name}
        </p>

        {/* Price */}
        <div className="flex items-baseline gap-2 mt-auto pt-1">
          <span className="text-base font-bold text-stone-900">
            ${product.current_price?.toFixed(2)}
          </span>
          {product.original_price &&
            product.original_price > (product.current_price ?? 0) && (
              <span className="text-sm text-stone-400 line-through">
                ${product.original_price.toFixed(2)}
              </span>
            )}
        </div>
      </div>
    </a>
  );
}
