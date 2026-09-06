import json,sys,re,collections
for p in sys.argv[1:]:
    d=json.load(open(p));qs=d['questions'];errs=[]
    if len(qs) not in (20,27): errs.append(f"count {len(qs)}")
    for q in qs:
        if q['answer'] not in q['options']: errs.append(f"q{q['n']} answer key")
        for k in q['options']:
            if k!=q['answer'] and not q['traps'].get(k): errs.append(f"q{q['n']} missing trap {k}")
        vals=[re.sub(r'<[^>]+>','',v) for v in q['options'].values()]
        if len(set(vals))!=len(vals): errs.append(f"q{q['n']} duplicate options")
        for bad in ['Wait','TODO','??','...']:
            if bad in q['solution_html'] or bad in q['stem_html'] or any(bad in t for t in q['traps'].values()): errs.append(f"q{q['n']} contains {bad}")
    keys=collections.Counter(q['answer'] for q in qs)
    diff=collections.Counter(q.get('difficulty') for q in qs)
    print(p, "OK" if not errs else errs, "| answer spread", dict(sorted(keys.items())), "| difficulty", dict(sorted(diff.items(),key=lambda x:str(x[0]))))
