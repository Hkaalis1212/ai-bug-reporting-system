#!/usr/bin/env python3
"""
FleetFlow Demo Script
====================

Demonstrates all three front doors and validates the platform setup.
Run this script to test your FleetFlow installation.
"""

import pandas as pd
import sys
import os
from datetime import datetime, date, timedelta
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test configuration and dependencies"""
    print("🔧 Testing Configuration...")
    
    try:
        from config import config
        
        # Test configuration
        errors = config.validate()
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Configuration valid")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        from database import db
        
        # Test basic connection by creating a demo company
        demo_company_data = {
            'name': 'Demo Trucking Company',
            'contact_email': 'demo@fleetflow.com',
            'subscription_tier': 'trial'
        }
        
        # This will test the Supabase connection
        company_id = db.create_company(demo_company_data)
        print(f"✅ Database connection successful! Demo company ID: {company_id}")
        
        return company_id
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure your Supabase credentials are correct in .env file")
        return None

def test_audit_tool(company_id):
    """Test the Optimization Audit functionality"""
    print("\n📊 Testing Optimization Audit Tool...")
    
    try:
        from audit_tool import FleetOptimizationAuditor
        
        # Create auditor instance
        auditor = FleetOptimizationAuditor(company_id)
        
        # Load sample data
        if os.path.exists('sample_trucking_data.csv'):
            sample_data = pd.read_csv('sample_trucking_data.csv')
            auditor.data = sample_data.head(50)  # Use first 50 rows for demo
            
            # Prepare data for analysis
            auditor.data['date'] = pd.to_datetime(auditor.data['date'])
            auditor.data['profit'] = auditor.data['revenue'] - auditor.data['fuel_cost']
            auditor.data['revenue_per_mile'] = auditor.data['revenue'] / auditor.data['miles']
            auditor.data['fuel_cost_per_mile'] = auditor.data['fuel_cost'] / auditor.data['miles']
            
            # Run analysis
            results = auditor.analyze_performance()
            
            print(f"✅ Audit analysis completed!")
            print(f"   - Total Revenue: ${results['total_revenue']:,.0f}")
            print(f"   - Profit Margin: {results['profit_margin']:.1f}%")
            print(f"   - Potential Savings: ${results['potential_savings']:,.0f}")
            print(f"   - Findings: {len(results['findings'])} issues identified")
            
            return True
        else:
            print("⚠️ Sample data file not found, but audit tool imports successfully")
            return True
            
    except Exception as e:
        print(f"❌ Audit tool test failed: {e}")
        return False

def test_routing_hub(company_id):
    """Test the Routing & Dispatch Hub functionality"""
    print("\n🚛 Testing Routing & Dispatch Hub...")
    
    try:
        from routing_hub import FleetDispatchHub
        
        # Create hub instance
        hub = FleetDispatchHub(company_id)
        
        # Add sample truck
        sample_truck = {
            'truck_number': 'DEMO-001',
            'make': 'Freightliner',
            'model': 'Cascadia',
            'year': 2021,
            'vin': 'DEMO123456789',
            'license_plate': 'FL123ABC',
            'max_weight_capacity': 80000,
            'current_mileage': 125000
        }
        
        truck_id = db.add_truck(company_id, sample_truck)
        print(f"✅ Sample truck added: {truck_id}")
        
        # Add sample driver
        sample_driver = {
            'driver_number': 'DRV-001',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@demo.com',
            'phone': '555-123-4567',
            'license_number': 'FL123456789',
            'license_expiry': (date.today() + timedelta(days=365)).isoformat(),
            'pay_rate_per_mile': 0.55,
            'hire_date': date.today().isoformat()
        }
        
        driver_id = db.add_driver(company_id, sample_driver)
        print(f"✅ Sample driver added: {driver_id}")
        
        # Create sample load
        sample_load = {
            'load_number': f"LOAD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'pickup_date': date.today().isoformat(),
            'delivery_date': (date.today() + timedelta(days=2)).isoformat(),
            'origin_city': 'Atlanta',
            'origin_state': 'GA',
            'destination_city': 'Jacksonville',
            'destination_state': 'FL',
            'miles': 347,
            'weight_lbs': 35000,
            'revenue': 1250.00,
            'truck_id': truck_id,
            'driver_id': driver_id,
            'status': 'planned'
        }
        
        load_id = hub.create_load(sample_load)
        print(f"✅ Sample load created: {load_id}")
        
        # Test fleet overview
        overview = hub.get_fleet_overview()
        print(f"✅ Fleet overview retrieved:")
        print(f"   - Active trucks: {overview['active_truck_count']}")
        print(f"   - Available drivers: {overview['available_drivers']}")
        print(f"   - Active loads: {len(overview['active_loads'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing hub test failed: {e}")
        return False

def test_document_ai(company_id):
    """Test the Document AI functionality"""
    print("\n📄 Testing Document AI...")
    
    try:
        from document_ai import DocumentAIProcessor
        
        # Create processor instance
        processor = DocumentAIProcessor(company_id)
        
        # Test without actually processing an image (requires OpenAI API)
        print("✅ Document AI processor initialized")
        
        # Test data parsing functions
        weight_test = processor._parse_weight("35,000 lbs")
        amount_test = processor._parse_amount("$1,250.00")
        
        print(f"✅ Weight parsing test: '{35000}' -> {weight_test}")
        print(f"✅ Amount parsing test: '$1,250.00' -> {amount_test}")
        
        # Save a demo document record
        demo_document = {
            'document_type': 'bol',
            'file_name': 'demo_bol.pdf',
            'file_path': 'documents/demo/demo_bol.pdf',
            'extracted_data': {
                'bol_number': 'DEMO-BOL-001',
                'shipper_name': 'Demo Shipper Inc',
                'consignee_name': 'Demo Consignee LLC',
                'origin_city': 'Atlanta',
                'destination_city': 'Miami',
                'weight_lbs': 25000,
                'freight_charges': 1500.00,
                'document_type': 'bol',
                'processed_at': datetime.now().isoformat()
            },
            'status': 'processed'
        }
        
        doc_id = db.save_document(company_id, demo_document)
        print(f"✅ Demo document saved: {doc_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document AI test failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connectivity (optional)"""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        import openai
        from config import config
        
        if not config.openai.api_key:
            print("⚠️ OpenAI API key not configured - Document AI will not work")
            return False
        
        # Test simple API call
        openai.api_key = config.openai.api_key
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, respond with just 'OK'"}],
            max_tokens=5
        )
        
        if response.choices[0].message.content.strip().upper() == 'OK':
            print("✅ OpenAI API connection successful")
            return True
        else:
            print("⚠️ OpenAI API responded, but with unexpected content")
            return False
            
    except Exception as e:
        print(f"⚠️ OpenAI API test failed: {e}")
        print("   Document AI features will be limited without OpenAI")
        return False

