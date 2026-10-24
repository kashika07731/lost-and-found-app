# 🎓 Smart Campus Lost & Found Matcher (CampusFind)

> **A beginner-friendly, algorithmic web application designed to reconnect college students with lost belongings through transparent, explainable smart matching.**

Built with **Python**, **Streamlit**, and **SQLite**. Zero paid APIs, 100% free, runs completely locally on any computer.

---

## 📌 1. Project Overview & Problem Statement

### The Problem
On college campuses, students frequently lose essential everyday items: water bottles, lanyards, student ID cards, earbud cases, notebook registers, keys, and umbrellas. 

Today, lost-and-found notifications are scattered across:
- Unofficial WhatsApp batch groups.
- Disorganized Instagram stories that expire after 24 hours.
- Physical noticeboards and security guards' desks where items sit unclaimed for semesters.

This chaotic process leads to low recovery rates, wasted time, and privacy risks (e.g., students broadcasting their personal phone numbers or photos of their full ID cards online).

### The Solution: CampusFind
**Smart Campus Lost & Found Matcher** provides:
1. **One Centralized Platform**: Simple, dedicated portal to submit and browse lost and found items.
2. **Transparent Algorithmic Matcher**: Compares reports across 6 weighted attributes (category, title, distinguishing features, color, campus location, and timeline) to generate a match score from 0 to 100%.
3. **Student Privacy Shield**: Obfuscates phone numbers and email addresses on public listings to prevent harassment, scam attempts, and phishing.
4. **Ownership Verification Protocol**: Reminds finders and campus security to require claimants to prove ownership by describing unlisted details before returning items.

---

## 🗂️ 2. Project Architecture & File Structure

```text
LOSTANDFOUND/
│
├── app.py                  # Main Streamlit web application & user interface
├── database.py             # SQLite database layer, schema, queries & deduplication
├── matcher.py              # Rule-based weighted scoring engine & NLP semantic matching
├── test_app.py             # System automated test script for database & matching engine
├── requirements.txt        # Minimal Python dependencies (Streamlit)
├── .gitignore              # Ignores bytecode, virtual environments, and local DBs
├── README.md               # Complete project documentation & presentation guide
└── uploads/                # Directory for user-uploaded item photos (.gitkeep preserved)
```

### Explanation of Core Files
| File | Role & Purpose |
| :--- | :--- |
| **`app.py`** | The frontend and page router. Uses Streamlit to render the Home Dashboard, Report Forms, Smart Matcher, Browse Grid, and Privacy Guide with modern custom CSS styling. |
| **`database.py`** | Manages local SQLite storage (`campus_lost_found.db`). Initializes tables, inserts records, queries with multi-criteria filters, and seeds realistic sample data only once (ensuring zero duplicates on restarts). |
| **`matcher.py`** | The core intelligence of the project. Contains the 0–100 explainable scoring algorithm, text normalization, keyword extraction, and the optional NLP synonym expansion layer. |
| **`test_app.py`** | A standalone verification script that tests database setup, deduplication, contact masking, and matching calculations. |
| **`requirements.txt`**| Lists the minimal dependencies needed to run the project (`streamlit`). |

---

## ⚡ 3. Quick Start Guide (Run Locally)

Follow these easy steps to run the application on your computer (Windows, macOS, or Linux):

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed.

### Step 1: Open Terminal or PowerShell
Navigate to the project directory:
```bash
cd c:\Users\ADMIN\Documents\LOSTANDFOUND
```

