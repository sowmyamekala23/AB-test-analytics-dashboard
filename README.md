# Pinterest A/B Test Analytics Dashboard

This project is a **Pinterest-style A/B Test Analytics Dashboard** built with Streamlit to simulate how product teams monitor and analyse A/B tests. I designed it with realism in mind, generating synthetic user-level and daily engagement data where the **treatment shows only a small lift**—mirroring real-world experiments where effects are subtle and require statistical analysis to detect. Beyond data engineering and dashboarding, the project integrates a **data science layer**: exploring control vs. treatment differences, visualising daily trends, and highlighting challenges like noise, low power, and marginal effect sizes. It demonstrates end-to-end skills in **data generation, statistical reasoning, and experiment evaluation** using Python, Pandas, Seaborn, and Streamlit.

## How to Run
1. Clone this repo:  
   ```bash
   git clone https://github.com/yourusername/pinterest-experiment-dashboard.git
   cd pinterest-experiment-dashboard
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Run Streamlit app:  
   ```bash
   streamlit run app.py
   ```
4. Open the dashboard in your browser at:  
   ```
   http://localhost:8501
   ```

## Future Improvements
- Automate data generation with more realistic distributions.
- Extend to multi-variant experiments (not just A/B).
- Deploy on Streamlit Cloud for live demo access. 

