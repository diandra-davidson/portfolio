# Portfolio Website - Senior Site Reliability Engineer

Professional portfolio website showcasing SRE expertise, platform engineering capabilities, and featured projects.

## 🎯 Project Overview

A Flask-based portfolio website featuring:
- **Hero Section**: Professional introduction with honeycomb profile design
- **Project Highlights**: Carousel showcasing selected GitHub projects
- **About Page**: Professional background and expertise
- **Services Page**: Consulting and platform engineering services
- **Experience Page**: Work history and achievements
- **Contact Form**: Direct communication channel for opportunities

**Target Role**: Senior Site Reliability Engineer / Platform Engineer (Identity & Reliability)
**Location**: NYC / New Jersey
**Availability**: Full-time / Contract ($95-105/hr)

## 🤖 AI Coding Assistant

This project includes an AI coding assistant that tracks your development progress and maintains project context.

**Quick Start:**
```bash
# See current project status
python tools/track_changes.py summary

# Ask AI: "Where did I leave off?"
```

📖 **Full Guide**: See [tools/AI_ASSISTANT_GUIDE.md](tools/AI_ASSISTANT_GUIDE.md)

The AI assistant:
- ✅ Tracks git commits and changes
- ✅ Maintains project vision and architecture docs
- ✅ Helps you resume work after time away
- ✅ Suggests next steps and improvements
- ✅ Analyzes code patterns and provides context

**Memory Files** (in `/memories/repo/`):
- `project-vision.md` - Project goals and features
- `development-log.md` - Recent commits and TODOs
- `codebase-structure.md` - Architecture and integrations

## 🏗️ Architecture

**Stack:**
- Backend: Flask 3.1.3 (Python 3.12+)
- Frontend: Bootstrap 5 with custom CSS
- Authentication: GitHub OAuth
- Server: Gunicorn WSGI
- Proxy: NGINX
- Containers: Docker + Docker Compose
- Hosting: Digital Ocean Droplet

**Security:**
- Docker secrets for sensitive data
- Keyring for credential management
- OAuth state tokens for CSRF protection
- Environment variable configuration

## 📁 Project Structure

```
portfolio/
├── __init__.py                  # Flask app factory
├── main.py                      # Blueprint routes & OAuth
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image
├── docker-compose.yml           # Production deployment
├── docker-compose-dev.yml       # Development setup
├── nginx.conf                   # Reverse proxy config
│
├── .github/
│   └── copilot-instructions.md  # GitHub Copilot config
│
├── memories/
│   └── repo/                    # AI assistant memory files
│       ├── project-vision.md
│       ├── development-log.md
│       ├── codebase-structure.md
│       └── keyring.md
│
├── tools/                       # Development utilities
│   ├── track_changes.py         # Progress tracking script
│   ├── git-hooks/               # Git automation
│   ├── README.md
│   └── AI_ASSISTANT_GUIDE.md    # AI assistant documentation
│
├── templates/                   # Jinja2 templates
│   ├── layout.html              # Base template
│   ├── nav.html                 # Navigation
│   ├── index.html               # Home page
│   ├── about.html               # About page
│   └── explore.html             # Additional template
│
└── static/                      # Static assets
    ├── css/
    │   └── style.css            # Custom styles
    └── images/                  # Profile images
```

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

### Local Development

1. **Activate virtual environment:**

   **Linux/MacOS:**
   ```bash
   source .venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file with:
   FLASK_SECRET_KEY=your_long_random_flask_secret_key
   CLIENT_ID=your_github_oauth_client_id
   AWS_REGION=your_aws_region
   AWS_SECRETSMANAGER_SECRET_NAME=your_aws_secret_name
   AWS_SECRETSMANAGER_SERVICE_NAME=your_service_name
   SCOPE="read:user user:email"
   AUTHORIZATION_URL=https://github.com/login/oauth/authorize
   CALLBACK_URL=http://localhost:8000/oauth/callback
   TOKEN_URL=https://github.com/login/oauth/access_token
   ```

   Notes:
   - If `FLASK_SECRET_KEY` is not set, the app generates a random key at startup.
   - A generated key is acceptable for local testing, but sessions and OAuth state cookies become invalid when the process restarts.
   - Set `FLASK_SECRET_KEY` explicitly for stable sessions, especially in production.

