/** @type {import('next').NextConfig} */
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.asos-media.com" },
      { protocol: "https", hostname: "**.hm.com" },
      { protocol: "https", hostname: "**.zara.com" },
      { protocol: "https", hostname: "**.nordstromrack.com" },
      { protocol: "https", hostname: "**.bloomingdales.com" },
      { protocol: "https", hostname: "**.anthropologie.com" },
      { protocol: "https", hostname: "**.abercrombie.com" },
      { protocol: "https", hostname: "images.asos-media.com" },
      { protocol: "https", hostname: "lp2.hm.com" },
      { protocol: "https", hostname: "img.abercrombie.com" },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
