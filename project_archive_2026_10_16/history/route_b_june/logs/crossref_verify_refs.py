import json, urllib.request, urllib.parse
DOIS = [
'10.1016/j.rser.2014.06.007',
'10.1016/j.enbuild.2004.01.009',
'10.3390/buildings12040393',
'10.1016/j.enbuild.2004.10.010',
'10.1016/j.rser.2015.12.073',
'10.1016/j.autcon.2020.103518',
'10.26868/25222708.2013.2499',
'10.1145/192161.192286',
'10.1016/S0378-7788(01)00058-5',
'10.1016/j.apenergy.2013.08.061',
'10.1016/j.solener.2015.12.020',
'10.1016/j.rser.2013.11.036',
'10.1016/j.autcon.2015.02.011',
'10.1016/j.progress.2010.12.001',
'10.1016/j.buildenv.2024.112147',
'10.1016/j.foar.2022.02.001',
'10.1016/S0378-7788(02)00079-8',
'10.3390/en13133302',
'10.1016/j.solener.2011.04.017',
'10.1016/j.buildenv.2021.107762',
]
for doi in DOIS:
    url='https://api.crossref.org/works/'+urllib.parse.quote(doi, safe='')
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data=json.load(r)['message']
        print('\nDOI', doi)
        print('title:', data.get('title',[''])[0])
        print('container:', data.get('container-title',[''])[0] if data.get('container-title') else '')
        print('year:', data.get('published-print', data.get('published-online', data.get('issued',{}))).get('date-parts',[[None]])[0][0])
        print('volume:', data.get('volume'), 'issue:', data.get('issue'), 'page:', data.get('page'))
        print('author:', '; '.join((a.get('family','')+', '+a.get('given','')).strip(', ') for a in data.get('author',[])[:5]))
    except Exception as e:
        print('\nDOI', doi, 'ERROR', e)
