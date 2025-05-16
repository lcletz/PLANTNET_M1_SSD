# Conforming prediction and PL@ntnet-crowdswe database

Welcome to our project conforming prediction and PL@ntnet-crowdswe database for the academic year 2025. 

Name of supervisors:

- Joseph Salmon (joseph.salmon@inria.fr)
- Christophe Botella (christophe.botella@inria.fr)

The team members are :

- AIGOIN Emilie (emilie.aigoin@etu.umontpellier.fr)
- CLETZ Laura (laura.cletz@etu.umontpellier.fr)
- THOMAS Anne-Laure (anne-laure.thomas@etu.umontpellier.fr)

---

PL@ntnet is a mobile plant recognition application used by 20 million users around the world, generating valuable observations for research. The algorithm can identify more than 50,000 species, but lacks valid images for most of them, which leads to frequent errors in predictions. This project is based on the Pl@ntnet-crowdswe database, i.e. around 7 mn observations of species of flora in south-western Europe, and will be divided into two sub-projects:
- statistical analysis of the data (scores, occurrences, etc.)
- conformal prediction's calibration and testing, in order to quantify the uncertainty of the model's predictions, while guaranteeing a controlled error rate.

Here is a diagram of the architecture of our project, detailing the location of each folder and file:

```PLANTNET
    ├── PlantNetM1SSD/
    │    ├── Analyses _Plantnet_300K/
    │    │   ├── readme.md
    │    │   └── Visualisation.Rmd
    │    ├── croisement_data/
    │    │   ├── ai.Rmd
    │    │   ├── Comptage_réponses.Rmd
    │    │   ├── croisement.Rmd
    │    │   ├── Predictions.Rmd
    │    │   ├── Scores.Rmd
    │    │   ├── Step1_predictions.Rmd
    │    │   ├── Step2_answer.Rmd
    │    │   ├── Step3_croisements.Rmd
    │    │   ├── Step4_scores.Rmd
    │    │   ├── Step5_graphiques_nonexp.Rmd
    │    │   ├── Step5_graphiques.Rmd
    │    │   └── test_set_sizes.Rmd
    │    ├── data_python/
    │    │   ├── code_extraction.py
    │    │   └── figures.py
    │    ├── multiple_data_python/
    │    │   ├── Expert_scores_division.py
    │    │   ├── extracted_tasks.py
    │    │   ├── Method1.py
    │    │   ├── Method2.py
    │    │   ├── Method3.py
    │    │   ├── Method4.py
    │    │   ├── scores_non_expertes.py
    │    │   ├── script_croisement.py
    │    │   ├── script_outpul_final.py
    │    │   └── script_output.py
    │    ├── PlantNet_M1_SSD.Rproj
    │    ├── PlantNetM1SSD_0.1.0.tar.gz
    │    ├── R/
    │    │   ├── data.Rmd
    │    │   ├── descriptive_stats.R
    │    │   ├── main_script.R
    │    │   ├── majority_vote.Rmd
    │    │   ├── samples_merge.Rmd
    │    │   ├── samples_processing.Rmd
    │    │   └── user_answers_crossing.Rmd
    │    ├── README.md
    │    ├── report/
    │    │   ├── images/
    │    │   ├── journal.tex
    │    │   ├── Rapport.fdb_latexmk
    │    │   ├── Rapport.fls
    │    │   ├── Rapport.log
    │    │   ├── Rapport.pdf
    │    │   ├── Rapport.tex
    │    │   └── references.bib
    │    └── slides/
```
