# encoding:utf-8
u"""
Usage:
    zmcli (-a|--all)
    zmcli checkout-all <branch>
    zmcli rollback <branch> [--arch=<arch_type>] [--build=<build_version>]
    zmcli show-builds <branch> [--arch=<arch_type>] [--num=<num_of_items>]
    zmcli update-all <branch> [--arch=<arch_type>]

Options:
    -h --help                   Show Help doc.
    -v --version                Show Version.
    -a --all                    show all params
    --arch=<arch_type>          assign an arch type
    --num=<num_of_items>        number of items will be showed
    --build=<build_version>     assign an build version
"""
__version__="0.2.3"

from ast import For, arg
from email import header
from filecmp import cmp
from hashlib import sha1
from operator import ge, imod
import os
import json
from platform import release
from re import A
from tkinter.messagebox import NO
from turtle import title
import requests
from tqdm import tqdm
from prettytable import PrettyTable
import zipfile
import subprocess
import time
from docopt import docopt
from functools import cmp_to_key
import git
from colorama import Back, Fore, Style, init
import hashlib

# Options below are no need to edit
artifacts_end_point = 'https://artifacts.corp.zoom.us/artifactory' # Artifactory EndPoint No need to edit
artifacts_repo = 'client-generic-dev'
local_repo_names = ['zoombase', 'common', 'ltt', 'client', 'thirdparties', 'mac-client'] # Repos that should checkout.

def version():
    return "version:"+__version__

def CalcSha1(filepath):
     with open(filepath,'rb') as f:
         sha1obj = hashlib.sha1()
         sha1obj.update(f.read())
         hash = sha1obj.hexdigest()
         return hash
 
def CalcSha256(filepath):
     with open(filepath,'rb') as f:
         md5obj = hashlib.sha256()
         md5obj.update(f.read())
         hash = md5obj.hexdigest()
         return hash