### Step 2: (Recommended) Create and Activate a Virtual Environment
```bash
# On Windows:
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

### Step 5: Open in Your Browser
Streamlit will automatically open your default browser at:
```text
http://localhost:8501
```

*(To run the automated verification test at any time, simply run `python test_app.py`).*

---

## 🧠 4. How the Smart Matching Algorithm Works

The core of this project is a **Rule-Based Weighted Scoring Algorithm** designed to be transparent, mathematically explainable, and reliable.

### Score Breakdown (0 to 100 Points)

$$\text{Total Score} = S_{\text{category}} + S_{\text{title}} + S_{\text{features}} + S_{\text{color}} + S_{\text{location}} + \Delta_{\text{date}}$$

| Factor | Maximum Points | Logic & How It Is Evaluated |
| :--- | :---: | :--- |
| **1. Item Category** | **30 pts** | Compares normalized categories. If categories mismatch (e.g. *Water Bottles* vs *Notebooks*), score is **0** and matching immediately halts. |
| **2. Title & Name Similarity** | **25 pts** | Compares cleaned keyword tokens and string character sequences (`difflib.SequenceMatcher`). Overlapping title words earn proportional points. |
| **3. Distinguishing Features** | **20 pts** | Analyzes the description for specific distinguishing marks (e.g., *scratches*, *stickers*, *dents*, *initials*, *brands*, *lanyards*). |
| **4. Colour Match** | **15 pts** | Exact color match = 15 pts; partial overlap or tone synonyms (e.g., *Navy Blue* vs *Blue*, *Dark* vs *Black*) = 10–12 pts. |
| **5. Campus Location** | **10 pts** | Same building/campus zone (e.g., *Central Library*, *CS Lab*, *Cafeteria*) = 8–10 pts; partial zone keyword = 5 pts. |
| **6. Timeline Consistency** | **Modifier (0 to -10 pts)**| An item cannot be found before it was lost. Found within 0–7 days after being lost receives full credit (+5 pts). Significant date anomalies receive a penalty. |

### Confidence Tiers
- 🟢 **High Match ($\ge 75\%$)**: Strong alignment across category, title, color, and location. Recommended for direct verification.
- 🟡 **Moderate Match ($50\% - 74\%$)**: Promising overlap; could be the same item described differently.
- ⚪ **Low Match ($35\% - 49\%$)**: Partial similarities that may require manual inspection.
- ❌ **Below $35\%$**: Filtered out to avoid false leads and unnecessary clutter.

### Optional AI Enhancement: NLP Semantic Matching
In the sidebar, you can toggle between **Rule-Based Weighted** and **NLP Semantic Assisted**. 
- The NLP mode uses a local semantic dictionary and token cluster mapping.
- It recognizes that *"flask"* $\approx$ *"bottle"*, *"earbuds"* $\approx$ *"airpods"*, and *"dark"* $\approx$ *"black"*, allowing the app to match items even when different students use different vocabulary!

---

## 🔒 5. Privacy & Verification System

1. **Automatic Contact Masking**:
   - `rohan.patel@college.edu` $\rightarrow$ `ro***l@college.edu`
   - `9876543210` $\rightarrow$ `******3210`
   - Contact details are never broadcasted openly to web crawlers or unauthorized visitors.
2. **Anti-Scam Ownership Checklist**:
   - The app explicitly displays a warning: *"A suggested match is NOT legal proof of ownership."*
   - Finders are instructed to ask claimants for **"The Hidden Detail"** (e.g., sticker theme, wallpaper, or internal contents) before handing over valuables.
3. **Status Tracking**:
   - Reports can be marked as **OPEN**, **MATCH_PENDING**, or **RESOLVED** once an item has been safely returned.

---

## 🎤 6. 3-Minute Innovation Challenge Presentation Pitch

Use this structured script when presenting your project to judges:

### 1. The Hook & Problem (30 seconds)
> *"Hello respected judges. Every single week on our campus, students misplace water bottles, student ID lanyards, calculator pouches, and earphones. Today, whenever someone loses an item, they frantically spam five different WhatsApp groups or post on Instagram. Meanwhile, the student who found the item turned it into the library front desk, where it sits forgotten. There is no central bridge between the person who lost an item and the person who found it. That's why I built **CampusFind: Smart Campus Lost & Found Matcher**."*

### 2. The Solution & Demo (90 seconds)
> *"CampusFind is a dedicated, beginner-friendly web platform built in Python with Streamlit and SQLite. Let me demonstrate how it works:
> 1. A student reports a lost **Hydro Flask** left on the 2nd floor of the library, noting a small NASA sticker on the side.
> 2. Simultaneously, a student who found a black water flask on study desk 14 logs it as a found item.
> 3. Instead of waiting for someone to manually search through dozens of messages, our **Smart Matching Algorithm** instantly compares both reports. It evaluates category, title tokens, color, location proximity, and timeline plausibility, awarding an **81% High Confidence Match**!
> 4. Judges can click the explainability dropdown to see exactly why the points were awarded: 30 points for category, 15 points for color, and 18 points for shared distinguishing features like the sticker."*

### 3. Privacy & Innovation (45 seconds)
> *"We prioritized student safety. Notice that phone numbers and email addresses are automatically masked. Furthermore, our system clearly warns that an algorithmic suggestion is not proof of ownership—claimants must verify the hidden sticker details before an item is handed over."*

### 4. Technical Stack & Future Scope (15 seconds)
> *"The system runs 100% locally with zero paid APIs, making it completely free and deployable on campus servers. In the future, we plan to integrate automated email notifications and lightweight computer vision to match item photos directly. Thank you, and I look forward to your questions!"*

---

## 💡 7. Frequently Asked Questions by Judges (And How to Answer)

### Q1: "Is this artificial intelligence, or is it rule-based?"
> **Answer**: *"The core matching engine is a deterministic, explainable rule-based algorithm. We deliberately avoided black-box AI models for the core because in a lost and found scenario, transparency is essential—both students and campus security need to understand exactly why two items were paired. However, we also implemented an optional NLP semantic enhancement that handles vocabulary variations like 'flask' versus 'bottle' using synonym cluster mapping."*

### Q2: "How do you prevent malicious people from claiming items that aren't theirs?"
> **Answer**: *"We designed an ownership verification protocol. First, we advise finders never to publish every single detail in the public description—they should withhold one 'secret' mark (like a scratch or specific sticker). When a claimant comes forward, the finder asks them to identify that missing detail. Second, student contact information is masked so bad actors cannot impersonate claimants."*

### Q3: "What database does this use, and how do you handle concurrency?"
> **Answer**: *"The prototype uses Python's built-in SQLite database, which requires zero external configuration and stores records reliably in a single local file (`campus_lost_found.db`). For our campus prototype, SQLite handles hundreds of concurrent reads seamlessly. If scaling to a university of 30,000 students, we can migrate the database schema directly to PostgreSQL with minimal code changes."*

### Q4: "Why did you choose Streamlit instead of React or Django?"
> **Answer**: *"As a first-year student with a background in basic C and Python, Streamlit allowed me to build a responsive, reactive web application entirely in Python without dealing with the steep learning curve of HTML/CSS/JavaScript build tools. It let me focus directly on data structures, database design, and the algorithmic matching logic."*

---

## 🚀 8. Deployment & Version Control

### Uploading to GitHub
1. Create a new repository on [GitHub](https://github.com) named `campus-lost-and-found`.
2. Run these commands in your project folder:
```bash
git init
git add .
git commit -m "Initial commit: Smart Campus Lost & Found Matcher"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/campus-lost-and-found.git
git push -u origin main
```

### Free Cloud Deployment via Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app**.
3. Select your repository `campus-lost-and-found`, branch `main`, and main file `app.py`.
4. Click **Deploy**. Your app will be live on a public URL in 2 minutes!

---

## ⚖️ 9. Features Implemented vs. Future Roadmap

| Status | Feature |
| :---: | :--- |
| ✅ **Implemented** | Interactive Home Dashboard with real-time statistics and problem statement. |
| ✅ **Implemented** | Report Lost Item Form with input validation and image attachment. |
| ✅ **Implemented** | Report Found Item Form with privacy safeguards. |
| ✅ **Implemented** | 0–100 Explainable Rule-Based Matching Engine with point breakdown. |
| ✅ **Implemented** | Optional NLP Semantic text similarity toggle. |
| ✅ **Implemented** | Browse and multi-criteria filter grid (Category, Location, Color, Status, Keywords). |
| ✅ **Implemented** | SQLite persistent storage with automatic sample deduplication. |
| ✅ **Implemented** | Automatic student contact info masking (`ro***l@college.edu`). |
| 🔮 *Future Roadmap* | Push notifications via College Webhook / WhatsApp Business API. |
| 🔮 *Future Roadmap* | Mobile barcode / QR code tags for student ID cards. |
| 🔮 *Future Roadmap* | Computer Vision model (MobileNet) to compare item images automatically. |

---

*Made with pride by a 1st-Year College Innovator! 🎓*
