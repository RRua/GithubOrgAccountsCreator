import csv
import json
import re
import io, sys, os
import shutil
import subprocess

out_json_filename="groups.json"

really_execute=False # 


def executeShCommand(command):
    if not really_execute:
        print(command)
        return 0
    pipes = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = pipes.communicate()
    if pipes.returncode != 0:
        print("error")
        err_msg = "%s. Code: %s" % (std_err.strip(), pipes.returncode)
        raise Exception(err_msg)
    elif len(std_err):
        return 0

def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
    except shutil.Error as e:
        # Directories are the same
        print('Directory not copied. Error: %s' % e)
    except OSError as e:
        # error saying that the directory doesn't exist
        print('Directory not copied. Error: %s' % e)

def readJSONFile(filepath):
    data={}
    with open(filepath,'r') as jfile:
        data=json.load(jfile)
    return data

class GithubStudentsAccountsCreator(object):
    """docstring for GithubStudentsAccountsCreator"""
    def __init__(self, json_config):
        # load fields from json config file
        self.input_csv   = json_config['input_csv']
        self.input_csv_delimeter = json_config['input_csv_delimeter']
        self.org_name    = json_config['org_name']
        self.oauth_token = json_config['oauth_token']
        self.group_repo_name_pattern = json_config['group_repo_name_pattern']
        self.repo_structure_model = json_config['repo_structure_model'] 
        self.repos_folder = json_config['repos_folder'] 

    def buildGroupsJSON(self,csvfile):
        with open(csvfile) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 0
            student_dict={}
            previous_group=1
            for row in csv_reader:
                if len(row)>0 and row[0]=='':
                    if row[1] != '':
                        student={}
                        student["group"]=previous_group
                        student["number"]=row[1]
                        student["name"]=row[2]
                        #print((row[2]))
                        student["github_id"]=row[3]
                        student_dict[str(previous_group)].append(student)
                    else:
                        print("Warning: ignoring line %d: blank or malformed line in input csv" % line_count)
                        pass
                elif len(row)>2 and re.match(r"[0-9]+", row[0]) and row[1] != '':
                    previous_group=int(row[0])
                    student_dict[str(previous_group)]=[]
                    student={}
                    student["group"]=previous_group
                    student["number"]=row[1]
                    student["name"]=row[2]
                    student["github_id"]=row[3]
                    student_dict[str(previous_group)].append(student)
                else:
                    print("Warning: ignoring line %d: blank or malformed line in input csv" % line_count)
                    pass
                line_count = line_count + 1
        return student_dict

    def writeGroupsToJSONFIle(groups_dict,out_json_filename):
        with open(out_json_filename, 'w') as f:
            json.dump(groups_dict, f, sort_keys=True, indent=4,ensure_ascii = False)

    def getGroupName(self,group_number):
        return  self.group_repo_name_pattern % str(group_number) 

    def getGroupRepo(self,group_name):
        return self.repos_folder + "/" + group_name + "/"

    def createLocalGroupDiretory(self,group_name):
        group_folder= self.getGroupRepo(group_name)
        if not os.path.exists(self.repos_folder):
            os.mkdir(self.repos_folder)
        copyDirectory(self.repo_structure_model ,group_folder)

    def initGroupGit(self,group_name):
        group_folder= self.getGroupRepo(group_name)
        command='''curl -H "Authorization: token %s" "https://api.github.com/orgs/%s/repos" -d "{\\"name\\":\\"%s\\" , \\"private\\":\\"true\\" }"
        '''% ( self.oauth_token, self.org_name, group_name)
        executeShCommand(command)
        command='''
        cd {group_folder};
        git init ; git add * ; 
        git commit -m \"project structure\";
        git remote add origin "https://github.com/{org_name}/{group_name}.git"
        git push origin master;
        cd ..
        '''.format(group_folder=group_folder, org_name=self.org_name, group_name=group_name)
        executeShCommand(command)


    def generateReadmeFile(self,group_name,group_members):
        group_folder= self.getGroupRepo(group_name)
        readmeString=""
        for member in group_members:
           readmeString+= "%s,%s,%s \n\n" % (member['number'],member['name'],member['github_id'])
        readmefile = open(group_folder +"README.md","w")#write mode 
        readmefile.write(readmeString) 
        readmefile.close() 

    def addGithubColaborators(self,group_name,group_members):
        for member in group_members:
            command='''curl -X PUT  -H "Authorization: token {oauth_token}"   "https://api.github.com/repos/{org_name}/{group_name}/collaborators/{github_id}"
            '''.format(oauth_token=self.oauth_token,org_name=self.org_name,group_name=group_name, github_id=member['github_id'])
            executeShCommand(command)

    def pullGithubRepos(self):
        students_dict = self.buildGroupsJSON(self.input_csv)
        for group_number ,group_members in students_dict.items():
            print("pulling repo of group %s" % group_number)
            group_folder= self.getGroupRepo(self.getGroupName(group_number))
            command='''
            cd {group_folder}; git pull origin master;
            cd ..
            '''.format(group_folder=group_folder, org_name=self.org_name, group_name=self.getGroupName(group_number))
            executeShCommand(command)

    def deleteRepo(self,group_name):
        command=''' curl -X DELETE -H "Authorization: token {oauth_token}"   "https://api.github.com/repos/{org_name}/{group_name}"
        '''.format(oauth_token=self.oauth_token,org_name=self.org_name,group_name=group_name)
        executeShCommand(command)
        #self.deleteLocalGroupDiretory(group_name)


    def deleteAllGithubGroups(self):
        students_dict = self.buildGroupsJSON(self.input_csv)
        for group_number in students_dict.keys():
            group_name = self.getGroupName(group_number)
            print("Deleting group %s" % group_name)
            self.deleteRepo(group_name)

    
    def createGithubGroups(self, more=True):
        students_dict = self.buildGroupsJSON(self.input_csv)
        for group_number ,group_members in students_dict.items():
            print("processing group %s" % group_number)
            group_name = self.getGroupName(group_number)
            self.createLocalGroupDiretory(group_name)
            self.generateReadmeFile(group_name,group_members)
            self.initGroupGit(group_name)
            self.addGithubColaborators(group_name,group_members)
            if not more:
                return

if __name__ == '__main__':
    if len(sys.argv)>2:
        gg = GithubStudentsAccountsCreator(readJSONFile(sys.argv[2]) )   
        action = sys.argv[1]
        if "create" in action:
            gg.createGithubGroups()
        if "instance" in action:
            gg.createGithubGroups(more=False)
        elif "pull" in action:
            gg.pullGithubRepos()
        elif "delete" in action:
            gg.deleteAllGithubGroups()
    else:
        print("please specify script args -> action (create | delete | pull ) and config file (config.json ?)")
        






