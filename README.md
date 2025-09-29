<h1 id="documentmanager">📄 DocumentManager</h1>
<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&amp;logo=python" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.111+-00a393.svg?style=for-the-badge&amp;logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=for-the-badge&amp;logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License">
  </p>
  <p><strong>Transform your document chaos into an AI-powered knowledge powerhouse</strong></p>
  <p><em>Most document management systems feel like they're stuck in 2005. DocumentManager brings AI intelligence to understand your documents' actual content and meaning - not just their titles or tags.</em></p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-demo">Demo</a> •
    <a href="#-documentation">Documentation</a> •
    <a href="#-api">API</a> •
    <a href="#-contributing">Contributing</a>
  </p>
</div>
<hr>

<h2 id="-features">🌟 Features</h2>
<h3 id="-ai-powered-intelligence">🤖 AI-Powered Intelligence</h3>
<ul>
  <li><strong>Semantic Search</strong>: Find documents by meaning, not just keywords. Search for "payment terms" and find invoicing documents, contracts with payment clauses, and financial agreements - even if they never use those exact words</li>
  <li><strong>Smart OCR</strong>: Extract text from scanned PDFs, photos of whiteboards, and documents in 50+ languages using Tesseract OCR</li>
  <li><strong>Auto-Tagging</strong>: AI automatically categorizes documents based on content - financial reports get tagged as "finance", contracts as "legal", technical specs as "engineering"</li>
  <li><strong>Natural Language Queries</strong>: Just ask questions like "Show me all contracts expiring this year" or "What were our Q4 marketing expenses?"</li>
  <li><strong>AI-Generated Summaries</strong>: Understand large documents at a glance with automatic summary generation</li>
</ul>
<h3 id="-enterprise-ready-security">🔒 Enterprise-Ready Security</h3>
<ul>
  <li><strong>Role-Based Access Control</strong>: Fine-grained permissions for users and groups</li>
  <li><strong>Complete Audit Trails</strong>: Track all document activities</li>
  <li><strong>Privacy First</strong>: Option to use Azure OpenAI to keep models in your own tenant</li>
  <li><strong>Self-Hosted</strong>: All data stays on your infrastructure - no vendor lock-in</li>
  <li><strong>Session Management</strong>: Secure session handling with automatic expiry</li>
</ul>
<h3 id="-modern-architecture">🚀 Modern Architecture</h3>
<ul>
  <li><strong>RESTful API</strong>: Complete OpenAPI 3.0 documented API built with FastAPI</li>
  <li><strong>Vector Database</strong>: ChromaDB for lightning-fast semantic search using embeddings</li>
  <li><strong>Flexible AI</strong>: Choose between OpenAI or Azure OpenAI (your choice)</li>
  <li><strong>Simple Frontend</strong>: Vanilla JavaScript keeping it simple and fast</li>
  <li><strong>Docker-Ready</strong>: Deploy in minutes with included setup script</li>
</ul>

<h2 id="-demo">📸 Demo</h2>
<div align="center">
  <h3 id="dashboard-overview">Dashboard Overview</h3>
  <img src="images/dashboard-overview.png" alt="Dashboard">
  <p><em>Clean, intuitive dashboard showing document statistics and recent activities</em></p>
  <h3 id="ai-powered-search">AI-Powered Search</h3>
  <img src="images/ai-search.jpeg" alt="AI Search">
  <p><em>Find documents by meaning, not just keywords - ask questions in natural language</em></p>
  <h3 id="ai-chat">AI Chat</h3>
  <img src="images/ai-chat.png" alt="AI Chat">
  <p><em>Interactive AI chat for document analysis and knowledge extraction</em></p>
  <h3 id="document-upload-processing">Document Upload &amp; Processing</h3>
  <img src="images/document-upload.jpeg" alt="Document Upload">
  <p><em>Drag-and-drop interface with automatic text extraction and AI tagging</em></p>
  <h3 id="smart-tags-organization">Smart Tags &amp; Organization</h3>
  <img src="images/tags.png" alt="Tags Management">
  <p><em>AI auto-generates correspondents, document types, and tags - fully customizable with color coding</em></p>
  <h3 id="document-viewer">Document Viewer</h3>
  <img src="images/document-viewer.png" alt="Document Viewer">
  <p><em>Built-in document viewer with search highlighting and annotations</em></p>
  <h3 id="user-management">User Management</h3>
  <img src="images/user-management.jpeg" alt="User Management">
  <p><em>Enterprise-grade user and permission management</em></p>
  <h3 id="settings-configuration">Settings &amp; Configuration</h3>
  <img src="images/settings-page.jpeg" alt="Settings">
  <p><em>Easy configuration of AI providers and system settings</em></p>
</div>

