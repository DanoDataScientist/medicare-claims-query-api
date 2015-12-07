"""Fabric configuration file for automated deployment."""
import subprocess, sys, os
from fabric.api import run, sudo, put, env, require, local, settings
from fabric.contrib.files import exists

# Location of Git repo to clone project from
GIT_ORIGIN = "https://github.com"
GIT_REPO = "nsh87/medicare-claims-query-api"

# Packages on install on server
INSTALL_PACKAGES = [
    "ntp",
    "python2.7-dev",
    "libxml2-dev",
    "libxslt1-dev",
    "python-libxml2",
    "python-setuptools",
    "git-core",
    "build-essential",
    "libxml2-dev",
    "libpcre3-dev",
    "libpcrecpp0",
    "libssl-dev",
    "zlib1g-dev",
    "libgeoip-dev",
    "supervisor",
    "postgresql-client",
    "python-psycopg2",
    "libpq-dev",
    "libffi-dev",
]

VAGRANT_PACKAGES =[
    "postgresql",
    "postgresql-contrib",
]

# Vagrant environment
def vagrant():
    raw_ssh_config = subprocess.Popen(['vagrant', 'ssh-config'], stdout=subprocess.PIPE).communicate()[0]
    ssh_config_list = [l.strip().split() for l in raw_ssh_config.split("\n") if l]
    ssh_config = dict([x for x in ssh_config_list if x != []])
    env.repo = ("env.medicare-api.com", "origin", "master")
    env.virtualenv, env.parent, env.branch = env.repo
    env.base = "/server"
    env.user = ssh_config["User"]
    env.hosts = ["127.0.0.1:%s" % (ssh_config["Port"])]
    env.key_filename = ssh_config["IdentityFile"]
    env.git_origin = GIT_ORIGIN
    env.git_repo = GIT_REPO
    env.dev_mode = True
    env.settings = 'vagrant'
    env.dbhost = 'medicare.chtdutbma0ig.us-west-2.rds.amazonaws.com'  # Change
    env.dbname = 'BENEFICIARYDATA'  # Change accordingly (RDS)
    env.dbuser = 'nikhil'  # Change accordingly (RDS)
    env.dbpass = None


def aws():
    env.hosts = ['52.32.95.188']  # Change accordingly (EC2)
    env.repo = ('env.medicare-api.com', 'origin', 'production')
    env.virtualenv, env.parent, env.branch = env.repo
    env.base = '/server'
    env.user = 'ubuntu'
    env.git_origin = GIT_ORIGIN
    env.git_repo = GIT_REPO
    env.dev_mode = False
    pem = os.path.join('/', 'Users', 'Nikhil', '.ssh', 'aws.pem')  # Change
    env.key_filename = pem
    env.settings = 'production'
    env.dbhost = 'medicare.chtdutbma0ig.us-west-2.rds.amazonaws.com'  # Change
    env.dbname = 'BENEFICIARYDATA'  # Change accordingly (RDS)
    env.dbuser = 'nikhil'  # Change accordingly (RDS)
    env.dbpass = None


def ssh():
    """SSH into a given environment."""
    require('hosts', provided_by=[vagrant, aws])
    cmd = "ssh -p {0} -i {1} {2}@{3}".format(
             2222 if env.dev_mode else 22,
             env.key_filename,
             env.user,
             env.hosts[0].split(':')[0]
    )
    local(cmd)


def bootstrap():
    """Initialize the server or VM."""
    require('hosts', provided_by=[vagrant, aws])
    sub_install_packages()
    sub_make_virtualenv()
    if not env.dev_mode:
        sub_clone_repo()
    sub_link_project()
    sub_install_requirements()


def sub_install_packages():
    """Install the necessary packages on the host."""
    require('hosts', provided_by=[vagrant, aws])
    package_str = " ".join(INSTALL_PACKAGES)
    # If Vagrant, install Postgres server so you can host DB on VM
    if env.dev_mode:
        package_str += " " + " ".join(VAGRANT_PACKAGES)
    sudo("apt-get update")
    sudo("apt-get -y upgrade")
    sudo("apt-get -y install " + package_str)
    sudo("easy_install pip")
    sudo("pip install pyopenssl ndg-httpsclient pyasn1")
    sudo("pip install virtualenv")


def sub_make_virtualenv():
    """Make a virtualenv for the project."""
    sudo("if [ ! -d %(base)s ]; then mkdir -p %(base)s; "
         "chmod 777 %(base)s; fi" % env)
    run("if [ ! -d %(base)s/%(virtualenv)s ]; "
        "then virtualenv %(base)s/%(virtualenv)s; fi" % env)
    sudo("chmod 777 %(base)s/%(virtualenv)s" % env)


def sub_link_project():
  """Link the project into the virtual env."""
  run("if [ ! -d %(base)s/%(virtualenv)s/project ]; "
      "then ln -f -s /project %(base)s/%(virtualenv)s/project; fi" % env)


def sub_clone_repo():
    """Clone the repositories into the virtualenv at /project."""
    run("cd %(base)s/%(virtualenv)s; "
        "git clone %(git_origin)s/%(git_repo)s project; "
        "cd project; git checkout %(branch)s; "
        "git pull %(parent)s %(branch)s" % env)


def sub_install_requirements():
  """Install the Python requirements for the project."""
  sudo("cd %(base)s/%(virtualenv)s; source bin/activate; "
       "pip install pyopenssl ndg-httpsclient pyasn1; "  # Make SSL secure
       "pip install -r project/requirements.txt" % env)
