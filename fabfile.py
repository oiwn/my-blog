# -*- coding: utf-8 -*-
import os
import logging

from fabric.colors import red, green
from fabric.api import env, warn, cd, prefix, local
from fabric.contrib import console
#from fabric.operations import prompt

from config import PROJECT_PATH, FREEZER_DESTINATION

logger = logging.getLogger(__name__)


def _setup_virtualenv():
	env.virtualenv = '%s/.env' % PROJECT_PATH
	env.activate = 'source %s/bin/activate ' % env.virtualenv


def init_blog_static_repo():
	with cd(os.path.join(PROJECT_PATH, FREEZER_DESTINATION)):
		local('git status')
		ask_msg = red("Init blog repo for this folder?")
		if console.confirm(ask_msg, default=False) is True:
			local('git init')
			local('git remote add origin git@github.com:istinspring/istinspring.github.io.git')


def push_blog():
	"""
	Build static blog and push new content to github
	"""

	warn(green("Update blog on github pages."))
	_setup_virtualenv()

	with cd(PROJECT_PATH):
		with prefix(env.activate):
			local('python blog.py build', shell='/bin/bash')

		local('cd {}'.format(FREEZER_DESTINATION), shell='/bin/bash')
		local('git status')
		ask_msg = red("Force push new content to blog?")
		if console.confirm(ask_msg, default=False) is True:
			local('git add --all')
			local('git commit -m "new articles"')
			local('git push --force origin master')
