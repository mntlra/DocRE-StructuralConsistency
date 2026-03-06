import json

def check_invalid(rules_path, preds, title2data):
    """
        Quality control on invalid triples.

        Args:
            rules_path (str): Path to the file containing the domain and range of each relation. The file is a JSON file, where the key is the domain and range entity type (example: PER+PER) 
            and the value is the allowed relations for the given entity type pair.

            preds (list(dict)): Predictions in DocRED official results format.

            title2data (dict): Evaluation dataset in DocRED format.

        Returns:
            Prints the total number of predictions and the number of invalid triples. The percentage is computed as the ratio between the number of invalid triples 
            and the total number of predictions. 
    """
    rules = json.load(open(rules_path, "r"))
    tot_labels = len(preds)
    invalid = 0
    for d in preds:
        type_h = title2data[d["title"]]["vertexSet"][d["h_idx"]][0]["type"]
        type_t = title2data[d["title"]]["vertexSet"][d["t_idx"]][0]["type"]

        if d["r"] not in rules[f"{type_h}+{type_t}"]:
            invalid += 1

    print(f"{tot_labels} labels, {invalid} ({round((invalid/tot_labels)*100, 2)} %) invalid.")

def check_inverse(rules_path, preds, verbose=False, rel_info_path=None):
    """
        Quality control on inverse relations.

        Args:
            rules_path (str): Path to the file containing the inverse relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation.

            preds (list(dict)): Predictions in DocRED official results format.

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
    for lbl in preds:
        if lbl["r"] in inverse_rels.keys():
            tot_inverse += 1
            try:
                inverse[lbl["r"]] += 1
            except KeyError:
                inverse[lbl["r"]] = 1
            found = False
            for l in preds:
                if l["title"] == lbl["title"] and l["r"] == inverse_rels[lbl["r"]] and l["h_idx"] == lbl["t_idx"] and l["t_idx"] == lbl["h_idx"]:
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
            print(f"Relation {r} ({rel_info[r]}): missing {inverse_missing[r]} out of {inverse[r]} ({(inverse_missing[r]/inverse[r])*100} %)")

def check_asymmetric(rules_path, preds, verbose=False, rel_info_path=None):
    """
        Quality control on asymmetric relations.

        Args:
            rules_path (str): Path to the file containing the symmetric relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation. In this case, the key and value are the same since we are condisering symmetric relations.

            preds (list(dict)): Predictions in DocRED official results format.

            verbose (bool): Whether to print the statistics for each relation.

            rel_info_path (str): Path to the file containing the relation labels (required if verbose=True). The file is a JSON file, where the key is the relation 
            and the value is the textual description of the relation. 

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
    for lbl in preds:
        if lbl["r"] not in symm_rels.keys():
            tot_inverse += 1
            try:
                inverse[lbl["r"]] += 1
            except KeyError:
                inverse[lbl["r"]] = 1
            found = False
            for l in preds:
                if l["title"] == lbl["title"] and l["r"] == lbl["r"] and l["h_idx"] == lbl["t_idx"] and l["t_idx"] == lbl["h_idx"]:
                    found = True
                    break
            if found:
                tot_missing += 1
                missing_preds.append({"title": lbl["title"], "r": lbl["r"], "h": lbl["h_idx"], "t": lbl["t_idx"]})
                try:
                    inverse_missing[lbl["r"]] += 1
                except KeyError:
                    inverse_missing[lbl["r"]] = 1
            else:
                inverse_found += 1

    print(f"Found: {inverse_found}")                
    print(f"Number of asymmetric labels: {tot_inverse}. Invalid symmetric {tot_missing} ({(tot_missing/tot_inverse)*100} %)")   
    if verbose:
        if rel_info_path is None:
            raise ValueError(f"When verbose is True, you must provide a value for rel_info_path.")

        rel_info = json.load(open(rel_info_path, "r"))
        for r in inverse_missing.keys():
            print(f"Relation {r} ({rel_info[r]}): Invalid symmetric {inverse_missing[r]} out of {inverse[r]} ({(inverse_missing[r]/inverse[r])*100} %)")

def check_cardinality(rules_path, preds):
    """
        Quality control on relations cardinality.

        Args:
            rules_path (str): Path to the file containing the cardinality of the relations with a maximum cardinality limit. The file is a JSON file, where the key is the relation and the value is the cardinality 
            of the relation.

            preds (list(dict)): Predictions in DocRED official results format.

        Returns:
            Prints the total number of triples in the ground truth where the relation has a limit in the cardinality and the number of triples exceeding the relation cardinality. 
            The percentage is computed as the ratio between the number of triples exceeding the relation cardinality and the total number of triples in the ground truth where 
            the relation has a limit in the cardinality. 
    """

    cardinalities = json.load(open(rules_path, "r"))

    invalid = {}
    pairs = []
    for l in preds: 
        if l["r"] in cardinalities.keys():
            if (l["title"], l["h_idx"], l["r"]) not in pairs:
                pairs.append((l["title"], l["h_idx"], l["r"]))
                triples = [l]
                for t in preds:
                    if l["title"] == t["title"] and l["h_idx"] == t["h_idx"] and l["r"] == t["r"] and l["t_idx"] != t["t_idx"]:
                        triples.append(t)
                if len(triples) > cardinalities[l["r"]]:
                    invalid[(l["title"], l["h_idx"], l["r"])] = len(triples)

    print(f"TOTAL pairs {len(pairs)}.")
    print(f"Invalid: {len(invalid)} ({round((len(invalid)/len(pairs))*100,2)} %)")
