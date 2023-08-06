
import vytools.utils as utils
import vytools.stage
from vytools.config import ITEMS
from vytools.composerun import run
import yaml, json, os, shutil, copy, re
import cerberus

KEYSRULES = '[a-zA-Z0-9_]+'
SCHEMA = utils.BASE_SCHEMA.copy()
SCHEMA.update({
  'thingtype':{'type':'string', 'allowed':['compose']},
  'ui':{'type':'string', 'maxlength': 64, 'required': False},
  'subcompose':{'type':'list',
    'schema': {
      'type': 'dict',
      'schema': {
        'name': {'type': 'string', 'maxlength': 64},
        'calibration':{'type': 'dict', 'required':False}
      }
    }
  },
  'anchors':{'type': 'dict', 'required': False, 'keysrules': {'type': 'string', 'regex': KEYSRULES}}
})
VALIDATE = cerberus.Validator(SCHEMA)

def parse(name, pth, items=None):
  if items is None: items = vytools.ITEMS
  item = {
    'name':name,
    'thingtype':'compose',
    'depends_on':[],
    'path':pth,
    'loaded':True
  }
  itemx = {'ui':None, 'subcompose':[], 'anchors':{}}
  try:
    with open(pth,'r') as r:
      content = yaml.safe_load(r.read())
      xvy = content.get('x-vy',{})
      itemx.update((k, xvy[k]) for k in itemx.keys() & xvy.keys())
      if itemx['ui'] is None: del itemx['ui']
      item.update(itemx)
    return utils._add_item(item, items, VALIDATE)
  except Exception as exc:
    vytools.printer.print_fail('Failed to parse/load compose file "{n}" at "{p}":\n    {e}'.format(n=name,p=pth,e=exc))
    return False
ANCHORTHINGTYPES = ['stage','definition','vydir','repo']
ANCHORTYPES = ['definition','argument','artifact','stage','vydir','repo','directory','file']

def find_all(items, contextpaths=None):
  success = utils.search_all(r'(.+)\.compose\.y[a]*ml', parse, items, contextpaths=contextpaths)
  for (type_name, item) in items.items():
    if type_name.startswith('compose:'):
      successi = True
      item['depends_on'] = []
      for e in item['anchors']:
        atype = [a for a in ANCHORTYPES if item['anchors'][e].startswith(a+':')]
        if len(atype) == 1 and atype[0] in ANCHORTHINGTYPES: 
          successi &= utils._check_add(item['anchors'][e], atype[0], item, items, type_name)
        elif len(atype) != 1:
          successi = False
          vytools.printer.print_fail('Unknown anchor type "{t} {v}" in {n}. Should be one of: {a}'.format(t=e,v=item['anchors'][e],n=type_name,a=','.join(ANCHORTYPES)))
      if 'ui' in item:
        successi &= utils._check_add(item['ui'].split('/')[0], 'vydir', item, items, type_name)
      for e in item['subcompose']:
        successi &= utils._check_add(e['name'], 'compose', item, items, type_name)
      success &= successi
      item['loaded'] &= successi
      utils._check_self_dependency(type_name, item)
      if not item['loaded']:
        vytools.printer.print_fail('Failed to interpret/link compose {c}'.format(c=type_name))
  return success

def _extract_anchors(item, items, object_mods, built, build_level, eppath, propagation):
  this_anchors = copy.deepcopy(item.get('anchors',{}))
  for tag in [k for atype in ANCHORTYPES for k,v in this_anchors.items() if v.startswith(atype+':')]: # SORTED TO ENSURE ORDER IS DEFINITION, ARGUMENT, STAGE, ARTIFACT
    val = this_anchors[tag]
    if val.startswith('definition:'):
      obj = propagation['anchors'][tag] if tag in propagation['anchors'] else None
      obj_mods = object_mods[tag] if object_mods and tag in object_mods else None
      if obj is not None:
        propagation['anchors'][tag],deplist_ = vytools.object.expand(obj, val, items, object_mods=obj_mods)
        propagation['dependencies'] += [d for d in deplist_ if d not in propagation['dependencies']]
        if propagation['anchors'][tag] is None:
          vytools.printer.print_fail('Failed to expand anchor "{}" in compose "{}"'.format(tag, item['name']))
          return False
      if tag not in propagation['anchors']:
        vytools.printer.print_warn('Anchor "{}" was not set for use in compose "{}"'.format(tag, item['name']))
    elif val.startswith('argument:'):
      if tag not in propagation['anchors']: 
        propagation['anchors'][tag] = val.replace('argument:','',1)
    elif val.startswith('stage:'):
      buildstage = propagation['anchors'][tag] if tag in propagation['anchors'] else val
      if buildstage.startswith('stage:'):
        tagged = vytools.stage.build([buildstage], items, propagation['anchors'], built, build_level, jobpath=eppath)
        if tagged == False: return False
        for v in tagged.values():
          propagation['stage_versions'] += [sv for sv in v['stage_versions'] if sv not in propagation['stage_versions']]
        propagation['anchors'][tag] = tagged[buildstage]['tag']
      else:
        propagation['anchors'][tag] = buildstage
    elif any([val.startswith(v+':') for v in ['directory','file','artifact','vydir','repo']]):
      if tag not in propagation['anchors']:
        # propagation['anchors'][tag] = val
        splitname = val.split(':',1)
        arttyp = splitname[0]
        artname = splitname[-1]
        if len(splitname) == 2 and len(artname) > 0:
          if arttyp in ['vydir','repo']:
            artname = vytools.utils.get_thing_path(val, items)
            if not artname:
              return False
          propagation['anchors'][tag] = artname
          if build_level == -1 and '..' not in artname and eppath and os.path.exists(eppath):
            artifactpath = os.path.join(eppath, artname)
            if arttyp in ['artifact','file']:
              if os.path.isdir(artifactpath):
                vytools.printer.print_fail('The {} "{}" already exists as a directory. You will need to delete it to continue with this compose file'.format(arttyp,artifactpath))
                return False
              with open(artifactpath,'w') as w: w.write('')
              os.chmod(artifactpath, 0o666)
            elif arttyp == 'directory':
              os.makedirs(artifactpath,exist_ok=True)
  return True

