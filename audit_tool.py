#!/usr/bin/env python3
"""
Fleet Optimization Audit Tool - Entry Point #1
==============================================

A professional analysis tool for trucking companies to identify cost savings,
efficiency improvements, and optimization opportunities.

This is the fastest path to first revenue - a one-time, fixed-fee analysis.
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
import streamlit as st
from typing import Dict, List, Optional
from database import db
from config import config
import tempfile
import os

warnings.filterwarnings('ignore')

class FleetOptimizationAuditor:
    """
    Enhanced audit tool that integrates with unified database
    """
    
    def __init__(self, company_id: str = None):
        self.company_id = company_id
        self.data = None
        self.analysis_results = {}
        self.charts = {}
        
    def load_data_from_csv(self, csv_file) -> bool:
        """Load data from uploaded CSV file"""
        try:
            self.data = pd.read_csv(csv_file)
            
            # Validate required columns
            required_columns = ['date', 'miles', 'revenue', 'fuel_cost']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                return False
                
            # Clean and prepare data
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data['profit'] = self.data['revenue'] - self.data['fuel_cost']
            self.data['revenue_per_mile'] = self.data['revenue'] / self.data['miles']
            self.data['fuel_cost_per_mile'] = self.data['fuel_cost'] / self.data['miles']
            
            return True
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def load_data_from_database(self) -> bool:
        """Load data from database for existing customers"""
        if not self.company_id:
            return False
            
        try:
            self.data = db.get_audit_data(self.company_id)
            if self.data.empty:
                return False
                
            # Prepare data for analysis
            self.data['date'] = pd.to_datetime(self.data['pickup_date'])
            self.data['profit'] = self.data['revenue'] - self.data['fuel_cost'] - self.data.get('other_expenses', 0)
            self.data['revenue_per_mile'] = self.data['revenue'] / self.data['miles']
            self.data['fuel_cost_per_mile'] = self.data['fuel_cost'] / self.data['miles']
            
            return True
            
        except Exception as e:
            st.error(f"Error loading database data: {str(e)}")
            return False
    
    def analyze_performance(self) -> Dict:
        """Comprehensive performance analysis"""
        if self.data is None or self.data.empty:
            return {}
        
        analysis = {}
        
        # Basic metrics
        analysis['total_loads'] = len(self.data)
        analysis['total_revenue'] = float(self.data['revenue'].sum())
        analysis['total_fuel_cost'] = float(self.data['fuel_cost'].sum())
        analysis['total_miles'] = float(self.data['miles'].sum())
        analysis['total_profit'] = float(self.data['profit'].sum())
        analysis['period_start'] = self.data['date'].min().strftime('%Y-%m-%d')
        analysis['period_end'] = self.data['date'].max().strftime('%Y-%m-%d')
        
        # Efficiency metrics
        analysis['avg_revenue_per_mile'] = float(self.data['revenue_per_mile'].mean())
        analysis['avg_fuel_cost_per_mile'] = float(self.data['fuel_cost_per_mile'].mean())
        analysis['profit_margin'] = float((analysis['total_profit'] / analysis['total_revenue']) * 100) if analysis['total_revenue'] > 0 else 0
        
        # Performance trends
        monthly_data = self.data.groupby(self.data['date'].dt.to_period('M')).agg({
            'revenue': 'sum',
            'fuel_cost': 'sum',
            'miles': 'sum',
            'profit': 'sum'
        }).reset_index()
        monthly_data['date'] = monthly_data['date'].astype(str)
        
        analysis['monthly_trends'] = monthly_data.to_dict('records')
        
        # Identify problem areas
        analysis['findings'] = self._identify_issues()
        analysis['recommendations'] = self._generate_recommendations()
        analysis['potential_savings'] = self._calculate_potential_savings()
        
        self.analysis_results = analysis
        return analysis
    
    def _identify_issues(self) -> List[Dict]:
        """Identify operational issues and inefficiencies"""
        findings = []
        
        # Low profit margin loads
        low_margin_threshold = 0.1  # 10%
        low_margin_loads = self.data[self.data['profit'] / self.data['revenue'] < low_margin_threshold]
        if len(low_margin_loads) > 0:
            findings.append({
                'issue': 'Low Profit Margin Loads',
                'severity': 'high',
                'description': f'{len(low_margin_loads)} loads ({len(low_margin_loads)/len(self.data)*100:.1f}%) have profit margins below 10%',
                'impact': f'${low_margin_loads["revenue"].sum() - low_margin_loads["profit"].sum():.0f} in potential revenue optimization'
            })
        
        # High fuel cost per mile
        fuel_cost_per_mile_median = self.data['fuel_cost_per_mile'].median()
        high_fuel_cost_threshold = fuel_cost_per_mile_median * 1.2
        high_fuel_loads = self.data[self.data['fuel_cost_per_mile'] > high_fuel_cost_threshold]
        if len(high_fuel_loads) > 0:
            findings.append({
                'issue': 'High Fuel Costs',
                'severity': 'medium',
                'description': f'{len(high_fuel_loads)} loads have fuel costs 20% above median',
                'impact': f'Potential savings of ${(high_fuel_loads["fuel_cost"].sum() - high_fuel_loads["miles"].sum() * fuel_cost_per_mile_median):.0f}'
            })
        
        # Deadhead analysis (if origin/destination data available)
        if 'origin_city' in self.data.columns and 'destination_city' in self.data.columns:
            route_efficiency = self._analyze_route_efficiency()
            if route_efficiency['inefficient_routes'] > 0:
                findings.append({
                    'issue': 'Routing Inefficiencies',
                    'severity': 'medium',
                    'description': f'{route_efficiency["inefficient_routes"]} potentially inefficient routes identified',
                    'impact': f'Estimated ${route_efficiency["potential_savings"]:.0f} in routing optimization'
                })
        
        return findings
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if self.analysis_results.get('profit_margin', 0) < 15:
            recommendations.append({
                'category': 'Pricing Strategy',
                'priority': 'high',
                'recommendation': 'Review pricing strategy to improve profit margins',
                'action': 'Analyze competitor rates and implement dynamic pricing based on lane profitability',
                'estimated_impact': 'Increase profit margin by 3-5%'
            })
        
        avg_fuel_cost = self.data['fuel_cost_per_mile'].mean()
        if avg_fuel_cost > 0.45:  # Industry benchmark
            recommendations.append({
                'category': 'Fuel Management',
                'priority': 'high',
                'recommendation': 'Implement fuel cost reduction strategies',
                'action': 'Negotiate fuel card discounts, optimize routes, improve driver training',
                'estimated_impact': f'Save ${(avg_fuel_cost - 0.40) * self.analysis_results["total_miles"]:.0f} annually'
            })
        
        recommendations.append({
            'category': 'Technology Investment',
            'priority': 'medium',
            'recommendation': 'Implement fleet management software',
            'action': 'Real-time tracking, route optimization, and automated reporting',
            'estimated_impact': 'Reduce operational costs by 8-12%'
        })
        
        return recommendations
    
    def _calculate_potential_savings(self) -> float:
        """Calculate total potential annual savings"""
        total_savings = 0
        
        # Fuel optimization (5% reduction)
        total_savings += self.analysis_results['total_fuel_cost'] * 0.05
        
        # Route optimization (3% mile reduction)
        total_savings += self.analysis_results['total_fuel_cost'] * 0.03
        
        # Pricing optimization (2% revenue increase)
        total_savings += self.analysis_results['total_revenue'] * 0.02
        
        return float(total_savings)
    
    def _analyze_route_efficiency(self) -> Dict:
        """Analyze route efficiency if location data is available"""
        # Simplified route analysis
        route_counts = self.data.groupby(['origin_city', 'destination_city']).size()
        single_occurrence_routes = (route_counts == 1).sum()
        
        return {
            'total_routes': len(route_counts),
            'inefficient_routes': single_occurrence_routes,
            'potential_savings': single_occurrence_routes * 200  # Estimated savings per optimized route
        }
    
    def create_visualizations(self) -> Dict[str, str]:
        """Create charts for the audit report"""
        charts = {}
        
        # Revenue vs Fuel Cost Over Time
        fig1 = go.Figure()
        monthly_data = pd.DataFrame(self.analysis_results['monthly_trends'])
        
        fig1.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['revenue'],
            name='Revenue',
            line=dict(color='green', width=3)
        ))
        
        fig1.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['fuel_cost'],
            name='Fuel Cost',
            line=dict(color='red', width=3)
        ))
        
        fig1.update_layout(
            title='Revenue vs Fuel Cost Trend',
            xaxis_title='Month',
            yaxis_title='Amount ($)',
            template='plotly_white'
        )
        
        charts['revenue_trend'] = self._fig_to_base64(fig1)
        
        # Profit Margin Analysis
        fig2 = px.histogram(
            self.data,
            x='profit',
            nbins=20,
            title='Profit Distribution by Load',
            template='plotly_white'
        )
        charts['profit_distribution'] = self._fig_to_base64(fig2)
        
        # Performance Metrics Dashboard
        fig3 = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue per Mile', 'Fuel Cost per Mile', 'Load Count by Month', 'Profit Margin Trend'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue per mile scatter
        fig3.add_trace(go.Scatter(
            x=self.data['miles'],
            y=self.data['revenue_per_mile'],
            mode='markers',
            name='Revenue/Mile'
        ), row=1, col=1)
        
        # Fuel cost per mile scatter
        fig3.add_trace(go.Scatter(
            x=self.data['miles'],
            y=self.data['fuel_cost_per_mile'],
            mode='markers',
            name='Fuel Cost/Mile',
            marker=dict(color='red')
        ), row=1, col=2)
        
        # Monthly load count
        monthly_loads = self.data.groupby(self.data['date'].dt.to_period('M')).size()
        fig3.add_trace(go.Bar(
            x=[str(x) for x in monthly_loads.index],
            y=monthly_loads.values,
            name='Load Count'
        ), row=2, col=1)
        
        # Profit margin trend
        profit_margin_trend = monthly_data.copy()
        profit_margin_trend['profit_margin'] = (profit_margin_trend['profit'] / profit_margin_trend['revenue']) * 100
        fig3.add_trace(go.Scatter(
            x=profit_margin_trend['date'],
            y=profit_margin_trend['profit_margin'],
            mode='lines+markers',
            name='Profit Margin %'
        ), row=2, col=2)
        
        fig3.update_layout(height=600, showlegend=False, template='plotly_white')
        charts['dashboard'] = self._fig_to_base64(fig3)
        
        return charts
    
    def _fig_to_base64(self, fig) -> str:
        """Convert Plotly figure to base64 string for PDF embedding"""
        img_bytes = fig.to_image(format="png", width=800, height=500)
        img_base64 = base64.b64encode(img_bytes).decode()
        return img_base64
    
    def generate_pdf_report(self, company_name: str = "Fleet Company") -> str:
        """Generate comprehensive PDF audit report"""
        if not self.analysis_results:
            self.analyze_performance()
        
        charts = self.create_visualizations()
        
        # Create temporary file for PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        
        doc = SimpleDocTemplate(temp_filename, pagesize=letter, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79')
        )
        
        story.append(Paragraph("Fleet Optimization Audit Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Company: {company_name}", styles['Heading2']))
        story.append(Paragraph(f"Analysis Period: {self.analysis_results['period_start']} to {self.analysis_results['period_end']}", styles['Normal']))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading1']))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${self.analysis_results['total_revenue']:,.0f}"],
            ['Total Fuel Cost', f"${self.analysis_results['total_fuel_cost']:,.0f}"],
            ['Total Miles', f"{self.analysis_results['total_miles']:,.0f}"],
            ['Profit Margin', f"{self.analysis_results['profit_margin']:.1f}%"],
            ['Potential Annual Savings', f"${self.analysis_results['potential_savings']:,.0f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(PageBreak())
        
        # Key Findings
        story.append(Paragraph("Key Findings", styles['Heading1']))
        for i, finding in enumerate(self.analysis_results['findings'], 1):
            story.append(Paragraph(f"{i}. {finding['issue']}", styles['Heading3']))
            story.append(Paragraph(f"Severity: {finding['severity'].title()}", styles['Normal']))
            story.append(Paragraph(finding['description'], styles['Normal']))
            story.append(Paragraph(f"Impact: {finding['impact']}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Charts
        story.append(PageBreak())
        story.append(Paragraph("Performance Analysis", styles['Heading1']))
        
        for chart_name, chart_b64 in charts.items():
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                temp_img.write(base64.b64decode(chart_b64))
                temp_img_path = temp_img.name
            
            story.append(Image(temp_img_path, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 20))
            os.unlink(temp_img_path)  # Clean up temp image
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Recommendations", styles['Heading1']))
        
        for i, rec in enumerate(self.analysis_results['recommendations'], 1):
            story.append(Paragraph(f"{i}. {rec['category']}", styles['Heading3']))
            story.append(Paragraph(f"Priority: {rec['priority'].title()}", styles['Normal']))
            story.append(Paragraph(rec['recommendation'], styles['Normal']))
            story.append(Paragraph(f"Action: {rec['action']}", styles['Normal']))
            story.append(Paragraph(f"Estimated Impact: {rec['estimated_impact']}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return temp_filename

def run_streamlit_audit_tool():
    """Streamlit interface for the audit tool"""
    st.set_page_config(
        page_title="Fleet Optimization Audit",
        page_icon="🚛",
        layout="wide"
    )
    
    st.title("🚛 Fleet Optimization Audit")
    st.markdown("**Discover Hidden Money in Your Fleet Data**")
    st.markdown("*Professional analysis to identify cost savings and efficiency improvements*")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Audit Configuration")
        company_name = st.text_input("Company Name", value="Your Fleet Company")
        
        audit_type = st.radio(
            "Data Source",
            ["Upload CSV File", "Connect to Database"]
        )
    
    auditor = FleetOptimizationAuditor()
    
    if audit_type == "Upload CSV File":
        st.header("Upload Your Fleet Data")
        st.markdown("Upload a CSV file with your fleet operations data. Required columns: date, miles, revenue, fuel_cost")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload your fleet data CSV file"
        )
        
        if uploaded_file is not None:
            if auditor.load_data_from_csv(uploaded_file):
                st.success(f"✅ Data loaded successfully! {len(auditor.data)} records found.")
                
                # Show data preview
                with st.expander("Preview Data"):
                    st.dataframe(auditor.data.head(10))
                
                # Run analysis
                if st.button("🔍 Run Optimization Analysis", type="primary"):
                    with st.spinner("Analyzing your fleet data..."):
                        results = auditor.analyze_performance()
                        
                        if results:
                            # Display key metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Total Revenue", f"${results['total_revenue']:,.0f}")
                            with col2:
                                st.metric("Profit Margin", f"{results['profit_margin']:.1f}%")
                            with col3:
                                st.metric("Total Miles", f"{results['total_miles']:,.0f}")
                            with col4:
                                st.metric("Potential Savings", f"${results['potential_savings']:,.0f}")
                            
                            # Show findings
                            st.header("🔍 Key Findings")
                            for finding in results['findings']:
                                severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                                st.write(f"{severity_color.get(finding['severity'], '⚪')} **{finding['issue']}**")
                                st.write(finding['description'])
                                st.write(f"💰 {finding['impact']}")
                                st.write("---")
                            
                            # Show recommendations
                            st.header("💡 Recommendations")
                            for rec in results['recommendations']:
                                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                                st.write(f"{priority_color.get(rec['priority'], '⚪')} **{rec['category']}**")
                                st.write(rec['recommendation'])
                                st.write(f"📈 {rec['estimated_impact']}")
                                st.write("---")
                            
                            # Generate PDF report
                            if st.button("📄 Generate Full PDF Report"):
                                with st.spinner("Generating comprehensive PDF report..."):
                                    pdf_path = auditor.generate_pdf_report(company_name)
                                    
                                    with open(pdf_path, 'rb') as pdf_file:
                                        st.download_button(
                                            label="⬇️ Download PDF Report",
                                            data=pdf_file.read(),
                                            file_name=f"fleet_audit_{company_name.replace(' ', '_')}.pdf",
                                            mime="application/pdf"
                                        )
                                    
                                    # Clean up temp file
                                    os.unlink(pdf_path)
    
    else:  # Database connection
        st.header("Connect to Your Fleet Database")
        st.info("This feature is available for existing customers with data in our system.")
        
        company_id = st.text_input("Company ID")
        
        if company_id and st.button("Load Data"):
            auditor.company_id = company_id
            if auditor.load_data_from_database():
                st.success("✅ Data loaded from database!")
                # Continue with analysis...
            else:
                st.error("❌ Could not load data. Please check your Company ID.")

if __name__ == "__main__":
    run_streamlit_audit_tool()