import json

def check_invalid(rules_path, data, remove=False):
    """
        Quality control on invalid triples.

        Args:
            rules_path (str): Path to the file containing the domain and range of each relation. The file is a JSON file, where the key is the domain and range entity type (example: PER+PER) 
            and the value is the allowed relations for the given entity type pair.

            data (dict): Dataset in DocRED format.

            remove (bool): Whether to return the dictionary with invalid triples (for removal purposes).

        Returns:
            Prints the total number of triples in the ground truth and the number of invalid triples. The percentage is computed as the ratio between the number of invalid triples 
            and the total number of triples in the ground truth. 
    """
    rules = json.load(open(rules_path, "r"))
    tot_labels = 0
    invalid = 0
    invalid_triples, doc2invalid = {}, {}
    for d in data:
        tot_labels += len(d["labels"])
        for l in d["labels"]:
            type_h = d["vertexSet"][l["h"]][0]["type"]
            type_t = d["vertexSet"][l["t"]][0]["type"]

            if l["r"] not in rules[f"{type_h}+{type_t}"]:
                invalid += 1
                invalid_triples[(d["title"], l["h"], l["t"])] = 1
                try:
                    doc2invalid[d["title"]].append((l["h"], l["t"]))
                except KeyError:
                    doc2invalid[d["title"]] = [(l["h"], l["t"])]

    print(f"{tot_labels} labels, {invalid} ({round((invalid/tot_labels)*100, 2)} %) invalid.")
    if remove:
        return doc2invalid

def check_inverse(rules_path, data, verbose=False, rel_info_path=None):
    """
        Quality control on inverse relations.

        Args:
            rules_path (str): Path to the file containing the inverse relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation.

            data (dict): Dataset in DocRED format.

            verbose (bool): Whether to print the statistics for each relation.

            rel_info_path (str): Path to the file containing the relation labels (required if verbose=True). The file is a JSON file, where the key is the relation 
            and the value is the textual description of the relation. 

        Returns:
            Prints the total number of inverse triples (triples where the relation has an inverse relation) and the number of missing inverse triples. 
            The percentage is computed as the ratio between the number of missing inverse triples and the total number of inverse triples.
    """
    inverse_rels = json.load(open(rules_path, "r"))

    tot_inverse, inverse_found, tot_missing = 0, 0, 0
    inverse_missing = {}
    inverse = {}
    for d in data:
        for lbl in d["labels"]:
            if lbl["r"] in inverse_rels.keys():
                tot_inverse += 1
                try:
                    inverse[lbl["r"]] += 1
                except KeyError:
                    inverse[lbl["r"]] = 1
                found = False
                for l in d["labels"]:
                    if l["r"] == inverse_rels[lbl["r"]] and l["h"] == lbl["t"] and l["t"] == lbl["h"]:
                        found = True
                        break
                if found:
                    inverse_found += 1
                else:
                    tot_missing += 1
                    try:
                        inverse_missing[lbl["r"]] += 1
                    except KeyError:
                        inverse_missing[lbl["r"]] = 1

    print(f"Found: {inverse_found}")                
    print(f"Number of inverse labels: {tot_inverse}. Missing {tot_missing} ({round((tot_missing/tot_inverse)*100, 2)} %)")   

    if verbose:
        if rel_info_path is None:
            raise ValueError(f"When verbose is True, you must provide a value for rel_info_path.")

        rel_info = json.load(open(rel_info_path, "r"))
        for r in inverse_missing.keys():
            print(f"Relation {r} ({rel_info[r]}): missing {inverse_missing[r]} out of {inverse[r]} ({round((inverse_missing[r]/inverse[r])*100, 2)} %)")

