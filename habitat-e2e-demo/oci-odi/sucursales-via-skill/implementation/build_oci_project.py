"""Build the deterministic, parameter-free OCI Data Integration project."""
from __future__ import annotations
import hashlib, json, sys, uuid, zipfile
from pathlib import Path
NS = uuid.UUID("7e999f47-95fa-4fd2-9d91-2f83d9820edc")
def key(name): return str(uuid.uuid5(NS, name))
def main(target: Path):
    pname="HABITAT_SUCURSALES_VIA_SKILL"; pk=key("project")
    project={"key":pk,"name":pname,"identifier":pname,"description":"Portable Sucursales migration","modelType":"USER_PROJECT","modelVersion":"20200901","objectStatus":8,"objectVersion":1,"metadata":{"registryVersion":1}}
    meta={"aggregator":{"key":pk,"name":pname,"identifier":pname,"description":project["description"],"type":"USER_PROJECT"},"aggregatorKey":pk,"registryVersion":1}
    rk=key("run"); rest={"key":rk,"name":"RUN_SUCURSALES","identifier":"RUN_SUCURSALES","description":"Calls the supplied mock service.","modelType":"REST_TASK","modelVersion":"20230421","objectStatus":8,"objectVersion":1,"metadata":meta,"parameters":[],"typedExpressions":[],"configProviderDelegate":{},"inputPorts":[],"outputPorts":[],"isConcurrentAllowed":False,"apiCallMode":"SYNCHRONOUS","executeRestCallConfig":{"methodType":"POST","requestHeaders":{"Content-Type":"application/json"},"configValues":{"parentRef":{"parent":rk},"configParamValues":{"requestURL":{"stringValue":"http://mock-backend.invalid/v1/run"},"requestPayload":{"refValue":{"modelType":"JSON_TEXT","configValues":{"configParamValues":{"dataParam":{"stringValue":"{\"as_of_date\":\"2024-03-15\"}"}}}}}}}}}
    pipk=key("pipeline")
    def node(name, task=None):
      nk=key("node"+name); typ="TASK_OPERATOR" if task else ("START_OPERATOR" if name=="START" else "END_OPERATOR"); op={"key":key("op"+name),"name":name,"identifier":name,"modelType":typ,"modelVersion":"20210408","objectVersion":0,"inputPorts":[],"outputPorts":[],"parentRef":{"parent":nk}}
      if task: op.update({"task":{k:task[k] for k in ("key","name","identifier","modelType","modelVersion")}|{"inputPorts":[],"outputPorts":[],"parameters":[],"objectStatus":1,"objectVersion":1},"configProviderDelegate":{},"retryAttempts":0})
      return {"key":nk,"name":name,"identifier":name,"modelType":"FLOW_NODE","modelVersion":"20211031","objectStatus":1,"objectVersion":1,"parentRef":{"parent":pipk},"operator":op,"inputLinks":[],"outputLinks":[]}
    nodes=[node("START"),node("RUN",rest),node("END")]
    for a,b in zip(nodes,nodes[1:]):
      out,inn=key("out"+a["name"]),key("in"+b["name"]); a["outputLinks"].append({"key":out,"modelType":"OUTPUT_LINK","modelVersion":"20211031","parentRef":{"parent":a["key"]},"toLinks":[inn]}); b["inputLinks"].append({"key":inn,"modelType":"INPUT_LINK","modelVersion":"20211031","parentRef":{"parent":b["key"]},"fromLink":out})
    pipeline={"key":pipk,"name":"cargaArchivoExterno","identifier":"CARGA_ARCHIVO_EXTERNO","description":"Pentaho job orchestration.","modelType":"PIPELINE","modelVersion":"20220124","objectStatus":8,"objectVersion":1,"metadata":meta,"parameters":[],"nestedDepth":0,"nodes":nodes}
    tk=key("task"); task={"key":tk,"name":"EjecutarCargaArchivoExterno","identifier":"EJECUTAR_CARGA_ARCHIVO_EXTERNO","description":"Runnable Sucursales pipeline.","modelType":"PIPELINE_TASK","modelVersion":"20230421","objectStatus":8,"objectVersion":1,"metadata":meta,"parameters":[],"inputPorts":[],"outputPorts":[],"configProviderDelegate":{},"pipeline":{"key":pipk,"name":pipeline["name"],"identifier":pipeline["identifier"],"modelType":"PIPELINE","modelVersion":"20220124","nestedDepth":0,"nodes":[],"objectStatus":1,"objectVersion":1,"parameters":[]}}
    root=target/(pname+".project"); objs=root/"Objects"; objs.mkdir(parents=True,exist_ok=True); docs=[project,rest,pipeline,task]; paths=[]
    for doc in docs:
      name=f'{doc["modelType"]}_{doc["identifier"]}_{doc["key"]}.json'; (objs/name).write_text(json.dumps(doc,sort_keys=True,separators=(",",":"))); paths.append("/Objects/"+name)
    (root/"manifest.json").write_text(json.dumps({"version":"V1","exportedWorkspaceOcid":"","objectKeysProvidedForExport":[pk],"referencedObjectsList":[],"modelVersionMap":{"257":"20200901","788":"20220124","67176213":"20230421","17230268181":"20230421"},"objects":paths},sort_keys=True,separators=(",",":")))
    archive=target/(pname+".project.zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
      z.writestr(root.name+"/",""); z.writestr(root.name+"/Objects/","")
      for p in sorted(objs.glob("*.json")): z.write(p,root.name+"/Objects/"+p.name)
      z.write(root/"manifest.json",root.name+"/manifest.json")
    archive.with_suffix(archive.suffix+".sha256").write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+"  "+archive.name+"\n")
if __name__ == "__main__": main(Path(sys.argv[1]))
