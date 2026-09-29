from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import csv, html, io, json, os, subprocess, threading
BASE=Path(__file__).resolve().parent
CONFIG=json.loads((BASE/'app_config.json').read_text())
PORT=int(os.environ.get('PORT', CONFIG['port']))
RUNTIME=BASE/'runtime'; RUNTIME.mkdir(exist_ok=True)
LOCK=threading.Lock()
LATEST=None
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def allowed(self): return self.headers.get('Host','') in {f'127.0.0.1:{PORT}',f'localhost:{PORT}'}
    def send(self,status,body,kind='application/json',filename=None):
        if not isinstance(body,bytes): body=body.encode('utf-8')
        self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('X-Frame-Options','DENY')
        if filename: self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
        self.end_headers(); self.wfile.write(body)
    def fail(self,status,message): self.send(status,json.dumps({'error':message}))
    def do_GET(self):
        if not self.allowed(): return self.fail(403,'Use the local application URL.')
        if self.path=='/':
            source=(BASE/'web/index.html').read_text()
            return self.send(200,source.replace('__CONFIG__',json.dumps({**CONFIG,'defaultPath':str(BASE/CONFIG['fixture'])})), 'text/html')
        if self.path=='/health': return self.send(200,json.dumps({'status':'ok','engine':CONFIG['engine']}))
        if self.path.startswith('/download/'):
            with LOCK: result=LATEST
            if result is None: return self.fail(404,'Run an analysis first.')
            fmt=self.path.rsplit('/',1)[-1]
            if fmt=='json': return self.send(200,json.dumps(result,indent=2,ensure_ascii=False),'application/json',CONFIG['engine']+'-report.json')
            rows=result.get('issues',result.get('records',[]))
            fields=['severity','code','path','detail'] if CONFIG['kind']=='paths' else ['line','timestamp','level','format','message']
            if fmt=='csv':
                output=io.StringIO(); writer=csv.DictWriter(output,fieldnames=fields); writer.writeheader()
                for row in rows:
                    safe={key:("'"+str(row.get(key,'')) if str(row.get(key,'')).startswith(('=','+','-','@','\t','\r')) else row.get(key,'')) for key in fields}; writer.writerow(safe)
                return self.send(200,output.getvalue(),'text/csv',CONFIG['engine']+'-report.csv')
            if fmt=='html':
                head=''.join('<th>'+html.escape(key)+'</th>' for key in fields)
                body=''.join('<tr>'+''.join('<td>'+html.escape(str(row.get(key,'')))+'</td>' for key in fields)+'</tr>' for row in rows)
                summary=html.escape(json.dumps({key:value for key,value in result.items() if key not in ('issues','records','diagnostics')},indent=2))
                report='<!doctype html><meta charset="utf-8"><title>'+CONFIG['name']+' report</title><style>body{font:15px system-ui;margin:48px;color:#122b37}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd9df;padding:10px;text-align:left;vertical-align:top}pre{white-space:pre-wrap;background:#eef4f5;padding:20px}</style><h1>'+CONFIG['name']+' · analysis report</h1><p>Independent local tool. No files were changed. See source documentation for coverage limits.</p><pre>'+summary+'</pre><table><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>'
                return self.send(200,report,'text/html',CONFIG['engine']+'-report.html')
        self.fail(404,'Not found.')
    def do_POST(self):
        global LATEST
        if not self.allowed() or self.headers.get('Origin','') not in {f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}'}: return self.fail(403,'Requests must originate from the local application.')
        if self.path!='/analyze': return self.fail(404,'Not found.')
        if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.fail(415,'JSON required.')
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=9*1024*1024: return self.fail(413,'Request exceeds the 9 MiB limit.')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError('A JSON object is required.')
            path=data.get('path','')
            if not isinstance(path,str) or len(path)>8192: raise ValueError('Invalid input path.')
            with LOCK:
                if CONFIG['kind']=='logs' and data.get('content') is not None:
                    content=data['content']
                    if not isinstance(content,str) or len(content.encode('utf-8'))>8*1024*1024: raise ValueError('Upload a UTF-8 log of at most 8 MiB.')
                    upload=RUNTIME/'uploaded.log'; upload.write_text(content); path=str(upload)
                if not path.strip(): raise ValueError('Enter an input path.')
                inputpath=Path(path).expanduser().resolve()
                if CONFIG['kind']=='paths' and not inputpath.is_dir(): raise ValueError('This directory does not exist or is not accessible.')
                if CONFIG['kind']=='logs' and (not inputpath.is_file() or inputpath.stat().st_size>256*1024*1024): raise ValueError('Select a regular log file of at most 256 MiB.')
                command=[str(RUNTIME/CONFIG['engine']),str(inputpath)]
                if CONFIG['kind']=='logs':
                    minimum=data.get('minimum','DEBUG'); query=data.get('query',''); year=data.get('year',2026)
                    if minimum not in ('DEBUG','INFO','WARNING','ERROR','CRITICAL') or not isinstance(query,str) or len(query)>256: raise ValueError('Invalid log filter.')
                    command += [minimum,query,str(year)]
                completed=subprocess.run(command,capture_output=True,text=True,timeout=30)
                if completed.returncode: raise ValueError(completed.stderr.strip() or 'The engine could not process this input.')
                result=json.loads(completed.stdout); (RUNTIME/'latest-report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)); LATEST=result
            self.send(200,json.dumps(result,ensure_ascii=False))
        except (ValueError,TypeError,OSError,UnicodeError) as error: self.fail(400,str(error))
        except subprocess.TimeoutExpired: self.fail(408,'Analysis exceeded 30 seconds. Select a smaller input.')
if __name__=='__main__':
    if os.name != 'nt':
        from generate_fixture import generate_fixture
        generate_fixture()
    print(f"{CONFIG['name']} ready at http://127.0.0.1:{PORT}",flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
