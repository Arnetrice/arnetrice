# Arnetrice.com - Data-Driven Solutions Provider

A professional business website for Arnetrice Smith, showcasing data analysis, business intelligence, and strategic consulting services.

## 🚀 Features

### MVP Features
- **Static Pages**: Home, About, Services, Portfolio, Blog, Contact
- **Contact Form**: Sends to FastAPI endpoint → saves to PostgreSQL + email notifications
- **Blog System**: Posts stored in PostgreSQL, retrieved dynamically via API
- **Portfolio**: Projects stored in PostgreSQL, retrieved dynamically via API
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **SEO Optimized**: Meta tags, structured data, and performance optimized

### Future-Ready Features
- Authentication system (client logins)
- Analytics dashboards for clients
- Service order forms tied to database
- API endpoints for data management/AI modules

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Email**: SMTP with Python email libraries

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styles with CSS variables
- **Bootstrap 5**: Responsive framework
- **JavaScript**: Vanilla JS with modular architecture
- **Fonts**: Poppins, Inter (Google Fonts)
- **Icons**: Font Awesome 6

### Deployment
- **Development**: Local development with hot reload
- **Production**: Railway/Render/Supabase (low-cost)
- **Future**: Azure-ready architecture

## 🎨 Design

### Color Scheme
- **Primary**: Blue (#0d6efd)
- **Secondary**: Green (#198754)
- **Accent**: Red (#dc3545)
- **Warning**: Yellow (#ffc107)
- **Background**: White (#ffffff)

### Typography
- **Headings**: Poppins (600 weight)
- **Body**: Inter (400 weight)
- **Modern, clean, professional appearance**

## 📁 Project Structure

```
arnetrice_com/
├── backend/                  # FastAPI + SQLAlchemy backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings (DB URL, secrets via dotenv)
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── crud.py           # Database operations
│   │   ├── routes/           # API routes
│   │   │   ├── __init__.py
│   │   │   ├── contact.py
│   │   │   ├── blog.py
│   │   │   └── portfolio.py
│   │   └── utils/
│   │       └── email.py      # Email notifications
│   └── tests/
│       └── test_main.py
├── frontend/                 # Static frontend (HTML, CSS, JS)
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── services.html
│   │   ├── contact.html
│   │   └── portfolio.html
│   └── static/
│       ├── css/
│       │   └── styles.css    # Custom CSS
│       └── js/
│           ├── main.js       # General site interactions
│           ├── contact.js    # Contact form logic
│           └── portfolio.js  # Portfolio functionality
├── env.example               # Example environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Node.js (optional, for development tools)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arnetrice_com
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **On Windows:**
   ```cmd
   venv\Scripts\activate
   ```
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

6. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb arnetrice_db
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

7. **Run the application**
   ```bash
   # Option 1: Using the run.py script (recommended)
   python run.py
   
   # Option 2: Direct uvicorn command
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - API Health Check: http://localhost:8000/health

## 📧 Email Configuration

To enable email notifications for contact form submissions:

1. **Gmail Setup** (recommended for development):
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password in your .env file

2. **Other SMTP providers**:
   - Update SMTP_SERVER, SMTP_PORT in .env
   - Use appropriate credentials

## 🗄 Database Setup

### Local Development
```bash
# Install PostgreSQL
# Create database
createdb arnetrice_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/arnetrice_db
```

### Production (Railway/Render/Supabase)
1. Create a PostgreSQL database on your chosen platform
2. Get the connection string
3. Update DATABASE_URL in your environment variables

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📦 Deployment

### Railway (Recommended for MVP)
1. Connect your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### Render
1. Create a new Web Service
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Local Production Testing
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Development

### Adding New Pages
1. Create HTML template in `frontend/templates/`
2. Add route in FastAPI backend
3. Update navigation in `base.html`

### Adding New API Endpoints
1. Create route file in `backend/app/routes/`
2. Add CRUD operations in `crud.py`
3. Update schemas in `schemas.py`
4. Include route in `main.py`

### Styling
- Main styles: `frontend/static/css/styles.css`
- Uses CSS variables for consistent theming
- Bootstrap 5 for responsive layout

## 📊 API Endpoints

### Contact
- `POST /api/contact/` - Submit contact form
- `GET /api/contact/` - Get all contacts (admin)
- `GET /api/contact/{id}` - Get specific contact
- `PUT /api/contact/{id}/read` - Mark contact as read

### Blog
- `GET /api/blog/` - Get all blog posts
- `POST /api/blog/` - Create new blog post
- `GET /api/blog/{id}` - Get specific blog post
- `PUT /api/blog/{id}` - Update blog post
- `DELETE /api/blog/{id}` - Delete blog post

### Portfolio
- `GET /api/portfolio/` - Get all portfolio items
- `POST /api/portfolio/` - Create new portfolio item
- `GET /api/portfolio/{id}` - Get specific portfolio item
- `PUT /api/portfolio/{id}` - Update portfolio item
- `DELETE /api/portfolio/{id}` - Delete portfolio item

## 🔒 Security

- Environment variables for sensitive data
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- XSS protection with proper HTML escaping

## 📈 Performance

- Static file serving
- Database connection pooling
- Optimized queries
- Minified CSS/JS (production)
- Image optimization
- CDN ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions:
- Email: hello@arnetrice.com
- Website: https://arnetrice.com

## 🚀 Future Enhancements

- [ ] Authentication system
- [ ] Client dashboard
- [ ] Analytics integration
- [ ] Payment processing
- [ ] Multi-language support
- [ ] Advanced search functionality
- [ ] Newsletter subscription
- [ ] Social media integration
