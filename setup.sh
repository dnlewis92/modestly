#!/bin/bash
set -e

echo "=== Modest Fashion Aggregator Setup ==="

# 1. Python env
echo ""
echo "--- Setting up Python environment ---"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Copy .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env — add your ANTHROPIC_API_KEY"
fi

# 3. Create data dir
mkdir -p data

# 4. Frontend
echo ""
echo "--- Setting up frontend ---"
cd frontend
npm install
cd ..

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Start the backend:  source .venv/bin/activate && uvicorn backend.main:app --reload"
echo "  3. Start the frontend: cd frontend && npm run dev"
echo "  4. Trigger first scrape: curl -X POST http://localhost:8000/api/scrape"
