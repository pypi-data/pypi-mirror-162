# Wikidata processing, not strictly specific to wikipedia validator tasks,
# but also not direct fetching of data like wikimedia_connection

import wikimedia_connection.wikimedia_connection as wikimedia_connection
import pprint
import time

def get_all_types_describing_wikidata_object(wikidata_id, ignored_entries_in_wikidata_ontology):
    base_type_ids = get_wikidata_type_ids_of_entry(wikidata_id)

    subclasses_via_types = []
    if base_type_ids != None:
        # as even base types can be blacklisted, see https://www.wikidata.org/wiki/Q1392479
        # and trademark is blacklisted
        base_type_ids = list(set(base_type_ids) - set(ignored_entries_in_wikidata_ontology))
        subclasses_via_types = get_recursive_all_subclass_of_list(base_type_ids, ignored_entries_in_wikidata_ontology)
    direct_subclasses = get_recursive_all_subclass_of_list([wikidata_id], ignored_entries_in_wikidata_ontology)
    return subclasses_via_types + direct_subclasses

def get_recursive_all_subclass_of_list(base_type_ids, ignored_entries_in_wikidata_ontology):
    all_types = []
    for type in base_type_ids:
        all_types += get_recursive_all_subclass_of(type, ignored_entries_in_wikidata_ontology)
    return all_types

def get_wikidata_type_ids_of_entry(wikidata_id):
    if wikidata_id == None:
        return None
    types = None
    try:
        forced_refresh = False
        wikidata_entry = wikimedia_connection.get_data_from_wikidata_by_id(wikidata_id, forced_refresh)
        if wikidata_entry == None:
            raise ValueError("got none for " + wikidata_id)
        wikidata_entry = wikidata_entry['entities']
        object_id = list(wikidata_entry)[0]
        types = wikidata_entry[object_id]['claims']['P31']
    except KeyError:
        return None
    return [type['mainsnak']['datavalue']['value']['id'] for type in types]

def wikidata_entries_for_abstract_or_very_broad_concepts():
    return ['Q1801244', 'Q28732711', 'Q223557', 'Q488383', 'Q16686448',
    'Q151885', 'Q35120', 'Q37260', 'Q246672', 'Q5127848', 'Q16889133',
    'Q386724', 'Q17008256', 'Q11348', 'Q11028', 'Q1260632', 'Q1209283',
    'Q673661', 'Q23008351', 'Q1914636', 'Q17334923', 'Q2221906',
    'Q2324993', 'Q58778', 'Q18340964', 'Q1544281', 'Q2101636',
    'Q30060700', 'Q3778211', 'Q937228',
    ]

# ignored_entries_in_wikidata_ontology is mandatory as severe issues with wikidata ontology are normal
# and not worth fixing
# (if you want to fix them - let me know and I can give you a list of problems that caused implementing this)
def get_recursive_all_subclass_of(wikidata_id, ignored_entries_in_wikidata_ontology, debug = False, callback = None):
    processed = []
    to_process = [{"id": wikidata_id, "depth": 0}]
    while to_process != []:
        process = to_process.pop()
        category_id = process["id"]
        depth = process["depth"]
        callback_text = ""
        if callback != None:
            callback_text = callback(category_id)
        if debug:
            print("   "*depth + wikidata_description(category_id) + callback_text)
        processed.append(category_id)
        new_ids = get_useful_direct_parents(category_id, processed + to_process + ignored_entries_in_wikidata_ontology)
        for parent_id in new_ids:
            to_process.append({"id": parent_id, "depth": depth+1})
    return processed


def get_recursive_all_subclass_of_with_depth_data(wikidata_id, ignored_entries_in_wikidata_ontology, debug = False, callback = None):
    processed = []
    found = []
    to_process = [{"id": wikidata_id, "depth": 0}]
    while to_process != []:
        process = to_process.pop()
        category_id = process["id"]
        depth = process["depth"]
        found.append(process)
        callback_text = ""
        if callback != None:
            callback_text = callback(category_id)
        if debug:
            print("   "*depth + wikidata_description(category_id) + callback_text)
        processed.append(category_id)
        new_ids = get_useful_direct_parents(category_id, processed + to_process + ignored_entries_in_wikidata_ontology)
        for parent_id in new_ids:
            to_process.append({"id": parent_id, "depth": depth+1})
    return found

def wikidata_description(wikidata_id):
    en_docs = get_wikidata_description(wikidata_id, 'en')
    if en_docs != None:
        return en_docs
    pl_docs = get_wikidata_description(wikidata_id, 'pl')
    if pl_docs != None:
        return pl_docs
    return("Unexpected type " + wikidata_id + " undocumented format")

def get_wikidata_label(wikidata_id, language):
    if wikidata_id == None:
        return None
    try:
        data = wikimedia_connection.get_data_from_wikidata_by_id(wikidata_id)['entities'][wikidata_id]
        return data['labels']['en']['value']
    except KeyError:
        return None

def get_wikidata_explanation(wikidata_id, language):
    if wikidata_id == None:
        return None
    try:
        data = wikimedia_connection.get_data_from_wikidata_by_id(wikidata_id)['entities'][wikidata_id]
        return data['descriptions'][language]['value']
    except KeyError:
        return None

def get_wikidata_description(wikidata_id, language):
    if wikidata_id == None:
        return None
    docs = wikimedia_connection.get_data_from_wikidata_by_id(wikidata_id)
    returned = ""
    label = get_wikidata_label(wikidata_id, language)
    explanation = get_wikidata_explanation(wikidata_id, language)

    if label == None and explanation == None:
        return None

    if explanation != None:
        explanation = ' (' + explanation +')'
    else:
        explanation = ''
    
    if label == None:
        label = ''

    return(language + ": " + label + explanation + ' [https://www.wikidata.org/wiki/' + wikidata_id + "]")

def get_useful_direct_parents(wikidata_id, forbidden):
    more_general_list = wikimedia_connection.get_property_from_wikidata(wikidata_id, 'P279') #subclass of
    if more_general_list == None:
        return []
    returned = []
    for more_general in more_general_list:
        if 'mainsnak' not in more_general:
            pprint.pprint(more_general)
            print("on processing", wikidata_id)
            raise ValueError("missing mainsnack in " + str(wikidata_id))

        if 'datavalue' not in more_general['mainsnak']:
            pprint.pprint(more_general)
            pprint.pprint(more_general['mainsnak'])
            print("on processing", wikidata_id)
            raise ValueError("missing datavalue in " + str(wikidata_id))

        if 'value' not in more_general['mainsnak']['datavalue']:
            pprint.pprint(more_general)
            pprint.pprint(more_general['mainsnak'])
            pprint.pprint(more_general['mainsnak']['datavalue'])
            print("on processing", wikidata_id)
            raise ValueError("missing value in " + str(wikidata_id))

        more_general_id = more_general['mainsnak']['datavalue']['value']['id']
        if more_general_id not in forbidden:
            returned.append(more_general_id)
    return returned

def decapsulate_wikidata_value(from_wikidata):
    # https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#Claims_and_Statements
    # todo fix flow by random exception
    try:
        from_wikidata = from_wikidata[0]['datavalue']['value']
    except KeyError:
        pass
    try:
        from_wikidata = from_wikidata[0]['mainsnak']['datavalue']['value']
    except KeyError:
        pass
    try:
        # for wikidata values formed like
        # {'entity-type': 'item', 'id': 'Q43399', 'numeric-id': 43399}
        if isinstance(from_wikidata, dict):
            if from_wikidata['entity-type'] == 'item':
                from_wikidata = from_wikidata['id']
    except KeyError:
        pass
    return from_wikidata
