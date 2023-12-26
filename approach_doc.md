# Preliminary Data Preperation
- Data extraction from PDF : The given pdf data was not easily extractable therefore was parsed by a multimodal model as screenshots which was converted to a csv file (data.csv)
- Schema Specification : To make queries more well definable for the LLM a single table schema was made with constraints based on the data given. Ideally these constrained fields must be a seperate table and be normalized , but for the purpose of the interview it was not worth the effort.
```
hardware (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL CHECK(type IN ('CPU', 'GPU', 'RAM', 'SSD', 'Motherboard', 'Power Supply', 'Cooling System')),  -- Constrained hardware types
  model TEXT NOT NULL,
  cost INTEGER NOT NULL,
  num_buyers INTEGER NOT NULL,
  region TEXT NOT NULL CHECK(region IN ('Africa', 'Asia', 'Australia', 'Europe', 'Middle East', 'North America', 'South America')),
  brand TEXT NOT NULL
)
```

# Model Choice
Various open source LLM models across various parameter sizes were tested (1B 3B 7B 8x7B) , some of the artifacts stored in workshop folder
The model choice was not a preliminary choice but something that was decided after multiple iterations but for ease of following along has been discussed earlier

## Concerns and Difficulties while choosing models :
The model is expected to take a users question and then process it into its corressponding SQL query and search the db and then process the output as natural language for the user to read. This involves a model that can handle language reallt well and understands SQL really well to perform sometimes complicated operations such as nested queries with join statements, something which even multi billion dollar companies are cracking their head at and requires huge servers to run them but the assignment task mandated that this must be run locally. Even GPT 3.5 produces factually incorrect queries and requires retries

Smaller models cannot reach this level of competency. I tested openhermes2.5-mistral (7B) , dolphin-phi2 finetune (3B ), starling-lm (7B) , tinyllama (1B).
They all write incorrect SQL queries or interpret the user's query in undesirable manner. There is also the issue of these models not producing outputs in consistent manner even with formal grammar specified (ollama json format)

The final choice was something built on top of mixtral 8x7B MoE. While 46B param in size for inference it has the same requirements as a 13B parameter model
NOTE : The requirement of not using a API for even hosting / inference such as together or deepinfra is a bit unfair here since not many can run models greater than 7B in size. My machine was barely able to run it after heavy quantization ( 3bit quantization )

Due to hardware limitations as mentioned in the note above the hardware I chose to run a Q3KM quantization variant (refer TheBloke's GGUF recommendation chart).
The model I chose was dolphin 2.6 mixtral, a finetune done by eric hartford. This was preferred since it was trained on more code data and chain of thought reasoning capabilities.

An additional consideration that was also taken into account was since these are expected to be used commercially the license was also checked to see if it complies with commerical use

DISCLAIMER : This model will take a long time to generate output for the above mentioned reasons so a test run has been saved with its logs and outputs in the project directory

# Higher Level Overview

![overview](https://i.imgur.com/8WJ9YLd.png)

For answering each question there are 2 LLM calls involved one to generate the query and one to make sense of the output data 
The code is self explanatory in terms of what the prompt actually does.

- Ollama is used as the inference interface (llama.cpp being the actual inference engine)  
- I have used regex for data clean up after the LLM inference as they sometimes contains special characters that cause the json decoder to fail  
- If anything else causes it to fail like a invalid sql operation then it is looped till its executed
- For the database to keep things simple used python inbuilt sqlite package

Additional Optimizations :
- Could use a smaller model for the second stage post processing of sql output to natural language

# Extras
Any ideas on improving the system under the same constraints would be good pointers for future improvement