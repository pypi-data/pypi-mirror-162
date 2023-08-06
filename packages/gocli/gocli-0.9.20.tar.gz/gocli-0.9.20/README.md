gocli - How to install as a dev (containerized)
===============================================
1. Within the gocli directory, build a local development container: `docker build -f Dev-Dockerfile -t us.gcr.io/graceful-medley-134315/gocli-dev:latest .`
2. Now you have a fully built gocli instance. You can run commands against your local POP instance, for example:
    `docker run -e KMS_SCHEMES=http -e KMS_HOST=interface:8000 -e KMS_TOKEN=8bd27700f0cd034c0569b9b1f48b778e02e18ec6 --network=knowledge_default -v ~/Desktop/gocli:/gocli_files -it us.gcr.io/graceful-medley-134315/gocli-dev:latest bash -c "gocli /gocli_files/genes_to_phenotype_test.txt - aggregate_tsv gene transform hpo load_annotations HPO test"`

    OR you can run commands against a remote server:
    `docker run -e KMS_SCHEMES=https -e KMS_HOST=q42020.genomoncology.io -e KMS_TOKEN=989c38a36eec154f01167274dbce2334ccf8ef11 -v ~/Desktop/gocli:/gocli_files -it us.gcr.io/graceful-medley-134315/gocli-dev:latest bash -c "gocli /gocli_files/genes_to_phenotype_test.txt - aggregate_tsv gene transform hpo load_annotations HPO test"`

gocli - How to install as a dev (non-containerized)
===============================

1. Within the gocli directory, make a virtual environment: `mkvirtualenv -a . {name of env}`
2. Install gocli (and dependencies): `pipsi install -e .`
3. Test to make sure that gocli works: `gocli --help`
4. A simple way to verify that the gocli version is a local version (and not from pip) is to modify one
of the docstrings (strings under function definition) in the commands.py file. Then run `gocli --help` again
and you should see your change in the help text for that command.
5. To install packages (to run make white and make test), run `pipenv install --dev`

How to get gocli working on your local:
---------------------------------------

Once you have installed gocli, you will need to set three environment variables in order for gocli to work (clients that use gocli also need to set these environment variables). The enviroment variables tell gocli where to find the running KMS that it will be making its API calls to. The enviroment variables are:

export KMS_SCHEMES=http (or https)

export KMS_HOST=localhost:8000 (or whatever the server name is)

export KMS_TOKEN={your admin token}  --> note: do NOT add "Token " to the beginning of it. Just put the actual token value

The cool thing about these env vars is that you can specify a different server name than local (if you need to run a command against another server). 

Also, we have had clients have issues in the past where the KMS_SCHEMES was either not set or not set to https and they would get errors like this when running gocli: bravado.exception.HTTPGatewayTimeout: 504 Gateway Time-out. This was caused because their server required https calls, not just http (the default). 


How to give an executable gocli to someone (a version not published to PyPi)
----------------------

1. edit setup.py and src/genomoncology/cli/commands.py and update the version field by adding 'a{number}' to the end (i.e. 0.9.9_a1)
2. make clean
3. pipenv run python setup.py bdist_wheel --universal
4. share the dist/*.whl file with the person 

General notes about gocli:
--------------------------

gocli uses the click python package to nicely handle command-line commands, parameters, and options. The commands can chain together, 
so the output of one command becomes the input of the next command. gocli also heavily uses the concept of currying. You'll see a ton of methods with the @curry decorator on them. From the code, the documentation on that decorator says:


    curry(self, *args, **kwargs)
    
        Curry a callable function
    
        Enables partial application of arguments through calling a function with an
        incomplete set of arguments.
    
        >>> def mul(x, y):
        ...     return x * y
        >>> mul = curry(mul)
    
        >>> double = mul(2)
        >>> double(10)
        20
    
        Also supports keyword arguments
    
        >>> @curry                  # Can use curry as a decorator
        ... def f(x, y, a=10):
        ...     return a * (x + y)
    
        >>> add = f(a=1)
        >>> add(2, 3)
        5
    
        See Also:
            cytoolz.curried - namespace of curried functions
           

Because of the way that commands are chained together, the one weird thing about gocli is that you often won't see parameters actually being passed in. For example, let's look at the following command:


    @gocli.command()
    @options.build_option
    @options.pass_state
    def annotate_genes(state):
        """Get gene objects by stream of names."""
        return [
            sources.TextFileSource,
            partition_all(state.batch_size),
            kms.create_sync_processor(
                state, kms.genes.sync_boundaries, build=state.build
            ),
            concat,
        ]

The kms.genes.sync_boundaries function takes in a parameter called "data", but that isn't explicitly passed in here. When the output of the previous command enters this one, that output will be substituted in as the input of this function, so the "data" parameter. It can 
be tricky to follow at first, but hopefully all of the examples in the code are helpful to understand what's going on.