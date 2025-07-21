#!/usr/bin/env python3
"""
Document AI Tool - Entry Point #3
=================================

A simple, powerful tool focused on ONE thing: eliminating paperwork.
Uses OpenAI Vision API to automatically extract data from trucking documents.

Target Customer: Back-office administrators or owners buried in 
Bills of Lading (BOLs) and Proofs of Delivery (PODs).
"""

import streamlit as st
import pandas as pd
from PIL import Image
import base64
import io
from datetime import datetime, date
from typing import Dict, List, Optional
import json
import openai
from database import db
from config import config

# Configure OpenAI
openai.api_key = config.openai.api_key

class DocumentAIProcessor:
    """
    AI-powered document processing for trucking paperwork
    """
    
    def __init__(self, company_id: str):
        self.company_id = company_id
    
    def encode_image_to_base64(self, image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def extract_document_data(self, image: Image.Image, document_type: str) -> Dict:
        """
        Use OpenAI Vision API to extract structured data from document images
        """
        try:
            # Convert image to base64
            base64_image = self.encode_image_to_base64(image)
            
            # Define extraction prompts based on document type
            prompts = {
                'bol': """
                Extract data from this Bill of Lading (BOL) document. Please identify and extract:
                
                1. BOL Number
                2. Shipper name and address
                3. Consignee name and address
                4. Pickup date
                5. Delivery date
                6. Origin city/state
                7. Destination city/state
                8. Commodity/goods description
                9. Weight (total pounds)
                10. Number of pieces/units
                11. Carrier information
                12. Pro number (if any)
                13. Special instructions
                14. Freight charges/rate
                
                Return as JSON with keys: bol_number, shipper_name, shipper_address, consignee_name, consignee_address, pickup_date, delivery_date, origin_city, origin_state, destination_city, destination_state, commodity, weight_lbs, pieces, carrier, pro_number, special_instructions, freight_charges
                """,
                
                'pod': """
                Extract data from this Proof of Delivery (POD) document. Please identify and extract:
                
                1. Delivery date and time
                2. BOL/Pro number reference
                3. Consignee name
                4. Delivery address
                5. Receiver signature (if legible)
                6. Driver name/signature
                7. Delivery status (complete/partial/damaged)
                8. Number of pieces delivered
                9. Any delivery notes or exceptions
                10. Truck/trailer number
                
                Return as JSON with keys: delivery_date, delivery_time, reference_number, consignee_name, delivery_address, receiver_signature, driver_name, delivery_status, pieces_delivered, delivery_notes, truck_number
                """,
                
                'invoice': """
                Extract data from this freight invoice. Please identify and extract:
                
                1. Invoice number
                2. Invoice date
                3. Customer/bill to information
                4. BOL/Pro number reference
                5. Service dates
                6. Origin and destination
                7. Line items and descriptions
                8. Rates and charges
                9. Total amount due
                10. Payment terms
                11. Due date
                
                Return as JSON with keys: invoice_number, invoice_date, customer_name, customer_address, reference_number, service_date, origin, destination, line_items, total_amount, payment_terms, due_date
                """,
                
                'receipt': """
                Extract data from this fuel/expense receipt. Please identify and extract:
                
                1. Date of purchase
                2. Vendor/station name
                3. Location/address
                4. Receipt/transaction number
                5. Fuel gallons (if fuel receipt)
                6. Price per gallon (if fuel)
                7. Total amount
                8. Payment method
                9. Vehicle/truck info (if available)
                10. Driver info (if available)
                
                Return as JSON with keys: purchase_date, vendor_name, location, receipt_number, fuel_gallons, price_per_gallon, total_amount, payment_method, vehicle_info, driver_info
                """
            }
            
            prompt = prompts.get(document_type, prompts['bol'])
            
            # Call OpenAI Vision API
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse the response
            extracted_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text extraction
            try:
                extracted_data = json.loads(extracted_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response from text
                extracted_data = {
                    'raw_text': extracted_text,
                    'extraction_method': 'text_parsing',
                    'document_type': document_type,
                    'processed_at': datetime.now().isoformat()
                }
            
            # Add metadata
            extracted_data['document_type'] = document_type
            extracted_data['processed_at'] = datetime.now().isoformat()
            extracted_data['confidence'] = 'high' if 'bol_number' in extracted_data or 'invoice_number' in extracted_data else 'medium'
            
            return extracted_data
            
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            return {
                'error': str(e),
                'document_type': document_type,
                'processed_at': datetime.now().isoformat(),
                'confidence': 'error'
            }
    
    def save_document_and_data(self, image: Image.Image, extracted_data: Dict, document_type: str, filename: str) -> str:
        """Save document image and extracted data to database"""
        try:
            # For demo purposes, we'll save the extracted data without actual file storage
            # In production, you'd upload to Supabase Storage
            
            document_data = {
                'document_type': document_type,
                'file_name': filename,
                'file_path': f"documents/{self.company_id}/{filename}",  # Mock path
                'extracted_data': extracted_data,
                'status': 'processed' if 'error' not in extracted_data else 'error'
            }
            
            document_id = db.save_document(self.company_id, document_data)
            return document_id
            
        except Exception as e:
            st.error(f"Error saving document: {str(e)}")
            return None
    
    def create_load_from_bol(self, bol_data: Dict) -> Optional[str]:
        """Create a load record from BOL data"""
        try:
            # Extract relevant fields for load creation
            load_data = {
                'load_number': bol_data.get('bol_number', f"BOL-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                'pickup_date': bol_data.get('pickup_date'),
                'delivery_date': bol_data.get('delivery_date'),
                'origin_city': bol_data.get('origin_city'),
                'origin_state': bol_data.get('origin_state'),
                'destination_city': bol_data.get('destination_city'),
                'destination_state': bol_data.get('destination_state'),
                'weight_lbs': self._parse_weight(bol_data.get('weight_lbs')),
                'revenue': self._parse_amount(bol_data.get('freight_charges')),
                'status': 'planned'
            }
            
            # Only create if we have minimum required data
            if load_data['load_number'] and load_data['origin_city'] and load_data['destination_city']:
                load_id = db.create_load(self.company_id, load_data)
                return load_id
            
            return None
            
        except Exception as e:
            st.error(f"Error creating load from BOL: {str(e)}")
            return None
    
    def _parse_weight(self, weight_str: str) -> Optional[int]:
        """Parse weight string to integer"""
        if not weight_str:
            return None
        try:
            # Remove common weight suffixes and parse number
            weight_clean = str(weight_str).replace('lbs', '').replace('pounds', '').replace(',', '').strip()
            return int(float(weight_clean))
        except:
            return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse currency string to float"""
        if not amount_str:
            return None
        try:
            # Remove currency symbols and parse
            amount_clean = str(amount_str).replace('$', '').replace(',', '').strip()
            return float(amount_clean)
        except:
            return None

def run_document_ai():
    """Main Streamlit interface for Document AI"""
    st.set_page_config(
        page_title="FleetFlow - Document AI",
        page_icon="📄",
        layout="wide"
    )
    
    # Authentication check (simplified for demo)
    if 'company_id' not in st.session_state:
        st.session_state.company_id = "demo-company-123"
    
    processor = DocumentAIProcessor(st.session_state.company_id)
    
    st.title("📄 Document AI - Paperwork Eliminator")
    st.markdown("**Transform paper documents into digital data instantly**")
    st.markdown("*Upload Bills of Lading, Proofs of Delivery, Invoices, and Receipts*")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📋 How It Works")
        st.markdown("""
        1. **Upload** your document image
        2. **Select** document type
        3. **AI extracts** data automatically
        4. **Review** and save to your system
        
        **Supported Documents:**
        - 📋 Bills of Lading (BOL)
        - ✅ Proof of Delivery (POD)
        - 💰 Freight Invoices
        - 🧾 Fuel/Expense Receipts
        """)
        
        st.markdown("---")
        st.markdown("**💡 Tips for Best Results:**")
        st.markdown("""
        - Use clear, high-resolution images
        - Ensure good lighting
        - Avoid shadows or glare
        - Capture the entire document
        """)
    
    # Main upload interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        
        # Document type selection
        document_type = st.selectbox(
            "Document Type",
            ['bol', 'pod', 'invoice', 'receipt'],
            format_func=lambda x: {
                'bol': '📋 Bill of Lading (BOL)',
                'pod': '✅ Proof of Delivery (POD)', 
                'invoice': '💰 Freight Invoice',
                'receipt': '🧾 Fuel/Expense Receipt'
            }[x]
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose document image",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload a clear image of your trucking document"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Uploaded {document_type.upper()}", use_column_width=True)
                
                # Process button
                if st.button("🚀 Extract Data with AI", type="primary"):
                    with st.spinner(f"AI is reading your {document_type.upper()} document..."):
                        # Extract data
                        extracted_data = processor.extract_document_data(image, document_type)
                        
                        # Store in session state for review
                        st.session_state.extracted_data = extracted_data
                        st.session_state.document_image = image
                        st.session_state.document_type = document_type
                        st.session_state.filename = uploaded_file.name
                        
                        st.success("✅ Document processed successfully!")
                        st.rerun()
                        
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
    
    with col2:
        st.subheader("📊 Recent Documents")
        
        # Show recent processed documents
        recent_docs = db.get_documents(st.session_state.company_id)
        
        if recent_docs:
            for doc in recent_docs[-5:]:  # Show last 5
                status_icon = "✅" if doc['status'] == 'processed' else "❌"
                doc_type_icon = {
                    'bol': '📋',
                    'pod': '✅', 
                    'invoice': '💰',
                    'receipt': '🧾'
                }.get(doc['document_type'], '📄')
                
                st.write(f"{status_icon} {doc_type_icon} {doc['file_name']}")
        else:
            st.info("No documents processed yet")
    
    # Review extracted data
    if 'extracted_data' in st.session_state:
        st.markdown("---")
        st.subheader("🔍 Extracted Data Review")
        
        extracted_data = st.session_state.extracted_data
        
        if 'error' in extracted_data:
            st.error(f"❌ Processing Error: {extracted_data['error']}")
        else:
            # Display confidence score
            confidence = extracted_data.get('confidence', 'medium')
            confidence_color = {'high': '🟢', 'medium': '🟡', 'low': '🟠', 'error': '🔴'}
            st.write(f"**Confidence Level:** {confidence_color.get(confidence, '⚪')} {confidence.title()}")
            
            # Create editable form with extracted data
            with st.form("review_extracted_data"):
                st.markdown("**Review and edit the extracted information:**")
                
                if st.session_state.document_type == 'bol':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        bol_number = st.text_input("BOL Number", value=extracted_data.get('bol_number', ''))
                        shipper_name = st.text_input("Shipper Name", value=extracted_data.get('shipper_name', ''))
                        consignee_name = st.text_input("Consignee Name", value=extracted_data.get('consignee_name', ''))
                        pickup_date = st.date_input("Pickup Date", value=date.today())
                        delivery_date = st.date_input("Delivery Date", value=date.today())
                    
                    with col2:
                        origin_city = st.text_input("Origin City", value=extracted_data.get('origin_city', ''))
                        origin_state = st.text_input("Origin State", value=extracted_data.get('origin_state', ''))
                        destination_city = st.text_input("Destination City", value=extracted_data.get('destination_city', ''))
                        destination_state = st.text_input("Destination State", value=extracted_data.get('destination_state', ''))
                        weight_lbs = st.number_input("Weight (lbs)", value=processor._parse_weight(extracted_data.get('weight_lbs')) or 0)
                        freight_charges = st.number_input("Freight Charges ($)", value=processor._parse_amount(extracted_data.get('freight_charges')) or 0.0)
                    
                    commodity = st.text_area("Commodity Description", value=extracted_data.get('commodity', ''))
                    special_instructions = st.text_area("Special Instructions", value=extracted_data.get('special_instructions', ''))
                
                elif st.session_state.document_type == 'pod':
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        delivery_date = st.date_input("Delivery Date", value=date.today())
                        reference_number = st.text_input("Reference Number", value=extracted_data.get('reference_number', ''))
                        consignee_name = st.text_input("Consignee Name", value=extracted_data.get('consignee_name', ''))
                        delivery_status = st.selectbox("Delivery Status", ['complete', 'partial', 'damaged'], index=0)
                    
                    with col2:
                        driver_name = st.text_input("Driver Name", value=extracted_data.get('driver_name', ''))
                        truck_number = st.text_input("Truck Number", value=extracted_data.get('truck_number', ''))
                        pieces_delivered = st.number_input("Pieces Delivered", value=int(extracted_data.get('pieces_delivered', 0)) if extracted_data.get('pieces_delivered') else 0)
                    
                    delivery_notes = st.text_area("Delivery Notes", value=extracted_data.get('delivery_notes', ''))
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    save_data = st.form_submit_button("💾 Save Document Data")
                
                with col2:
                    if st.session_state.document_type == 'bol':
                        create_load = st.form_submit_button("🚛 Create Load from BOL")
                    else:
                        create_load = False
                
                with col3:
                    discard = st.form_submit_button("🗑️ Discard")
                
                # Handle form submissions
                if save_data:
                    # Update extracted data with form values
                    if st.session_state.document_type == 'bol':
                        updated_data = {
                            'bol_number': bol_number,
                            'shipper_name': shipper_name,
                            'consignee_name': consignee_name,
                            'pickup_date': pickup_date.isoformat(),
                            'delivery_date': delivery_date.isoformat(),
                            'origin_city': origin_city,
                            'origin_state': origin_state,
                            'destination_city': destination_city,
                            'destination_state': destination_state,
                            'weight_lbs': weight_lbs,
                            'freight_charges': freight_charges,
                            'commodity': commodity,
                            'special_instructions': special_instructions,
                            'document_type': 'bol',
                            'processed_at': datetime.now().isoformat()
                        }
                    elif st.session_state.document_type == 'pod':
                        updated_data = {
                            'delivery_date': delivery_date.isoformat(),
                            'reference_number': reference_number,
                            'consignee_name': consignee_name,
                            'delivery_status': delivery_status,
                            'driver_name': driver_name,
                            'truck_number': truck_number,
                            'pieces_delivered': pieces_delivered,
                            'delivery_notes': delivery_notes,
                            'document_type': 'pod',
                            'processed_at': datetime.now().isoformat()
                        }
                    
                    # Save to database
                    document_id = processor.save_document_and_data(
                        st.session_state.document_image,
                        updated_data,
                        st.session_state.document_type,
                        st.session_state.filename
                    )
                    
                    if document_id:
                        st.success(f"✅ Document saved successfully! ID: {document_id}")
                        # Clear session state
                        for key in ['extracted_data', 'document_image', 'document_type', 'filename']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                
                if create_load and st.session_state.document_type == 'bol':
                    # Create load from BOL data
                    bol_data = {
                        'bol_number': bol_number,
                        'pickup_date': pickup_date.isoformat(),
                        'delivery_date': delivery_date.isoformat(),
                        'origin_city': origin_city,
                        'origin_state': origin_state,
                        'destination_city': destination_city,
                        'destination_state': destination_state,
                        'weight_lbs': weight_lbs,
                        'freight_charges': freight_charges
                    }
                    
                    load_id = processor.create_load_from_bol(bol_data)
                    
                    if load_id:
                        st.success(f"✅ Load created successfully! Load ID: {load_id}")
                        st.balloons()
                    else:
                        st.warning("⚠️ Could not create load. Please check the data and try again.")
                
                if discard:
                    # Clear session state and start over
                    for key in ['extracted_data', 'document_image', 'document_type', 'filename']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.info("Document discarded. Upload a new document to continue.")
                    st.rerun()
            
            # Raw data expander
            with st.expander("🔍 View Raw AI Response"):
                st.json(extracted_data)
    
    # Statistics section
    st.markdown("---")
    st.subheader("📈 Document Processing Statistics")
    
    # Get document statistics
    all_docs = db.get_documents(st.session_state.company_id)
    
    if all_docs:
        docs_df = pd.DataFrame(all_docs)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", len(all_docs))
        
        with col2:
            success_count = len(docs_df[docs_df['status'] == 'processed'])
            st.metric("Successfully Processed", success_count)
        
        with col3:
            if 'document_type' in docs_df.columns:
                most_common = docs_df['document_type'].value_counts().index[0] if not docs_df.empty else 'N/A'
                st.metric("Most Common Type", most_common.upper())
            else:
                st.metric("Most Common Type", "N/A")
        
        with col4:
            today_count = len(docs_df[docs_df['uploaded_at'].str.startswith(date.today().isoformat())])
            st.metric("Processed Today", today_count)
        
        # Document type breakdown
        if 'document_type' in docs_df.columns and not docs_df.empty:
            st.subheader("📊 Document Type Breakdown")
            type_counts = docs_df['document_type'].value_counts()
            
            type_labels = {
                'bol': '📋 Bills of Lading',
                'pod': '✅ Proofs of Delivery',
                'invoice': '💰 Invoices',
                'receipt': '🧾 Receipts'
            }
            
            for doc_type, count in type_counts.items():
                st.write(f"{type_labels.get(doc_type, doc_type)}: {count}")
    else:
        st.info("No documents processed yet. Upload your first document to get started!")

if __name__ == "__main__":
    run_document_ai()