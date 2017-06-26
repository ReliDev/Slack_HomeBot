#!/usr/bin/env python
"""
 A simple slackbot to run commands for home automation or homelab use.

 Original code by Matt Makai, taken from here:
 https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

"""
import os
import sys
import subprocess
from time import asctime
import yaml
from slackclient import SlackClient

# bot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"

def loadconfig():
    """
        Load our configuration file.
    """
    try:
        configfile = open("config.yml", "r")
        configdata = yaml.load(configfile)
    except:
        print "Error: couldn't open our configuration file"
        sys.exit(1)
    return configdata

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def message(response, channel):
    """
       Send a message to a slack channel.
    """
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def run_task(command, name, channel):
    """
       Run a user-defined Ansible playbook by waiting for a command from a client on slack.
    """
    subcommand = command.split()
    process = subprocess.Popen(subcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() != None:
            break
        if output != '':
            code = output.rstrip('\n')
            message("`"+code+"`\n", channel)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    configdata = loadconfig()
    if slack_client.rtm_connect():
        print "Bot connected and running!"
        while True:
            try:
                command, channel = parse_slack_output(slack_client.rtm_read())
            except Exception as err:
                print err.__doc__
                print err.message
            if command and channel:
                runAttempt = False
                valid_commands = ['reloadconfig']
                for defined_command in configdata['commands']:
                    valid_commands.append(defined_command['slack_command'])
                    if command == defined_command['slack_command']:
                        runAttempt = True
    	                print "%s: Attempting to run command: '%s (%s)' from channel: '%s'" % (asctime(), command, defined_command['run_command'], channel)
                        run_task(defined_command['run_command'], defined_command['name'], channel)
                else:
                    if command == 'reloadconfig':
                        runAttempt = True
                        configdata = loadconfig()
                        response = "Attempting to reload our configuration from config.yml"
                        message(response, channel)
                    if not runAttempt:
                        response = "My currently supported commands are: %s " % (",".join(valid_commands))
                        message(response, channel)
