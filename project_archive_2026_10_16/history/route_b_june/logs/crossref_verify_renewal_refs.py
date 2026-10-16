import json, urllib.request, urllib.parse
for doi in ['10.1016/j.landusepol.2021.105571','10.1038/s41598-024-54883-3','10.3390/land13111806','10.3389/frsc.2023.913500']:
    try:
        with urllib.request.urlopen('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''), timeout=20) as r:
            data=json.load(r)['message']
        print('\n',doi)
        print(data.get('title',[''])[0])
        print(data.get('container-title',[''])[0] if data.get('container-title') else '')
        print(data.get('volume'), data.get('issue'), data.get('page'))
        print('; '.join((a.get('family','')+', '+a.get('given','')).strip(', ') for a in data.get('author',[])[:5]).encode('utf-8','replace').decode('utf-8'))
    except Exception as e:
        print(doi, 'ERR', repr(e))
