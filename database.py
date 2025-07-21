"""
Database connection and operations for Fleet Management SaaS
Unified data layer supporting all three front doors
"""

import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import pandas as pd
from supabase import create_client, Client
import json
from config import config

class DatabaseManager:
    """
    Unified database manager for all three front doors:
    1. Optimization Audit
    2. Routing & Dispatch Hub  
    3. Document AI
    """
    
    def __init__(self):
        self.supabase: Client = create_client(
            config.database.url,
            config.database.key
        )
    
    # ============= COMPANY MANAGEMENT =============
    
    def create_company(self, company_data: Dict) -> str:
        """Create a new company and return the ID"""
        result = self.supabase.table('companies').insert(company_data).execute()
        return result.data[0]['id']
    
    def get_company(self, company_id: str) -> Optional[Dict]:
        """Get company details"""
        result = self.supabase.table('companies').select("*").eq('id', company_id).execute()
        return result.data[0] if result.data else None
    
    # ============= TOOL 1: OPTIMIZATION AUDIT =============
    
    def import_audit_data(self, company_id: str, csv_data: pd.DataFrame) -> bool:
        """Import CSV data for audit analysis"""
        try:
            # Convert DataFrame to list of dicts for Supabase
            loads_data = []
            
            for _, row in csv_data.iterrows():
                load_data = {
                    'company_id': company_id,
                    'pickup_date': row.get('date'),
                    'miles': float(row.get('miles', 0)),
                    'weight_lbs': int(row.get('load_weight', 0)) if pd.notna(row.get('load_weight')) else None,
                    'revenue': float(row.get('revenue', 0)),
                    'fuel_gallons': float(row.get('fuel_gallons', 0)),
                    'fuel_cost': float(row.get('fuel_cost', 0)),
                    'hours_driven': float(row.get('hours_driven', 0)),
                    'origin_city': row.get('origin', '').split(',')[0] if row.get('origin') else None,
                    'destination_city': row.get('destination', '').split(',')[0] if row.get('destination') else None,
                    'status': 'delivered'
                }
                loads_data.append(load_data)
            
            # Insert in batches to avoid timeout
            batch_size = 100
            for i in range(0, len(loads_data), batch_size):
                batch = loads_data[i:i + batch_size]
                self.supabase.table('loads').insert(batch).execute()
            
            return True
            
        except Exception as e:
            print(f"Error importing audit data: {e}")
            return False
    
    def get_audit_data(self, company_id: str, start_date: date = None, end_date: date = None) -> pd.DataFrame:
        """Get load data for audit analysis"""
        query = self.supabase.table('loads').select("*").eq('company_id', company_id)
        
        if start_date:
            query = query.gte('pickup_date', start_date.isoformat())
        if end_date:
            query = query.lte('pickup_date', end_date.isoformat())
            
        result = query.execute()
        return pd.DataFrame(result.data)
    
    def save_audit_report(self, company_id: str, audit_data: Dict) -> str:
        """Save audit report results"""
        audit_record = {
            'company_id': company_id,
            'analysis_period_start': audit_data.get('period_start'),
            'analysis_period_end': audit_data.get('period_end'),
            'total_revenue': audit_data.get('total_revenue'),
            'total_expenses': audit_data.get('total_expenses'),
            'total_miles': audit_data.get('total_miles'),
            'key_findings': audit_data.get('key_findings'),
            'recommendations': audit_data.get('recommendations'),
            'potential_savings': audit_data.get('potential_savings'),
            'report_file_path': audit_data.get('report_file_path'),
            'status': 'completed',
            'completed_at': datetime.now().isoformat()
        }
        
        result = self.supabase.table('audit_reports').insert(audit_record).execute()
        return result.data[0]['id']
    
    # ============= TOOL 2: ROUTING & DISPATCH HUB =============
    
    def get_trucks(self, company_id: str) -> List[Dict]:
        """Get all trucks for a company"""
        result = self.supabase.table('trucks').select("*").eq('company_id', company_id).eq('status', 'active').execute()
        return result.data
    
    def get_drivers(self, company_id: str) -> List[Dict]:
        """Get all drivers for a company"""
        result = self.supabase.table('drivers').select("*").eq('company_id', company_id).eq('status', 'active').execute()
        return result.data
    
    def create_load(self, company_id: str, load_data: Dict) -> str:
        """Create a new load/trip"""
        load_data['company_id'] = company_id
        result = self.supabase.table('loads').insert(load_data).execute()
        return result.data[0]['id']
    
    def update_load_status(self, load_id: str, status: str) -> bool:
        """Update load status"""
        try:
            self.supabase.table('loads').update({'status': status}).eq('id', load_id).execute()
            return True
        except:
            return False
    
    def get_active_loads(self, company_id: str) -> List[Dict]:
        """Get all active loads for dispatch"""
        result = self.supabase.table('loads').select("*, trucks(truck_number), drivers(first_name, last_name)").eq('company_id', company_id).in_('status', ['planned', 'in_transit']).execute()
        return result.data
    
    def create_route(self, company_id: str, route_data: Dict) -> str:
        """Create optimized route"""
        route_data['company_id'] = company_id
        route_data['optimized_at'] = datetime.now().isoformat()
        result = self.supabase.table('routes').insert(route_data).execute()
        return result.data[0]['id']
    
    # ============= TOOL 3: DOCUMENT AI =============
    
    def save_document(self, company_id: str, document_data: Dict) -> str:
        """Save uploaded document metadata"""
        document_data['company_id'] = company_id
        result = self.supabase.table('documents').insert(document_data).execute()
        return result.data[0]['id']
    
    def update_document_extraction(self, document_id: str, extracted_data: Dict) -> bool:
        """Update document with AI-extracted data"""
        try:
            update_data = {
                'extracted_data': extracted_data,
                'status': 'processed',
                'processed_at': datetime.now().isoformat()
            }
            self.supabase.table('documents').update(update_data).eq('id', document_id).execute()
            return True
        except:
            return False
    
    def get_documents(self, company_id: str, document_type: str = None) -> List[Dict]:
        """Get documents for a company"""
        query = self.supabase.table('documents').select("*").eq('company_id', company_id)
        if document_type:
            query = query.eq('document_type', document_type)
        result = query.execute()
        return result.data
    
    # ============= FLEET MANAGEMENT (SHARED) =============
    
    def add_truck(self, company_id: str, truck_data: Dict) -> str:
        """Add a new truck"""
        truck_data['company_id'] = company_id
        result = self.supabase.table('trucks').insert(truck_data).execute()
        return result.data[0]['id']
    
    def add_driver(self, company_id: str, driver_data: Dict) -> str:
        """Add a new driver"""
        driver_data['company_id'] = company_id
        result = self.supabase.table('drivers').insert(driver_data).execute()
        return result.data[0]['id']
    
    def record_maintenance(self, company_id: str, maintenance_data: Dict) -> str:
        """Record maintenance activity"""
        maintenance_data['company_id'] = company_id
        result = self.supabase.table('maintenance_records').insert(maintenance_data).execute()
        return result.data[0]['id']
    
    def get_maintenance_due(self, company_id: str) -> List[Dict]:
        """Get trucks due for maintenance"""
        result = self.supabase.table('maintenance_records').select("*, trucks(truck_number)").eq('company_id', company_id).lte('next_service_due_date', datetime.now().date().isoformat()).execute()
        return result.data
    
    # ============= ANALYTICS & REPORTING =============
    
    def get_fleet_kpis(self, company_id: str) -> Dict:
        """Get key performance indicators for the fleet"""
        loads_result = self.supabase.table('loads').select("revenue, fuel_cost, miles").eq('company_id', company_id).execute()
        trucks_result = self.supabase.table('trucks').select("id").eq('company_id', company_id).eq('status', 'active').execute()
        
        loads_df = pd.DataFrame(loads_result.data)
        
        if loads_df.empty:
            return {
                'total_revenue': 0,
                'total_fuel_cost': 0,
                'total_miles': 0,
                'profit_margin': 0,
                'fuel_efficiency': 0,
                'revenue_per_mile': 0,
                'active_trucks': len(trucks_result.data)
            }
        
        total_revenue = loads_df['revenue'].sum()
        total_fuel_cost = loads_df['fuel_cost'].sum()
        total_miles = loads_df['miles'].sum()
        
        return {
            'total_revenue': float(total_revenue),
            'total_fuel_cost': float(total_fuel_cost),
            'total_miles': float(total_miles),
            'profit_margin': float((total_revenue - total_fuel_cost) / total_revenue * 100) if total_revenue > 0 else 0,
            'fuel_efficiency': float(total_miles / total_fuel_cost) if total_fuel_cost > 0 else 0,
            'revenue_per_mile': float(total_revenue / total_miles) if total_miles > 0 else 0,
            'active_trucks': len(trucks_result.data)
        }

# Global database instance
db = DatabaseManager()