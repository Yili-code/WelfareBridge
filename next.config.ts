import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  output: "standalone",
  // /api/* 轉給後端的代理預設 30 秒逾時；小幫手「整理需求登記」要等本地 AI（模型冷啟動可能超過一分鐘），
  // 與前端 330 秒的逾時對齊，才不會代理先斷線
  experimental: { proxyTimeout: 330_000 },
  // 舊的使用者頁面已整合進首頁（查詢補助／我的資料卡／訴求專區）
  async redirects() {
    return [
      { source: "/dashboard", destination: "/", permanent: false },
      { source: "/my-benefits", destination: "/#profile", permanent: false },
      { source: "/my-scholarships", destination: "/#profile", permanent: false },
    ];
  },
  async rewrites() {
    return { fallback: [{
      source: "/api/:path*",
      destination: `${process.env.BENEFIT_API_URL || "http://127.0.0.1:8000"}/api/:path*`,
    }] };
  },
};

export default nextConfig;
