import os, shutil
from pathlib import Path
from xml.etree.ElementTree import VERSION

MODULE_DIRECTORY = Path(__file__).parent
LICENSE_TEMPLATE_DIRECTORY = os.path.join(MODULE_DIRECTORY,'all_templates','licenses_templates')

"""
Python Package helper CLI 
"""

"""
Issues :

    * license types finder is quiet bad - need to upgrade the finding algorythm
"""


def add_LICENSE_file(LICENSE_type):
    """
    Adds the LICENSE file to root directory
    """

    if not os.path.exists('LICENSE'):
        for temp_license_type in os.listdir(os.path.join(MODULE_DIRECTORY,LICENSE_TEMPLATE_DIRECTORY)):
            if LICENSE_type.lower().startswith(temp_license_type.lower()):

                # copy the template to the project directory
                template_license_file_path = os.path.join(LICENSE_TEMPLATE_DIRECTORY, temp_license_type)
                shutil.copyfile(os.path.join(MODULE_DIRECTORY,template_license_file_path), 'LICENSE')
                return

        print("LICENSE type not valid! creating Default one... (MIT) ")
        template_license_file_path = os.path.join(LICENSE_TEMPLATE_DIRECTORY, 'mit.txt')
        shutil.copyfile(os.path.join(MODULE_DIRECTORY,template_license_file_path), 'LICENSE')
    else:
        print("LICENSE file already exists...")
        

def add_pyproject_file():
    """
    Adds the pyproject.toml file to root directory
    """

    if not os.path.exists('pyproject.toml'):
    
        shutil.copyfile(os.path.join(MODULE_DIRECTORY,'all_templates\\pyproject.toml'),'pyproject.toml')
    else:
        print("pyproject.toml file already exist...")


def add_README_file(package_name,author_name,description,url,install_requires):
    """
    Adds the README.md file to root directory
    """

    #check if the directory have a README file, and if not - make one
    if os.path.exists('README.md'):
            return

    with open('README.md','w+') as f:
        
        # writes the info that we got from the user in README.md file: 
        f.write("# "+package_name+'\n')
        f.write(description+'\n\n')
        f.write("## Developed by "+author_name+'\n')
        f.write("[Visit Package]("+url+')'+'\n\n')
        f.write("### Prerequisits\nThe dependencies of the package:"+'\n')
        for dependency in install_requires:
            f.write(dependency+'\n')
        

def add_setup_cfg_file(package_name,package_version,author_name,author_email,description,url,python_version,LICENSE_type,python_requires,install_requires):
    """
    Adds the setup.cfg file to root directory
    """
    if install_requires:
        install_requires_text = "install_requires = \n"+'\n    ' + install_requires
    else:
        install_requires_text = ''
    # Initializing the text the program is going to put inside setup.cfg file:
    SETUP_CFG_TEXT = '[metadata]\nname = {package_name}\nversion = {package_version}\nauthor = {author_name}\nauthor_email = {author_email}\ndescription = {description}\nlong_description = file: README.md\nlong_description_content_type = text/markdown\nurl = {url}\nproject_urls =\nBug Tracker = https://github.com/pypa/sampleproject/issues\nclassifiers =\nProgramming Language :: Python :: {python_version}\nLicense :: OSI Approved :: {LICENSE_type} License\nOperating System :: OS Independent\n[options]\npackage_dir =\n = src \npackages = find:\npython_requires = {python_requires}\n{install_requires_text}\n[options.packages.find]\nwhere = src'.format(package_name=package_name,package_version=package_version,author_name=author_name,author_email=author_email,description=description,url=url,python_version=python_version,LICENSE_type=LICENSE_type.upper(),python_requires=python_requires,install_requires=install_requires,install_requires_text=install_requires_text)

    with open("setup.cfg",'w') as f:
        f.write(SETUP_CFG_TEXT)

        print("setup.cgf file created! ")


