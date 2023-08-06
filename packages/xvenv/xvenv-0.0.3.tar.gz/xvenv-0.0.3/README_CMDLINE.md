
# all `xvenv` cmd-line options


## xvenv

run `xvenv -h` for help

    usage: python3 -m xvenv [options]
    
    venv mangement and builder tool
    
    positional arguments:
      {setup,pip,req,tools,clean,build,install,pypi,binst,make,run,test,clone,drop,qtest}
                            sub-command --help
        setup               setup a venv in folder '.venv'
        pip                 install pip
        req                 install requirements.txt if present
        tools               install tools
        clean               clean all build related folders
        build               build with setuptools. like calling setup sdist build
                            bdist_wheel
        install             pip install editabe in venv
        pypi                pypi helper. just prints some helping information for
                            using with twine
        binst               build and install
        make                sets up a venv and installs everything
        run                 run a command
        test                test venv environment. outputs pip path and os.environ
        clone               clone xvenv.py to cwd folder
        drop                removes the '.venv' folder, and all contents
        qtest               run quality helpers
    
    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         show program's version number and exit
      --verbose, -V         show more info (default: False)
      -debug, -d            display debug info (default: False)
      -python PYTHON, -p PYTHON
                            display debug info (default: python3)
      -ewd EWD, -venv EWD   venv folder (default: .)
      -cwd CWD              working folder (default: .)
      -cdvenv               cd into venv before activate (default: False)
      --keep-temp, -kt      keep temporay file (default: False)
    
    for more information refer to https://github.com/kr-g/xvenv


## xvenv setup

run `xvenv setup -h` for help

    usage: python3 -m xvenv [options] setup [-h] [--clear] [--copy]
    
    optional arguments:
      -h, --help   show this help message and exit
      --clear, -c  clear before setup (default: False)
      --copy, -cp  use copy instead of symlink (default: False)


## xvenv pip

run `xvenv pip -h` for help

    usage: python3 -m xvenv [options] pip [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv req

run `xvenv req -h` for help

    usage: python3 -m xvenv [options] req [-h] [--no-req-update] [--update-req]
    
    optional arguments:
      -h, --help            show this help message and exit
      --no-req-update, -norequp, -nru
                            do not update requirements (default: False)
      --update-req, -ureq, -ur
                            update requirements (default: False)


## xvenv tools

run `xvenv tools -h` for help

    usage: python3 -m xvenv [options] tools [-h] [--update-deps] [--remove-tool]
                                            [-tool [TOOL [TOOL ...]]]
    
    optional arguments:
      -h, --help            show this help message and exit
      --update-deps, -u     update deps (default: False)
      --remove-tool, -R     remove tool (default: False)
      -tool [TOOL [TOOL ...]]
                            tool to install (default: ['setuptools', 'twine',
                            'wheel', 'black', 'flake8'])


## xvenv clean

run `xvenv clean -h` for help

    usage: python3 -m xvenv [options] clean [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv build

run `xvenv build -h` for help

    usage: python3 -m xvenv [options] build [-h] [--build-clean]
                                            [--build-clean-only]
    
    optional arguments:
      -h, --help            show this help message and exit
      --build-clean, -bclr  clean all build related folders (default: False)
      --build-clean-only, -bcl
                            clean all build related folders, but don't start build
                            (default: False)


## xvenv install

run `xvenv install -h` for help

    usage: python3 -m xvenv [options] install [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv pypi

run `xvenv pypi -h` for help

    usage: python3 -m xvenv [options] pypi [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv binst

run `xvenv binst -h` for help

    usage: python3 -m xvenv [options] binst [-h] [--build-clean]
                                            [--build-clean-only]
    
    optional arguments:
      -h, --help            show this help message and exit
      --build-clean, -bclr  clean all build related folders (default: False)
      --build-clean-only, -bcl
                            clean all build related folders, but don't start build
                            (default: False)


## xvenv make

run `xvenv make -h` for help

    usage: python3 -m xvenv [options] make [-h] [--quick] [--clear] [--copy]
                                           [--update-deps] [--no-req-update]
                                           [--update-req] [--remove-tool]
                                           [-tool [TOOL [TOOL ...]]]
                                           [--build-clean] [--build-clean-only]
    
    optional arguments:
      -h, --help            show this help message and exit
      --quick, -q           quick install without build and install steps
                            (default: False)
      --clear, -c           clear before setup (default: False)
      --copy, -cp           use copy instead of symlink (default: False)
      --update-deps, -u     update deps (default: False)
      --no-req-update, -norequp, -nru
                            do not update requirements (default: False)
      --update-req, -ureq, -ur
                            update requirements (default: False)
      --remove-tool, -R     remove tool (default: False)
      -tool [TOOL [TOOL ...]]
                            tool to install (default: ['setuptools', 'twine',
                            'wheel', 'black', 'flake8'])
      --build-clean, -bclr  clean all build related folders (default: False)
      --build-clean-only, -bcl
                            clean all build related folders, but don't start build
                            (default: False)


## xvenv run

run `xvenv run -h` for help

    usage: python3 -m xvenv [options] run [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv test

run `xvenv test -h` for help

    usage: python3 -m xvenv [options] test [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv clone

run `xvenv clone -h` for help

    usage: python3 -m xvenv [options] clone [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv drop

run `xvenv drop -h` for help

    usage: python3 -m xvenv [options] drop [-h]
    
    optional arguments:
      -h, --help  show this help message and exit


## xvenv qtest

run `xvenv qtest -h` for help

    usage: python3 -m xvenv [options] qtest [-h] [--exclude EXCLUDE] [--format]
                                            [--lint] [--unit-test]
    
    optional arguments:
      -h, --help            show this help message and exit
      --exclude EXCLUDE, -ex EXCLUDE
                            rexclude folder. (default: None)
      --format, --pep8, -f  run black, use black.cfg file for configuration
      --lint, -l            run flake8, use flake.cfg file for configuration
      --unit-test, --test, -t
                            run unittest