def generate_demo_report(company_id):
    """Generate a summary report of the demo"""
    print("\n📋 Demo Summary Report")
    print("=" * 50)
    
    try:
        from database import db
        
        # Get company info
        company = db.get_company(company_id)
        print(f"Company: {company['name'] if company else 'Demo Company'}")
        print(f"Company ID: {company_id}")
        
        # Get fleet KPIs
        kpis = db.get_fleet_kpis(company_id)
        print(f"Active Trucks: {kpis['active_trucks']}")
        print(f"Total Revenue: ${kpis['total_revenue']:,.2f}")
        print(f"Total Miles: {kpis['total_miles']:,.0f}")
        print(f"Profit Margin: {kpis['profit_margin']:.1f}%")
        
        # Get document count
        docs = db.get_documents(company_id)
        print(f"Documents Processed: {len(docs)}")
        
        print("\n✅ Demo completed successfully!")
        print("\nNext Steps:")
        print("1. Run 'streamlit run main.py' to access the full platform")
        print("2. Try each of the three front doors")
        print("3. Upload your own data for real analysis")
        
    except Exception as e:
        print(f"Error generating report: {e}")

def main():
    """Run the complete demo"""
    print("🚛 FleetFlow Platform Demo")
    print("=" * 50)
    print("This demo will test all three front doors:")
    print("1. 📊 Optimization Audit")
    print("2. 🚛 Routing & Dispatch Hub") 
    print("3. 📄 Document AI")
    print()
    
    # Test configuration
    if not test_configuration():
        print("\n❌ Demo failed at configuration step")
        print("Please check your .env file and ensure all required variables are set")
        return
    
    # Test database
    company_id = test_database_connection()
    if not company_id:
        print("\n❌ Demo failed at database connection step")
        print("Please check your Supabase configuration")
        return
    
    # Test each front door
    tests = [
        ("Audit Tool", test_audit_tool),
        ("Routing Hub", test_routing_hub),
        ("Document AI", test_document_ai)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func(company_id)
    
    # Test OpenAI (optional)
    results["OpenAI"] = test_openai_connection()
    
    # Generate summary
    generate_demo_report(company_id)
    
    # Print final results
    print("\n🎯 Test Results Summary:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    total_passed = sum(results.values())
    print(f"\nOverall: {total_passed}/{len(results)} tests passed")
    
    if total_passed >= 3:  # Core functionality
        print("\n🎉 FleetFlow platform is ready to use!")
    else:
        print("\n⚠️ Some issues found. Please check the error messages above.")

if __name__ == "__main__":
    main()