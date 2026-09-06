import json,sys
swaps={"ESAT-PHY-A.json":{8:("D","E"),14:("D","E"),21:("D","E"),24:("D","E"),4:("D","A"),15:("D","A"),10:("C","A"),17:("C","A"),22:("C","E"),27:("C","E")},"ESAT-M1-A.json":{1:("B","A"),3:("B","A"),9:("B","A"),17:("B","D"),8:("C","A"),25:("C","A"),16:("C","D")},"ESAT-M2-A.json":{1:("C","E"),8:("C","E"),12:("C","E"),2:("C","B"),9:("C","B"),14:("C","B"),16:("C","B")},"TMUA-P1-A.json":{5:("C","E"),9:("C","A")},"TMUA-P2-A.json":{1:("C","E"),9:("C","A"),10:("C","E"),16:("C","A"),20:("C","E")}}
import os
for fn,sw in swaps.items():
    if not os.path.exists(fn): continue
    d=json.load(open(fn))
    if d.get('rebalanced'): print(fn,'already rebalanced'); continue
    d['rebalanced']=True
    for q in d['questions']:
        if q['n'] in sw:
            a,b=sw[q['n']];o=q['options'];t=q['traps']
            o[a],o[b]=o[b],o[a]
            ta,tb=t.get(a),t.get(b)
            t.pop(a,None);t.pop(b,None)
            if ta: t[b]=ta
            if tb: t[a]=tb
            q['answer']={a:b,b:a}.get(q['answer'],q['answer'])
            q['options']=dict(sorted(o.items()));q['traps']=dict(sorted(t.items()))
    json.dump(d,open(fn,'w'),indent=1)
