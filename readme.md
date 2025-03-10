<div align="right">
    <a href="#sefaria-ebooks-1">🇺🇸 English</a> | 
    <a href="#sefaria-ebooks">🇮🇱 עברית</a>
</div>

# Sefaria Ebooks
ספריית כלים להורדת ספרים מ-Sefaria בפורמט EPUB

## תיאור
מאפשר להוריד ספרים מ-Sefaria בפורמט EPUB עם אפשרות לכלול פרשנויות מקושרות. הכלי תומך בארבעה ממשקים:
- ממשק web להורדה דרך הדפדפן
- ממשק CLI להורדה מרובת ספרים
- ממשק GUI להורדה נוחה דרך תוכנת שולחן עבודה
- ממשק ייבוא מייצוא Sefaria

### תכונות עיקריות
- תמיכה בעברית ואנגלית
- אפשרות להוספת פרשנויות מקושרות
- המרה אוטומטית להערות שוליים
- שמירת מטא-דאטה (מחברים, תקופה, תיאור)
- ארגון לפי קטגוריות
- תמיכה בהרצה באמצעות Docker

## התקנה והרצה

### דרישות מערכת
עבור התקנה מקומית:
- Python 3.x
- Calibre (נדרש להיות מותקן ונגיש דרך משתני הסביבה)

עבור Docker:
- Docker Engine
- 2GB RAM מינימום
- 5GB שטח דיסק פנוי

### התקנה והרצה באמצעות Docker

#### בנייה והרצה בסיסית
```bash
docker build -t sefaria_ebooks .
docker run -p 8000:8000 sefaria_ebooks
```
גש ל-[http://localhost:8000](http://localhost:8000)

### התקנה מקומית
1. התקן את Calibre
2. צור סביבה וירטואלית:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. התקן דרישות:
```bash
pip install -r requirements.txt
```

### הרצת הכלי
- ממשק web: `python main.py`
- הורדה מרובה: `python cli.py`
- ממשק גרפי: `python gui.py`
- ייבוא מייצוא: `python main_from_export.py`

#### שימוש בייבוא מייצוא
1. התקן Git LFS:
```bash
git lfs install
```

2. הורד את מאגר הנתונים (בחר אחת מהאפשרויות):
```bash
# אפשרות 1 - מאגר HuggingFace (מעודכן יותר)
git clone https://huggingface.co/Sefaria/database_export

# אפשרות 2 - מאגר GitHub
git clone https://github.com/Sefaria/Sefaria-Export.git
```

---

<div align="left">
    <a href="#sefaria-ebooks">🇮🇱 עברית</a> | 
    <a href="#sefaria-ebooks-1">🇺🇸 English</a>
</div>

# Sefaria Ebooks
A toolkit for downloading books from Sefaria in EPUB format

## Description
Enables downloading books from Sefaria in EPUB format with the option to include linked commentaries. The tool supports four interfaces:
- Web interface for browser-based downloads
- CLI interface for bulk downloads
- GUI interface for desktop application
- Import interface from Sefaria export

### Key Features
- Hebrew and English support
- Option to add linked commentaries
- Automatic footnote conversion
- Metadata preservation (authors, era, description)
- Category-based organization
- Docker support

## Installation and Usage

### System Requirements
For local installation:
- Python 3.x
- Calibre (must be installed and accessible via environment variables)

For Docker:
- Docker Engine
- Minimum 2GB RAM
- 5GB free disk space

### Docker Installation and Usage

#### Basic Build and Run
```bash
docker build -t sefaria_ebooks .
docker run -p 8000:8000 sefaria_ebooks
```
Navigate to [http://localhost:8000](http://localhost:8000)


### Local Installation
1. Install Calibre
2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Install requirements:
```bash
pip install -r requirements.txt
```

### Running the Tool
- Web interface: `python main.py`
- Bulk download: `python cli.py`
- GUI interface: `python gui.py`
- Export import: `python main_from_export.py`

#### Using Export Import
1. Install Git LFS:
```bash
git lfs install
```

2. Clone the database (choose one option):
```bash
# Option 1 - HuggingFace repository (more up-to-date)
git clone https://huggingface.co/Sefaria/database_export

# Option 2 - GitHub repository
git clone https://github.com/Sefaria/Sefaria-Export.git
```



