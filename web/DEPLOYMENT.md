# Deploying to Vercel

## Quick Start

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
   - Vercel auto-detects Next.js - no config needed
   - Click "Deploy"

3. **Done!**
   - Your site will be live at `https://your-project.vercel.app`
   - By default, only shows **Mingdom portfolio** (public mode)

---

## GOD_MODE (Show All Portfolios)

To show all portfolios (Mingdom + Fidelity), set environment variable in Vercel:

### In Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add variable:
   - **Name**: `NEXT_PUBLIC_GOD_MODE`
   - **Value**: `true`
   - **Environment**: Production (or all)
3. Redeploy

### Result:
- **Without GOD_MODE**: Only Mingdom visible (public)
- **With GOD_MODE=true**: All portfolios visible (private/admin)

---

## Local Development

GOD_MODE is enabled by default locally via `web/.env.local`:

```bash
# web/.env.local
NEXT_PUBLIC_GOD_MODE=true
```

This lets you see all portfolios during development.

---

## Custom Domain

1. In Vercel dashboard → Settings → Domains
2. Add your domain (e.g., `portfolio.mingdom.com`)
3. Update DNS records as instructed
4. SSL certificate auto-provisioned

---

## Automatic Deployments

Vercel automatically deploys:
- **Production**: Every push to `main` branch
- **Preview**: Every pull request gets a preview URL

---

## Build Configuration

The project is already configured for Vercel:
- `web/next.config.ts` - Next.js config
- `web/package.json` - Dependencies
- Root `Makefile` has `web-build` target

Vercel runs:
```bash
cd web && npm install && npm run build
```

---

## Data Updates

To update portfolio data on Vercel:

1. **Option A: Manual**
   - Run `make web-export` locally
   - Commit `web/public/data/portfolio.json`
   - Push to GitHub
   - Vercel auto-deploys

2. **Option B: GitHub Actions** (future)
   - Set up scheduled action to run `export_web_data.py`
   - Auto-commit and deploy daily

---

## Monitoring

Vercel provides:
- **Analytics**: Page views, performance
- **Logs**: Build and runtime logs
- **Alerts**: Deploy status notifications

Access via Vercel dashboard.

---

## Troubleshooting

### Build fails
- Check Vercel build logs
- Verify `npm run build` works locally
- Ensure all dependencies in `package.json`

### Data not updating
- Verify `web/public/data/portfolio.json` is committed
- Check file is in the build output
- Clear Vercel cache and redeploy

### Environment variables not working
- Must start with `NEXT_PUBLIC_` to be available in browser
- Redeploy after changing env vars
- Check browser console for actual value
