#!/usr/bin/python
"""
Since there are no means to modify the event trigger parameter in
the github web interface, this script modifies the webhook
parameter to respond to specified events, in addition to OR
rather than, the default, which is

    ...
    "events": ["push"]

For the hooks to trigger when a pull-request is submitted,

    ...
    "events": ["pull_request"]

"""

import copy
import logging
import json
import os
import sys

from pprint import pprint
from getpass import getpass
from urlparse import urlparse

import argh
import keyring
import requests
import yaml

from argh.decorators import arg, named
from requests.auth import HTTPBasicAuth


def gimmehooks(args, token=''):
    """ get list of existing hook urls, return list """

    items = []
    hooks_url = ("%s/repos/%s/%s/hooks?access_token=%s"
                 % (args.github, args.owner, args.repos, token))
    hooks_response = requests.get(hooks_url)

    if not hooks_response.ok:
        sys.exit("\n[ %s : %s ] doesn't exist, or something went wrong." % (args.owner, args.repos))
        keyring.set_password('hookie', 'token', '')

    return hooks_response.json()

def deletehook(args, hooks, token=''):
    """ delete specified service hooks by webhook ID number """

    match=False

    if args.delete.isdigit():
        print ("\nDeleting hook with id => %s from %s:%s "
               % (args.delete, args.owner, args.repos))

        delete_url = ("%s/repos/%s/%s/hooks/%s?access_token=%s"
                     % (args.github, args.owner, args.repos, args.delete, token))
        delete_response = requests.delete(delete_url)
        if not delete_response.ok:
            keyring.set_password('hookie', 'token', '')
        print delete_response
        if delete_response.status_code == 204:
            match = True
    else:
        print "\n! That doesn't look like a webhook id."

    if not match:
        print "\nNo hooks found to delete. Tried to delete [ %s ]" % args.delete
        urls = []
        print "Try deleting one of:"
        for hook in hooks:
            for key in hook['config'].keys():
                if 'url' in key:
                    print "  > id: [%s] -- %s: [%s]" % (hook['id'], key, hook['config'][key])


def createhook(args, hooks=None, token=''):
    """ create the webhook if it doesn't already exist """

    #check for existing, if list is given
    hookexists = False
    if hooks:
        for hook in hooks:
            if any(substring in hook['config']['url'] for substring in args.create):
                hookexists = True
                print ('%s is already a webhook url for %s:%s'
                       % (args.create, args.owner, args.repos))
                break

    if not hookexists:
        print ("\nCreating hook [ %s ] for %s -- %s "
                   % (args.create, args.owner, args.repos))
        create_url = ("%s/repos/%s/%s/hooks?access_token=%s"
                      % (args.github, args.owner, args.repos, token))
        data = {"name": "web",
                "active": True,
                "events": args.events,
                "config": {"url": "%s" % args.create,
                           "content_type": args.content_type,
                           "insecure_ssl": "1"}}
        jdata = json.dumps(data)
        create_response = requests.post(create_url, data=jdata)
        if not create_response.ok:
            keyring.set_password('hookie', 'token', '')

@named('patch')
def patch_hooks(args):
    """ now patch parameters for webhooks in hook_IDs """
    for hookID in hook_IDs:
        patch_url = ("%s/repos/%s/%s/hooks/%s?access_token=%s"
                     % (base_url, user, blueprint_name, hookID, token))
        data = {"events": ["issue_comment", "pull_request"],
                "active": True,
                "name": "web",
                "config": {"content_type": "form",
                           "insecure_ssl": "1"}}
        jdata = json.dumps(data)
        patch_response = requests.patch(patch_url, data=jdata)
        if not patch_response.ok:
            keyring.set_password('hookie', 'token', '')
        verify = requests.get(patch_url)
        verify_json = verify.json()
        if verify_json['events'] != data['events']:
            print ("exiting because\n%s\n!=\n%s"
                   % (verify_json['events'], data['events']))
            print "verification failed."
            sys.exit(1)


