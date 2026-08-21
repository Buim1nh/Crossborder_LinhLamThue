const fs = require('fs')
const path = require('path')

// Automatically load root .env if running inside frontend/ subdirectory
const rootEnvPath = path.resolve(__dirname, '../.env')
if (fs.existsSync(rootEnvPath)) {
  const envContent = fs.readFileSync(rootEnvPath, 'utf8')
  envContent.split('\n').forEach((line) => {
    const trimmed = line.trim()
    if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
      const firstEqual = trimmed.indexOf('=')
      const key = trimmed.slice(0, firstEqual).trim()
      let val = trimmed.slice(firstEqual + 1).trim()
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1)
      }
      if (!process.env[key]) {
        process.env[key] = val
      }
    }
  })
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
}

module.exports = nextConfig