4. **Run development server:**
   ```bash
   flask run --reload
   # Or with Gunicorn:
   gunicorn "__init__:create_app()" --bind 0.0.0.0:8000 --reload
   ```

5. **Access application:**
   - Open browser to `http://localhost:8000`

### Docker Development

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose -f docker-compose-dev.yml up --build
   ```

2. **Access application:**
   - Open browser to `http://localhost:80`

3. **Stop containers:**
   ```bash
   docker-compose -f docker-compose-dev.yml down
   ```

## 🚀 Deployment

### Production Deployment on Digital Ocean

1. **Build production image:**
   ```bash
   docker build -t portfolio:latest .
   ```

2. **Store OAuth secret in AWS Secrets Manager**
   - Secret value can be either:
     - Plain string: the OAuth client secret
     - JSON object with key `client_secret`

3. **Configure host environment variables** on the Digital Ocean droplet (do not commit these):
   ```bash
   export AWS_REGION=your_aws_region
   export AWS_SECRETSMANAGER_SECRET_NAME=portfolio/github/oauth
   export AWS_SECRETSMANAGER_SERVICE_NAME=client_secret
   ```

4. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

5. **Configure domain and SSL** (recommended: Let's Encrypt)

### Environment Variables

Required for production:
- `FLASK_SECRET_KEY`: stable secret for Flask session and CSRF state cookies
- `CLIENT_ID`: GitHub OAuth App Client ID
- `AWS_REGION`: your_aws_region
- `AWS_SECRETSMANAGER_SECRET_NAME`: your_aws_secret_name
- `AWS_SECRETSMANAGER_SERVICE_NAME`: your_service_name
- `SCOPE`: OAuth permissions (read:user user:email)
- `AUTHORIZATION_URL`: GitHub OAuth URL
- `CALLBACK_URL`: Your domain callback URL
- `TOKEN_URL`: GitHub token exchange URL

## 📝 Development Workflow

### Starting a Session

```bash
# Check current status
python tools/track_changes.py summary

# Ask AI assistant
# "Where did I leave off? What should I work on next?"
```

### During Development

1. Make changes to code
2. Test locally
3. Commit regularly with descriptive messages
4. Push to GitHub

### Committing Changes

```bash
# Check what changed
git status
python tools/track_changes.py status

# Stage and commit
git add .
git commit -m "KAN-#: Description of changes"
git push origin main
```

### Code Review Process

1. Create feature branch
2. Make changes
3. Submit pull request
4. Review and merge

## 🔧 Development Tools

### Track Changes Script

```bash
# Show current status
python tools/track_changes.py status

# Generate AI assistant summary
python tools/track_changes.py summary

# Show commit history
python tools/track_changes.py commits 20
```

### Git Hooks (Optional)

Install post-commit hook to auto-update development log:

```bash
ln -s ../../tools/git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## 🎨 Key Features

### Home Page
- **Hero Section**: Professional introduction with animated honeycomb profile image
- **Social Links**: LinkedIn, GitHub, Email with Bootstrap icons
- **CTA Buttons**: Contact Me, Download Resume
- **Scroll Indicator**: Smooth scroll to highlights section

### Project Highlights Carousel
- Auto-rotating carousel (5s intervals)
- Project cards with:
  - Title and description
  - Technology tags
  - Key achievements
  - Links to GitHub repositories

### OAuth Integration
- GitHub OAuth flow for fetching project metadata
- State token CSRF protection
- Secure credential storage with keyring
- Automatic project data refresh

## 📊 Current Status

**Completed:**
- ✅ Flask application with Blueprint routing
- ✅ Bootstrap 5 integration and custom styling
- ✅ Hero section with profile and social links
- ✅ Project highlights carousel (static content)
- ✅ Docker containerization
- ✅ NGINX reverse proxy configuration
- ✅ OAuth flow initialization
- ✅ AI assistant tracking system

**In Progress:**
- 🔄 Complete OAuth callback implementation
- 🔄 Dynamic GitHub project loading via API

**Planned:**
- ⏳ Services page content and layout
- ⏳ Experience page with work history
- ⏳ Contact form with email integration
- ⏳ About page content expansion
- ⏳ Production deployment to Digital Ocean
- ⏳ Domain configuration and SSL setup

See [memories/repo/development-log.md](memories/repo/development-log.md) for detailed progress tracking.

## 🤝 Working with AI Assistant

### Common Commands

```bash
# Check project status
python tools/track_changes.py summary
```

### Questions to Ask AI

**When starting work:**
- "Where did I leave off in this project?"
- "What should I work on next?"
- "What are the current TODOs?"

**During development:**
- "How should I implement [feature]?"
- "Explain the architecture of [component]"
- "Help me debug [issue]"

**Code review:**
- "Review my uncommitted changes"
- "Suggest improvements for [file]"
- "Are there any code quality issues?"

📖 **Complete Guide**: [tools/AI_ASSISTANT_GUIDE.md](tools/AI_ASSISTANT_GUIDE.md)

## 🔍 Testing

### Manual Testing
```bash
# Activate virtual environment
source .venv/bin/activate

# Run Flask in debug mode
export FLASK_ENV=development
flask run --debug
```

### Docker Testing
```bash
# Build and test
docker-compose -f docker-compose-dev.yml up --build

# View logs
docker-compose logs -f app

# Stop and cleanup
docker-compose down
```

## 📚 Documentation

- **[AI Assistant Guide](tools/AI_ASSISTANT_GUIDE.md)** - How to use the AI coding assistant
- **[Development Tools](tools/README.md)** - Helper scripts and utilities
- **[Project Vision](memories/repo/project-vision.md)** - Goals and architecture overview
- **[Codebase Structure](memories/repo/codebase-structure.md)** - Detailed code organization
- **[Development Log](memories/repo/development-log.md)** - Recent commits and progress

## 🐛 Troubleshooting

### OAuth Issues
- Check environment variables are set correctly
- Verify GitHub OAuth App callback URL matches `CALLBACK_URL`
- Ensure client secret is properly mounted in Docker

### Keyring Issues
- Follow setup instructions in keyring section
- Verify GPG key is initialized
- Check `pass` is working: `pass ls`

### Docker Issues
- Ensure Docker daemon is running
- Check port 80 and 8000 are not in use
- Review logs: `docker-compose logs`

### Import Errors
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.12+)

## 🚧 Technical Debt

Current items requiring attention:
1. Complete OAuth callback token exchange (main.py line 92+)
2. Implement remaining page templates (services, experience, contact)
3. Add error handling for GitHub API calls
4. Implement rate limiting for API requests
5. Add comprehensive logging
6. Set up monitoring for production
7. Add automated tests

## 📝 Contributing

This is a personal portfolio project, but the AI assistant system and development tools can be useful for others. Feel free to adapt them for your own projects!

## 📄 License

This project is open source and available under your chosen license.

## 🔗 Links

- **Live Site**: Coming soon (Digital Ocean deployment pending)
- **GitHub**: [diandra-davidson/portfolio](https://github.com/diandra-davidson/portfolio)
- **LinkedIn**: [diandradavidson](https://www.linkedin.com/in/diandradavidson/)

## 📞 Contact

For opportunities or consulting inquiries:
- **Email**: user@email.com
- **Rate**: $95-105/hr for contract work
- **Location**: New York City / New Jersey
- **Availability**: Full-time / Contract

---

**Last Updated**: June 16, 2026
**Project Status**: Active Development
**AI Assistant**: Enabled ✅
