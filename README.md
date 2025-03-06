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
    ├── PlantNetM1SSD/
    |     ├── R/
    |     |   |── data.R
    |     |   ├── fetch_data.R
    |     |   ├── first_plots.R
    |     |   ├── limited_data.R
    |     |   ├── samples_processing.R
    |     |   ├── samples_test.R
    │     │   └── truth_data.R 
    |     ├── .Rbuildignore
    |     ├── .Rhistory
    |     ├── DESCRIPTION
    |     ├── NAMESPACE
    │     └── PlantNetM1SSD.Rproj
    ├── R_plot/ 
    │     ├── Données.Rmd   
    │     └── Visualization.Rmd
    ├── data_python/
    │     ├── code_extraction.py  
    │     └── code_figure_ai_answers.py
    ├── multiple_data/
    │     └── Script.py
    ├── multiple_data_python/
    │     ├── extracted_tasks.json.py
    │     ├── script.py  
    │     └── script2.py
    ├── slides/
    │     └── Réunion 2.pptx
    ├── .RData 
    ├── .Rhistory
    ├── .gitignore
    └── README.md
```
