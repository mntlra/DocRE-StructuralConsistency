import argparse
import json
from check_rules_predictions import check_invalid, check_inverse, check_asymmetric, check_cardinality

parser = argparse.ArgumentParser()
parser.add_argument("--preds_path", required=True, type=str, help="The path of the file containing model predictions. The data file must be a JSON file in the DocRED results format.")
parser.add_argument("--data_path", required=True, type=str, help="The path of the file of the evaluation dataset. The data file must be a JSON file in the DocRED results format.")
parser.add_argument("--domain_range_path", default="../data/rules/domain_range_rules.json", type=str, help="Path to the file containing the domain and range of each relation.")
parser.add_argument("--inverse_path", default="../data/rules/inverse_relations.json", type=str, help="Path to the file containing the inverse relations.")
parser.add_argument("--symmetric_path", default="../data/rules/symmetric_relations.json", type=str, help="Path to the file containing the symmetric relations.")
parser.add_argument("--cardinality_path", default="../data/rules/max_cardinality.json", type=str, help="Path to the file containing the cardinality of the relations with a maximum cardinality limit.")

def main():
    args = parser.parse_args()
    print(f"Loading evaluation dataset from {args.data_path} ...")
    data = json.load(open(args.data_path, "r"))
    # prepare data dictionary
    title2data = {}
    for d in data:
        title2data[d["title"]] = d

    print(f"Loading predictions from {args.preds_path} ...")
    preds = json.load(open(args.preds_path, "r"))

    print("Invalid Relations")
    check_invalid(args.domain_range_path, preds, title2data)
    print()
    print("Inverse Relations")
    check_inverse(args.inverse_path, preds)
    print()
    print("Asymmetric")
    check_asymmetric(args.symmetric_path, preds)
    print()
    print("Cardinality")
    check_cardinality(args.cardinality_path, preds)

if __name__ == "__main__":
    main()
