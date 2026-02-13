/**
 * PM2 Ecosystem Configuration for LARAI.VN
 * Install PM2: npm install -g pm2
 * Start all: pm2 start ecosystem.config.js
 * View logs: pm2 logs
 * Monitor: pm2 monit
 */

module.exports = {
  apps: [
    // ==========================================
    // MAIN SERVICES
    // ==========================================
    
    // Backend API (FastAPI)
    {
      name: 'larai-backend',
      script: '/home/coin87/.local/bin/uvicorn',
      args: 'app.main:app --host 127.0.0.1 --port 9010 --workers 4',
      cwd: '/home/coin87/coin87sourcev2/backend',
      interpreter: '/home/coin87/coin87sourcev2/backend/venv/bin/python',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PYTHONPATH: '/home/coin87/coin87sourcev2/backend',
        NODE_ENV: 'production'
      },
      error_file: '/var/log/coin87/backend-error.log',
      out_file: '/var/log/coin87/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000
    },

    // Frontend (Next.js)
    {
      name: 'larai-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/coin87/coin87sourcev2/frontend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '800M',
      env: {
        NODE_ENV: 'production',
        PORT: 9011
      },
      error_file: '/var/log/coin87/frontend-error.log',
      out_file: '/var/log/coin87/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000
    },

    // ==========================================
    // BACKGROUND JOBS (Continuous)
    // ==========================================

    // Main Crawler - Chạy liên tục 24/7
    {
      name: 'larai-crawler',
      script: '/home/coin87/coin87sourcev2/backend/venv/bin/python',
      args: 'main_crawler.py',
      cwd: '/home/coin87/coin87sourcev2/backend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/home/coin87/coin87sourcev2/backend'
      },
      error_file: '/var/log/coin87/crawler-error.log',
      out_file: '/var/log/coin87/crawler-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '30s',
      max_restarts: 10,
      restart_delay: 10000
    },

    // Background Ranking - Tính ranking
    {
      name: 'larai-ranking',
      script: '/home/coin87/coin87sourcev2/backend/venv/bin/python',
      args: 'background_ranking.py',
      cwd: '/home/coin87/coin87sourcev2/backend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/home/coin87/coin87sourcev2/backend'
      },
      error_file: '/var/log/coin87/ranking-error.log',
      out_file: '/var/log/coin87/ranking-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '30s',
      max_restarts: 10,
      restart_delay: 10000
    },

    // Background Clustering - Gom nhóm tin
    {
      name: 'larai-clustering',
      script: '/home/coin87/coin87sourcev2/backend/venv/bin/python',
      args: 'background_clustering.py',
      cwd: '/home/coin87/coin87sourcev2/backend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/home/coin87/coin87sourcev2/backend'
      },
      error_file: '/var/log/coin87/clustering-error.log',
      out_file: '/var/log/coin87/clustering-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '30s',
      max_restarts: 10,
      restart_delay: 10000
    },

    // Background Verifier - Truth Engine
    {
      name: 'larai-verifier',
      script: '/home/coin87/coin87sourcev2/backend/venv/bin/python',
      args: 'background_verifier.py',
      cwd: '/home/coin87/coin87sourcev2/backend',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        PYTHONPATH: '/home/coin87/coin87sourcev2/backend'
      },
      error_file: '/var/log/coin87/verifier-error.log',
      out_file: '/var/log/coin87/verifier-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      min_uptime: '30s',
      max_restarts: 10,
      restart_delay: 10000
    }
  ]
};
