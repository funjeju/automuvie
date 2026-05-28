/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // ESLint는 별도 step(`npm run lint`)에서 검증한다. build를 block하지 않는다.
  eslint: { ignoreDuringBuilds: true },
  // 타입 체크는 별도 step(`npm run type-check`)에서 처리. build 차단 방지.
  typescript: { ignoreBuildErrors: true },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.googleusercontent.com" },
      { protocol: "https", hostname: "**.firebasestorage.app" },
      { protocol: "https", hostname: "storage.googleapis.com" },
      { protocol: "http", hostname: "localhost" },
      { protocol: "http", hostname: "127.0.0.1" },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
