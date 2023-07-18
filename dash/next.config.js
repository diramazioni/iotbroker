/** @type {import('next').NextConfig} */
const nextConfig = {
    async redirects() {
        return [
            {
                source: '/',
                destination: '/d',
                permanent: true,
            },
        ]
    },
}

module.exports = nextConfig

