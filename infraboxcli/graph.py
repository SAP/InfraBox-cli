from builtins import range

from infraboxcli.job_list import load_infrabox_json, get_job_list, get_parent_name

def graph(args):
    data = load_infrabox_json(args.infrabox_json)
    jobs = get_job_list(data, args, base_path=args.project_root)

    d = 'digraph "%s" {' % args.project_name

    for j in jobs:
        parents = j['parents']

        if len(parents) == 0:
            continue

        parent_name = get_parent_name(parents)

        for i in range(0, len(parents)):
            p = parents[i]
            d += ' subgraph "cluster_%s" {\n' % get_parent_name(parents[0:i + 1])

        d += '   label="%s";\n' % parent_name.split('/')[-1]
        d += '   "%s";\n' % j['name']

        for i in range(0, len(parents)):
            p = parents[i]
            d += ' }\n'


    for j in jobs:
        for dep in j.get('depends_on', []):
            d += '"%s" -> "%s";\n' % (dep, j['name'])

    d += "}"

    with open(args.output, 'w') as out:
        out.write(d)
