from fastapi import FastAPI, __version__
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware  # Import middleware for CORS handling
from app.api.api_main import api_routers

app = FastAPI()

# Include your API routers under the "/api/v1" prefix
app.include_router(api_routers, prefix="/api/v1")

# List of allowed origins (domains) that can access your API
origins = [
    "http://localhost:5173",              # Your local dev frontend
    "https://invoice-maker-orpin.vercel.app",  # Your deployed frontend domain
]

# Add CORS middleware to handle Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Allow these origins only
    allow_credentials=True,     # Allow cookies, authorization headers, etc.
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],        # Allow all headers
)

# Simple HTML page returned on root URL "/"
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to Invoice Maker App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            background: #f7fafc;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 480px;
            margin: 60px auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            padding: 32px 24px;
            text-align: center;
        }}
        h1 {{
            color: #2563eb;
            margin-bottom: 16px;
        }}
        ul {{
            list-style: none;
            padding: 0;
            margin: 16px 0;
        }}
        li {{
            margin: 8px 0;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 24px;
            color: #64748b;
            font-size: 0.95em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Invoice Maker APP </h1>
        <ul>
            <li><a href="/docs">Interactive API Docs (Swagger UI)</a></li>
            <li><a href="/redoc">ReDoc API Reference</a></li>
        </ul>
        <div class="footer">
            Powered by <a href="https://fastapi.tiangolo.com/" target="_blank"> FastAPI <span style="font-size:0.7em; color:#64748b;">(v{__version__})</span></a>
        </div>
    </div>
</body>
</html>
"""

# Root endpoint that returns the above HTML page
@app.get("/")
async def root():
    return HTMLResponse(html)
