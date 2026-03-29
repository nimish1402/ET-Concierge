/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow backend API URL via env
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

module.exports = nextConfig;
