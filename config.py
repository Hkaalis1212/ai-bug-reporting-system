"""
Configuration management for Fleet Management SaaS
Supports all three front doors: Audit, Routing, Document AI
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Supabase database configuration"""
    url: str
    key: str
    service_role_key: str

@dataclass
class OpenAIConfig:
    """OpenAI API configuration for AI features"""
    api_key: str
    model: str = "gpt-4-vision-preview"
    temperature: float = 0.3

@dataclass
class StorageConfig:
    """File storage configuration"""
    bucket_name: str = "fleet-documents"
    max_file_size_mb: int = 10

@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str = "FleetFlow"
    version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "your-secret-key-here"
    
    # Pricing configuration
    audit_price: float = 497.0  # One-time audit price
    monthly_price_per_truck: float = 29.0  # Monthly SaaS pricing
    
    # Email configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.database = DatabaseConfig(
            url=os.getenv("SUPABASE_URL", ""),
            key=os.getenv("SUPABASE_ANON_KEY", ""),
            service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        
        self.openai = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", "")
        )
        
        self.storage = StorageConfig()
        
        self.app = AppConfig(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
            email_user=os.getenv("EMAIL_USER", ""),
            email_password=os.getenv("EMAIL_PASSWORD", "")
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.database.url:
            errors.append("SUPABASE_URL environment variable is required")
        if not self.database.key:
            errors.append("SUPABASE_ANON_KEY environment variable is required")
        if not self.openai.api_key:
            errors.append("OPENAI_API_KEY environment variable is required")
            
        return errors

# Global config instance
config = Config()

# Environment file template for easy setup
ENV_TEMPLATE = """
# Fleet Management SaaS Environment Variables

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
SECRET_KEY=your_secret_key_for_sessions
DEBUG=False

# Email Configuration (for notifications)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
"""

def create_env_file():
    """Create a template .env file"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(ENV_TEMPLATE)
        print("Created .env template file. Please fill in your values.")
    else:
        print(".env file already exists.")

if __name__ == "__main__":
    create_env_file()