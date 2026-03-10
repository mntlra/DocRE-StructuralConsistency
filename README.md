# Ontology-Driven Structural Regularization for Document-Level Relation Extraction

This repository contains the code to perfom a structural consistency analysis of DocRE datasets. The analysis is based on the presence of invalid triples (violating the domain and range constraint of a specific relation), missing inverse triples, invalid symmetric triples (presence of symmetric triples when the relation is asymmetric), and maximum cardinality violations. 

The structural consistency analysis can be performed in any DocRE dataset formatted as DocRED (package `dataset_quality`) and in model predictions formatted as DocRED official results (package `predictions_quality`).

We also share the code to correct datasets containing structural inconsistencies (package `dataset_correction`). 

## Structural inconsistencies
We share the ontoogy-driven structural inconsistencies defined for DocRED in `data/rules`. 

By default, all scripts uses the structural inconsistencies defined for DocRED. One can change the considered rules by setting the arguments:

- `--domain_range_path` for the domain and range constraints
- `--inverse_path` for the inverse relations
- `--symmetric_path` for the symmetric relations (used for the asymmetric violations)
- `--cardinality_path`for the maximum cardinality of the relations

### Creating your own rules
The script can work with any structural inconsistencies. If you are working with a different dataset than DocRED, you can define your own structural inconsistencies by following the format of shared rules. 

#### Domain-Range Constraints
The file `data/rules/domain_range_rules.json` contains the domain and range constraints identified for DocRED relations. The rules are formatted as a JSON file where the key is an entity type pair and the value is the list of relations allowing the considered domain and range. 

Example: "PER+LOC": [P19, P20] => Relations P19 (place of birth) and P20 (place of death) allow as domain entity type "person" (PER) and as range entity type "location" (LOC).

#### Inverse Relations
The file `data/rules/inverse_relations.json` contains the inverse relations identified for DocRED relations. The rules are formatted as a JSON file where the key is a relation and the value is its inverse relations. 

Example: "P36": "P1376" => The inverse relation of P36 (capital) is P1376 (capital of).

#### Symmetric Relations
The file `data/rules/symmetric_relations.json` contains the symmetric relations identified for DocRED relations. The rules are formatted as a JSON file following the same format as for inverse relations.

#### Maximum Cardinality
The file `data/rules/max_cardinality.json` contains the maximum cardinality of a set of relations identified for DocRED relations. The rules are formatted as a JSON file where the key is the relation and the value is its maximum cardinality. 

Example: "P571": 2 => The relation P571 (inception) has maximum cardinality 2.

## Consistency Analysis of DocRE Datasets
To perform a consistency analysis any DocRE dataset, run the script `src/main_correct_dataset.py`. The script takes as input the path to the dataset (must be in DocRED format).

To check the consistency of the DocRED distant dataset:
1. Download the DocRED distant dataset from https://github.com/thunlp/DocRED/tree/master and place it in `data/datasets`
2. Change the directory to src:
````
cd src/
````
3. Run:
````
python main_dataset_quality.py --data_path="../data/train_distant.json"
````

## Correcting the datasets
To correct any DocRE dataset, run the script `src/main_correct_dataset.py`. The script takes as input the path to the dataset and the path where to save the corrected file.

### Usage example
To correct the DocRED distant dataset:
1. Download the DocRED distant dataset from https://github.com/thunlp/DocRED/tree/master and place it in `data/datasets`
2. Change the directory to src:
````
cd src/
````
3. Run:
````
python main_correct_dataset.py --data_path="../data/datasets/train_distant.json" --save_path="../data/datasets/train_distant_correct.json"
````
This script generates the corrected DocRED distant exploited for the experimental results in Table 2 and 3.

## Predictions Consistency Analysis
To perform a consistency analysis of any DocRE model's predictions, run the script `src/main_predictions_quality.py`. The script takes as input the path to the predictions file (must be in the DocRED official results format) and the evaluation datasets of the predictions.

### Usage example
To check the structurual consistency of the predictions of a model on the Re-DocRED test dataset:
1. Place the predictions file (for example `results_test_revised.json`) in the data folder.
2.Download the Re-DocRED test dataset from https://github.com/tonytan48/Re-DocRED and place it in `data/datasets`
2. Change the directory to src:
````
cd src/
````
3. Run:
````
python predictions_quality/main_predictions_quality.py --data_path="../data/datasets/test_revised.json" --preds_path="../data/preds/results_test_revised.json"
````
This script generates the consistency analysis reported in Table 2.
