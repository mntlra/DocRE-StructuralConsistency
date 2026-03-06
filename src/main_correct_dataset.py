import argparse
import json
from correct_data import remove_invalid, insert_inverse, remove_asymmetric
from check_rules_dataset import check_invalid, check_inverse, check_asymmetric, check_cardinality

parser = argparse.ArgumentParser()
parser.add_argument("--data_path", required=True, type=str, help="The path of the data file. The data file must be a JSON file in the DocRED dataset format.")
parser.add_argument("--domain_range_path", default="../data/rules/domain_range_rules.json", type=str, help="Path to the file containing the domain and range of each relation.")
parser.add_argument("--inverse_path", default="../data/rules/inverse_relations.json", type=str, help="Path to the file containing the inverse relations.")
parser.add_argument("--symmetric_path", default="../data/rules/symmetric_relations.json", type=str, help="Path to the file containing the symmetric relations.")
parser.add_argument("--cardinality_path", default="../data/rules/max_cardinality.json", type=str, help="Path to the file containing the cardinality of the relations with a maximum cardinality limit.")
parser.add_argument("--save_path", required=True, type=str, help="The path of the corrected dataset.")

def main():
    args = parser.parse_args()
    print(f"Loading data from {args.data_path} ...")
    data = json.load(open(args.data_path, "r"))
    print("Remove Invalid Triples")
    data = remove_invalid(args.domain_range_path, data)
    print()
    print("Add Missing Inverse Triples")
    data = insert_inverse(args.inverse_path, data)
    print()
    print("Remove Invalid Symmetric Triples")
    data = remove_asymmetric(args.symmetric_path, data)

    print("Checking dataset is clean ...")
    print("Invalid Relations")
    check_invalid(args.domain_range_path, data)
    print()
    print("Inverse Relations")
    check_inverse(args.inverse_path, data)
    print()
    print("Asymmetric")
    check_asymmetric(args.symmetric_path, data)

    print(f"Saving corrected data in {args.save_path} ...")
    json.dump(data, open(args.save_path, "w"))

if __name__ == "__main__":
    main()