def check_asymmetric(rules_path, data, verbose=False, rel_info_path=None, remove=False):
    """
        Quality control on asymmetric relations.

        Args:
            rules_path (str): Path to the file containing the symmetric relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation. In this case, the key and value are the same since we are condisering symmetric relations.

            data (dict): Dataset in DocRED format.

            verbose (bool): Whether to print the statistics for each relation.

            rel_info_path (str): Path to the file containing the relation labels (required if verbose=True). The file is a JSON file, where the key is the relation 
            and the value is the textual description of the relation. 

            remove (bool): Whether to return the dictionary with invalid triples (for removal purposes).

        Returns:
            Prints the total number of  asymmetric triples (where the relation is asymmetric) and the number of asymmetric triples (s,r,o) 
            where the ground truth also includes the symmetric triple (o,r,s). The percentage is computed as the ratio between asymmetric 
            triples with a symmetric triple in the ground truth and the total number of asymmetric triples.
    """
    symm_rels = json.load(open(rules_path, "r"))

    tot_inverse, inverse_found, tot_missing = 0, 0, 0
    inverse_missing = {}
    inverse = {}
    missing_preds = []
    invalid_triples, invalid_list = {}, {}
    for d in data:
        for lbl in d["labels"]:
            if lbl["r"] not in symm_rels.keys():
                tot_inverse += 1
                try:
                    inverse[lbl["r"]] += 1
                except KeyError:
                    inverse[lbl["r"]] = 1
                found = False
                for l in d["labels"]:
                    if l["r"] == lbl["r"] and l["h"] == lbl["t"] and l["t"] == lbl["h"]:
                        found = True
                        break
                if found:
                    tot_missing += 1
                    missing_preds.append({"title": d["title"], "r": lbl["r"], "h": lbl["h"], "t": lbl["t"]})
                    try:
                        inverse_missing[lbl["r"]] += 1
                    except KeyError:
                        inverse_missing[lbl["r"]] = 1
                    invalid_list[(d["title"], lbl["h"], lbl["t"])] = 1
                    try:
                        invalid_triples[d["title"]].append((l["h"], l["t"]))
                    except KeyError:
                        invalid_triples[d["title"]] = [(l["h"], l["t"])]
                else:
                    inverse_found += 1

    print(f"Found: {inverse_found}")                
    print(f"Number of asymmetric labels: {tot_inverse}. Invalid symmetric {tot_missing} ({round((tot_missing/tot_inverse)*100, 2)} %)")   
    if verbose:
        if rel_info_path is None:
            raise ValueError(f"When verbose is True, you must provide a value for rel_info_path.")

        rel_info = json.load(open(rel_info_path, "r"))
        for r in inverse_missing.keys():
            print(f"Relation {r} ({rel_info[r]}): Invalid symmetric {inverse_missing[r]} out of {inverse[r]} ({round((inverse_missing[r]/inverse[r])*100, 2)} %)")

    if remove:
        return invalid_triples

def check_cardinality(rules_path, data):
    """
        Quality control on relations cardinality.

        Args:
            rules_path (str): Path to the file containing the cardinality of the relations with a maximum cardinality limit. The file is a JSON file, where the key is the relation and the value is the cardinality 
            of the relation.

            data (dict): Dataset in DocRED format.

        Returns:
            Prints the total number of triples in the ground truth where the relation has a limit in the cardinality and the number of triples exceeding the relation cardinality. 
            The percentage is computed as the ratio between the number of triples exceeding the relation cardinality and the total number of triples in the ground truth where 
            the relation has a limit in the cardinality. 
    """

    cardinalities = json.load(open(rules_path, "r"))

    invalid = {}
    invalid_strict = {}
    pairs = []
    for d in data: 
        for l in d["labels"]:
            if l["r"] in cardinalities.keys():
                if (d["title"], l["h"], l["r"]) not in pairs:
                    pairs.append((d["title"], l["h"], l["r"]))
                    triples = [l]
                    for t in d["labels"]:
                        if l["h"] == t["h"] and l["r"] == t["r"] and l["t"] != t["t"]:
                            triples.append(t)
                    if len(triples) > cardinalities[l["r"]]:
                        invalid[(d["title"], l["h"], l["r"])] = len(triples)

    print(f"TOTAL pairs {len(pairs)}.")
    print(f"Invalid: {len(invalid)} ({round((len(invalid)/len(pairs))*100, 2)} %)")
