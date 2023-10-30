git pull 
cd svelte-dash
pnpm run build && pm2 restart ecosystem.config.cjs
tail -f ~/.pm2/logs/greenlab-welaser-error.log 