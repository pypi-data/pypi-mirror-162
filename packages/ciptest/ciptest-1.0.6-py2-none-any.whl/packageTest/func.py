import os
import os.path
import click

def get_key():
    key_path = os.path.expanduser("~/.CIP/") + 'key'

    if not os.path.exists(key_path):
        raise click.ClickException('Please "cip init" commands first before using this command')
    
    with open(key_path, "r") as f:
        return f.read().strip()

def save_results(param, result):
    result_path = os.path.expanduser("~/CIP_results/")

    if not os.path.exists(result_path):
        os.mkdir(result_path)
    
    with open(result_path + str(param), "w") as f:
        f.write(result)