def build(rootcompose, items=None, anchors=None, built=None, build_level=1, object_mods=None, eppath=None, label=None):
  if items is None: items = ITEMS
  if not vytools.utils.ok_dependency_loading('build', rootcompose, items):
    return False

  if built is None: built = []
  if label is None: label = rootcompose.replace('compose:','') 
  if not utils.exists([rootcompose], items):
    return False
  elif not rootcompose.startswith('compose:'):
    vytools.printer.print_fail('Item {} is not a compose file'.format(rootcompose))
    return False

  propagation = {
    'command':[],
    'stage_versions':[],
    'dependencies':[rootcompose],
    'anchors':{} if anchors is None else copy.deepcopy(anchors)
  }
  item = items[rootcompose]
  if not _extract_anchors(item, items, object_mods, built, build_level, eppath, propagation):
    return False
  for sa in item['subcompose']:
    subname = sa['name']
    sublabel = label + '.'+subname.replace('compose:','')
    subcmds = build(subname, items=items, anchors=propagation['anchors'], built=built,
                            build_level=build_level, object_mods=object_mods, eppath=eppath, label=sublabel)
    if subcmds == False: return False
    propagation['command'] += subcmds['command']
    for k in ['dependencies','stage_versions']:
      propagation[k] += [d for d in subcmds[k] if d not in propagation[k]]
    propagation['anchors'].update(subcmds['anchors'])

  if build_level == -1:
    compose_file_name = label + '.yaml'
    compose_pth = item['path']
    composition = {}
    with open(compose_pth,'r') as r:
      composition = yaml.safe_load(r.read())
    if 'x-vy' in composition: del composition['x-vy']
    ok = _recursiv_replace(composition, propagation['anchors'], eppath, label)
    if not ok:
      return False
    
    oktowrite = '..' not in compose_file_name and eppath and os.path.exists(eppath)
    if oktowrite:
      with open(os.path.join(eppath, compose_file_name),'w') as w:
        w.write(yaml.safe_dump(composition))
      propagation['command'] += ['-f',compose_file_name]
  
  propagation['stage_versions'] = sorted(propagation['stage_versions'])
  return propagation

def _prefx(key,char,replkeys):
  return [r for r in replkeys if key.startswith(r+char)]

def stripkey(key):
  if key.startswith('$'):
    key = key[1:]
    if key.startswith('{'):
      key = ''.join(key[1:].split('}',1))
  return key

def _replkeysf(key, repl, eppath):
  replkeys = [str(i) for i in len(repl)] if type(repl) == list else \
    (repl.keys() if type(repl) == dict else [])
  if key in replkeys:
    return repl[key]
  else:
    if type(repl) == dict:
      for kkey in replkeys:
        if key.startswith(kkey+':') or key.startswith(kkey+'/'):
          return key.replace(kkey,repl[kkey],1)
  for x in ['.','>']:
    prefx = _prefx(key,x,replkeys)
    if len(prefx) == 1:
      repl_ = repl[prefx[0]]
      key_ = stripkey(key.replace(prefx[0]+x,'',1))
      if x == '.':
        return _replkeysf(key_, repl_, eppath)
      elif x == '>' and eppath and os.path.exists(eppath) and '..' not in key_:
        path = os.path.join(eppath, key_)
        if os.path.isdir(path):
          raise Exception('Path "{}" is referenced in the compose as if it were a file, but it is a directory'.format(path))
        with open(path,'w') as w:
          if key.endswith('.json'):
            w.write(json.dumps(repl_))
          elif key.endswith('.yaml'):
            w.write(yaml.safe_dump(repl_))
        return path

def _recursiv_replace(obj, repl, eppath, cfile):
  if type(obj) == dict:
    ks = obj.keys()
  elif type(obj) == list:
    ks = range(len(obj))
  else:
    return True
  for k in ks:
    if type(obj[k]) == str:
      # Find environment variables e.g. ${a} $a  $a.b.c  ${a.b.c}
      keys = re.findall(r'\$[\{]?[a-zA-Z0-9_\.\>]+[\}]?',obj[k],re.I)
      for key in keys:
        try:
          val = _replkeysf(key.strip('$').strip('{').strip('}'), repl, eppath)
          if val: obj[k] = obj[k].replace(key, str(val))
        except Exception as exc:
          vytools.printer.print_fail('Failed to substitute anchor {} in vy compose "{}". {}'.format(key,cfile,exc))
          return False
    elif type(obj[k]) in [list,dict]:
      if not _recursiv_replace(obj[k], repl, eppath, cfile):
        return False
  return True

def artifact_paths(compose_name, items, eppath):
  artifacts = {}
  def get_artifacts(i,artifacts):
    if i in items:
      for tag,val in items[i].get('anchors',{}).items():
        pth = os.path.join(eppath,val.replace('artifact:','',1))
        if val.startswith('artifact:') and '..' not in val and os.path.exists(pth):
          artifacts[tag] = pth
      for sa in items[i]['subcompose']: get_artifacts(sa['name'],artifacts)
  if eppath and os.path.exists(eppath):
    get_artifacts(compose_name,artifacts)
  return artifacts
