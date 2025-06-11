/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  assetPrefix: process.env.NODE_ENV === 'production' ? '/LibreDomains-beta' : '',
  basePath: process.env.NODE_ENV === 'production' ? '/LibreDomains-beta' : '',
}

module.exports = nextConfig
