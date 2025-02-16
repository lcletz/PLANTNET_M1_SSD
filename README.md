# Conforming prediction and PL@ntnet-crowdswe database

Welcome to our project conforming prediction and PL@ntnet-crowdswe database for the academic year 2025. 

Name of supervisors:

- Joseph Salmon (joseph.salmon@inria.fr)
- Christophe Botella (christophe.botella@inria.fr)

The team members are :

- AIGOIN Emilie
- CLETZ Laura
- THOMAS Anne-Laure

## Introduction:

PL@ntnet is a mobile plant recognition application used by 20 million users around the world, generating valuable observations for research. The algorithm can identify more than 50,000 species, but lacks valid images for most of them, which leads to frequent errors in predictions. This project explores the application of the "conformal pre -prediction" approach to quantify the uncertainty of the predictions of the model, guaranteeing a controlled error rate. It is based on the PL@ntnet-crowdswe database to assess the efficiency of this method.

Here is a diagram of the architecture of our project, detailing the location of each folder and file:

```PLANTNET
    ├── data/
    |     ├── __init__.py
    |     ├── fetch_data.py
    ├── extracted_data/ 
    │     ├── aggregation/
    |     |     |── ai_answers.json
    |     |     ├── ai_classes.json
    |     |     ├── ai_scores.json
    |     |     ├── authors.txt
    │     │     └── k-southwestern-europe.json
    |     ├── answers/
    |     |     |── answers.json
    │     │     └── ground_truth.txt      
    │     └── converters/
    │           ├── classes.json     
    |           └── tasks.json
    ├── multiple_data/
    │     ├── 00/
    |     |     |── 00
    |     |     |     |── 10003830000.json
    |     |     |     |── ...
    |     |     |── 01
    |     |     |── ...
    |     |     |── 99
    │     ├── 1000460000.json
    │     ├── tasks.json
    ├── .gitignore
    ├── LICENSE  
    ├── README.md
    └── requirements.txt 
```

The ‘multiple_data’ folder contains a sample of the prediction data for the list of species with their score for each observation in the dataset (rather than a single prediction score).
