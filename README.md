📝 AIMS – AI Meeting Summarizer

Automated Minutes of Meeting Generator using AI

AIMS is an AI-powered system designed to automatically generate Minutes of Meeting (MoM) from transcripts, PDFs, or audio recordings. It detects meeting details, summarizes discussions, identifies action items, and exports results in the official Minutes of Meeting format used in our college.

🚀 Features
Feature	Description
📤 Multiple upload options	Paste transcript, upload text/PDF, or upload audio
🎤 Audio transcription	Automatic transcription using Whisper + optional speaker diarization
🧠 AI summarization	Uses BART model to extract agenda, decisions, summary, and action items
✏️ Editable UI	Users can review and modify auto-generated details
📄 Export	Export Minutes of Meeting as PDF and DOCX
📧 Email	Send MoM directly to attendees (text email or attachment mode)
🏫 College format	Uses our college-standard MoM structure & layout
🏗️ Tech Stack
Component	Technology
Frontend	Streamlit
AI Summarization	BART (facebook/bart-large-cnn)
Audio Transcription	Whisper
Speaker Identification	Diarization module
Export	python-docx & ReportLab
Email	SMTP with Streamlit Secrets
📂 Project Workflow

1️⃣ Upload Transcript / Audio
2️⃣ AI Processing

Chunking long transcripts

BART summarization

Agenda & action item extraction
3️⃣ Summary Page

Review and edit attendees, agenda, decisions, summary, next meeting
4️⃣ Export

Download PDF / DOCX

Send via email

📌 Folder Structure
MeetingMinutesAI/
 ├─ app.py
 ├─ export_utils.py
 ├─ email_utils.py
 ├─ summarizer/
 │   ├─ bart_summarizer.py
 │   ├─ summarize.py
 │   ├─ structure_formatter.py
 ├─ audio_processing/
 │   ├─ transcribe.py
 │   ├─ diarize.py
 │   ├─ transcript_parser.py
 ├─ .streamlit/
 │   ├─ secrets.toml   ← For SMTP email config
 ├─ college_header.jpg
 ├─ requirements.txt

💌 Email Configuration (SMTP)

In .streamlit/secrets.toml:

smtp_host = "smtp.gmail.com"
smtp_port = "587"
email = "your_email@gmail.com"
password = "your_16_character_app_password"
smtp_sender = "your_email@gmail.com"
smtp_use_tls = "true"

▶️ How to Run
pip install -r requirements.txt
streamlit run app.py

📑 Output Format (PDF & DOCX)

The exported minutes include:

✔ Title
✔ Date, Time, Venue, Organizer, Recorder
✔ Attendees
✔ Agenda
✔ Discussion Summary
✔ Decisions (if added)
✔ Action Items (if added)
✔ Next Meeting
✔ Closing note

Fully matches our college Minutes of Meeting format.

🎯 Future Enhancements

🔹 Multi-language summarization
🔹 Department-wise automatic storage
🔹 Voice-controlled meeting recorder
🔹 Analytics dashboard for meeting insights

👩‍💻 Developed by
Name	Role
Sakshi Gowda	Development & UI
Nayana	Transcript Testing & Dataset
Nikitha & Prathiksha	Documentation & Validation
