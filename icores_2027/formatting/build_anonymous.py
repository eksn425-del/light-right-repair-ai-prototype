#!/usr/bin/env python3
"""Build the pinned official LLNCS skeleton in a private temporary TeX tree.
No vendor templates, package archives, or font files are copied to the repository.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, pathlib, shutil, subprocess, tempfile, time, urllib.request, zipfile
HERE = pathlib.Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def safe_extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            target=(destination / entry.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError('Unsafe archive entry')
        z.extractall(destination)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cache-dir',type=pathlib.Path,required=True)
    p.add_argument('--download',action='store_true',help='Retrieve missing public dependencies using pinned URLs')
    p.add_argument('--texmf-dist',type=pathlib.Path,default=pathlib.Path('/usr/share/texlive/texmf-dist'))
    p.add_argument('--out-dir',type=pathlib.Path,default=HERE)
    args=p.parse_args()
    cache=args.cache_dir.resolve(); cache.mkdir(parents=True,exist_ok=True)
    out=args.out_dir.resolve(); (out/'anonymous').mkdir(parents=True,exist_ok=True)
    (out/'evidence').mkdir(exist_ok=True); (out/'rendered').mkdir(exist_ok=True)
    manifest=json.loads((HERE/'TEMPLATE_MANIFEST.json').read_text())
    record={'started_utc':stamp(),'status':'RUNNING','commands':[], 'download_checks':[], 'source_sha256':sha(HERE/'anonymous/skeleton.tex'), 'bib_sha256':sha(HERE/'anonymous/references.bib')}
    work=pathlib.Path(tempfile.mkdtemp(prefix='icores-latex-'))
    def clean(s):
        # Compiler wraps path strings, so fold only wrapped absolute paths first.
        import re
        for path,token in [(str(work),'<BUILD>'),(str(cache),'<CACHE>'),(str(HERE),'<FORMATTING>'),(str(pathlib.Path.home()),'<HOME>')]:
            wrapped_pattern='\n?'.join(re.escape(ch) for ch in path)
            s=re.sub(wrapped_pattern,lambda match: token,s)
        return s
    def run(name,cmd,cwd=work,env=None):
        started=stamp(); tick=time.perf_counter()
        r=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/'evidence'/f'{name}.log').write_text(clean(r.stdout))
        record['commands'].append({'name':name,'command':[clean(str(x)) for x in cmd], 'started_utc':started,'finished_utc':stamp(),'elapsed_seconds':time.perf_counter()-tick,'exit_code':r.returncode,'log':f'evidence/{name}.log'})
        if r.returncode: raise RuntimeError(f'{name} exited {r.returncode}; see saved log')
        return r.stdout
    try:
        for item in manifest['downloads']:
            f=cache/item['cache_name']
            if not f.exists():
                if not args.download: raise FileNotFoundError(f'Missing {f.name}; use --download or provide the verified cache')
                with urllib.request.urlopen(item['url'],timeout=90) as response: f.write_bytes(response.read())
            actual=sha(f)
            if actual!=item['sha256']: raise ValueError(f'Hash mismatch for {f.name}; review the changed upstream asset')
            record['download_checks'].append({'name':f.name,'sha256':actual,'bytes':f.stat().st_size,'status':'PASS'})
        safe_extract(cache/'latex.zip',work/'vendor')
        for f in ['newtx.zip','kastrup.zip','tex-gyre.zip']: safe_extract(cache/f,work/'packages')
        for f in ['llncs.cls','splncs04.bst']: shutil.copy2(work/'vendor'/f,work/f)
        for f in ['skeleton.tex','references.bib']: shutil.copy2(HERE/'anonymous'/f,work/f)
        td=args.texmf_dist.resolve(); pk=work/'packages'; ntx=pk/'newtx'; gyre=pk/'tex-gyre'
        env=os.environ.copy()
        env.update({'TEXMF':str(td),'TEXMFVAR':str(work/'texmf-var'),'TEXMFCONFIG':str(work/'texmf-config'),'TEXMFHOME':str(work/'texmf-home'), 'TEXFORMATS':f'.:{work}//:', 'TEXINPUTS':f'.:{pk}/kastrup//:{ntx}/tex//:{td}/tex//:', 'TFMFONTS':f'{gyre}/tfm//:{ntx}/tfm//:{td}/fonts/tfm//:', 'VFFONTS':f'{gyre}/vf//:{ntx}/vf//:{td}/fonts/vf//:', 'T1FONTS':f'{gyre}/type1//:{ntx}/type1//:{td}/fonts/type1//:', 'ENCFONTS':f'{gyre}/enc//:{ntx}/enc//:{td}/fonts/enc//:', 'TEXFONTMAPS':f'.:{ntx}/map//:{td}/fonts/map//:', 'TZ':'UTC'})
        maps=[ntx/'map/newtx.map', gyre/'map/qtm.map', td/'fonts/map/dvips/amsfonts/cm.map',td/'fonts/map/dvips/amsfonts/latxfont.map']
        data='\n'.join(f.read_text() for f in maps)
        data+='\n'+'\n'.join(s for s in (td/'fonts/map/dvips/txfonts/txfonts.map').read_text().splitlines() if s.startswith('t1xtt '))+'\n'
        (work/'pdftex.map').write_text(data)
        record['engine_version']=run('engine-version',['pdflatex','--version'],env=env).splitlines()[0]
        run('format-generation',['pdftex','-ini','-etex','-jobname=pdflatex','-progname=pdflatex','-interaction=nonstopmode',r'\input latex.ltx'],env=env)
        command=['pdflatex','-output-format=pdf','-no-shell-escape','-halt-on-error','-interaction=nonstopmode']
        run('binhex-generation',command+['binhex.ins'],cwd=pk/'kastrup',env=env)
        run('pdflatex-pass-1',command+['skeleton.tex'],env=env)
        run('bibtex',['bibtex','skeleton'],env=env)
        run('pdflatex-pass-2',command+['skeleton.tex'],env=env)
        run('pdflatex-pass-3',command+['skeleton.tex'],env=env)
        shutil.copy2(work/'skeleton.pdf',out/'anonymous/skeleton.pdf')
        shutil.copy2(work/'skeleton.bbl',out/'anonymous/skeleton.bbl')
        shutil.copy2(work/'DescriptionTexts.txt',out/'anonymous/DescriptionTexts.txt')
        (out/'evidence/final-tex.log').write_text(clean((work/'skeleton.log').read_text()))
        run('pdfinfo',['pdfinfo','skeleton.pdf'],env=env)
        run('pdffonts',['pdffonts','skeleton.pdf'],env=env)
        run('pdftotext',['pdftotext','skeleton.pdf','skeleton.txt'],env=env)
        (out/'evidence/extracted-text.txt').write_text((work/'skeleton.txt').read_text())
        run('render',['pdftoppm','-scale-to','1800','-png','skeleton.pdf','page'],env=env)
        for f in work.glob('page-*.png'):shutil.copy2(f,out/'rendered'/f.name)
        record['status']='BUILT_PENDING_VISUAL_AND_ANONYMITY_QA'
        record['pdf_sha256']=sha(out/'anonymous/skeleton.pdf')
        record['template_class_sha256']=sha(work/'llncs.cls')
        record['bibliography_style_sha256']=sha(work/'splncs04.bst')
    except Exception as e:
        record['status']='FAILED';record['error']=clean(str(e));raise
    finally:
        record['finished_utc']=stamp()
        (out/'evidence/BUILD_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
        # Keep temporary work for diagnostic inspection. Never release its fonts or paths.
    print(json.dumps({'status':record['status'],'pdf_sha256':record.get('pdf_sha256')}))

if __name__=='__main__': main()
