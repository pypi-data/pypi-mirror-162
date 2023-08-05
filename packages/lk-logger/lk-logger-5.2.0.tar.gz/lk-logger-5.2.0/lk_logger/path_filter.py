"""
what we need:
    1. if source came from '~/libs/site-packages', show short form of path.
    2. use built-in print method for external source paths.
    3. do not print anything for external source paths.
    4. ...
"""


class PathFilter:
    
    def __init__(self):
        self.whitelist = set()
        self.blacklist = set()
        self.policy = None
        
    def block_site_packages(self):
        pass
    
    def block_any_externals(self):
        pass
        
    def filter_dir(self, dirpath: str):
        pass
    
    def check_pass(self, path: str) -> bool:
        pass
