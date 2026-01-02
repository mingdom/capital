# Quick Reference

## Common Commands

```bash
make install    # Install everything (Python + Node)
make web        # Run web dashboard (dev mode, GOD_MODE enabled)
make build      # Build for production
make preview    # Preview production build locally (public mode)
make test       # Run tests
make run        # Run CLI
```

## Development

```bash
make format     # Format code
make lint       # Lint code
make import     # Import latest data
make report     # Generate HTML report
```

## Utilities

```bash
make clean      # Remove build artifacts
make hook       # Install git pre-commit hook
make help       # Show all commands
```

## Web Dashboard

**Local development:**
- `make web` → http://localhost:3000
- GOD_MODE enabled (shows all portfolios)

**Production deployment:**
- Push to GitHub
- Deploy to Vercel (one-click)
- Default: Shows only Mingdom
- Set `NEXT_PUBLIC_GOD_MODE=true` to show all

See `web/DEPLOYMENT.md` for details.
