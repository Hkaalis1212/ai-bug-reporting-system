#!/usr/bin/env python3
"""
Routing & Dispatch Hub - Entry Point #2
======================================

The core SaaS platform for fleet managers and dispatchers.
Interactive, subscription-based dashboard for real-time fleet operations.

Target Customer: Fleet managers and dispatchers who need real-time tools
for daily operations and decision-making.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
import numpy as np
from typing import Dict, List, Optional
from database import db
from config import config
import openai

# Configure OpenAI
openai.api_key = config.openai.api_key

class FleetDispatchHub:
    """
    Core SaaS platform for fleet routing and dispatch operations
    """
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.company_data = db.get_company(company_id)
        
    def get_fleet_overview(self) -> Dict:
        """Get real-time fleet overview"""
        trucks = db.get_trucks(self.company_id)
        drivers = db.get_drivers(self.company_id)
        active_loads = db.get_active_loads(self.company_id)
        kpis = db.get_fleet_kpis(self.company_id)
        
        return {
            'trucks': trucks,
            'drivers': drivers,
            'active_loads': active_loads,
            'kpis': kpis,
            'active_truck_count': len([t for t in trucks if t['status'] == 'active']),
            'available_drivers': len([d for d in drivers if d['status'] == 'active']),
            'loads_in_transit': len([l for l in active_loads if l['status'] == 'in_transit']),
            'loads_planned': len([l for l in active_loads if l['status'] == 'planned'])
        }
    
    def create_load(self, load_data: Dict) -> str:
        """Create a new load assignment"""
        return db.create_load(self.company_id, load_data)
    
    def optimize_route_with_ai(self, stops: List[Dict]) -> Dict:
        """Use OpenAI to optimize route planning"""
        try:
            # Prepare stops data for AI
            stops_text = "\n".join([
                f"Stop {i+1}: {stop.get('address', stop.get('city', 'Unknown'))} - {stop.get('type', 'pickup/delivery')}"
                for i, stop in enumerate(stops)
            ])
            
            prompt = f"""
            You are a logistics optimization expert. Given these stops for a truck route:
            
            {stops_text}
            
            Please provide:
            1. The most efficient order to visit these stops
            2. Estimated total distance
            3. Estimated total time
            4. Key optimization insights
            5. Any potential issues or recommendations
            
            Respond in JSON format with keys: optimized_order, estimated_distance_miles, estimated_time_hours, insights, recommendations
            """
            
            response = openai.chat.completions.create(
                model=config.openai.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.openai.temperature
            )
            
            # Parse AI response
            import json
            ai_response = json.loads(response.choices[0].message.content)
            return ai_response
            
        except Exception as e:
            st.error(f"AI optimization error: {str(e)}")
            return {
                'optimized_order': list(range(len(stops))),
                'estimated_distance_miles': sum([stop.get('distance', 50) for stop in stops]),
                'estimated_time_hours': len(stops) * 2,
                'insights': 'AI optimization temporarily unavailable',
                'recommendations': ['Manual route planning recommended']
            }
    
    def get_maintenance_alerts(self) -> List[Dict]:
        """Get maintenance alerts and reminders"""
        return db.get_maintenance_due(self.company_id)
    
    def create_dispatch_map(self, loads: List[Dict]) -> folium.Map:
        """Create interactive map for dispatch visualization"""
        # Default center (US center)
        center_lat, center_lon = 39.8283, -98.5795
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4)
        
        # Color mapping for load status
        status_colors = {
            'planned': 'blue',
            'in_transit': 'orange',
            'delivered': 'green',
            'cancelled': 'red'
        }
        
        for load in loads:
            if load.get('origin_city') and load.get('destination_city'):
                # Add origin marker
                folium.Marker(
                    location=[40 + np.random.uniform(-5, 5), -95 + np.random.uniform(-10, 10)],  # Mock coordinates
                    popup=f"Origin: {load['origin_city']}<br>Load: {load.get('load_number', 'N/A')}",
                    icon=folium.Icon(color=status_colors.get(load['status'], 'gray'), icon='play')
                ).add_to(m)
                
                # Add destination marker
                folium.Marker(
                    location=[40 + np.random.uniform(-5, 5), -95 + np.random.uniform(-10, 10)],  # Mock coordinates
                    popup=f"Destination: {load['destination_city']}<br>Load: {load.get('load_number', 'N/A')}",
                    icon=folium.Icon(color=status_colors.get(load['status'], 'gray'), icon='stop')
                ).add_to(m)
        
        return m

def run_routing_hub():
    """Main Streamlit interface for Routing & Dispatch Hub"""
    st.set_page_config(
        page_title="FleetFlow - Dispatch Hub",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Authentication check (simplified for demo)
    if 'company_id' not in st.session_state:
        st.session_state.company_id = "demo-company-123"  # Demo company
    
    # Initialize hub
    hub = FleetDispatchHub(st.session_state.company_id)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🚛 FleetFlow")
        st.markdown("### Dispatch Hub")
        
        page = st.selectbox(
            "Navigate to:",
            ["Dashboard", "Active Loads", "Create Load", "Fleet Management", "Route Optimizer", "Maintenance", "Analytics"]
        )
        
        # Company info
        if hub.company_data:
            st.markdown("---")
            st.markdown(f"**Company:** {hub.company_data.get('name', 'Demo Company')}")
            st.markdown(f"**Plan:** {hub.company_data.get('subscription_tier', 'demo').title()}")
    
    # Main content area
    if page == "Dashboard":
        st.title("📊 Fleet Dashboard")
        
        # Get fleet overview
        overview = hub.get_fleet_overview()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Trucks",
                overview['active_truck_count'],
                delta=None
            )
        
        with col2:
            st.metric(
                "Available Drivers",
                overview['available_drivers'],
                delta=None
            )
        
        with col3:
            st.metric(
                "Loads in Transit",
                overview['loads_in_transit'],
                delta=None
            )
        
        with col4:
            st.metric(
                "Planned Loads",
                overview['loads_planned'],
                delta=None
            )
        
        # Performance metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${overview['kpis']['total_revenue']:,.0f}",
                delta=f"{overview['kpis']['profit_margin']:.1f}% margin"
            )
        
        with col2:
            st.metric(
                "Fuel Efficiency",
                f"{overview['kpis']['fuel_efficiency']:.1f} MPG",
                delta=None
            )
        
        with col3:
            st.metric(
                "Revenue/Mile",
                f"${overview['kpis']['revenue_per_mile']:.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Total Miles",
                f"{overview['kpis']['total_miles']:,.0f}",
                delta=None
            )
        
        # Fleet map
        st.subheader("🗺️ Fleet Location Overview")
        fleet_map = hub.create_dispatch_map(overview['active_loads'])
        st_folium(fleet_map, width=1200, height=400)
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Recent Loads")
            if overview['active_loads']:
                loads_df = pd.DataFrame(overview['active_loads'])
                loads_display = loads_df[['load_number', 'origin_city', 'destination_city', 'status']].head(5)
                st.dataframe(loads_display, use_container_width=True)
            else:
                st.info("No recent loads to display")
        
        with col2:
            st.subheader("🔧 Maintenance Alerts")
            maintenance_alerts = hub.get_maintenance_alerts()
            if maintenance_alerts:
                for alert in maintenance_alerts[:5]:
                    st.warning(f"🚛 {alert.get('trucks', {}).get('truck_number', 'Unknown')} - Maintenance due")
            else:
                st.success("✅ No maintenance alerts")
    
    elif page == "Active Loads":
        st.title("🚚 Active Loads Management")
        
        # Load status filter
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "planned", "in_transit", "delivered"],
                index=0
            )
        
        with col2:
            date_filter = st.date_input("Filter by Date", datetime.now().date())
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        
        # Get and display loads
        loads = db.get_active_loads(st.session_state.company_id)
        
        if loads:
            loads_df = pd.DataFrame(loads)
            
            # Apply filters
            if status_filter != "All":
                loads_df = loads_df[loads_df['status'] == status_filter]
            
            # Display loads table
            st.dataframe(
                loads_df[['load_number', 'origin_city', 'destination_city', 'miles', 'revenue', 'status']],
                use_container_width=True
            )
            
            # Load details expander
            if not loads_df.empty:
                selected_load = st.selectbox(
                    "Select load for details:",
                    loads_df['load_number'].tolist() if 'load_number' in loads_df.columns else []
                )
                
                if selected_load:
                    load_details = loads_df[loads_df['load_number'] == selected_load].iloc[0]
                    
                    with st.expander(f"Load Details: {selected_load}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Origin:** {load_details.get('origin_city', 'N/A')}")
                            st.write(f"**Destination:** {load_details.get('destination_city', 'N/A')}")
                            st.write(f"**Miles:** {load_details.get('miles', 'N/A')}")
                            st.write(f"**Weight:** {load_details.get('weight_lbs', 'N/A')} lbs")
                        
                        with col2:
                            st.write(f"**Revenue:** ${load_details.get('revenue', 0):,.2f}")
                            st.write(f"**Status:** {load_details.get('status', 'N/A').title()}")
                            st.write(f"**Pickup Date:** {load_details.get('pickup_date', 'N/A')}")
                            
                            # Status update buttons
                            new_status = st.selectbox(
                                "Update Status:",
                                ["planned", "in_transit", "delivered", "cancelled"],
                                index=["planned", "in_transit", "delivered", "cancelled"].index(load_details.get('status', 'planned'))
                            )
                            
                            if st.button("Update Status"):
                                if db.update_load_status(load_details['id'], new_status):
                                    st.success("✅ Status updated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update status")
        else:
            st.info("No active loads found")
    
    elif page == "Create Load":
        st.title("➕ Create New Load")
        
        with st.form("create_load_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Load Information")
                load_number = st.text_input("Load Number", value=f"LOAD-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
                pickup_date = st.date_input("Pickup Date", datetime.now().date())
                delivery_date = st.date_input("Delivery Date", datetime.now().date() + timedelta(days=2))
                
                origin_city = st.text_input("Origin City")
                origin_state = st.text_input("Origin State")
                destination_city = st.text_input("Destination City")
                destination_state = st.text_input("Destination State")
            
            with col2:
                st.subheader("Load Details")
                miles = st.number_input("Estimated Miles", min_value=1, value=500)
                weight = st.number_input("Weight (lbs)", min_value=1, value=25000)
                revenue = st.number_input("Revenue ($)", min_value=0.0, value=1500.0, step=0.01)
                
                # Truck and driver assignment
                trucks = db.get_trucks(st.session_state.company_id)
                drivers = db.get_drivers(st.session_state.company_id)
                
                truck_options = {f"{t['truck_number']} ({t['make']} {t['model']})": t['id'] for t in trucks}
                driver_options = {f"{d['first_name']} {d['last_name']} ({d['driver_number']})": d['id'] for d in drivers}
                
                selected_truck = st.selectbox("Assign Truck", list(truck_options.keys()) if truck_options else ["No trucks available"])
                selected_driver = st.selectbox("Assign Driver", list(driver_options.keys()) if driver_options else ["No drivers available"])
            
            submitted = st.form_submit_button("🚛 Create Load", type="primary")
            
            if submitted:
                if not all([load_number, origin_city, destination_city, miles, revenue]):
                    st.error("Please fill in all required fields")
                else:
                    load_data = {
                        'load_number': load_number,
                        'pickup_date': pickup_date.isoformat(),
                        'delivery_date': delivery_date.isoformat(),
                        'origin_city': origin_city,
                        'origin_state': origin_state,
                        'destination_city': destination_city,
                        'destination_state': destination_state,
                        'miles': miles,
                        'weight_lbs': weight,
                        'revenue': revenue,
                        'truck_id': truck_options.get(selected_truck) if truck_options else None,
                        'driver_id': driver_options.get(selected_driver) if driver_options else None,
                        'status': 'planned'
                    }
                    
                    try:
                        load_id = hub.create_load(load_data)
                        st.success(f"✅ Load created successfully! ID: {load_id}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error creating load: {str(e)}")
    
    elif page == "Route Optimizer":
        st.title("🗺️ AI Route Optimizer")
        st.markdown("*Powered by OpenAI for intelligent route planning*")
        
        # Route optimization interface
        st.subheader("Create Optimized Route")
        
        # Add stops
        if 'route_stops' not in st.session_state:
            st.session_state.route_stops = []
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add Stops")
            with st.form("add_stop_form"):
                stop_address = st.text_input("Stop Address/City")
                stop_type = st.selectbox("Stop Type", ["Pickup", "Delivery", "Fuel Stop"])
                stop_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                
                if st.form_submit_button("➕ Add Stop"):
                    if stop_address:
                        st.session_state.route_stops.append({
                            'address': stop_address,
                            'type': stop_type,
                            'priority': stop_priority,
                            'distance': np.random.randint(50, 200)  # Mock distance
                        })
                        st.success("Stop added!")
                        st.rerun()
        
        with col2:
            st.markdown("#### Current Stops")
            if st.session_state.route_stops:
                for i, stop in enumerate(st.session_state.route_stops):
                    st.write(f"{i+1}. {stop['address']} ({stop['type']})")
                
                if st.button("🗑️ Clear All Stops"):
                    st.session_state.route_stops = []
                    st.rerun()
            else:
                st.info("No stops added yet")
        
        # Optimize route
        if len(st.session_state.route_stops) >= 2:
            if st.button("🚀 Optimize Route with AI", type="primary"):
                with st.spinner("AI is optimizing your route..."):
                    optimization_result = hub.optimize_route_with_ai(st.session_state.route_stops)
                    
                    st.subheader("🎯 Optimization Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Estimated Distance", f"{optimization_result.get('estimated_distance_miles', 0)} miles")
                    with col2:
                        st.metric("Estimated Time", f"{optimization_result.get('estimated_time_hours', 0)} hours")
                    with col3:
                        st.metric("Total Stops", len(st.session_state.route_stops))
                    
                    # Show optimized order
                    st.subheader("📋 Optimized Stop Order")
                    optimized_order = optimization_result.get('optimized_order', list(range(len(st.session_state.route_stops))))
                    for i, stop_index in enumerate(optimized_order):
                        if stop_index < len(st.session_state.route_stops):
                            stop = st.session_state.route_stops[stop_index]
                            st.write(f"{i+1}. {stop['address']} ({stop['type']})")
                    
                    # Show insights
                    st.subheader("💡 AI Insights")
                    insights = optimization_result.get('insights', 'No insights available')
                    st.write(insights)
                    
                    # Show recommendations
                    st.subheader("📝 Recommendations")
                    recommendations = optimization_result.get('recommendations', [])
                    for rec in recommendations:
                        st.write(f"• {rec}")
                    
                    # Save route button
                    if st.button("💾 Save Optimized Route"):
                        route_data = {
                            'route_name': f"Route_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'route_date': datetime.now().date().isoformat(),
                            'stops': st.session_state.route_stops,
                            'total_miles': optimization_result.get('estimated_distance_miles', 0),
                            'estimated_duration_hours': optimization_result.get('estimated_time_hours', 0),
                            'status': 'planned'
                        }
                        
                        route_id = db.create_route(st.session_state.company_id, route_data)
                        st.success(f"✅ Route saved! ID: {route_id}")
    
    elif page == "Fleet Management":
        st.title("🚛 Fleet Management")
        
        tab1, tab2, tab3 = st.tabs(["Trucks", "Drivers", "Add New"])
        
        with tab1:
            st.subheader("🚛 Truck Fleet")
            trucks = db.get_trucks(st.session_state.company_id)
            
            if trucks:
                trucks_df = pd.DataFrame(trucks)
                st.dataframe(
                    trucks_df[['truck_number', 'make', 'model', 'year', 'status', 'current_mileage']],
                    use_container_width=True
                )
            else:
                st.info("No trucks in fleet")
        
        with tab2:
            st.subheader("👥 Driver Roster")
            drivers = db.get_drivers(st.session_state.company_id)
            
            if drivers:
                drivers_df = pd.DataFrame(drivers)
                st.dataframe(
                    drivers_df[['driver_number', 'first_name', 'last_name', 'status', 'hire_date']],
                    use_container_width=True
                )
            else:
                st.info("No drivers in roster")
        
        with tab3:
            st.subheader("➕ Add New Assets")
            
            asset_type = st.radio("Asset Type", ["Truck", "Driver"])
            
            if asset_type == "Truck":
                with st.form("add_truck_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        truck_number = st.text_input("Truck Number")
                        make = st.text_input("Make")
                        model = st.text_input("Model")
                        year = st.number_input("Year", min_value=1990, max_value=datetime.now().year + 1)
                    
                    with col2:
                        vin = st.text_input("VIN")
                        license_plate = st.text_input("License Plate")
                        max_weight = st.number_input("Max Weight Capacity (lbs)", min_value=1000)
                        current_mileage = st.number_input("Current Mileage", min_value=0)
                    
                    if st.form_submit_button("🚛 Add Truck"):
                        truck_data = {
                            'truck_number': truck_number,
                            'make': make,
                            'model': model,
                            'year': year,
                            'vin': vin,
                            'license_plate': license_plate,
                            'max_weight_capacity': max_weight,
                            'current_mileage': current_mileage
                        }
                        
                        try:
                            truck_id = db.add_truck(st.session_state.company_id, truck_data)
                            st.success(f"✅ Truck added successfully! ID: {truck_id}")
                        except Exception as e:
                            st.error(f"❌ Error adding truck: {str(e)}")
            
            else:  # Driver
                with st.form("add_driver_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        driver_number = st.text_input("Driver Number")
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                        email = st.text_input("Email")
                    
                    with col2:
                        phone = st.text_input("Phone")
                        license_number = st.text_input("License Number")
                        license_expiry = st.date_input("License Expiry")
                        pay_rate = st.number_input("Pay Rate per Mile ($)", min_value=0.0, step=0.01)
                    
                    if st.form_submit_button("👥 Add Driver"):
                        driver_data = {
                            'driver_number': driver_number,
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'phone': phone,
                            'license_number': license_number,
                            'license_expiry': license_expiry.isoformat(),
                            'pay_rate_per_mile': pay_rate,
                            'hire_date': datetime.now().date().isoformat()
                        }
                        
                        try:
                            driver_id = db.add_driver(st.session_state.company_id, driver_data)
                            st.success(f"✅ Driver added successfully! ID: {driver_id}")
                        except Exception as e:
                            st.error(f"❌ Error adding driver: {str(e)}")
    
    elif page == "Analytics":
        st.title("📈 Fleet Analytics")
        
        # Get KPIs
        kpis = db.get_fleet_kpis(st.session_state.company_id)
        
        # Performance overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Profit Margin", f"{kpis['profit_margin']:.1f}%")
        with col2:
            st.metric("Fuel Efficiency", f"{kpis['fuel_efficiency']:.1f} MPG")
        with col3:
            st.metric("Revenue/Mile", f"${kpis['revenue_per_mile']:.2f}")
        with col4:
            st.metric("Active Trucks", kpis['active_trucks'])
        
        # Charts (placeholder for now)
        st.subheader("📊 Performance Trends")
        
        # Generate sample trend data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        revenue_trend = np.random.normal(50000, 10000, len(dates))
        fuel_cost_trend = np.random.normal(15000, 3000, len(dates))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=revenue_trend, name='Revenue', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=dates, y=fuel_cost_trend, name='Fuel Cost', line=dict(color='red')))
        fig.update_layout(title='Revenue vs Fuel Cost Trend', xaxis_title='Month', yaxis_title='Amount ($)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional analytics placeholder
        st.info("🚧 Advanced analytics features coming soon! This will include detailed performance metrics, predictive insights, and custom reporting.")

if __name__ == "__main__":
    run_routing_hub()