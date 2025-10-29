import streamlit as st
import PyPDF2
import pdfplumber
from io import BytesIO
from datetime import datetime
from nlp_processor import MeetingNLPProcessor
from export_utils import MeetingExporter

st.set_page_config(
    page_title="AIMS - AI Meeting Summarizer",
    page_icon="📝",
    layout="wide"
)

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def main():
    st.title("📝 AIMS - AI Meeting Summarizer")
    st.markdown("### Rule-Based NLP System for Automated Meeting Minutes Generation")
    st.markdown("---")
    
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'current_transcript' not in st.session_state:
        st.session_state.current_transcript = ""
    
    st.sidebar.header("📄 Input Options")
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["Paste Text", "Upload PDF", "Upload Text File"]
    )
    
    transcript_text = ""
    
    if input_method == "Paste Text":
        st.sidebar.info("Paste your meeting transcript in the text area below")
        transcript_text = st.text_area(
            "Meeting Transcript",
            height=300,
            placeholder="Paste your meeting transcript here...\n\nExample:\nTitle: Planning the College Technical Fest\nDate: 29/10/2025\nTime: 3:30 PM – 4:15 PM\n\nAttendees:\nSakshi – Event Coordinator\nNayana – Technical Lead\n\nThe meeting began with..."
        )
    
    elif input_method == "Upload PDF":
        uploaded_file = st.sidebar.file_uploader("Upload PDF transcript", type=['pdf'])
        if uploaded_file:
            with st.spinner("Extracting text from PDF..."):
                transcript_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF text extracted successfully!")
    
    elif input_method == "Upload Text File":
        uploaded_file = st.sidebar.file_uploader("Upload text file", type=['txt'])
        if uploaded_file:
            transcript_text = uploaded_file.read().decode('utf-8')
            st.success("✅ Text file loaded successfully!")
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Process Transcript", type="primary", use_container_width=True):
        if transcript_text.strip():
            with st.spinner("Processing transcript using rule-based NLP..."):
                processor = MeetingNLPProcessor()
                processed_data = processor.process_transcript(transcript_text)
                st.session_state.processed_data = processed_data
                st.session_state.current_transcript = transcript_text
                st.success("✅ Transcript processed successfully!")
                st.rerun()
        else:
            st.error("⚠️ Please provide a transcript first!")
    
    if st.sidebar.button("🗑️ Clear All", use_container_width=True):
        st.session_state.processed_data = None
        st.session_state.current_transcript = ""
        st.rerun()
    
    if st.session_state.processed_data:
        data = st.session_state.processed_data
        
        st.markdown("## 📋 Generated Meeting Minutes")
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📌 Meeting Information")
            metadata = data.get('metadata', {})
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                title = st.text_input("Title", value=metadata.get('title') or "Meeting Summary", key="title_edit")
                date = st.text_input("Date", value=metadata.get('date') or datetime.now().strftime('%d/%m/%Y'), key="date_edit")
                time = st.text_input("Time", value=metadata.get('time') or "", key="time_edit")
            
            with info_col2:
                venue = st.text_input("Venue", value=metadata.get('venue') or "", key="venue_edit")
                organizer = st.text_input("Organizer", value=metadata.get('organizer') or "", key="organizer_edit")
                recorder = st.text_input("Recorder", value=metadata.get('recorder') or "", key="recorder_edit")
            
            data['metadata']['title'] = title
            data['metadata']['date'] = date
            data['metadata']['time'] = time
            data['metadata']['venue'] = venue
            data['metadata']['organizer'] = organizer
            data['metadata']['recorder'] = recorder
        
        with col2:
            st.markdown("### 📊 Processing Stats")
            st.metric("Key Topics Extracted", len(data.get('key_topics', [])))
            st.metric("Decisions Identified", len(data.get('decisions', [])))
            st.metric("Action Items Found", len(data.get('action_items', [])))
            st.metric("Attendees Detected", len(data.get('attendees', [])))
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "👥 Attendees", 
            "🔑 Key Topics", 
            "📝 Summary", 
            "✅ Decisions", 
            "📌 Action Items", 
            "📅 Next Meeting"
        ])
        
        with tab1:
            st.markdown("### 👥 Attendees")
            attendees = data.get('attendees', [])
            if attendees:
                for i, attendee in enumerate(attendees):
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        attendees[i]['name'] = st.text_input(
                            f"Name {i+1}", 
                            value=attendee.get('name', ''),
                            key=f"attendee_name_{i}"
                        )
                    with col_b:
                        attendees[i]['role'] = st.text_input(
                            f"Role {i+1}", 
                            value=attendee.get('role', ''),
                            key=f"attendee_role_{i}"
                        )
                
                if st.button("➕ Add Attendee"):
                    attendees.append({'name': '', 'role': ''})
                    st.rerun()
            else:
                st.info("No attendees detected. Click below to add manually.")
                if st.button("➕ Add Attendee"):
                    data['attendees'] = [{'name': '', 'role': ''}]
                    st.rerun()
        
        with tab2:
            st.markdown("### 🔑 Key Topics")
            key_topics = data.get('key_topics', [])
            if key_topics:
                for i, topic in enumerate(key_topics):
                    data['key_topics'][i] = st.text_input(
                        f"Topic {i+1}",
                        value=topic,
                        key=f"topic_{i}"
                    )
                
                if st.button("➕ Add Topic"):
                    key_topics.append("")
                    st.rerun()
            else:
                st.info("No key topics extracted automatically.")
                if st.button("➕ Add Topic"):
                    data['key_topics'] = [""]
                    st.rerun()
        
        with tab3:
            st.markdown("### 📝 Discussion Summary")
            summary = data.get('summary', '')
            data['summary'] = st.text_area(
                "Summary",
                value=summary,
                height=200,
                key="summary_edit",
                help="Edit the auto-generated summary"
            )
        
        with tab4:
            st.markdown("### ✅ Decisions")
            decisions = data.get('decisions', [])
            if decisions:
                for i, decision in enumerate(decisions):
                    data['decisions'][i] = st.text_area(
                        f"Decision {i+1}",
                        value=decision,
                        height=80,
                        key=f"decision_{i}"
                    )
                
                if st.button("➕ Add Decision"):
                    decisions.append("")
                    st.rerun()
            else:
                st.info("No decisions detected. Click below to add manually.")
                if st.button("➕ Add Decision"):
                    data['decisions'] = [""]
                    st.rerun()
        
        with tab5:
            st.markdown("### 📌 Action Items")
            action_items = data.get('action_items', [])
            if action_items:
                for i, action in enumerate(action_items):
                    st.markdown(f"**Action Item {i+1}**")
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        action_items[i]['task'] = st.text_input(
                            "Task",
                            value=action.get('task', ''),
                            key=f"task_{i}"
                        )
                    with col2:
                        action_items[i]['responsible'] = st.text_input(
                            "Responsible",
                            value=action.get('responsible', ''),
                            key=f"responsible_{i}"
                        )
                    with col3:
                        action_items[i]['deadline'] = st.text_input(
                            "Deadline",
                            value=action.get('deadline', ''),
                            key=f"deadline_{i}"
                        )
                    with col4:
                        action_items[i]['status'] = st.selectbox(
                            "Status",
                            options=["Pending", "In progress", "Completed", "Upcoming"],
                            index=["Pending", "In progress", "Completed", "Upcoming"].index(
                                action.get('status', 'Pending')
                            ),
                            key=f"status_{i}"
                        )
                    st.markdown("---")
                
                if st.button("➕ Add Action Item"):
                    action_items.append({
                        'task': '',
                        'responsible': '',
                        'deadline': '',
                        'status': 'Pending'
                    })
                    st.rerun()
            else:
                st.info("No action items detected. Click below to add manually.")
                if st.button("➕ Add Action Item"):
                    data['action_items'] = [{
                        'task': '',
                        'responsible': '',
                        'deadline': '',
                        'status': 'Pending'
                    }]
                    st.rerun()
        
        with tab6:
            st.markdown("### 📅 Next Meeting")
            next_meeting = data.get('next_meeting', {})
            
            col1, col2 = st.columns(2)
            with col1:
                next_meeting['date'] = st.text_input(
                    "Date",
                    value=next_meeting.get('date') or "",
                    key="next_date"
                )
                next_meeting['time'] = st.text_input(
                    "Time",
                    value=next_meeting.get('time') or "",
                    key="next_time"
                )
            with col2:
                next_meeting['venue'] = st.text_input(
                    "Venue",
                    value=next_meeting.get('venue') or "",
                    key="next_venue"
                )
                next_meeting['agenda'] = st.text_area(
                    "Agenda",
                    value=next_meeting.get('agenda') or "",
                    key="next_agenda",
                    height=100
                )
        
        st.markdown("---")
        st.markdown("## 📥 Export Options")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📄 Export as PDF", type="primary", use_container_width=True):
                exporter = MeetingExporter()
                pdf_buffer = exporter.export_to_pdf(data)
                
                filename = f"Meeting_Minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📝 Export as DOCX", type="primary", use_container_width=True):
                exporter = MeetingExporter()
                docx_buffer = exporter.export_to_docx(data)
                
                filename = f"Meeting_Minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                st.download_button(
                    label="⬇️ Download DOCX",
                    data=docx_buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
    
    else:
        st.info("👈 Please provide a meeting transcript using the sidebar and click 'Process Transcript' to generate structured minutes.")
        
        with st.expander("ℹ️ About AIMS - AI Meeting Summarizer"):
            st.markdown("""
            **AIMS** (AI Meeting Summarizer) is a rule-based NLP system that automatically generates structured minutes of meetings from transcripts.
            
            ### Features:
            - **Rule-Based Processing**: Uses TF-IDF, keyword extraction, and pattern matching (no heavy ML models)
            - **Automatic Extraction**: Identifies key topics, decisions, and action items
            - **Structured Output**: Generates professional meeting minutes with all standard sections
            - **Export Options**: Export to PDF or DOCX format
            - **Editable Results**: Review and modify extracted information before export
            
            ### How to Use:
            1. Choose an input method (paste text, upload PDF, or upload text file)
            2. Provide your meeting transcript
            3. Click "Process Transcript"
            4. Review and edit the extracted information
            5. Export as PDF or DOCX
            
            ### Processing Phases:
            - **Phase I - Preprocessing**: Remove filler words, normalize text, apply NER
            - **Phase II - Rule-Based Extraction**: Extract topics, decisions, and action items
            - **Phase III - Assembly**: Generate structured minutes with verification
            
            ### Developed by:
            Project Group 16 | Academic Year 2025-26
            - Nayana K (4MW23CS080)
            - Nikitha (4MW23CS085)
            - Prathiksha (4MW23CS102)
            - Sakshi H C (4MW23CS130)
            """)
        
        with st.expander("📖 Sample Transcript Format"):
            st.code("""
Title: Planning the College Technical Fest
Date: 29/10/2025
Time: 3:30 PM – 4:15 PM
Venue: Main Seminar Hall
Organizer: Technical Committee, AIMS College
Recorder: Sakshi H.C

Attendees:
Sakshi – Event Coordinator
Nayana – Technical Lead
Prathiksha – Finance Head
Nikitha – Marketing & Sponsorship Lead

The meeting began with an overview of Technova 2025. Members discussed possible events such as a 24-hour hackathon, web design challenge, and robotics line follower competition.

We decided to approach sponsors for financial support. The team agreed on preparing the event proposal and budget sheet by this weekend.

Action Items:
Find sponsors for additional funds - Aditya - 31/10/2025 - Pending
Allocate ₹5,000 for workshop materials - Sakshi - 30/10/2025 - Pending

Next Meeting:
Date: 02/11/2025
Time: 3:00 PM
Venue: Project Lab
Agenda: Review event progress, confirm sponsors, and finalize technical requirements.
            """, language="text")

if __name__ == "__main__":
    main()