def auth(args):
    """ prompts for password, returns token """

    netloc = urlparse(args.github).netloc
    git_pass = getpass("%s's (%s) password: " % (args.youare, netloc))
    data = json.dumps({"scopes": ["repo"],
                       "note": "hookie"})

    auth_url = "%s/authorizations" % args.github
    auth_response = requests.post(auth_url, data=data,
                                  auth=HTTPBasicAuth(args.youare, git_pass))

    if auth_response.status_code not in range(200, 300):
        sys.exit("sorry. failed to authenticate against [ %s ]\n%s"
                 % (args.github, auth_response.reason))

    return auth_response.json()['token']


def _if_not_owner(args):
    """ youare owner if not owner """
    if not args.owner:
        args.owner = args.youare

def check_yaml(args):

    dat_yaml = 'hookie.yaml'
    if not os.path.exists(dat_yaml):
        dat_yaml = 'hookie/hookie.yaml'
        if not os.path.exists(dat_yaml):
            dat_yaml = os.path.join(os.path.dirname(__file__), 'hookie.yaml')
            if not os.path.exists(dat_yaml):
                print "Didn't find your config. Using defaults."
                return

    attrs = yaml.load(file(dat_yaml, 'r'))
    if args.github == 'https://api.github.com':
        custom_endpoint = attrs['github']
        if not custom_endpoint == 'https://github.{starshipenterprise}.com/api/v3':
            args.github = custom_endpoint

@arg('-g', '--github', help=' ',
     default='https://api.github.com')
@arg('-u', '--youare', required=True,
     help="Your github username (could be the same as _whose_ repo's "
          "webhooks you want to modify, which is indicated by --owner)")
@arg('-o', '--owner', required=False, default=None,
     help='whose repos? required if different than --youare')
@arg('-r', '--repos', nargs='+', required=True, help='name of repo(s) to modify')
def show(args):
    """ pretty-printed json webhook objects for repo """

    check_yaml(args)
    _if_not_owner(args)

    token = keyring.get_password('hookie', 'token')
    if not token:
        token = auth(args)
        keyring.set_password('hookie', 'token', token)

    repos = copy.deepcopy(args.repos)
    for item in repos:
        message = " ### WEBHOOKS ON %s:%s ###" % (args.owner, item)
        divider = "-"*len(message)
        print "%s\n%s\n%s" % (divider, message, divider)

        args.repos = item
        hooks = gimmehooks(args, token=token)

        for hook in hooks:
            print "--- ID: %s ---" % hook['id']
            pprint(hook)
            print divider

#--repos, create, delete currently only support one item
@arg('-t', '--content-type', help='content type for hook to post',
     default='form')
@arg('-e', '--events', help='Event types for the new hook(s) to trigger on',
     type=str,
     default=['issue_comment', 'pull_request'], nargs='+')
@arg('-g', '--github', help=' ',
     default='https://api.github.com')
@arg('-u', '--youare', required=True,
     help="Your github username (could be the same as _whose_ repo's "
          "webhooks you want to modify, which is indicated by --owner)")
@arg('-o', '--owner', required=False, default=None,
     help='whose repos? *required if* different than --youare')
@arg('-r', '--repos', nargs='+', required=True, help='name of repo(s) to modify')
@arg('-d', '--delete', nargs='+', required=False, default=None,
     help='webhook id to be deleted')
@arg('-c', '--create', nargs='+', required=False, help='webhook url to add')
def run(args):

    check_yaml(args)
    _if_not_owner(args)

    token = keyring.get_password('hookie', 'token')
    if not token:
        token = auth(args)
        keyring.set_password('hookie', 'token', token)

    repos = copy.deepcopy(args.repos)
    for item in repos:
        args.repos = item
        print ("fetching list of existing hooks for %s:%s"
               % (args.owner, args.repos))
        hooks = gimmehooks(args, token=token)

        if args.delete:
            delete = copy.deepcopy(args.delete)
            for item in delete:
                args.delete = item
                deletehook(args, hooks, token)

        if args.create:
            create = copy.deepcopy(args.create)
            for item in create:
                args.create = item
                createhook(args, token=token)

def main():
    argp = argh.ArghParser()
    argp.add_commands([run, patch_hooks, show])
    argp.dispatch()

if __name__ == '__main__':
    main()
#EOF