def cmp(build_info_1, build_info_2):
        t1 = time.mktime(time.strptime(build_info_1['created'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        t2 = time.mktime(time.strptime(build_info_2['created'], "%Y-%m-%dT%H:%M:%S.%fZ"))
        if t1 < t2:
            return 1
        elif t1 == t2:
            return 0
        return -1

class CommandLineTool:
    def __init__(self, api_key, user_name, work_space_path):
        self.api_key = api_key
        self.user_name = user_name
        self.work_space_path = work_space_path
        

    def checkout_repo(self, build_info):
        print(Fore.MAGENTA + '🤖 Start checking out repos...')
        repo_infos = build_info['repo_infos']
        for info in repo_infos:
            repo_name = info['repo']
            branch_name = info['branch']
            commit_hash = info['commit_hash']
            path = self.work_space_path + repo_name
            if not os.access(path, os.W_OK):
                print(Fore.RED + '🤖 ' + path + ' is not writable')
                return False
            repo = git.Repo.init(path)
            unstaged_list = [item.a_path for item in repo.index.diff(None)]
            if len(unstaged_list) > 0:
                print(Fore.RED + "You have unstaged files on repo " + dir)
                for line in unstaged_list:
                    print('\t' + Fore.YELLOW + line)
                untracked_list = repo.untracked_files
                return
            print(Fore.MAGENTA + "[" +repo_name + "] Start checking out to " + commit_hash + '...')
            res = repo.git.checkout(commit_hash)
            print(res)
        return True

    def get_latest_lib_build_info(self, lib):
        path = '/' + lib['repo'] + '/' + lib['path'] + '/' + lib['name']
        headers = {
            'content-type' : 'application/json',
            'X-JFrog-Art-Api' : self.api_key
        }
        
        params = {
            'deep' : 0,
            'listFolders' : 0,
            'mdTimestamps' : 1,
            'includeRootPath' : 0,
        }
        r = requests.get(artifacts_end_point + '/api/storage' + path + '?list', headers=headers, params=params)
        if r.status_code == 200:
            response = r.json()
            files = response['files']
            if len(files) > 0:
                build_info = {};
                for file in files:
                    uri = file['uri']
                    resource_url = artifacts_end_point + path + uri
                    if str(uri).endswith('build_info.json'):
                        r = requests.get(resource_url, headers=headers)
                        data = r.json()
                        build_version = data['env']['BUILDVERSION']
                        build_info['build_version'] = build_version
                        commits = data['commits']
                        repo_infos = []
                        for commit in commits:
                            target = str(commit['target']).lower()
                            commit_hash = commit['commit']
                            branch = commit['branch']

                            if str(target).lower() in local_repo_names:
                                info = {'repo': target, 'branch' : branch, 'commit_hash' : commit_hash}
                                repo_infos.append(info)
                        build_info['repo_infos'] = repo_infos
                    if str(uri).endswith('libs_' + lib['name'] + '.zip'):
                        build_info['lib_url'] = resource_url
                        build_info['lib_sha1'] = file['sha1']
                        build_info['lib_sha2'] = file['sha2']
                        build_info['lib_size'] = file['size']
                return build_info
            return None
        print(Fore.RED, r.status_code, r.text)
        return None

    def download_by_aria(self, url, sha1, sha2):
        print(Fore.MAGENTA + '🤖 Start downloading libs...')
        print(Fore.CYAN + 'Download Link: ' + Fore.YELLOW + url)
        target_folder = self.work_space_path + 'Downloaded_libs'
        if not os.path.exists(target_folder):
            os.system('mkdir ' + target_folder)
        file_name = str(url).split('/')[-1]
        target_path = target_folder + '/' + file_name
        if os.path.exists(target_path):
            if CalcSha1(target_path) == sha1 and CalcSha256(target_path) == sha2:
                print(Fore.YELLOW + 'File already exists.')
                return target_path
            os.system('rm -rf ' + target_path)
        print(Fore.CYAN + file_name + ' will be download to ' + target_folder)
        cmd = 'aria2c --http-user ' + self.user_name + ' --http-passwd ' + '\"' + self.api_key + '\"' + ' -d ' + target_folder + ' --max-concurrent-downloads 10 --max-connection-per-server 15 --split 10 --min-split-size 3M ' + url
        os.system(cmd)
        return target_path

    def replace_lib(self, zip_path, release_path):
        print(Fore.MAGENTA + '🤖 Start replacing libs...')
        cmd = 'unzip -o ' + zip_path + ' -d ' + release_path
        os.system(cmd)
        print(Fore.GREEN + "Finished replacing libs")


    def checkout_all(self, branch, pull):
        print(Fore.MAGENTA + '🤖 Start checking out all repos to ' + branch + '.\n')
        for dir in os.listdir(self.work_space_path):
            if dir in local_repo_names:
                path = self.work_space_path + dir
                if not os.access(path, os.W_OK):
                    print(Fore.RED + path + ' is not writable')
                    return False
                repo = git.Repo.init(path)
                unstaged_list = [item.a_path for item in repo.index.diff(None)]
                if len(unstaged_list) > 0:
                    print(Fore.RED + "You have unstaged files on repo " + dir)
                    for line in unstaged_list:
                        print('\t' + Fore.YELLOW + line)
                    untracked_list = repo.untracked_files
                    return
                repo.git.checkout(branch)
                print(Fore.GREEN + '🤖 [' + dir + '] - ' + "Sucessfully checked out to " + branch + '!')
                if pull:
                    print(Fore.MAGENTA + '[' + dir + '] Start pulling...')
                    res = repo.git.pull()
                    print(res + '\n')

    def rollback(self, branch, build_version, arch_type):
        print(Fore.MAGENTA + '🤖 Start rolling back...')
        list = self.get_latest_builds(branch, arch_type, 0)
        roll_back_build = list[0]
        if build_version:
            flag = False
            for build_info in list:
                if build_info['name'] == build_version:
                    roll_back_build = build_info
                    flag = True
            if not flag:
                print(Fore.RED + 'Didn\'t find build_version ' + build_version + ' for arch_type ' + arch_type + ' on branch ' + branch)
                return
            print(Fore.GREEN + 'Finded build_version ' + build_version + ' for arch_type ' + arch_type + ' on branch ' + branch)
        print(Fore.MAGENTA + "Will roll back to build" + roll_back_build['name'])
        build = self.get_latest_lib_build_info(roll_back_build)
        print(Fore.GREEN + '')
        if self.checkout_repo(build):
            release_path = self.release_path(arch_type)
            dest_path = self.download_by_aria(url=build['lib_url'], sha1=build['lib_sha1'], sha2=build['lib_sha2'])
            self.replace_lib(dest_path, release_path)


    def get_latest_builds(self, branch, arch_type, num):
        params = {
            '$or' : [{
                'type' : 'folder'
            }, {
                'type' : 'file'
            }],
            'repo' : {
                '$eq' : 'client-generic-dev'
            },
            'path' : {
                '$eq' : 'zoom/client/' + branch + '/' + arch_type
            }
        }
        headers = {
            'content-type' : 'text/plain',
            'X-JFrog-Art-Api' : self.api_key
        }
        data = 'items.find('+json.dumps(params)+').include(\"property\").transitive()'
        r = requests.post(artifacts_end_point+'/api/search/aql', data=data, headers=headers)
        if r.status_code == 200:
            json_data = json.loads(r.text)
            results = json_data['results']
            results = sorted(results, key=cmp_to_key(cmp))
            res = []
            if num > 0:
                results = results[:num]
            for build_info in results:
                res.append(build_info)
            return res
        print(r.text)
        return None
    
    def update_repos(self, branch, arch_type):
        if branch:
            self.checkout_all(branch,True)
            list = self.get_latest_builds(branch, arch_type, 0)
            roll_back_build = list[0]
            build = self.get_latest_lib_build_info(roll_back_build)

            release_path = self.release_path(arch_type)
            dest_path = self.download_by_aria(url=build['lib_url'], sha1=build['lib_sha1'], sha2=build['lib_sha2'])
            self.replace_lib(dest_path, release_path)
    
    def release_path(self, arch_type):
        release_path = self.work_space_path + 'Bin/'
        if arch_type == 'mac_x86_64':
            release_path += 'Mac/Release'
        else:
            release_path += 'Mac_arm64/Release'
        return release_path


def cmd(conf):
    args = docopt(__doc__)
    if conf is None:
        conf_file_path = os.path.expanduser('~') + '/.zmcli_conf'
        with open(conf_file_path,'r') as load_f:
            conf = json.load(load_f)
        load_f.close()
    
    is_at_work_space = False
    for dir in os.listdir():
        if dir in local_repo_names:
            is_at_work_space = True
            break
    if not is_at_work_space:
        print(Fore.RED + 'Please cd to your work space dir')
        return
    cli = CommandLineTool(api_key=conf['artifactory_api_key'], user_name=conf['artifactory_user_name'], work_space_path=(os.getcwd() + '/'))
    if args.get('checkout-all'):
        branch_name = args.get('<branch>')
        if branch_name:
            cli.checkout_all(branch_name, False)
    elif args.get('show-builds'):
        branch_name = args.get('<branch>')
        arch_type = args.get('--arch') if args.get('--arch') else 'mac_x86_64'
        num = int(args.get('--num')) if args.get('--num') else 10
        if branch_name:
            print(Fore.MAGENTA + '🤖 Getting latest build info for ' + branch_name + '(' + arch_type + ')')
            res = []
            if arch_type:
                res = cli.get_latest_builds(branch_name, arch_type, num)
            else:
                res = cli.get_latest_builds(branch_name, None, num)
            table = PrettyTable(['Version','Created At', 'Arch_type'], title='Latest builds for ' + branch_name + '(' + arch_type + ')')
            if len(res) <= 0:
                print(Fore.RED + '🤖 Did not find latest build info for ' + branch_name + '(' + arch_type + ')')
            for build_info in res:
                table.add_row([build_info['name'], build_info['created'], arch_type])
            print(table)

    elif args.get('rollback'):
        branch_name = args.get('<branch>')
        build_version = args.get('--build')
        arch_type = args.get('--arch') if args.get('--arch') else 'mac_x86_64'
        if branch_name:
            cli.rollback(branch_name, build_version, arch_type)

    elif args.get('-h') or args.get('--help'):
        print(__doc__)
    elif args.get("-a") or args.get("--all"):
        print(args)
    elif args.get('-a') or args.get('--version'):
        print(__version__)
    elif args.get('update-all'):
        branch_name = args.get('<branch>')
        arch_type = args.get('--arch') if args.get('--arch') else 'mac_x86_64'
        if branch_name:
            cli.update_repos(branch=branch_name, arch_type=arch_type)

def main():
    init(autoreset=True)
    conf_file_path = os.path.expanduser('~') + '/.zmcli_conf'
    if not os.path.exists(conf_file_path):
        print(Fore.MAGENTA + '🤖 Setup config file...')
        artifactory_user_name = input(Fore.CYAN + 'Your artifactory user name:\n')
        artifactory_api_key = input(Fore.CYAN + 'Your artifactory api key:\n')
        conf = { 'artifactory_user_name' : artifactory_user_name,
        'artifactory_api_key' : artifactory_api_key}
        with open(conf_file_path,"w") as f:
            json.dump(conf,f)
            print(Fore.YELLOW + "Config file is at '~/.zmcli_conf'")
        f.close()
        cmd(conf)
    else:
        cmd(None)

if __name__ == '__main__':
    main()
