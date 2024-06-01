import os
import json
import argparse
import time

def log(message, log_file):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'[{timestamp}] {message}\n'
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_message)

def create_directory(directory_path, log_file):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        log(f'Created directory: {directory_path}', log_file)

def build_file_tree(node, parent_path, log_file):
    inodes = 0
    if node['type'] == 'file':
        file_path = os.path.join(parent_path, node['name'])
        with open(file_path, 'w'):
            pass
        inodes += 1
        log(f'Created file: {file_path}', log_file)
    else:
        dir_path = os.path.join(parent_path, node['name'])
        create_directory(dir_path, log_file)
        inodes += 1
        for child in node['children']:
            child_inodes = build_file_tree(child, dir_path, log_file)
            inodes += child_inodes
    return inodes

def deploy_tree(json_path, deploy_path):
    log_file = os.path.join(deploy_path, 'deploy_log.txt')
    with open(json_path, 'r', encoding='utf-8') as f:
        tree = json.load(f)
    
    create_directory(deploy_path, log_file)
    log(f'Started deploying tree from {json_path} to {deploy_path}', log_file)
    total_inodes = build_file_tree(tree, deploy_path, log_file)
    log(f'Finished deploying tree. Total used inodes: {total_inodes}', log_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy JSON tree into directory')
    parser.add_argument('json_path', help='Path to the JSON file containing the tree')
    parser.add_argument('deploy_path', help='Path to deploy the tree')
    
    args = parser.parse_args()
    deploy_tree(args.json_path, args.deploy_path)