<h2 id="-quick-start">🚀 Quick Start</h2>
<h3 id="getting-started-in-3-minutes">Getting Started in 3 Minutes</h3>
<p>The beauty of open source? You can have this running on your machine right now:</p>
<h3 id="prerequisites">Prerequisites</h3>
<ul>
  <li>Docker installed and running</li>
  <li>4GB+ RAM recommended</li>
  <li>10GB+ free disk space</li>
</ul>

<h3 id="-using-docker-recommended">🐳 Using Docker (Recommended)</h3>
<pre><code># Clone the repository
git clone https://github.com/JayRHa/Document-Manager.git
cd Document-Manager

# Run the setup script
./setup.sh prod

# Or manually with Docker
docker build -t documentmanager .
docker run -d \
  --name documentmanager \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/storage:/app/storage \
  documentmanager
</code></pre>
<p>The application will be available at <code>http://localhost:8000</code></p>

<h3 id="-windows-notes-crucial-fixes">⚠️ Windows Notes (Crucial Fixes)</h3>
<p>Op Windows 10/11 moet u **Git Bash** gebruiken voor de meest betrouwbare installatie. De meegeleverde shell-scripts bevatten line endings die fouten veroorzaken in Linux-containers (<code>exec... no such file or directory</code> error).</p>
<p><strong>Aanbevolen Installatieprocedure op Windows (Na <code>git clone</code>):</strong></p>
<ol>
  <li><p><strong>Corrigeer de Line Endings in Git Bash:</strong><br>
    Repareer de <code>docker-entrypoint.sh</code> en <code>docker-entrypoint-aio.sh</code> scripts:</p>
    <pre><code># Gebruik sed om de Windows-specifieke carriage return karakters te verwijderen
sed -i 's/\r$//' docker-entrypoint.sh
sed -i 's/\r$//' docker-entrypoint-aio.sh
</code></pre>
  </li>
  <li><p><strong>Pas de SECRET_KEY aan:</strong><br>
    De container crasht bij de start als de standaard <code>SECRET_KEY</code> niet is gewijzigd. Open het <code>.env</code> bestand en vervang de placeholder door een veilige, willekeurige waarde:</p>
    <pre><code># Wijzig dit in het .env bestand:
SECRET_KEY=een_unieke_en_lange_willekeurige_geheime_sleutel
</code></pre>
  </li>
  <li><p><strong>Bouw de Image op een schone manier:</strong><br>
    Dit zorgt ervoor dat de gecorrigeerde scripts worden meegenomen in de Docker image:</p>
    <pre><code># Stop en verwijder eerdere mislukte containers
docker stop documentmanager 2>/dev/null
docker rm documentmanager 2>/dev/null

# Herbouw de image
docker build -t documentmanager .
</code></pre>
  </li>
  <li><p><strong>Start de Container:</strong></p>
    <pre><code>docker run -d \
  --name documentmanager \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/storage:/app/storage \
  documentmanager
</code></pre>
    <p>Controleer de status met <code>docker ps -f name=documentmanager</code>. De status moet <code>Up (healthy)</code> zijn.</p>
  </li>
</ol>

<h3 id="-using-the-setup-script">🛠️ Using the Setup Script</h3>
<p>The <code>setup.sh</code> script provides an easy way to manage your DocumentManager installation:</p>
<pre><code># Start development environment with hot reload
./setup.sh dev

# Start production environment
./setup.sh prod

# Build Docker image
./setup.sh build

# View logs
./setup.sh logs

# Check status
./setup.sh status

# Stop all containers
./setup.sh stop
</code></pre>

<h3 id="-local-development">💻 Local Development</h3>
<pre><code># Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
</code></pre>

<h2 id="-initial-setup">📋 Initial Setup</h2>
<ol>
  <li><strong>Create Admin Account</strong>
    <ul>
      <li>Navigate to <code>http://localhost:8000</code></li>
      <li>The first user registration automatically becomes admin</li>
    </ul>
  </li>
  <li><strong>Configure AI Provider</strong>
    <ul>
      <li>Go to Settings → AI Configuration</li>
      <li>Choose between OpenAI or Azure OpenAI</li>
      <li>Enter your API credentials</li>
      <li>Test the connection</li>
    </ul>
  </li>
  <li><strong>Start Using</strong>
    <ul>
      <li>Upload documents via drag-and-drop</li>
      <li>Watch AI automatically extract text, generate summaries, and categorize</li>
      <li>AI detects: Title, Summary, Correspondent, Document Type, Document Date, Tags, and Tax Relevance</li>
      <li>Use semantic search to find information instantly with natural language</li>
    </ul>
  </li>
</ol>

<h2 id="-architecture">🏗️ Architecture</h2>
<pre><code>DocumentManager/
├── app/                    # Backend FastAPI application
│   ├── api/               # REST API endpoints
│   ├── core/              # Core business logic
│   ├── models/            # SQLAlchemy models
│   └── services/          # AI, OCR, and storage services
├── frontend/              # Vanilla JS frontend
├── docker/                # Docker configuration
├── tests/                 # Test suite
└── docs/                  # Documentation
</code></pre>

