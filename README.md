# 🇺🇸 US Import Opportunity Scout

A real-time data dashboard built with **Streamlit** and **Python** that helps entrepreneurs and investors identify high-growth import categories entering the USA.

It queries the **US Census Bureau International Trade API** to find products with explosive Year-over-Year (YoY) growth, allowing users to filter by industry (HS Chapters) and volume.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Features

* **Real-Time Data:** Fetches the latest available import data directly from the US Government (Census Bureau).
* **Trend Spotting:** Calculates Year-over-Year growth percentages for specific quarters (Q1, Q2, Q3).
* **Deep Dive Filters:**
    * **HS Chapters:** Filter by specific industries (e.g., "85 - Electrical Machinery" or "09 - Coffee/Spices").
    * **Volume Control:** Filter out noise by setting minimum and maximum import volumes.
* **"Hidden Gem" Detector:** A specialized algorithm that spots low-volume items (niche markets) with massive growth rates (e.g., >200%).
* **Interactive Visualizations:** Dynamic bar charts and data tables using Plotly.

## 🛠️ Installation & Local Usage

To run this dashboard on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/import-opportunity-scout.git](https://github.com/YOUR_USERNAME/import-opportunity-scout.git)
    cd import-opportunity-scout
    ```

2.  **Install dependencies:**
    Make sure you have Python installed. Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```
    The app will open automatically in your browser at `http://localhost:8501`.

## 📦 Deployment (Free)

You can deploy this app for free using **Streamlit Community Cloud**:

1.  Push this code to a GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Click "New App" and select your repository.
4.  Click **Deploy**.

## 📂 Project Structure

```text
import-opportunity-scout/
├── app.py               # The main application logic and UI
├── requirements.txt     # List of Python libraries required
└── README.md            # Documentation
