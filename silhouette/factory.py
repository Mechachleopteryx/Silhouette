import os
from os import listdir, mkdir, makedirs
from os.path import isfile, join, isdir, dirname, basename
import tempfile
import shutil
import errno
import stat
import glob
import re
import configparser
import io
from silhouette.config import ApplicationConfig
from silhouette.download_manager import clone_repo_locally
from silhouette.validation import validate_project_structure
from silhouette.template_engine import TemplateEngine
import click
from shutil import copyfile

def handleRemoveReadonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean_temporary_repo(path):
    repo_main_dir = os.listdir(path)[0]
    shutil.rmtree(join(path, repo_main_dir), ignore_errors=False, onerror=handleRemoveReadonly)

def copy_file(src, dst):
    dst_root = dirname(dst)
    if not os.path.exists(dst_root):
        makedirs(dst_root)
    copyfile(src, dst)

def render_file_paths(src_paths, vars):
    te = TemplateEngine(vars)
    return [ te.eval_str(src)  for src in src_paths ]

def create_new_from_local(name, template_path, output_dir):
    app_config = ApplicationConfig(join(template_path, "default.properties"))
    template_vars = app_config.get_vars()
    
    for k,v in template_vars.items():
        template_vars[k] = click.prompt(k, default=v)

    te = TemplateEngine(template_vars)

    files = [ f for f in glob.glob(join(template_path, "project") + "\\**/*", recursive=True) if isfile(f) ]
    files_to_dst = { f:te.eval_str( f.replace(join(template_path, "project"), "") ) for f in files }

    base_dir = join(output_dir, name)
    mkdir(base_dir)
    
    for src, dst in files_to_dst.items():
        copy_file(src, base_dir + dst )

    click.secho("{} files copied".format(len(files_to_dst)), fg = "green")
    pass

def create_new_from_template(name, template, output_dir):
    """ Creates a new project from remote template. """
    repo_url = "https://github.com/{}.git".format(template)
    repo_user = template.split("/")[0]
    repo_name = template.split("/")[1]

    with tempfile.TemporaryDirectory(prefix=".", dir=os.getcwd()) as tmpdirname:
        clone_repo_locally(tmpdirname, repo_url)
        local_repo_path = join(tmpdirname, repo_name)
        # properties_file_path = join(local_repo_path, "default.properties")
        properties_file_path="C:\\Users\\HamzaELKAROUI\\hamza_projects\\Silhouette\\silhouette\\default.properties"
        app_config = ApplicationConfig(properties_file_path)
        template_vars = app_config.get_vars()
        
        for k,v in template_vars.items():
            click.prompt(k, default=v)
        # files = [f.replace(local_repo_path, "") for f in glob.glob(local_repo_path + "\\**/*", recursive=True) if isfile(f) ]        
        clean_temporary_repo(tmpdirname)



class Template():
    def __init__(self, template):
        self.template = template
    def __enter__(self):
        self.fd = open(self.dev, MODE)
        return self.fd
    def __exit__(self, type, value, traceback):
        close(self.fd)