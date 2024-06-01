import json
import os
import shutil
import sys
import logging
from pathlib import Path
import pexpect

def setup_logger(log_dir, log_name):
    log_path = log_dir / log_name
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # File handler for logging to a file
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Stream handler for logging to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(stream_handler)

    return logger

def execute_command_as_user(command, user, password, logger):
    try:
        if user == "root":
            child = pexpect.spawn(f'sudo -S {command}', encoding='utf-8')
            child.expect('Password:')
            child.sendline(password)
        else:
            child = pexpect.spawn(f'su - {user} -c "{command}"', encoding='utf-8')
            child.expect('Password:')
            child.sendline(password)
        child.logfile = sys.stdout
        child.logfile_read = sys.stdout
        child.expect(pexpect.EOF)
        child.close()
        return child.exitstatus == 0
    except pexpect.exceptions.EOF:
        logger.error("Command execution failed with EOF.")
        return False
    except pexpect.exceptions.TIMEOUT:
        logger.error("Command execution failed with TIMEOUT.")
        return False
    except pexpect.exceptions.ExceptionPexpect as e:
        logger.error(f"Command execution failed: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 updater.py <path_to_json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.is_file():
        print(f"Error: File {json_path} does not exist.")
        sys.exit(1)

    with open(json_path) as json_file:
        data = json.load(json_file)

    update_dir = Path(data["update_dir"])
    if not update_dir.is_dir():
        print(f"Error: Directory {update_dir} does not exist.")
        sys.exit(1)

    log_dir = Path(__file__).parent / "update_log"
    log_dir.mkdir(exist_ok=True)

    main_logger = setup_logger(log_dir, "main.log")

    passwords = data.get("passwords", {})

    # Process replace section
    if "replace" in data:
        for src_relative, dest_full in data["replace"].items():
            src_path = update_dir / src_relative
            dest_path = Path(dest_full)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            main_logger.info(f"Replaced {dest_path} with {src_path}")

    # Process remove section
    if "remove" in data:
        for remove_path in data["remove"]:
            remove_path = Path(remove_path)
            if remove_path.exists():
                if remove_path.is_file():
                    remove_path.unlink()
                    main_logger.info(f"Removed file {remove_path}")
                elif remove_path.is_dir():
                    shutil.rmtree(remove_path)
                    main_logger.info(f"Removed directory {remove_path}")

    # Process execute section
    if "execute" in data:
        for user, command in data["execute"].items():
            exec_log_name = f"execute_{user}.log"
            exec_logger = setup_logger(log_dir, exec_log_name)
            password = passwords.get(user, "")
            success = execute_command_as_user(command, user, password, exec_logger)
            if success:
                main_logger.info(f"Executed command '{command}' as user '{user}'")
            else:
                main_logger.error(f"Failed to execute command '{command}' as user '{user}'")

if __name__ == "__main__":
    main()
