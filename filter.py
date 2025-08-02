

from utils import add_quote

def get_predicates():
    context_list = []
    attrs = set()
    try:
        with open('data/knowledge.pl', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('place('):
                    parts = line[line.find('(')+1:line.find(')')].split(',')
                    if len(parts) == 3:
                        attr = parts[1].strip("' ")
                        value = parts[2].strip("' ")
                        context_list.append([attr, None, value])
                        attrs.add(attr)
    except FileNotFoundError:
        pass
    return list(attrs), context_list


def match_predicates(attr:str, values:list, name_list:list):
    if 'require' in attr:
        return attr + '(' + add_quote(values[0]) + ',' + add_quote(values[1]) + ')'
    elif 'query' in attr or 'prefer' in attr or attr == 'another_option' or attr == 'view_history':
        return attr + '(' + add_quote(values[0]) + ')'


def parse_predicates(inputs:str, attrs, values):
    pred_heads = ['query(', 'require(', 'prefer(', 'another_option(', 'view_history(', 'new_recommend(']
    close_domain = ['food type', 'establishment', 'family-friendly', 'dating', 'price range', 'customer rating']
    names = [x[2] for x in values if x[0] == 'name']
    attr_dict = {a:list(set([x[2] for x in values if x[0] == a])) for a in list(set([v[0] for v in values]))}

    preds = inputs.split(')')
    output = ''
    for pred in preds:
        pred = pred.strip('.').strip()
        pred_list = []
        in_list = any([pred.startswith(x) for x in pred_heads]) or any([pred.startswith('not_' + x) for x in pred_heads])
        if in_list:
            pred_split = pred.split('(')
            pred_values = pred_split[1].split(', ')
            pred_values = [x.strip() for x in pred_values]
            if pred_split[0] == 'require' and pred_values[0] in attr_dict and (pred_values[0] not in close_domain or pred_values[1] in attr_dict[pred_values[0]] or pred_values[1] == 'any'):
                pred_list.append({pred_split[0]:pred_values})
            if pred_split[0] != 'require':
                pred_list.append({pred_split[0]:pred_values})
        else:
            continue
        if not pred_list:
            continue
        for pred in pred_list:
            p_pred = match_predicates(list(pred.keys())[0], list(pred.values())[0], names)
            if p_pred:
                output += p_pred + '. '
    if output:
        output = output.strip(' ')
    return output

def filter(input, attrs, values):
    if input == 'thank.' or input == 'quit.':
        return input
    preds = parse_predicates(input, attrs, values)
    if not preds:
        return 'irrelevant.'
    else:
        return preds


