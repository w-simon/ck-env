#
# Collective Knowledge (Grigori's misc research functions)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# Replace string in file

def replace_string_in_file(i):
    """
    Input:  {
              file
              (file_out)  - if !='', use this file for output, otherwise overwrite original one!
              string      - string to replace
              replacement - replacement string
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              (updated)    - if 'yes', files was updated
            }

    """

    import copy

    o=i.get('out','')

    fin=i['file']
    s1=i['string']
    s2=i['replacement']

    fout=i.get('file_out','')
    if fout=='': fout=fin

    rx=ck.load_text_file({'text_file':fin})
    if rx['return']>0: return rx

    s=rx['string']
    sx=s.replace(s1,s2)

    r={'return':0, 'updated':'no'}

    if s!=sx or fin!=fout:
       r=ck.save_text_file({'text_file':fout, 'string':sx})
       r['updated']='yes'

    return r

##############################################################################
# updating json file

def refresh_json(i):
    """
    Input:  {
              json_file     - file with json
              (output_file) - if !='' use this file for output instead of rewriting original file
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    jf=i['json_file']

    of=i.get('output_file','')
    if of=='': of=jf

    r=ck.load_json_file({'json_file':jf})
    if r['return']>0: return r

    d=r['dict']

    return ck.save_json_to_file({'json_file':of, 'dict':d, 'sort_keys':'yes'})

##############################################################################
# process all files recursively using some action

def process_all_files_recursively(i):
    """
    Input:  {
               (path)     - starting path (or current)
               (pattern)  - file pattern
               (cmd)      - perform action with a file

               (ck)       - call CK access
               (file_key) - substitute this key in 'ck' with file name with full path
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    o=i.get('out','')

    p=i.get('path','')
    if p=='':
       p=os.getcwd()

    cka=i.get('ck',{})
    fk=i.get('file_key','')

    pat=i.get('pattern','')

    if o=='con':
       ck.out('')
       x=''
       if pat!='': x=' ('+pat+')'
       ck.out('Obtaining list of all files'+x+'. May take some time ...')

    r=ck.list_all_files({'path':p, 'pattern':pat, 'all':'yes'})
    if r['return']>0: return r

    lst=r['list']

    for qq in lst:
        if p=='': q=qq
        else:     q=os.path.join(p,qq)

        if len(cka)>0:
           if fk!='':
              cka[fk]=q

           if o=='con':
              ck.out('  '+q)

           r=ck.access(cka)
           if r['return']>0: return r

    return {'return':0, 'list':lst}

##############################################################################
# merge dictionaries in 2 files

def merge_dicts(i):
    """
    Input:  {
              file1   - dict1
              file2   - dict2
              (file3) - output to this file. If empty use file1
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    f1=i.get('file1','')
    f2=i.get('file2','')

    if f1=='' or f2=='':
       return {'return':1, 'error':'--file1 and --file2 should be specified'}

    fo=i.get('file3','')
    if fo=='': fo=f1

    r=ck.load_json_file({'json_file':f1})
    if r['return']>0: return r
    d1=r['dict']

    r=ck.load_json_file({'json_file':f2})
    if r['return']>0: return r
    d2=r['dict']

    if type(d1)==list and type(d2)==list:
       for q in d2:
           d1.append(q)
    else:
       r=ck.merge_dicts({'dict1':d1, 'dict2':d2})
       if r['return']>0: return r
       d1=r['dict1']

    r=ck.save_json_to_file({'json_file':fo, 'dict':d1})
    if r['return']>0: return r

    return {'return':0}

##############################################################################
# sort JSON file

def sort_json_file(i):
    """
    Input:  {
              json_file     - file with json
              (output_file) - if !='' use this file for output instead of rewriting original file
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    return refresh_json(i)

##############################################################################
# add key to meta/files of different entries

def add_key(i):
    """
    Input:  {
              data            - CID of entries to update (can be wild cards)
              (tags)          - prune entries by tags

              key             - key in flat format
              value           - value

              (ignore_update) - ignore update info in entries
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    data=i.get('data','')
    if data=='':
       return {'return':1, 'error':'"data" is not defined'}

    tags=i.get('tags','')

    key=i.get('key','')
    if key=='':
       return {'return':1, 'error':'"key" is not defined'}

    value=i.get('value','')
    if value=='':
       return {'return':1, 'error':'"value" is not defined'}

    iu=i.get('ignore_update','')

    # Search entries
    r=ck.access({'action':'search',
                 'cid':data,
                 'tags':tags})
    if r['return']>0: return r
    lst=r['lst']

    llst=len(lst)

    if llst>0 and o=='con':
       ck.out('Updating '+str(llst)+' entries ...')
       ck.out('')

    # Iterate over entries
    for l in lst:
        ruid=l['repo_uid']
        ruoa=l['repo_uoa']
        muid=l['module_uid']
        muoa=l['module_uoa']
        duid=l['data_uid']
        duoa=l['data_uoa']

        if o=='con':
           ck.out('* '+ruoa+':'+muoa+':'+duoa)

        # Load meta
        r=ck.access({'action':'load',
                     'repo_uoa':ruid,
                     'module_uoa':muid,
                     'data_uoa':duid})
        if r['return']>0: return r
        d=r['dict']

        # Updating dict
        r=ck.set_by_flat_key({'dict':d,
                              'key':key,
                              'value':value})
        if r['return']>0: return r

        # Store meta
        r=ck.access({'action':'update',
                     'repo_uoa':ruid,
                     'module_uoa':muid,
                     'data_uoa':duid,
                     'dict':d,
                     'substitute':'yes',
                     'ignore_update':iu})
        if r['return']>0: return r

    return {'return':0}

##############################################################################
# internal file to ignore files/directories from templates

def prepare_entry_template_ignore_files(dr, files):
    lst=['.cm','tmp']
    return lst

##############################################################################
# prepare template for a given entry
# (trying to unify templates for CK when adding program, soft, package, program, dataset, etc)

def prepare_entry_template(i):
    """
    Input:  {
              original_module_uoa - add template for this original module 
              (template)          - force using this template
              (skip_custom_note)  - if 'yes', do not print note about customization at the end

              all params from "ck add" function
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import shutil

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    omuoa=i.get('original_module_uoa','')
    ruoa=i.get('repo_uoa','')
    duoa=i.get('data_uoa','')

    # Search templates
    tuoa=i.get('template','')
    truoa=i.get('template_repo','')

    if tuoa=='':
       lst=[{'data_uid':'', 'data_uoa':'', 'repo_uid':'', 'info':{'data_name':'Empty entry'}, 'meta':{'sort':9999}}] # Add it to the end

       if tuoa=='':
          if oo=='con':
             ck.out('Searching for templates ...')

          ii={'action':'search',
              'module_uoa':omuoa,
              'data_uoa':tuoa,
              'add_info':'yes',
              'search_dict':{'template':'yes'}}
          r=ck.access(ii)
          if r['return']>0: return r

          lst+=r['lst']

       if len(lst)==1:
          c=lst[0]

       # Make selection
       if oo=='con' and len(lst)>1:
          ck.out('')

          r=select_uoa({'text':'Select template for the new entry', 
                        'choices':lst})
          if r['return']>0: return r

          c=r['choice']

          ck.out('')

       tuoa=c['data_uid']
       truoa=c['repo_uid']

    d=i.get('dict',{})

    if tuoa!='':
       # Attempt to load entry
       ii={'action':'load',
           'module_uoa':omuoa,
           'data_uoa':tuoa,
           'repo_uoa':truoa}
       r=ck.access(ii)
       if r['return']>0: return r

       p=os.path.realpath(r['path'])

       d.update(r['dict'])

    i['action']='add'
    i['module_uoa']=omuoa

    i['common_func']='yes'
    i['sort_keys']='yes'

    i['dict']=d
    
    r=ck.access(i)
    if r['return']>0: return r

    pnew=r['path']

    # Copy files to a new entry if template
    if tuoa!='':
       d=os.listdir(p)
       for f in d:
           if f!='.cm' and not f.endswith('.pyc') and 'tmp' not in f:
              porig2=os.path.join(p,f)
              pnew2=os.path.join(pnew,f)

              try:

                 if os.path.isdir(porig2):
                    shutil.copytree(porig2, pnew2, ignore=shutil.ignore_patterns('.cm', '*tmp*', '*.pyc'))
                 else:
                    shutil.copyfile(porig2, pnew2)

              except IOError as e: 
                 return {'return':1, 'error':'problem copying files from template ('+str(e)+')'}

    # Print info about customization
    if i.get('skip_custom_note', '')!='yes' and oo=='con':
       ck.out('')
       ck.out('You can continue customizing this entry (tags, dependencies, etc):')
       ck.out('')
       ck.out(' * JSON meta:   '+os.path.join(pnew, ck.cfg['subdir_ck_ext'], ck.cfg['file_meta']))
       ck.out(' * Other files: '+pnew)

    return r

##############################################################################
# Universal string selector.
#
# Given an ordered list of options (strings)

def select_string(i):
    """
    Input:  {
                options         - an ordered list of strings to select from
                (question)      - the question to ask
                (default)       - default selection
            }

    Output: {
                return          - return code =  0, if successful
                                              >  0, if error
                (error)         - error text if return > 0
                selected_index  - an index < len(options)
            }

    """

    question    = i.get('question', 'Please select from the options above')
    options     = i.get('options')
    default     = i.get('default', None)
    num_options = len(options)

    if not options or len(options)==0:
        return {'return': 1, 'error': 'No options provided - please check the docstring for correct syntax'}

    for i in range(num_options):
        if not isinstance(options[i], list):
            options[i] = [ options[i] ]

        ck.out("{:>2}) {}".format(i, options[i][0]))
        for extra_line in options[i][1:]:
            ck.out('    {}'.format(extra_line))
        ck.out('')

    inp_adict = ck.inp({'text': "{}{}: ".format(question, ' [ hit return for "{}" ]'.format(default) if len(default) else '')})

    response = inp_adict['string']

    if response=='' and default!=None:
        response = default

        if response=='':    # since it was a default, it was an allowed scenario (not having a selected_index)
            return {'return':0, 'response': response}

    try:    # try to convert into int() and see if it works
        selected_index = int(response)
        if selected_index >= num_options:
            return {'return': 2, 'response': response, 'error': 'Selected index out of range [0..{}]'.format(num_options-1)}
    except:
        num_matches = 0
        for i in range(num_options):
            if response in options[i][0]:
                selected_index = i
                num_matches += 1

        if num_matches!=1:
            return {'return': 3, 'response': response, 'error': 'Instead of 1 unique match there were {}'.format(num_matches)}

    #ck.out("You selected [{:02}]".format(selected_index))

    return {'return':0, 'response': response, 'selected_index': selected_index}

##############################################################################
# Universal UOA selector (improved version forked 
# from ck-autotuning:module:choice and ck.kernel)

def select_uoa(i):
    """
    Input:  {
              choices      - list from search function
              (text)       - selection text
              (skip_enter) - if 'yes', do not select 0 when user presses Enter
              (skip_sort)  - if 'yes', do not sort array
            }

    Output: {
              return  - return code =  0, if successful
                                    >  0, if error
              (error) - error text if return > 0
              choice  - {dict of selection from lst}
            }

    """

    se=i.get('skip_enter','')

    lst=i.get('choices',[])

    # Prepare data_name and then data_uoa

    if i.get('skip_sort','')!='yes':
       slst=sorted(lst, key=lambda v: (v.get('meta',{}).get('sort',0), v.get('info',{}).get('data_name',''), v['data_uoa']))
    else:
       slst=lst

    array={}
    n=0

    for x in slst:
        sn=str(n)
        array[sn]=x

        duoa=x['data_uoa']
        name=x.get('info',{}).get('data_name','')
        if name=='': name=duoa

        s=sn+') '+name
        if duoa!='': s+=' (--template='+duoa+')'

        ck.out(s)

        n+=1

    ck.out('')

    text=i.get('text','')
    if text=='': text='Select UOA'

    s=text
    if se!='yes': s+=' (or press Enter for 0)'
    s+=': '

    rx=ck.inp({'text':s})
    y=rx['string'].strip()

    if y=='' and se!='yes': y='0' 

    if y not in array:
       return {'return':1, 'error':'number is not recognized'}

    return {'return':0, 'choice':array[y]}

##############################################################################
# list CK kernel functions

def list_kernel_functions(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')

    of=i.get('out_file','')
    if of!='':
       xof=os.path.splitext(of)

    html=False
    if o=='html' or i.get('web','')=='yes':
       html=True

    h=''
    h2=''
    hcfg=''
    if i.get('new','')=='yes':
       ii=copy.deepcopy(i)
       ii['ck_title']='Shared CK kernel functions and configurations'
       r=preload_html_for_lists(ii)
       if r['return']>0: return r

       h=r['html_start']+'\n'
       h2=r['html_stop']+'\n'

       hcfg=h

    p=ck.work['env_root'] # Internal CK path

    pk=os.path.join(p, 'ck', 'kernel.py')
    if not os.path.isfile(pk):
       return {'return':1, 'error':'Can\'t find kernel in '+pk}

    r=ck.load_text_file({'text_file':pk, 'split_to_list':'yes'})
    if r['return']>0: return r

    l=r['lst']

    funcs={}
    desc=[]
    ld=0
    target=''

    cfg=[]
    cfg_start=False

    ll=len(l)
    for k in range(0, ll):
        x=l[k]

        if x.startswith('cfg={'):
           cfg_start=True

        if cfg_start:
           cfg.append(x)
           if x=='    }':
              cfg_start=False

        if x.startswith('##################'):
           desc=[]
           ld=k

        if x.startswith('# '):
           x1=x[2:].strip()
           if x1.startswith('TARGET: '):
              target=x1[8:]
           else:
              desc.append(x1)

        if x.startswith('def '):
           j1=x.find('(')
           j2=x.find(')', j1+1)
           j3=x.find(':')

           fn=x[4:j1]
           i=x[j1+1:j2]
           rem=x[j3+1:]

           api=[]

           k+=1

           found=False
           first=False
           while not found or k<ll:
              x=l[k]
              if x.strip().startswith('"""'):
                 if first:
                    found=True
                    break
                 else:
                    first=True
              elif first:
                 api.append(x)
              k+=1
           
           if found:
              funcs[fn]={'api':api,
                         'input':i,
                         'rem':rem,
                         'desc':desc,
                         'line':ld,
                         'target':target}

           api=[]
           desc=[]
           target=''

    # Process functions
    if html:
       h+='We encourage you to reuse these portable productivity functions (Python 2.6+ and 3+) from the CK modules or in your own Python scripts:\n'
       h+='\n'
       h+='<pre>\n'
       h+='    import ck.kernel as ck\n'
       h+='\n'
       h+='    ck.out("Hello world")\n'
       h+='\n'
       h+='    r=ck.access({"action":"ls", "module_uoa":"env", "out":"con"})\n'
       h+='    if r["return"]>0: ck.err(r)\n'
       h+='    print (r["lst"])\n'
       h+='\n'
       h+='    r=ck.load_json_file({"json_file":"my_file.json", "dict":{"test":"yes"}})\n'
       h+='    if r["return"]>0: return r\n'
       h+='\n'
       h+='    r=ck.save_text_file({"text_file":"my_file.txt", "string":"test=yes\\n"})\n'
       h+='    if r["return"]>0: return r\n'
       h+='\n'
       h+='</pre>\n'

       h+='See <a href="https://github.com/ctuning/ck/wiki">CK documentation for further details</a>.\n'

       h+='<p>\n'
       h+='<table cellpadding="4" border="1" style="border-collapse: collapse; border: 1px solid black;">\n'

       h+=' <tr>\n'
       h+='  <td nowrap><b>#</b></td>\n'
       h+='  <td nowrap><b>Function name</b></td>\n'
       h+='  <td nowrap><b>Note and API</b></td>\n'
       h+=' </tr>\n'

    hdev=h

    num1=0
    num2=0
    for f in sorted(funcs):
        x=funcs[f]

        api=x['api']
        i=x['input']
        rem=x['rem']
        line=x['line']
        desc=x['desc']
        target=x['target']

        xapi='<i>'
        for y in desc:
            j=y.find('\\n=')
            if j>=0: 
               y=y[:j]
            xapi+=y
        xapi+='</i>\n'

        xapi+='<p>\n'
        xapi+='<pre>\n'
        for y in api:
            xapi+=y+'\n'
        xapi+='</pre>\n'

        url='https://github.com/ctuning/ck/blob/master/ck/kernel.py'

        x=''
        if target!='':
           x+='<p>&nbsp;&nbsp;&nbsp;<i>for '+target+'</i>'

        if 'end users' in target or 'end-users' in target:
           num1+=1
           num=num1
        else:
           num2+=1
           num=num2

        zh=' <tr>\n'
        zh+='  <td nowrap valign="top"><a name="'+f+'">'+str(num)+'</td>\n'
        zh+='  <td nowrap valign="top"><a href="'+url+'#L'+str(line+1)+'"><b>ck.'+f+'('+i+')</b></a>'+x+'</b></td>\n'
        zh+='  <td nowrap valign="top">'+xapi+'</td>\n'
        zh+=' </tr>\n'

        if 'end users' in target or 'end-users' in target:
           h+=zh
        else:
           hdev+=zh

    # Prepare config
    hcfg+='You can access the following CK internal variables:\n'
    hcfg+='\n'
    hcfg+='<pre>\n'
    hcfg+='    import ck.kernel as ck\n'
    hcfg+='\n'
    hcfg+='    print (ck.cfg)\n'
    hcfg+='</pre>\n'

    hcfg+='See <a href="https://github.com/ctuning/ck/wiki">CK documentation for further details</a>.\n'

    hcfg+='<p>\n'
    hcfg+='<pre>\n'
    for x in cfg:
        hcfg+=x+'\n'
    hcfg+='</pre>\n'
    hcfg+=h2

    if html:
       h+='</table>\n'
       h+=h2
       hdev+='</table>\n'
       hdev+=h2

       if of!='':
          r=ck.save_text_file({'text_file':of+'.html', 'string':h})
          if r['return']>0: return r

          r=ck.save_text_file({'text_file':of+'-dev.html', 'string':hdev})
          if r['return']>0: return r

          r=ck.save_text_file({'text_file':of+'-dev-cfg.html', 'string':hcfg})
          if r['return']>0: return r

    return {'return':0}

##############################################################################
# list repositories

def list_repos(i):
    """
    Input:  {
               (the same as ck search; can use wildcards)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')

    of=i.get('out_file','')
    if of!='':
       xof=os.path.splitext(of)

    html=False
    if o=='html' or i.get('web','')=='yes':
       html=True

    h=''
    h2=''
    if i.get('new','')=='yes':
       ii=copy.deepcopy(i)
       ii['ck_title']='Shared CK repositories'
       r=preload_html_for_lists(ii)
       if r['return']>0: return r

       h=r['html_start']+'\n'
       h2=r['html_stop']+'\n'

    unique_repo=False
    if i.get('repo_uoa','')!='': unique_repo=True

    import copy
    ii=copy.deepcopy(i)

    ii['out']=''
    ii['module_uoa']=cfg['module_deps']['repo']
    ii['action']='list'
    ii['add_meta']='yes'

    rx=ck.access(ii)
    if rx['return']>0: return rx

    ll=rx['lst']

    if html:
       h+='You can reuse modules and other components with a common API from below repositories (most of them were shared with the permissive 3-clause BSD license or CC-BY):\n'
       h+='<pre>\n'
       h+=' ck pull repo:{Repo UOA - see below}\n'
       h+='</pre>\n'

       h+='You can add dependency on a given repository in your own CK repository by editing your .ckr.json file as follows:\n'
       h+='<pre>\n'
       h+=' {\n'
       h+='   ...\n'
       h+='   "dict": {\n'
       h+='      "repo_deps": [\n'
       h+='         {\n'
       h+='           "repo_uoa": "ck-tensorflow",\n'
       h+='           "repo_url": "https://github.com/ctuning/ck-tensorflow"\n'
       h+='         }\n'
       h+='         ...\n'
       h+='      ]\n'
       h+='      ...\n'
       h+='   }\n'
       h+='}\n'
       h+='</pre>\n'

       h+='<p>Feel free to add description of your own CK repository in this <a href="https://github.com/ctuning/ck-env/blob/master/cfg/list-of-repos/.cm/meta.json">JSON file</a>.\n'

       h+='<p>See <a href="https://github.com/ctuning/ck/wiki">CK documentation</a>\n'
       h+=' and <a href="https://github.com/ctuning/ck/wiki#user-content-reusable-ck-components">already shared reusable components</a> for further details.\n'

       h+='<p>\n'
       h+='<table cellpadding="4" border="1" style="border-collapse: collapse; border: 1px solid black;">\n'

       h+=' <tr>\n'
       h+='  <td nowrap><b>#</b></td>\n'
       h+='  <td nowrap><b>Repository UOA</b></td>\n'
       h+='  <td><b>Description</b></td>\n'
       h+=' </tr>\n'

    repos={}
    repo_url={}
    repo_private={}

    # Checking installed repos
    private=''
    remote=''
    for l in ll:

        lr=l['data_uoa']
        lr_uid=l['data_uid']

        url=''

        if lr=='default':
           url='https://github.com/ctuning/ck/tree/master/ck/repo'
        else:
           rx=ck.load_repo_info_from_cache({'repo_uoa':lr_uid})
           if rx['return']>0: return rx
           url=rx.get('dict',{}).get('url','')
           private=rx.get('dict',{}).get('private','')
           remote=rx.get('dict',{}).get('remote','')

        if lr not in cfg.get('skip_repos',[]) and remote!='yes' and private!='yes' and url!='':
           repos[lr_uid]={'data_uoa':lr}

    # Check which already manually added from cfg:list-of-repos
    rruoa=i.get('repo_uoa','')

    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['cfg'],
                 'data_uoa':cfg['cfg-list-of-repos']})
    if r['return']>0 and r['return']!=16: return r
    if r['return']==0:
       repos.update(r['dict'])
       if rruoa=='': rruoa=r['repo_uid']

    # Try to fill in missing information
    for repo in repos:
        x=repos[repo]

        d=x.get('dict',{})
        if len(d)==0:
           # Find real repo and get .ckr.json
           rx=ck.access({'action':'where',
                         'module_uoa':cfg['module_deps']['repo'],
                         'data_uoa':repo})
           if rx['return']==0: 
              pckr=os.path.join(rx['path'], ck.cfg['repo_file'])
              if os.path.isfile(pckr):
                 rx=ck.load_json_file({'json_file':pckr})
                 if rx['return']>0: return rx

                 d=rx['dict']['dict']

                 if 'path' in d:
                    del(d['path'])

                 x['dict']=d

    # Record list
    if rruoa=='': rruoa='ck-env'

    r=ck.access({'action':'update',
                 'module_uoa':cfg['module_deps']['cfg'],
                 'data_uoa':cfg['cfg-list-of-repos'],
                 'repo_uoa':rruoa,
                 'dict':repos,
                 'sort_keys':'yes',
                 'ignore_update':'yes'})
    if r['return']>0: return r
    
    # Show repos
    num=0
    for repo in sorted(repos, key=lambda k: repos[k]['data_uoa']):
        l=repos[repo]

        lr=l['data_uoa']
        lr_uid=repo

        d=l.get('dict',{})

        if d.get('skip_from_index','')=='yes':
           continue

        url=d.get('url','')
        external_url=d.get('external_url','')
        rd=d.get('repo_deps',{})

        ld=d.get('desc','')

        to_get=''
        if url.find('github.com/ctuning/')>0:
           to_get='ck pull repo:'+lr
        elif url!='':
           to_get='ck pull repo --url='+url
        elif external_url!='':
           to_get='[ <a href=\"'+external_url+'\">external link</a> ]'

        num+=1

        ###############################################################
        if html:
           h+=' <tr>\n'

           x1=''
           x2=''
           z1=''
           z11=''

           if url=='' and lr=='default':
              url='https://github.com/ctuning/ck/tree/master/ck/repo'

           if url!='':
              x1='<a href="'+url+'">'
              x2='</a>'

              url2=url

              if url2.endswith('.git'):
                 url2=url2[:-4]

              if '/tree/master/' not in url2:
                 url2+='/tree/master/'
              else:
                 url2+='/'

              z1='<a href="'+url2+'.ckr.json">'

           h+='  <td nowrap valign="top"><a name="'+lr+'">'+str(num)+'</b></td>\n'
                                                     
           x5=''
           if url!='':
              x5=' <i>('+z1+'.ckr.json)</i>'
           h+='  <td nowrap valign="top"><b>'+x1+lr+x2+'</b>'+x5+'</td>\n'

           h+='  <td valign="top">'+ld+'\n'

           if to_get!='':
              h+='<p>\n'
              h+='How to get:\n'
              h+='<pre>\n'
              h+=to_get+'\n'
              h+='</pre>\n'

           if len(rd)>0:
              h+='<p>Dependencies on other repositories:\n'
              h+='<ul>\n'
              for qq in sorted(rd, key=lambda k: k['repo_uoa']):
                  repo_uoa=qq['repo_uoa']
                  repo_url=qq.get('repo_url','')

                  if repo_url=='':
                     repo_url='https://github.com/ctuning/'+repo_uoa

                  if repo_url!='':
                     repo_uoa='<a href="#'+repo_uoa+'">'+repo_uoa+'</a>'

                  h+='<li>'+repo_uoa+'\n'
              h+='</ul>\n'

           if d.get('ck_artifact','')!='' or d.get('passed_artifact_evaluation','')=='yes':
              h+='<p>Workflow passed <a href="http://cTuning.org/ae">Artifact Evaluation</a>\n'
              h+='<p><center><img src="https://www.acm.org/binaries/content/gallery/acm/publications/replication-badges/artifacts_evaluated_reusable_dl.jpg" width="64"></center>\n'

           h+='</td>\n'

           h+=' </tr>\n'

    if html:
       h+='</table>\n'
       h+=h2

       if of!='':
          r=ck.save_text_file({'text_file':of, 'string':h})
          if r['return']>0: return r

    return {'return':0}

##############################################################################
# list modules

def list_modules(i):
    """
    Input:  {
              (new) - if 'yes', add htmls
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')

    of=i.get('out_file','')
    if of!='':
       xof=os.path.splitext(of)

    html=False
    if o=='html' or i.get('web','')=='yes':
       html=True

    h=''
    h2=''
    if i.get('new','')=='yes':
       ii=copy.deepcopy(i)
       ii['ck_title']='Shared CK modules'
       r=preload_html_for_lists(ii)
       if r['return']>0: return r

       h=r['html_start']+'\n'
       h2=r['html_stop']+'\n'

    unique_repo=False
    if i.get('repo_uoa','')!='': unique_repo=True

    ii=copy.deepcopy(i)

    ii['out']=''
    ii['action']='list'
    ii['module_uoa']=cfg['module_deps']['module']
    ii['add_meta']='yes'

    rx=ck.access(ii)
    if rx['return']>0: return rx

    ll=sorted(rx['lst'], key=lambda k: k['data_uoa'])

    if html:
       h+='You can install and reuse CK modules as follows:\n'
       h+='<pre>\n'
       h+=' ck pull repo:{Repo UOA - see below}\n'
       h+=' ck help {module UOA - see below}\n'
       h+='</pre>\n'

       h+='You can check a JSON API of a given action of a given module as follows:\n'
       h+='<pre>\n'
       h+=' ck {module action - see below} {module UOA} --help\n'
       h+='</pre>\n'

       h+='You can add your own dummy CK module as follows:\n'
       h+='<pre>\n'
       h+=' ck add module:{my module alias}\n'
       h+='</pre>\n'

       h+='You can add a new action to the CK module as follows:\n'
       h+='<pre>\n'
       h+=' ck add_action module:{my module alias}\n'
       h+='</pre>\n'

       h+='See <a href="https://github.com/ctuning/ck/wiki">CK documentation</a>\n'
       h+=' and the latest <a href="http://cKnowledge.org/rpi-crowd-tuning">CK paper</a> for further details.\n'

       h+='<p>\n'
       h+='<table cellpadding="4" border="1" style="border-collapse: collapse; border: 1px solid black;">\n'

       h+=' <tr>\n'
       h+='  <td nowrap><b>#</b></td>\n'
       h+='  <td nowrap><b>Module&nbsp;UOA with JSON API<br>(Python module/wrapper/plugin)</b></td>\n'
       h+='  <td nowrap><b>Repo UOA</b></td>\n'
       h+='  <td><b>Description and actions</b></td>\n'
       h+=' </tr>\n'

    repo_url={}
    repo_private={}

    private=''
    num=0
    for l in ll:
        ln=l['data_uoa']
        lr=l['repo_uoa']

        lr_uid=l['repo_uid']
        url=''
        if lr=='default':
           url='https://github.com/ctuning/ck/tree/master/ck/repo'
        elif lr_uid in repo_url:
           url=repo_url[lr_uid]
        else:
           rx=ck.load_repo_info_from_cache({'repo_uoa':lr_uid})
           if rx['return']>0: return rx
           url=rx.get('dict',{}).get('url','')
           repo_private[lr_uid]=rx.get('dict',{}).get('private','')
           repo_url[lr_uid]=url

        private=repo_private.get(lr_uid,'')

#        if lr not in cfg.get('skip_repos',[]) and private!='yes' and url!='':
        if lr not in cfg.get('skip_repos',[]) and private!='yes' and url!='':
           num+=1

           lm=l['meta']
           ld=lm.get('desc','')

           actions=lm.get('actions',{})

           if lr=='default':
              to_get=''
           elif url.find('github.com/ctuning/')>0:
              to_get='ck pull repo:'+lr
           else:
              to_get='ck pull repo --url='+url

           ###############################################################
           if html:
              h+=' <tr>\n'

              x1=''
              x2=''
              z1=''
              z11=''
              if url!='':
                 x1='<a href="'+url+'">'
                 x2='</a>'

                 url2=url

                 if url2.endswith('.git'):
                    url2=url2[:-4]

                 if '/tree/master/' not in url2:
                    url2+='/tree/master/module/'
                 else:
                    url2+='/module/'

                 z1='<a href="'+url2+ln+'/module.py">'
                 z11='<a href="'+url2+ln+'/.cm/meta.json">'

              h+='  <td nowrap valign="top"><a name="'+ln+'">'+str(num)+'</b></td>\n'

              h+='  <td nowrap valign="top">'+z1+ln+x2+'</b> <i>('+z11+'CK meta'+x2+')</i></td>\n'

              h+='  <td nowrap valign="top"><b>'+x1+lr+x2+'</b></td>\n'

              h+='  <td valign="top">'+ld+'\n'

              if len(actions)>0:
                 h+='<ul>\n'
                 for q in sorted(actions):
                     qq=actions[q]
                     qd=qq.get('desc','')
                     h+='<li>"ck <i>'+q+'</i> '+ln+'"'
                     if qd!='':
                        h+=' - '+qd
                 h+='</ul>\n'

              h+='</td>\n'

              h+=' </tr>\n'

           ###############################################################
           elif o=='mediawiki':
              x=lr
              if url!='':
                 x='['+url+' '+lr+']'
              ck.out('')
              ck.out('=== '+ln+' ('+lr+') ===')
              ck.out('')
              ck.out('Desc: '+ld)
              ck.out('<br>CK Repo URL: '+x)
              if to_get!='':
                 ck.out('<br>How to get: <i>'+to_get+'</i>')
              ck.out('')
              if len(actions)>0:

                 ck.out('Actions (functions):')
                 ck.out('')

                 for q in sorted(actions):
                     qq=actions[q]
                     qd=qq.get('desc','')
                     ck.out('* \'\''+q+'\'\' - '+qd)

           ###############################################################
           elif o=='con' or o=='txt':
              if unique_repo:
                 ck.out('')
                 s=ln+' - '+ld

              else:
                 ss=''
                 if len(ln)<35: ss=' '*(35-len(ln))

                 ss1=''
                 if len(lr)<30: ss1=' '*(30-len(lr))

                 s=ln+ss+'  ('+lr+')'
                 if ld!='': s+=ss1+'  '+ld

              ck.out(s)

              if len(actions)>0:
                 ck.out('')
                 for q in sorted(actions):
                     qq=actions[q]
                     qd=qq.get('desc','')
                     ck.out('  * '+q+' - '+qd)


    if html:
       h+='</table>\n'
       h+=h2

       if of!='':
          r=ck.save_text_file({'text_file':of, 'string':h})
          if r['return']>0: return r

    return {'return':0}

##############################################################################
# preload HTMLs for lists of components

def preload_html_for_lists(i):
    """
    Input:  {
              (html_file_start) - ck_start_html by default
              (html_file_stop)  - ck_stop_html by default
              (ck_title)        - update title in the start file
              (out_file)        - get page name
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              html_start
              html_stop
            }

    """

    import os

    out_file=i.get('out_file','')

    page_name=os.path.basename(out_file)
    if page_name.endswith('.html'):
       page_name=page_name[:-5]

    fstart=i.get('html_file_start','')
    if fstart=='': fstart='ck_start.html'

    fstop=i.get('html_file_stop','')
    if fstop=='': fstop='ck_stop.html'

    ck_title=i.get('ck_title','')

    # Load first file
    r=ck.load_text_file({'text_file':fstart})
    if r['return']>0: return r

    html_start=r['string'].replace('$#ck_title#$',ck_title)
    html_start=html_start.replace('$#ck_page#$',page_name)

    # Load second file
    r=ck.load_text_file({'text_file':fstop})
    if r['return']>0: return r

    html_stop=r['string'].replace('$#ck_title#$',ck_title)

    return {'return':0, 'html_start':html_start, 'html_stop':html_stop}

##############################################################################
# replace multiple strings in a given file

def replace_strings_in_file(i):
    """
    Input:  {
              file
              (file_out)            - if !='', use this file for output, otherwise overwrite original one!
              replacement_json_file - replacement file with multiple strings to substitute
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              (updated)    - if 'yes', files was updated
            }

    """

    import copy

    o=i.get('out','')

    fin=i['file']
    rjf=i['replacement_json_file']

    fout=i.get('file_out','')
    if fout=='': fout=fin

    rx=ck.load_text_file({'text_file':fin})
    if rx['return']>0: return rx
    s=rx['string']

    rx=ck.load_json_file({'json_file':rjf})
    if rx['return']>0: return rx
    rep=rx['dict']

    sx=s
    for k in rep:
        v=rep[k]
        sx=sx.replace(k,v)

    r={'return':0, 'updated':'no'}

    if s!=sx or fin!=fout:
       r=ck.save_text_file({'text_file':fout, 'string':sx})
       r['updated']='yes'

    return r
