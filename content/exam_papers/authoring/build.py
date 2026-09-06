import json,sys
tpl=open('player_template.html').read()
for p in sys.argv[1:]:
    paper=json.load(open(p));out=tpl.replace('__PAPER_JSON__',json.dumps(paper).replace('</script>','<\\/script>'))
    fn=f"/mnt/user-data/outputs/telos_{paper['paper_code'].lower().replace('-','_')}.html";open(fn,'w').write(out);print('built',fn)
