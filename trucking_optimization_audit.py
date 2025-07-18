#!/usr/bin/env python3
"""
Trucking Fleet Optimization Audit Tool
=====================================

A professional analysis tool for trucking companies to identify cost savings,
efficiency improvements, and optimization opportunities.

Author: AI Consulting Solutions
Target: Small to mid-size trucking fleets
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import base64
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TruckingOptimizationAuditor:
    """
    Main class for analyzing trucking fleet data and generating optimization reports.
    """
    
    def __init__(self):
        self.data = None
        self.analysis_results = {}
        self.charts = {}
        
    def load_data(self, csv_file_path):
        """
        Load and validate trucking data from CSV file.
        
        Expected columns:
        - date: Trip date
        - truck_id: Truck identifier
        - driver_id: Driver identifier
        - origin: Starting location
        - destination: End location
        - miles: Distance traveled
        - fuel_gallons: Fuel consumed
        - fuel_cost: Cost of fuel
        - revenue: Trip revenue
        - load_weight: Weight of cargo
        - hours_driven: Driving time
        - maintenance_cost: Any maintenance costs
        """
        try:
            self.data = pd.read_csv(csv_file_path)
            self._validate_and_clean_data()
            print(f"✅ Successfully loaded {len(self.data)} records")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def _validate_and_clean_data(self):
        """Clean and validate the loaded data."""
        # Convert date column
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Calculate derived metrics
        if 'miles' in self.data.columns and 'fuel_gallons' in self.data.columns:
            self.data['mpg'] = self.data['miles'] / self.data['fuel_gallons'].replace(0, np.nan)
        
        if 'revenue' in self.data.columns and 'miles' in self.data.columns:
            self.data['revenue_per_mile'] = self.data['revenue'] / self.data['miles'].replace(0, np.nan)
        
        if 'fuel_cost' in self.data.columns and 'fuel_gallons' in self.data.columns:
            self.data['fuel_price_per_gallon'] = self.data['fuel_cost'] / self.data['fuel_gallons'].replace(0, np.nan)
        
        # Remove invalid records
        self.data = self.data.dropna(subset=['miles', 'fuel_gallons'])
        
    def analyze_fleet_performance(self):
        """Perform comprehensive fleet performance analysis."""
        print("🔍 Analyzing fleet performance...")
        
        # Basic metrics
        total_trips = len(self.data)
        total_miles = self.data['miles'].sum()
        total_fuel = self.data['fuel_gallons'].sum()
        total_revenue = self.data['revenue'].sum() if 'revenue' in self.data.columns else 0
        total_fuel_cost = self.data['fuel_cost'].sum() if 'fuel_cost' in self.data.columns else 0
        
        # Efficiency metrics
        avg_mpg = self.data['mpg'].mean()
        avg_revenue_per_mile = self.data['revenue_per_mile'].mean() if 'revenue_per_mile' in self.data.columns else 0
        avg_fuel_price = self.data['fuel_price_per_gallon'].mean() if 'fuel_price_per_gallon' in self.data.columns else 0
        
        # Store results
        self.analysis_results.update({
            'basic_metrics': {
                'total_trips': total_trips,
                'total_miles': total_miles,
                'total_fuel_gallons': total_fuel,
                'total_revenue': total_revenue,
                'total_fuel_cost': total_fuel_cost,
                'avg_mpg': avg_mpg,
                'avg_revenue_per_mile': avg_revenue_per_mile,
                'avg_fuel_price': avg_fuel_price
            }
        })
        
        # Truck performance analysis
        if 'truck_id' in self.data.columns:
            truck_performance = self.data.groupby('truck_id').agg({
                'mpg': 'mean',
                'miles': 'sum',
                'revenue': 'sum' if 'revenue' in self.data.columns else 'count',
                'fuel_cost': 'sum' if 'fuel_cost' in self.data.columns else 'count'
            }).round(2)
            
            self.analysis_results['truck_performance'] = truck_performance
        
        # Driver performance analysis
        if 'driver_id' in self.data.columns:
            driver_performance = self.data.groupby('driver_id').agg({
                'mpg': 'mean',
                'miles': 'sum',
                'revenue': 'sum' if 'revenue' in self.data.columns else 'count',
                'fuel_cost': 'sum' if 'fuel_cost' in self.data.columns else 'count'
            }).round(2)
            
            self.analysis_results['driver_performance'] = driver_performance
        
        print("✅ Fleet performance analysis complete")
    
    def identify_optimization_opportunities(self):
        """Identify specific areas for cost savings and efficiency improvements."""
        print("💡 Identifying optimization opportunities...")
        
        opportunities = []
        potential_savings = 0
        
        # Fuel efficiency opportunities
        if 'mpg' in self.data.columns:
            top_10_percent_mpg = self.data['mpg'].quantile(0.9)
            avg_mpg = self.data['mpg'].mean()
            
            if top_10_percent_mpg > avg_mpg * 1.1:  # 10% difference threshold
                mpg_improvement = top_10_percent_mpg - avg_mpg
                annual_fuel_savings = (self.analysis_results['basic_metrics']['total_miles'] * 
                                     (mpg_improvement / avg_mpg) * 
                                     self.analysis_results['basic_metrics']['avg_fuel_price'])
                
                opportunities.append({
                    'category': 'Fuel Efficiency',
                    'description': f'Improve fleet MPG from {avg_mpg:.1f} to {top_10_percent_mpg:.1f}',
                    'potential_annual_savings': annual_fuel_savings,
                    'implementation': 'Driver training, vehicle maintenance, route optimization'
                })
                potential_savings += annual_fuel_savings
        
        # Underperforming vehicle identification
        if 'truck_performance' in self.analysis_results:
            truck_perf = self.analysis_results['truck_performance']
            worst_performers = truck_perf[truck_perf['mpg'] < truck_perf['mpg'].quantile(0.25)]
            
            if len(worst_performers) > 0:
                maintenance_savings = len(worst_performers) * 5000  # Estimated annual savings per truck
                opportunities.append({
                    'category': 'Vehicle Maintenance',
                    'description': f'{len(worst_performers)} trucks performing below fleet average',
                    'potential_annual_savings': maintenance_savings,
                    'implementation': 'Preventive maintenance, possible vehicle replacement'
                })
                potential_savings += maintenance_savings
        
        # Route optimization opportunities
        if 'origin' in self.data.columns and 'destination' in self.data.columns:
            route_efficiency = self.data.groupby(['origin', 'destination']).agg({
                'miles': 'mean',
                'mpg': 'mean'
            })
            
            # Simplified route optimization estimate
            route_savings = self.analysis_results['basic_metrics']['total_fuel_cost'] * 0.05  # 5% estimated savings
            opportunities.append({
                'category': 'Route Optimization',
                'description': 'Optimize routes using AI-powered planning',
                'potential_annual_savings': route_savings,
                'implementation': 'Implement route optimization software'
            })
            potential_savings += route_savings
        
        self.analysis_results['optimization_opportunities'] = opportunities
        self.analysis_results['total_potential_savings'] = potential_savings
        
        print(f"✅ Identified {len(opportunities)} optimization opportunities")
        print(f"💰 Total potential annual savings: ${potential_savings:,.2f}")
    
    def create_visualizations(self):
        """Create charts and visualizations for the report."""
        print("📊 Creating visualizations...")
        
        # 1. Fleet MPG Distribution
        fig_mpg = px.histogram(self.data, x='mpg', nbins=20, 
                              title='Fleet Fuel Efficiency Distribution',
                              labels={'mpg': 'Miles Per Gallon', 'count': 'Number of Trips'})
        fig_mpg.add_vline(x=self.data['mpg'].mean(), line_dash="dash", 
                         annotation_text=f"Fleet Average: {self.data['mpg'].mean():.1f} MPG")
        self.charts['mpg_distribution'] = self._fig_to_image(fig_mpg)
        
        # 2. Top/Bottom Performing Trucks
        if 'truck_performance' in self.analysis_results:
            truck_perf = self.analysis_results['truck_performance'].sort_values('mpg')
            fig_trucks = px.bar(x=truck_perf.index, y=truck_perf['mpg'],
                               title='Truck Performance by Fuel Efficiency',
                               labels={'x': 'Truck ID', 'y': 'Average MPG'})
            self.charts['truck_performance'] = self._fig_to_image(fig_trucks)
        
        # 3. Monthly Trends (if date data available)
        if 'date' in self.data.columns:
            monthly_data = self.data.set_index('date').resample('M').agg({
                'mpg': 'mean',
                'revenue': 'sum' if 'revenue' in self.data.columns else 'count',
                'fuel_cost': 'sum' if 'fuel_cost' in self.data.columns else 'count'
            })
            
            fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
            fig_trends.add_trace(
                go.Scatter(x=monthly_data.index, y=monthly_data['mpg'], name="Avg MPG"),
                secondary_y=False,
            )
            if 'revenue' in self.data.columns:
                fig_trends.add_trace(
                    go.Scatter(x=monthly_data.index, y=monthly_data['revenue'], name="Revenue"),
                    secondary_y=True,
                )
            fig_trends.update_layout(title_text="Monthly Performance Trends")
            fig_trends.update_xaxes(title_text="Date")
            fig_trends.update_yaxes(title_text="Miles Per Gallon", secondary_y=False)
            fig_trends.update_yaxes(title_text="Revenue ($)", secondary_y=True)
            
            self.charts['monthly_trends'] = self._fig_to_image(fig_trends)
        
        print("✅ Visualizations created")
    
    def _fig_to_image(self, fig):
        """Convert plotly figure to image for PDF inclusion."""
        img_bytes = fig.to_image(format="png", width=800, height=500)
        return img_bytes
    
    def generate_pdf_report(self, output_filename="fleet_optimization_audit.pdf", company_name="Your Trucking Company"):
        """Generate a professional PDF report."""
        print("📄 Generating PDF report...")
        
        doc = SimpleDocTemplate(output_filename, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Build the story
        story = []
        
        # Title Page
        story.append(Paragraph(f"Fleet Optimization Audit", title_style))
        story.append(Paragraph(f"{company_name}", styles['Heading2']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Prepared by: AI Consulting Solutions", styles['Normal']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        metrics = self.analysis_results['basic_metrics']
        total_savings = self.analysis_results.get('total_potential_savings', 0)
        
        summary_text = f"""
        This comprehensive audit analyzed {metrics['total_trips']:,} trips covering {metrics['total_miles']:,.0f} miles.
        Our analysis identified potential annual savings of <b>${total_savings:,.2f}</b> through strategic optimizations.
        
        Key findings:
        • Fleet average fuel efficiency: {metrics['avg_mpg']:.1f} MPG
        • Total fuel consumption: {metrics['total_fuel_gallons']:,.0f} gallons
        • Average fuel cost per gallon: ${metrics['avg_fuel_price']:.2f}
        """
        
        if metrics['total_revenue'] > 0:
            summary_text += f"\n• Total revenue analyzed: ${metrics['total_revenue']:,.2f}"
            summary_text += f"\n• Average revenue per mile: ${metrics['avg_revenue_per_mile']:.2f}"
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Optimization Opportunities
        story.append(Paragraph("Optimization Opportunities", heading_style))
        
        opportunities = self.analysis_results.get('optimization_opportunities', [])
        for i, opp in enumerate(opportunities, 1):
            opp_text = f"""
            <b>{i}. {opp['category']}</b><br/>
            {opp['description']}<br/>
            <b>Potential Annual Savings: ${opp['potential_annual_savings']:,.2f}</b><br/>
            Implementation: {opp['implementation']}<br/><br/>
            """
            story.append(Paragraph(opp_text, styles['Normal']))
        
        story.append(PageBreak())
        
        # Charts Section
        story.append(Paragraph("Performance Analysis", heading_style))
        
        for chart_name, chart_data in self.charts.items():
            # Save chart as temporary image
            chart_filename = f"temp_{chart_name}.png"
            with open(chart_filename, 'wb') as f:
                f.write(chart_data)
            
            # Add to story
            story.append(Image(chart_filename, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Next Steps & Recommendations", heading_style))
        
        recommendations = f"""
        Based on our analysis, we recommend the following implementation priority:
        
        <b>Immediate Actions (0-30 days):</b>
        • Implement driver fuel efficiency training program
        • Schedule maintenance for underperforming vehicles
        • Begin tracking additional KPIs for ongoing monitoring
        
        <b>Short-term Improvements (1-3 months):</b>
        • Deploy route optimization software
        • Establish preventive maintenance schedules
        • Implement driver performance monitoring dashboard
        
        <b>Long-term Optimizations (3-12 months):</b>
        • Consider fleet vehicle replacements for poor performers
        • Implement comprehensive fleet management system
        • Develop predictive maintenance capabilities
        
        <b>ROI Projection:</b>
        With an estimated annual savings of ${total_savings:,.2f}, most optimizations 
        will pay for themselves within 6-12 months while providing ongoing benefits.
        """
        
        story.append(Paragraph(recommendations, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Clean up temporary chart files
        for chart_name in self.charts.keys():
            try:
                import os
                os.remove(f"temp_{chart_name}.png")
            except:
                pass
        
        print(f"✅ PDF report generated: {output_filename}")
    
    def run_complete_audit(self, csv_file_path, output_filename=None, company_name="Your Trucking Company"):
        """Run the complete audit process."""
        print("🚛 Starting Trucking Fleet Optimization Audit...")
        print("=" * 50)
        
        # Load data
        if not self.load_data(csv_file_path):
            return False
        
        # Run analysis
        self.analyze_fleet_performance()
        self.identify_optimization_opportunities()
        self.create_visualizations()
        
        # Generate report
        if output_filename is None:
            output_filename = f"fleet_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        self.generate_pdf_report(output_filename, company_name)
        
        print("=" * 50)
        print("🎉 Audit complete! Check your PDF report for detailed findings.")
        
        # Display summary
        total_savings = self.analysis_results.get('total_potential_savings', 0)
        print(f"\n💰 POTENTIAL ANNUAL SAVINGS: ${total_savings:,.2f}")
        
        return True

def create_sample_data(filename="sample_trucking_data.csv"):
    """Create sample trucking data for testing."""
    print("📊 Creating sample trucking data...")
    
    np.random.seed(42)
    
    # Generate sample data
    n_records = 500
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', periods=n_records)
    
    trucks = [f"TRUCK-{i:03d}" for i in range(1, 21)]  # 20 trucks
    drivers = [f"DRIVER-{i:03d}" for i in range(1, 31)]  # 30 drivers
    
    cities = ["Atlanta", "Chicago", "Dallas", "Denver", "Los Angeles", 
              "Miami", "New York", "Phoenix", "Seattle", "Houston"]
    
    data = []
    for i in range(n_records):
        # Some trucks are more efficient than others
        truck_id = np.random.choice(trucks)
        truck_efficiency_factor = 1.0
        if "001" in truck_id or "002" in truck_id:  # These are efficient trucks
            truck_efficiency_factor = 1.2
        elif "019" in truck_id or "020" in truck_id:  # These need maintenance
            truck_efficiency_factor = 0.7
        
        miles = np.random.normal(300, 100)
        miles = max(50, miles)  # Minimum 50 miles
        
        base_mpg = 6.5 * truck_efficiency_factor
        mpg = np.random.normal(base_mpg, 0.8)
        mpg = max(3, mpg)  # Minimum 3 MPG
        
        fuel_gallons = miles / mpg
        fuel_price = np.random.normal(3.75, 0.25)  # Average diesel price
        fuel_cost = fuel_gallons * fuel_price
        
        revenue = miles * np.random.normal(2.25, 0.35)  # Revenue per mile
        revenue = max(revenue, fuel_cost * 1.1)  # Ensure profitability
        
        record = {
            'date': dates[i].strftime('%Y-%m-%d'),
            'truck_id': truck_id,
            'driver_id': np.random.choice(drivers),
            'origin': np.random.choice(cities),
            'destination': np.random.choice(cities),
            'miles': round(miles, 1),
            'fuel_gallons': round(fuel_gallons, 2),
            'fuel_cost': round(fuel_cost, 2),
            'revenue': round(revenue, 2),
            'load_weight': round(np.random.normal(25000, 5000)),
            'hours_driven': round(miles / np.random.normal(55, 10), 1),
            'maintenance_cost': round(np.random.exponential(50), 2) if np.random.random() < 0.1 else 0
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✅ Sample data created: {filename}")
    return filename

if __name__ == "__main__":
    # Example usage
    auditor = TruckingOptimizationAuditor()
    
    # Create sample data for demonstration
    sample_file = create_sample_data()
    
    # Run the audit
    auditor.run_complete_audit(
        csv_file_path=sample_file,
        company_name="Demo Trucking Company",
        output_filename="demo_fleet_audit.pdf"
    )