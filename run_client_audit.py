#!/usr/bin/env python3
"""
Simple script to run fleet optimization audit for a real client
"""

from trucking_optimization_audit import TruckingOptimizationAuditor

def run_client_audit():
    """Run audit for a real client"""
    
    # Get client information
    print("🚛 FleetOptimize AI Consulting - Client Audit Tool")
    print("=" * 50)
    
    client_name = input("Enter client company name: ")
    csv_file = input("Enter path to client's CSV file: ")
    
    # Initialize the auditor
    auditor = TruckingOptimizationAuditor()
    
    # Create output filename
    output_file = f"{client_name.replace(' ', '_')}_fleet_audit.pdf"
    
    # Run the complete audit
    success = auditor.run_complete_audit(
        csv_file_path=csv_file,
        company_name=client_name,
        output_filename=output_file
    )
    
    if success:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Report generated: {output_file}")
        print(f"💰 Send this report to {client_name} with your invoice!")
    else:
        print(f"\n❌ Error processing {client_name}'s data")
        print("Check the CSV file format and try again")

if __name__ == "__main__":
    run_client_audit()