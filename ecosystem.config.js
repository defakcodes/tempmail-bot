// PM2 Configuration for TempMail Bot
// Install PM2: npm install -g pm2
// Start: pm2 start ecosystem.config.js
// Monitor: pm2 monit

module.exports = {
  apps: [
    {
      name: 'tempmail-bot',
      script: 'python3',
      args: 'main.py all',
      cwd: '/path/to/temporary-mail-main',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        TELEGRAM_BOT_TOKEN: 'YOUR_BOT_TOKEN',
        SERVER_HOST: '0.0.0.0',
        SERVER_PORT: '8000',
        AUTOFILL_SERVER_URL: 'http://localhost:8000'
      },
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 5000
    }
  ]
};
