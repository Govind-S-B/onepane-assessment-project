# OnePane Assessment Project
To use a local LLM to read user query and make SQL queries and then answer the user questions.
Given a test data and sample questions to work with.

You can find the approach document in [here](linktoreadme)

# How to run

1. Setup the LLM model and runner
install [ollama](https://ollama.ai/download)
and have it up and running with command `ollama serve` ( applicable to some systems only )  

download the required model
```
ollama pull dolphin-mixtral:8x7b-v2.6-q3_K_M
```
2. Clone the repo and move into the directory
```
git clone 
cd
```
3. Run the script
```
python3 main.py
```