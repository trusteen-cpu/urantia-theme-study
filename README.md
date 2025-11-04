# Urantia Theme Study

A Streamlit-based research tool for studying *The Urantia Book* concepts.
It allows users to:
- Search glossary definitions
- Find related passages in the Urantia text
- Automatically analyze and generate a 5-slide outline using GPT-5

## Data Files
Inside `/data` directory, include:
- `urantia_en.txt` (English Urantia text)
- `glossary.xlsx` (with columns: Term, Definition)

## Deployment (Render)
1. Push to GitHub → new repo `urantia-theme-study`
2. Add a new Web Service in Render
3. Environment Variables:
   - **OPENAI_API_KEY = your_api_key**
4. Build Command:


