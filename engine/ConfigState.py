import bios
import os
import shutil
from .app import AppState
from .app import LogLevel


class State(AppState):
    """
    An abstract class to handle paths to in/output files regarding different data splits.
    
    Attributes
    ----------
    app_name: str
        Name of the app (used for both docker image and the config file)
    config: dict
        content of config file for the app
        config.yml file can contain configs for more than one app.
    input_dir: str
        path to directory inside the app's docker container for input files
        Default: `/mnt/input`
    output_dir: str
        path to directory inside the app's docker container for output files
        Default: `/mnt/output`
    config_file: str
        the path to `config.yml` file inside the input directory
    mode: str
        Choices:
        `directory`: data files have splits.
        `file`: there is only a single file for each data.
    dir: str
        the directory name for input/output data.

    Methods
    -------
    lazy_init()
    read_config()
    finalize_config()
    """

    def __init__(self, app_name, input_dir: str = "/mnt/input", output_dir: str = "/mnt/output"):
        self.config = {}
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.config_file = f"{self.input_dir}/config.yml"
        self.mode = 'file'
        self.dir = '.'
        self.app_name = app_name

    def lazy_init(self):
        """ Add new key-value pairs into the `app-internal` dictionary, shared memory between states so that they can be accessible for other states.
            
            Keys:
            
            `use_smpc`: User-preference on using SMPC.
            `splits`: names of splits(it should be the same for all data).
            `input_files`: paths to all input files regarding the data splits.
            `output_files`: paths to all output files regarding the data splits.
            
        """
        # For Practical checking either SMPC was used or not.
        self.app.internal['smpc_used'] = False
        # use_smpc as functions' argument are for app-developers to declare their decision in specific.
        # self.config['use_smpc'] is the end-user preference that can be regarded or ignored by developers.

        self.app.internal['splits'] = set()
        self.app.internal['input_files'] = {}
        self.app.internal['output_files'] = {}

    def read_config(self):
        """ Read config.yml file
            it looks for `mode` and `dir` in `logic` part of the file,
            if it does not exist, default values will be used.
        """
        self.config = bios.read(self.config_file)[self.app_name]
        if 'debug' in self.config:
            if self.config['debug']:
                self.app.internal['debug'] = True
                self.app.log("Debug mode is ON", LogLevel.DEBUG)
            else:
                self.app.internal['debug'] = False
        if 'logic' in self.config:
            self.mode = self.config['logic']['mode']
            self.dir = self.config['logic']['dir']
        else:
            self.app.log(f"There are no 'logic' options in 'config.yml' file!\n"
                         f"default values will be used:\n"
                         f"mod: 'file'\n"
                         f"dir: '.'", LogLevel.DEBUG)

    def finalize_config(self):
        """  Generates split names, paths to input and output files.
             Regarding the `mode` of the app, there should be some splits for data,
             and for each data, different splits should be processed.
        """
        if self.mode == "directory":
            splits = [f.path for f in os.scandir(f'{self.input_dir}/{self.dir}') if f.is_dir()]
        else:
            splits = [self.input_dir, ]
        self.app.internal['splits'] = set(sorted(splits))
        self.app.log(f" Splits order:")
        for i, split in enumerate(self.app.internal['splits']):
            self.app.log(f"Split {i}: {split}")
        self.app.internal['input_files'] = \
            {k: [f"{split}/{v}" for split in self.app.internal['splits']]
             for k, v in self.config['local_dataset'].items()}
        self.app.internal['output_files'] = \
            {k: [f"{split.replace('/input', '/output')}/{v}" for split in self.app.internal['splits']]
             for k, v in self.config['result'].items()}

        for split in self.app.internal['splits']:
            os.makedirs(split.replace("/input", "/output"), exist_ok=True)
        shutil.copyfile(self.input_dir + '/config.yml', self.output_dir + '/config.yml')
