import re
import sys

import yaml

ITEM = ['uuid', 'name', 'type', 'snmp_oid', 'key', 'delay', 'history', 'trends', 'value_type', 'units', 'logtimefmt',
        'description', 'inventory_link', 'valuemap', 'preprocessing', 'tags', 'triggers', 'trigger_prototypes']
TRIGGER = ['uuid', 'expression', 'recovery_mode', 'recovery_expression', 'name', 'event_name', 'opdata', 'priority',
           'description', 'manual_close', 'dependencies', 'tags']
RULE = ['uuid', 'name', 'type', 'snmp_oid', 'key', 'delay', 'filter', 'description', 'preprocessing',
        'item_prototypes', 'trigger_prototypes', 'graph_prototypes']
GRAPH = ['uuid', 'name', 'ymin_type_1', 'ymax_type_1', 'graph_items']
GRAPH_ITEM = ['sortorder', 'drawtype', 'color', 'yaxisside', 'item']
PREPROCESSING = ['type', 'parameters', 'error_handler', 'error_handler_params']
ITEM_DEFAULTS = {'delay': '1m', 'history': '31d', 'trends': '365d', 'value_type': 'UNSIGNED'}
HEADER = [
    '# Zabbixは既定値（delay: 1m / history: 31d / trends: 365d / value_type: UNSIGNED / error_handler: DISCARD_VALUE）を省略してエクスポートするため、',
    '# インポート時の差分が出ないよう、既定値の行はコメントアウトして記載している。',
]
COMMENT_OUT = re.compile(
    r'^(\s+)(delay: 1m|history: 31d|trends: 365d|value_type: UNSIGNED|error_handler: DISCARD_VALUE)$')


def order(obj, keys):
    unknown = [k for k in obj if k not in keys]
    if unknown:
        sys.exit(f'unknown keys {unknown} in {obj.get("name", obj.get("key", obj))}')
    return {k: obj[k] for k in keys if k in obj}


def fix_preprocessing(step):
    if step['type'] == 'CHECK_NOT_SUPPORTED':
        step.setdefault('error_handler', 'DISCARD_VALUE')
    return order(step, PREPROCESSING)


def fix_item(item):
    for key, value in ITEM_DEFAULTS.items():
        item.setdefault(key, value)
    item = order(item, ITEM)
    if 'preprocessing' in item:
        item['preprocessing'] = [fix_preprocessing(s) for s in item['preprocessing']]
    for key in ('triggers', 'trigger_prototypes'):
        if key in item:
            item[key] = [order(t, TRIGGER) for t in item[key]]
    return item


def fix_graph(graph):
    graph = order(graph, GRAPH)
    graph['graph_items'] = [order(g, GRAPH_ITEM) for g in graph['graph_items']]
    return graph


def normalize(doc):
    export = doc['zabbix_export']
    for template in export['templates']:
        template['items'] = [fix_item(i) for i in template.get('items', [])]
        if 'macros' in template:
            template['macros'] = sorted(template['macros'], key=lambda m: m['macro'])
        rules = []
        for rule in template.get('discovery_rules', []):
            rule['item_prototypes'] = [fix_item(i) for i in rule.get('item_prototypes', [])]
            if 'trigger_prototypes' in rule:
                rule['trigger_prototypes'] = [order(t, TRIGGER) for t in rule['trigger_prototypes']]
            if 'graph_prototypes' in rule:
                rule['graph_prototypes'] = [fix_graph(g) for g in rule['graph_prototypes']]
            if 'preprocessing' in rule:
                rule['preprocessing'] = [fix_preprocessing(s) for s in rule['preprocessing']]
            rules.append(order(rule, RULE))
        if rules:
            template['discovery_rules'] = rules
        else:
            template.pop('discovery_rules', None)
    if 'graphs' in export:
        export['graphs'] = [fix_graph(g) for g in export['graphs']]
    if 'triggers' in export:
        export['triggers'] = [order(t, TRIGGER) for t in export['triggers']]
    return doc


def literal_multiline(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|' if '\n' in data else None)


def main(path):
    yaml.add_representer(str, literal_multiline, Dumper=yaml.SafeDumper)
    doc = normalize(yaml.safe_load(open(path)))
    text = yaml.dump(doc, Dumper=yaml.SafeDumper, sort_keys=False, allow_unicode=True, width=100000)
    lines = [COMMENT_OUT.sub(r'\1# \2', line) for line in text.split('\n')]
    open(path, 'w').write('\n'.join(HEADER + lines))
    uuids = re.findall(r'uuid: (\w+)', text)
    if len(uuids) != len(set(uuids)):
        sys.exit('duplicate uuid')


main(sys.argv[1])
