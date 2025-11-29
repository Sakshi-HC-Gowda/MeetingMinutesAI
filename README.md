# 📝 AIMS – AI Meeting Summarizer  
**Automated Minutes of Meeting Generator using AI**

AIMS is an AI-powered system designed to automatically generate **Minutes of Meeting (MoM)** from **transcripts, PDFs, or audio recordings**.  
It detects meeting details, summarizes discussions, identifies action items, and exports results in the **official Minutes of Meeting format used in our college**.

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
| 📤 Multiple upload options | Paste transcript, upload text/PDF, or upload audio |
| 🎤 Audio transcription | Automatic transcription using **Whisper** + optional **speaker diarization** |
| 🧠 AI summarization | Uses **BART (facebook/bart-large-cnn)** to extract summary, agenda, decisions & action items |
| ✏️ Editable UI | Users can review and modify all auto-generated information |
| 📄 Export | Generate **PDF** & **DOCX** Minutes of Meeting |
| 📧 Email | Send MoM to attendees — **as text email** or **as PDF/DOCX attachments** |
| 🏫 College format | Layout strictly follows our **institution’s MoM standard** |

---

## 🏗️ Tech Stack

| Component | Technology |
|----------|------------|
| Frontend | Python+Streamlit |
| AI Summarization | **BART – facebook/bart-large-cnn (Hugging Face Transformers)** |
| Audio Transcription | **Whisper** |
| Speaker Identification | Diarization Module |
| Export | **python-docx & ReportLab** |
| Email | SMTP + Streamlit Secrets |

---

## 📂 Project Workflow

1️⃣ Upload Transcript / PDF / Audio
2️⃣ AI Processing
• Chunking long transcripts
• BART summarization
• Agenda / decisions / action item extraction
3️⃣ Summary Page
• Review & edit extracted content
4️⃣ Export
• Download PDF / DOCX
• Send to emails

---

## 📌 Folder Structure

MeetingMinutesAI/
├─ app.py
├─ export_utils.py
├─ email_utils.py
├─ summarizer/
│ ├─ bart_summarizer.py
│ ├─ summarize.py
│ ├─ structure_formatter.py
├─ audio_processing/
│ ├─ transcribe.py
│ ├─ diarize.py
│ ├─ transcript_parser.py
├─ .streamlit/
│ ├─ secrets.toml ← For SMTP email configuration
├─ college_header.jpg
├─ requirements.txt

---

## 💌 SMTP Email Configuration

Create `.streamlit/secrets.toml`:

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

The generated Minutes of Meeting include:

✔ Title
✔ Date, Time, Venue, Organizer, Recorder
✔ Attendees
✔ Agenda
✔ Discussion Summary
✔ Decisions (optional)
✔ Action Items (optional)
✔ Next Meeting
✔ Closing Note

💯 Output layout fully matches our college MoM format.

🎯 Future Enhancements

Multi-language summarization

Department-wise storage of MoMs

Voice-controlled meeting recorder

Analytics dashboard for meeting insights

## 👩‍💻 Developed By

| Name | Role |
|------|------|
| **Sakshi Gowda** | Development & UI |
| **Nayana** | Transcript Testing & Dataset |
| **Nikitha & Prathiksha** | Documentation & Validation |
