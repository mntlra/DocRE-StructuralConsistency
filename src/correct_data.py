import json
from check_rules_dataset import check_invalid, check_asymmetric

def remove_invalid(rules_path, data):
    """
        Remove invalid triples.

        Args:
            rules_path (str): Path to the file containing the domain and range of each relation. The file is a JSON file, where the key is the domain and range entity type (example: PER+PER) 
            and the value is the allowed relations for the given entity type pair.

            data (dict): Dataset in DocRED format.

        Returns:
            new_data (dict): Dataset in DocRED format without invalid triples. 
    """
    doc2invalid = check_invalid(rules_path, data, remove=True)
    new_data = []
    invalid_ents = 0
    old_num_labels, old_num_ents = 0, 0
    new_num_labels, new_num_ents = 0, 0
    for d in data:
        old_num_ents += len(d["vertexSet"])
        old_num_labels += len(d["labels"])
        if d["title"] in doc2invalid.keys():
            new_doc = {"title": d["title"], "sents": d["sents"]}
            invalid = []
            for pair in doc2invalid[d["title"]]:
                if pair[0] not in invalid:
                    invalid.append(pair[0])
                if pair[1] not in invalid:
                    invalid.append(pair[1])
            invalid = sorted(invalid)
            invalid_ents += len(invalid)
            new_vertexSet = []
            old2new = {}
            offset = 0
            for e_id, e in enumerate(d["vertexSet"]):
                if e_id in invalid:
                    offset += 1
                else:
                    old2new[e_id] = e_id-offset
                    new_vertexSet.append(e)
            if len(new_vertexSet) > 1:
                # there must be at least two entities in a document to make it a valid training example
                new_doc["vertexSet"] = new_vertexSet
                new_labels = []
                for l in d["labels"]:
                    if l["h"] not in invalid and l["t"] not in invalid:
                        new_labels.append({"h": old2new[l["h"]], "r": l["r"], "t": old2new[l["t"]], "evidence": l["evidence"]})
                new_doc["labels"] = new_labels

                new_num_ents += len(new_vertexSet)
                new_num_labels += len(new_labels)

                new_data.append(new_doc)
        else:
            new_num_ents += len(d["vertexSet"])
            new_num_labels += len(d["labels"])
            new_data.append(d)

    print(f"Corrected dataset has {len(new_data)} documents ({len(new_data)-len(data)}), {new_num_ents} entities ({new_num_ents-old_num_ents}) and {new_num_labels} labels ({new_num_labels-old_num_labels})")

    return new_data

def insert_inverse(rules_path, data, verbose=False):
    """
        Insert missing inverse relations.

        Args:
            rules_path (str): Path to the file containing the inverse relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation. In this case, the key and value are the same since we are condisering symmetric relations.

            data (dict): Dataset in DocRED format.

            verbose (bool): Whether to print the statistics for each relation.

        Returns:
            data (dict): Dataset in DocRED format without missing inverse triples. 
    """

    inverse_rels = json.load(open(rules_path, "r"))
    tot_added = 0
    added = {}
    for d in data:
        for lbl in d["labels"]:
            if lbl["r"] in inverse_rels.keys():
                found = False
                for l in d["labels"]:
                    if l["r"] == inverse_rels[lbl["r"]] and l["h"] == lbl["t"] and l["t"] == lbl["h"]:
                        found = True
                        break
                if not found:
                    d["labels"].append({"h": lbl["t"], "t": lbl["h"], "r": inverse_rels[lbl["r"]], "evidence": []})
                    tot_added += 1
                    try:
                        added[lbl["r"]] += 1
                    except KeyError:
                        added[lbl["r"]] = 1

    print(f"Added {tot_added} relations")
    if verbose:
        print(added)

    return data

def remove_asymmetric(rules_path, data):
    """
        Remove invalid symmetric triples.

        Args:
            Path to the file containing the symmetric relations. The file is a JSON file, where the key is the relation 
            and the value is the inverse relation. In this case, the key and value are the same since we are condisering symmetric relations.

            data (dict): Dataset in DocRED format.

        Returns:
            new_data (dict): Dataset in DocRED format without invalid symmetric triples.
    """
    invalid_triples = check_asymmetric(rules_path, data, remove=True)

    new_data = []
    old_num_labels, old_num_ents = 0, 0
    new_num_labels, new_num_ents = 0, 0
    for d in data:
        if d["title"] in invalid_triples.keys():
            old_num_ents += len(d["vertexSet"])
            old_num_labels += len(d["labels"])
            new_doc = {"title": d["title"], "sents": d["sents"]}
            invalid = []
            for pair in invalid_triples[d["title"]]:
                if pair[0] not in invalid:
                    invalid.append(pair[0])
                if pair[1] not in invalid:
                    invalid.append(pair[1])
            invalid = sorted(invalid)
            new_vertexSet = []
            old2new = {}
            offset = 0
            for e_id, e in enumerate(d["vertexSet"]):
                if e_id in invalid:
                    offset += 1
                else:
                    old2new[e_id] = e_id-offset
                    new_vertexSet.append(e)
            if len(new_vertexSet) > 1:
                new_doc["vertexSet"] = new_vertexSet
                new_labels = []
                for l in d["labels"]:
                    if l["h"] not in invalid and l["t"] not in invalid:
                        new_labels.append({"h": old2new[l["h"]], "r": l["r"], "t": old2new[l["t"]], "evidence": l["evidence"]})
                new_doc["labels"] = new_labels

                new_num_ents += len(new_vertexSet)
                new_num_labels += len(new_labels)
                new_data.append(new_doc)
        else:
            new_num_ents += len(d["vertexSet"])
            new_num_labels += len(d["labels"])
            new_data.append(d)
    
    print(f"Corrected dataset has {len(new_data)} documents ({len(new_data)-len(data)}), {new_num_ents} entities ({new_num_ents-old_num_ents}) and {new_num_labels} labels ({new_num_labels-old_num_labels})")

    return new_data
