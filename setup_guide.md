# FleetFlow Setup Guide
## "One Platform, Three Front Doors" Fleet Management SaaS

### 🚀 Quick Start

This guide will help you set up FleetFlow locally or deploy to production. The platform provides three entry points:

1. **📊 Optimization Audit** - One-time analysis tool
2. **🚛 Routing & Dispatch Hub** - Core SaaS platform
3. **📄 Document AI** - Paperwork automation

---

## 📋 Prerequisites

### Required Services
- **Supabase Account** (Database & Auth)
- **OpenAI API Key** (AI Features)
- **Python 3.8+**

### Optional Services
- **Stripe Account** (Payment processing)
- **SendGrid/SMTP** (Email notifications)

---

## 🔧 Local Development Setup

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd fleetflow

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Supabase Database

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your project URL and API keys

2. **Run Database Schema**
   ```sql
   -- Copy and run the contents of database_schema.sql
   -- in your Supabase SQL editor
   ```

3. **Enable Row Level Security**
   - Go to Authentication > Policies
   - Enable RLS on all tables
   - The schema includes basic policies

### 3. Configure Environment Variables

Create a `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key_here

# Application Configuration
SECRET_KEY=your_secret_key_for_sessions
DEBUG=True

# Email Configuration (Optional)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 4. Run the Application

```bash
# Run the main application
streamlit run main.py

# Or run individual front doors:
streamlit run audit_tool.py          # Optimization Audit
streamlit run routing_hub.py         # Dispatch Hub  
streamlit run document_ai.py         # Document AI
```

The application will be available at `http://localhost:8501`

---

## 🌐 Production Deployment

### Option 1: Streamlit Cloud (Recommended for MVP)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial FleetFlow setup"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set `main.py` as the main file
   - Add environment variables in the settings

3. **Configure Secrets**
   - In Streamlit Cloud, go to App Settings > Secrets
   - Add all your environment variables

### Option 2: Railway/Render/Heroku

1. **Create deployment configuration**
   ```dockerfile
   # Dockerfile (if needed)
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Deploy using platform-specific instructions**

### Option 3: Custom Server

1. **Install on Ubuntu server**
   ```bash
   # Install Python and dependencies
   sudo apt update
   sudo apt install python3 python3-pip nginx
   
   # Install application
   git clone <your-repo>
   cd fleetflow
   pip3 install -r requirements.txt
   
   # Set up environment variables
   sudo nano /etc/environment
   # Add your environment variables
   
   # Run with screen or systemd
   screen -S fleetflow
   streamlit run main.py --server.port=8501
   ```

---

## 🗄️ Database Setup Details

### Tables Created
- `companies` - Multi-tenant company data
- `trucks` - Vehicle fleet management
- `drivers` - Driver information
- `loads` - Trip/load tracking
- `documents` - Document AI storage
- `routes` - Route optimization
- `maintenance_records` - Maintenance tracking
- `audit_reports` - Audit analysis results

### Sample Data (Optional)
```sql
-- Insert sample company
INSERT INTO companies (name, contact_email, subscription_tier) 
VALUES ('Demo Trucking Co', 'demo@company.com', 'trial');

-- Get the company ID and use it for sample data
```

---

## 🔑 API Keys & Configuration

### Supabase Setup
1. **Project Settings**
   - Go to Settings > API
   - Copy Project URL and API keys
   - Enable "Email confirmations" if using auth

2. **Storage Setup** (for Document AI)
   ```sql
   -- Create storage bucket
   INSERT INTO storage.buckets (id, name, public) 
   VALUES ('fleet-documents', 'fleet-documents', false);
   ```

### OpenAI Setup
1. **Get API Key**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create API key
   - Set usage limits if needed

2. **Test API Access**
   ```python
   import openai
   openai.api_key = "your-key"
   response = openai.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hello"}]
   )
   print(response.choices[0].message.content)
   ```

---

## 🎯 Three Front Doors Configuration

### 1. Optimization Audit
- **Purpose**: Lead generation and conversion
- **Target**: Skeptical fleet owners
- **Pricing**: $497 one-time
- **Files**: `audit_tool.py`, existing audit logic

### 2. Routing & Dispatch Hub  
- **Purpose**: Core SaaS platform
- **Target**: Fleet managers and dispatchers
- **Pricing**: $29/truck/month
- **Files**: `routing_hub.py`, `database.py`

### 3. Document AI
- **Purpose**: Niche problem solver
- **Target**: Back-office administrators
- **Pricing**: $0.50/document
- **Files**: `document_ai.py`, OpenAI Vision API

---

## 🧪 Testing & Validation

### Test Each Front Door
```bash
# Test Audit Tool
streamlit run audit_tool.py
# Upload sample_trucking_data.csv

# Test Dispatch Hub
streamlit run routing_hub.py
# Create sample loads and trucks

# Test Document AI
streamlit run document_ai.py
# Upload sample BOL/POD images
```

### Database Validation
```sql
-- Check table creation
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Test data insertion
SELECT * FROM companies LIMIT 5;
SELECT * FROM loads LIMIT 5;
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Supabase Connection Error**
   ```
   Error: Invalid API key
   ```
   - Check SUPABASE_URL and SUPABASE_ANON_KEY
   - Ensure RLS policies allow access

2. **OpenAI API Error**
   ```
   Error: Incorrect API key
   ```
   - Verify OPENAI_API_KEY
   - Check API usage limits

3. **Streamlit Import Errors**
   ```
   ModuleNotFoundError: No module named 'X'
   ```
   - Run `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Database Schema Errors**
   ```
   relation "companies" does not exist
   ```
   - Run database_schema.sql in Supabase
   - Check table permissions

### Performance Optimization

1. **Database Indexing**
   - Indexes are included in schema
   - Monitor query performance in Supabase

2. **Streamlit Caching**
   ```python
   @st.cache_data
   def load_data():
       # Cache expensive operations
   ```

3. **API Rate Limiting**
   - Implement OpenAI request caching
   - Add retry logic for API calls

---

## 📈 Scaling Considerations

### Multi-Tenancy
- All tables include `company_id`
- Row Level Security enforces data isolation
- User authentication via Supabase Auth

### Performance
- Database connection pooling
- Redis caching for frequent queries
- CDN for static assets

### Monitoring
- Supabase built-in analytics
- Custom logging for business metrics
- Error tracking (Sentry integration)

---

## 🔒 Security Checklist

- [ ] Environment variables secured
- [ ] RLS policies enabled
- [ ] API keys rotated regularly
- [ ] HTTPS enabled in production
- [ ] Input validation on all forms
- [ ] SQL injection protection
- [ ] File upload restrictions

---

## 📞 Support & Next Steps

### Getting Help
- **Documentation**: Check this guide first
- **Issues**: Create GitHub issues for bugs
- **Questions**: Contact development team

### Roadmap
1. **Phase 1**: MVP deployment
2. **Phase 2**: Payment integration
3. **Phase 3**: Advanced analytics
4. **Phase 4**: Mobile app

---

## 💡 Tips for Success

1. **Start with Audit Tool**
   - Fastest to market
   - Immediate revenue potential
   - Builds customer relationships

2. **Focus on One Entry Point**
   - Perfect one before expanding
   - Deep customer discovery
   - Iterate based on feedback

3. **Leverage AI Differentiation**
   - OpenAI integration is competitive advantage
   - Document AI solves real pain point
   - Route optimization saves money

4. **Measure Everything**
   - Conversion rates between front doors
   - Customer acquisition costs
   - Feature usage analytics

---

*This setup guide should get you running quickly. For specific deployment questions or customization needs, reach out to the development team.*