def add_src_folder(package_name, ignore_list):
    """
    Adds the 'src' folder to root directory
    Adds the 'package_name' folder inside 'src' folder
    Adds the __init__.py file inside 'package_name' folder
    Moving All files (except the ignored ones in 'ignore_list') to 'package_name' folder
    """

    # check if 'src' folder exists, if not create on:
    if not os.path.exists('src'):
        os.mkdir('src')
        print("'src' folder created! ")

    # check if 'package_name' folder exists, if not create one:
    if not os.path.exists(os.path.join('src',package_name)):
        os.mkdir(os.path.join('src',package_name))

        # creats the package folder inside the src
        print("'{}' folder created! ".format(package_name))


    package_name_folder = os.path.join('src',package_name)
    open(os.path.join(package_name_folder,'__init__.py'), 'a').close() # Create __init__.py file in src\\package_name folder
    print("'__init__.py' file created! ")

    # move all the files (except the ignored files) to the package_name folder :

    with open(os.path.join(os.getcwd(),'.gitignore')) as f:
        gitignore_list = f.readlines()

    folders_ignore = [x[:-2] for x in gitignore_list if x.endswith("/\n")]
    ext_ignore = [x[1:-1] for x in gitignore_list if x.startswith("*")]

    files_to_move = []
    

    for file in os.listdir():
        ignored = False
        
        if file in ignore_list:
            continue

        for ext in ext_ignore:
            if file.endswith(ext):
                ignored = True
                break

        for folder in folders_ignore:
            if file.startswith(folder):
                ignored = True
                break

        if not ignored:
            files_to_move.append(file)
    

    for file in files_to_move:
        source = file
        destination = os.path.join(package_name_folder,file)
        shutil.move(source, destination)
        print(file," Moved to: ",destination)

    
def add_tests_folder():
    # check if the directory have this folder ('tests') - if no create one 
    if not os.path.exists('tests'):
        os.mkdir('tests')
        print("'tests' folder created! ")


def main():
    """
    CLI in Action
    
    """
    
    # Start of CLI:

    print("Welcome to HelpMePack - the Python Package Helper CLI ! ")
    print("Please make sure that: '.git' folder, README.md, .gitignore, requirments.txt, LICENSE files - are in your project directory.")
    print("All the other project files will be moved to 'src' folder.")
    print("Make sure you running in the Project Main Directory")

    # Initializing the files list to ignore when adding all the package files to 'src' folder
                                                    
    ignore_list = ['.git','README.md','.gitignore','requirements.txt','LICENSE','src','tests','pyproject.toml','setup.cfg','setup.py']

    # Checks if the package got virtual environment folder, and if so - add it to ignore list

    venv_folder_name = input("Virtual Environment folder name (if it don't have one - press Enter) : ")
    if venv_folder_name:
        ignore_list.append(str(venv_folder_name))

    # Main CLI action (Getting the info from the user):
    package_name = input("Package Name: ")
    package_version = input("Package Version (press Enter for Default - 0.0.1) : ")
    if not package_version:
        package_version = '0.0.1'
    author_name = input("Author name: ")
    author_email = input("Author Email: ")
    description = input("Package short Desription: ")
    url = input("Package url (GitHub,GitLab,etc..) : ")

    LICENSE_type = input("LICENSE type: press Enter for Default - MIT, (For Licenses list press: i) : ").lower()
    if LICENSE_type == 'i':
        licenses = [os.path.splitext(filename)[0].upper() for filename in os.listdir(LICENSE_TEMPLATE_DIRECTORY)]
        for license in licenses: print(license, end=", ")
        while LICENSE_type == 'i':
            LICENSE_type = input("press Enter for Default - MIT) : ").lower()

    python_requires = input("Python Version: (<=x.x,==x.x,>=x.x) : ")
    python_version = python_requires[2] # 2.5 is Python 2

    # gets dependencies of package
    install_requires = os.popen('pip freeze').read()
    install_requires = '\n'.join([requirement for requirement in install_requires.split('\n') if not requirement.startswith("helpmepack")]) # removing `helpmepack`` package from reqs
    
    # The HelpMePack program uses the default way of handling packaging in Python - 'src' folder:
    add_src_folder(package_name, ignore_list)

    # adds mandatory files to package root directory: 
    add_LICENSE_file(LICENSE_type)
    add_pyproject_file()
    add_README_file(package_name,author_name,description,url,install_requires)
    add_tests_folder()
    add_setup_cfg_file(package_name,package_version,author_name,author_email,description,url,python_version,LICENSE_type,python_requires,install_requires)

    print("Done!")

if __name__ == '__main__':
    main()