<h3 id="technology-stack">Technology Stack</h3>
<ul>
  <li><strong>Backend</strong>: FastAPI, SQLAlchemy, Pydantic</li>
  <li><strong>AI/ML</strong>: OpenAI GPT-4, Azure OpenAI, ChromaDB</li>
  <li><strong>OCR</strong>: Tesseract (50+ languages)</li>
  <li><strong>Database</strong>: SQLite (default), PostgreSQL (production)</li>
  <li><strong>Frontend</strong>: Vanilla JavaScript, modern CSS</li>
  <li><strong>Deployment</strong>: Docker, Docker Compose</li>
</ul>

<h2 id="-configuration">🔧 Configuration</h2>
<h3 id="environment-variables">Environment Variables</h3>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre><code># Security - CHANGE IN PRODUCTION!
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./data/documents.db
# For PostgreSQL: postgresql://user:pass@localhost/dbname

# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
# Or for Azure:
# AI_PROVIDER=azure
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
# AZURE_OPENAI_KEY=your-key

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,txt,doc,docx

# Storage
STORAGE_TYPE=local
STORAGE_PATH=/app/data/storage
</code></pre>

<h2 id="-api-documentation">📚 API Documentation</h2>
<h3 id="interactive-api-docs">Interactive API Docs</h3>
<p>Once running, access the interactive API documentation at:</p>
<ul>
  <li>Swagger UI: <code>http://localhost:8000/docs</code></li>
  <li>ReDoc: <code>http://localhost:8000/redoc</code></li>
</ul>

<h3 id="quick-api-examples">Quick API Examples</h3>
<pre><code>import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Authentication
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "admin",
    "password": "your-password"
})
session = requests.Session()
session.cookies = response.cookies

# 2. Upload Document
with open("document.pdf", "rb") as f:
    response = session.post(
        f"{BASE_URL}/api/documents/upload",
        files={"file": f},
        data={"title": "Q4 Report", "tags": "finance,quarterly"}
    )
    document_id = response.json()["id"]

# 3. Semantic Search
response = requests.get(f"{BASE_URL}/api/search/semantic", params={
    "query": "What were the Q4 revenue numbers?",
    "limit": 5
})
results = response.json()

# 4. Ask Questions
response = requests.post(f"{BASE_URL}/api/ai/ask", json={
    "question": "Summarize the key findings from Q4 reports",
    "document_ids": [document_id]
})
answer = response.json()["answer"]
</code></pre>

<h2 id="-why-open-source">🌟 Why Open Source?</h2>
<p>Your document management system shouldn't be a black box. With DocumentManager you can:</p>
<ul>
  <li><strong>Audit the code</strong> - Know exactly what happens to your documents</li>
  <li><strong>Customize for your needs</strong> - Modify anything to fit your workflow</li>
  <li><strong>Self-host everything</strong> - Your documents, your rules</li>
  <li><strong>Contribute improvements</strong> - Join the community making document management better</li>
</ul>
<p>No vendor lock-in. Complete transparency. Total control.</p>

<h2 id="-roadmap">🚀 Roadmap</h2>
<p>The foundation is solid, but we're just getting started:</p>
<ul>
  <li><strong>Self-hosted AI models</strong> - Run everything locally</li>
  <li><strong>Mobile apps</strong> - For on-the-go access and document scanning</li>
  <li><strong>Workflow automation</strong> - Documents that route themselves</li>
  <li><strong>Advanced analytics</strong> - Insights from your document repository</li>
  <li><strong>Plugin system</strong> - Custom integrations for your needs</li>
</ul>

<h2 id="-contributing">🤝 Contributing</h2>
<p>We love contributions! Please see our <a href="CONTRIBUTING.md">Contributing Guide</a> for details.</p>
<ol>
  <li>Fork the repository</li>
  <li>Create your feature branch (<code>git checkout -b feature/AmazingFeature</code>)</li>
  <li>Commit your changes (<code>git commit -m 'Add some AmazingFeature'</code>)</li>
  <li>Push to the branch (<code>git push origin feature/AmazingFeature</code>)</li>
  <li>Open a Pull Request</li>
</ol>

<h3 id="development-setup">Development Setup</h3>
<pre><code># Clone your fork
git clone https://github.com/JayRHa/Document-Manager.git
cd Document-Manager

# Create branch
git checkout -b feature/your-feature

# Install pre-commit hooks
pip install pre-commit
pre-commit install
</code></pre>

<h2 id="-license">📄 License</h2>
<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
<hr>

<div align="center">
  <p>Built with ❤️ by Jannik Reinhard and Fabian Peschke</p>
  <p>⭐ Star the repo if you find it useful — it really helps with motivation!</p>
  <p>☕ If you want to support the project, you can <a href="https://www.buymeacoffee.com/your-link">buy us a coffee</a></p>
</div>
