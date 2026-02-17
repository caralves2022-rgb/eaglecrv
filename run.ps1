# Start the Data Collector in the background
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "collector.py"

# Start the Streamlit Dashboard without prompts
streamlit run app.py --browser.gatherUsageStats false
