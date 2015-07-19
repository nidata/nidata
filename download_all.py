import nidata

data_categories = filter(lambda mod: not mod.startswith('_') and mod != 'core',
                         dir(nidata))
for cat in data_categories:
    exec('objs = dir(nidata.%s)' % cat)
    objs = filter(lambda obj: obj.endswith('Dataset') and obj not in ['Dataset', 'HttpDataset'],
                  objs)
    for obj in objs:
        if "Brainomics" in obj or 'Hcp' in obj:
            continue
        print(cat, obj)
        exec('from nidata.%s import %s' % (cat, obj))
        exec('klass = %s' % obj)
        exec('dset = %s().fetch()' % obj)

        mod_path = klass.__module__.rsplit('.', 1)[0]
        exec('import %s as mod' % mod_path)

        if obj not in ["OasisVbmDataset", "HaxbyEtal2011Dataset"]:
            try:
                exec('import %s.example1' % mod_path)
            except ImportError as ie:
                if 'example1' in ie.message:
                    pass
                else:
                    raise ie
            else:
                print("cool!")
