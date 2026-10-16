import json, urllib.request, urllib.parse
for doi in ['10.1016/j.solener.2011.04.027','10.1016/j.enbuild.2011.05.008','10.1016/j.solener.2009.07.013','10.1016/j.egypro.2012.11.127']:
    try:
        with urllib.request.urlopen('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''), timeout=20) as r:
            data=json.load(r)['message']
        s=f"{doi}\n{data.get('title',[''])[0]}\n{data.get('container-title',[''])[0] if data.get('container-title') else ''}\n{data.get('volume')} {data.get('issue')} {data.get('page')}\n".encode('utf-8','replace').decode('utf-8')
        print(s)
    except Exception as e:
        print(doi, 'ERR', repr(e))
