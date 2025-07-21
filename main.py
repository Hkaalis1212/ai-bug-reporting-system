#!/usr/bin/env python3
"""
FleetFlow - Main Application Launcher
===================================

The "One Platform, Three Front Doors" fleet management SaaS.
This launcher provides access to all three entry points:

1. Optimization Audit (Entry Point for Skeptical Owners)
2. Routing & Dispatch Hub (Core SaaS for Fleet Managers)
3. Document AI (Niche Problem-Solver for Back Office)
"""

import streamlit as st
import sys
import os
from config import config

# Import the three front doors
from audit_tool import run_streamlit_audit_tool
from routing_hub import run_routing_hub
from document_ai import run_document_ai

def main():
    """Main application launcher"""
    
    # Page configuration
    st.set_page_config(
        page_title="FleetFlow - Fleet Management Platform",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5f8f 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        height: 100%;
    }
    .feature-card h3 {
        color: #1f4e79;
        margin-bottom: 1rem;
    }
    .pricing-tag {
        background: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 1rem;
    }
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: #1f4e79;
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h1>🚛 FleetFlow</h1>
            <p><i>One Platform, Three Front Doors</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Choose Your Entry Point")
        
        entry_point = st.radio(
            "Select Application:",
            [
                "🏠 Home & Overview",
                "📊 Optimization Audit", 
                "🚛 Routing & Dispatch Hub",
                "📄 Document AI"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Quick stats or company info
        if 'company_id' in st.session_state:
            st.markdown("### Your Account")
            st.markdown(f"**Company ID:** {st.session_state.company_id}")
            st.markdown("**Plan:** Demo")
            
            if st.button("🚪 Switch Company"):
                if 'company_id' in st.session_state:
                    del st.session_state.company_id
                st.rerun()
        else:
            st.markdown("### Demo Mode")
            st.info("You're using the demo version. All data will be temporary.")
            
            if st.button("🏢 Set Company ID"):
                st.session_state.company_id = "demo-company-123"
                st.rerun()
        
        st.markdown("---")
        st.markdown("### Need Help?")
        st.markdown("""
        📧 Email: support@fleetflow.com  
        📞 Phone: 1-800-FLEET-AI  
        💬 Chat: Available 24/7
        """)
    
    # Main content based on selected entry point
    if entry_point == "🏠 Home & Overview":
        show_homepage()
    elif entry_point == "📊 Optimization Audit":
        run_streamlit_audit_tool()
    elif entry_point == "🚛 Routing & Dispatch Hub":
        run_routing_hub()
    elif entry_point == "📄 Document AI":
        run_document_ai()

def show_homepage():
    """Display the main homepage with overview of all three front doors"""
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🚛 FleetFlow</h1>
        <h2>The Complete Fleet Management Platform</h2>
        <p>One platform, three powerful entry points designed for different roles in your trucking business</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Value proposition
    st.markdown("## Why FleetFlow?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 💰 Reduce Costs
        - Cut fuel expenses by 15-20%
        - Optimize routes and reduce deadhead miles
        - Identify unprofitable loads
        """)
    
    with col2:
        st.markdown("""
        ### ⚡ Increase Efficiency
        - Real-time fleet tracking
        - Automated paperwork processing
        - AI-powered route optimization
        """)
    
    with col3:
        st.markdown("""
        ### 📈 Grow Your Business
        - Data-driven decision making
        - Scalable platform
        - Professional reporting
        """)
    
    st.markdown("---")
    
    # Three front doors
    st.markdown("## Three Ways to Get Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Optimization Audit</h3>
            <p><strong>Perfect for:</strong> Skeptical owners who want to see results before committing</p>
            
            <p><strong>What it does:</strong></p>
            <ul>
                <li>Analyzes your historical data</li>
                <li>Identifies hidden money leaks</li>
                <li>Professional PDF report</li>
                <li>One-time analysis</li>
            </ul>
            
            <p><strong>Ideal customer:</strong> Owner-operators or small fleets (3-15 trucks) who track data in spreadsheets</p>
            
            <div class="pricing-tag">$497 One-Time</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Audit Analysis", key="audit_btn"):
            st.session_state.page = "audit"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🚛 Routing & Dispatch Hub</h3>
            <p><strong>Perfect for:</strong> Fleet managers and dispatchers who need daily operational tools</p>
            
            <p><strong>What it does:</strong></p>
            <ul>
                <li>Real-time fleet dashboard</li>
                <li>Load creation and tracking</li>
                <li>AI route optimization</li>
                <li>Driver and truck management</li>
            </ul>
            
            <p><strong>Ideal customer:</strong> Growing fleets (5-50 trucks) with dedicated dispatch operations</p>
            
            <div class="pricing-tag">$29/truck/month</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 Access Dispatch Hub", key="dispatch_btn"):
            st.session_state.page = "dispatch"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Document AI</h3>
            <p><strong>Perfect for:</strong> Back-office staff drowning in paperwork</p>
            
            <p><strong>What it does:</strong></p>
            <ul>
                <li>Scans Bills of Lading</li>
                <li>Extracts Proof of Delivery data</li>
                <li>Processes invoices and receipts</li>
                <li>Creates digital records automatically</li>
            </ul>
            
            <p><strong>Ideal customer:</strong> Any fleet tired of manual data entry from paper documents</p>
            
            <div class="pricing-tag">$0.50/document</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🤖 Try Document AI", key="doc_ai_btn"):
            st.session_state.page = "document_ai"
            st.rerun()
    
    st.markdown("---")
    
    # Customer testimonials
    st.markdown("## What Our Customers Say")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        > "FleetFlow's audit showed us we were losing $2,400 per month on inefficient routes. 
        > The recommendations paid for themselves in the first week."
        > 
        > **- Mike Thompson, Thompson Trucking (12 trucks)**
        """)
    
    with col2:
        st.markdown("""
        > "The Document AI saved our office manager 15 hours per week. 
        > No more typing BOL data - it just works automatically."
        > 
        > **- Sarah Chen, Midwest Logistics (28 trucks)**
        """)
    
    st.markdown("---")
    
    # Getting started section
    st.markdown("## Ready to Get Started?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🆓 Free Trial Options
        
        - **Audit Tool**: Upload sample data and see the analysis
        - **Dispatch Hub**: 14-day full access trial
        - **Document AI**: Process 5 documents free
        
        No credit card required for trials.
        """)
    
    with col2:
        st.markdown("""
        ### 📞 Talk to an Expert
        
        Not sure which entry point is right for you?
        
        Schedule a 15-minute call with our fleet optimization experts.
        
        We'll help you choose the best starting point for your specific needs.
        """)
    
    # Call-to-action buttons
    st.markdown("### Choose Your Starting Point")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Start with Audit", type="primary"):
            st.session_state.entry_point = "audit"
            st.rerun()
    
    with col2:
        if st.button("🚛 Go to Dispatch Hub", type="primary"):
            st.session_state.entry_point = "dispatch"
            st.rerun()
    
    with col3:
        if st.button("📄 Try Document AI", type="primary"):
            st.session_state.entry_point = "document_ai"
            st.rerun()
    
    with col4:
        if st.button("📞 Schedule Call"):
            st.info("Feature coming soon! Email us at sales@fleetflow.com")
    
    # Technical specifications footer
    with st.expander("🔧 Technical Specifications"):
        st.markdown("""
        ### Platform Features
        
        **Infrastructure:**
        - Cloud-hosted on secure servers
        - 99.9% uptime guarantee
        - Real-time data synchronization
        - Mobile-responsive design
        
        **Security:**
        - Enterprise-grade encryption
        - SOC 2 Type II compliant
        - GDPR and CCPA compliant
        - Regular security audits
        
        **Integrations:**
        - Popular fuel card providers
        - Telematics systems
        - Accounting software (QuickBooks, etc.)
        - ELD providers
        
        **AI Technology:**
        - OpenAI GPT-4 for document processing
        - Advanced route optimization algorithms
        - Predictive maintenance insights
        - Natural language processing
        """)

if __name__ == "__main__":
    # Configuration validation
    config_errors = config.validate()
    
    if config_errors:
        st.error("⚠️ Configuration Error")
        st.markdown("Please check your environment variables:")
        for error in config_errors:
            st.markdown(f"- {error}")
        st.stop()
    
    # Run the main application
    main()