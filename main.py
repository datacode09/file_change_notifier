import logging
from configparser import ConfigParser
from datetime import datetime, timedelta
from pathlib import Path

def configure_logging(log_directory):
    current_date = datetime.now().strftime('%Y_%m_%d')
    log_filename = f'file_changes_log_{current_date}.log'
    logging.basicConfig(filename=log_directory / log_filename,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

def read_config(config_file_path):
    config = ConfigParser()
    try:
        config.read(config_file_path)
        # Assuming 'Paths' is a section in your INI file
        paths_config = {key: value for key, value in config['Paths'].items()}
    except FileNotFoundError as e:
        logging.error(f"Config file not found: {e}")
        raise
    except KeyError as e:
        logging.error(f"Missing expected section or keys in config file: {e}")
        raise
    return paths_config

def find_modified_files(directories, cutoff_time):
    modified_files = []
    for directory in directories:
        for path in Path(directory).rglob('*'):
            if path.suffix in ['.py', '.sh'] and path.stat().st_mtime > cutoff_time.timestamp():
                modified_files.append(path)
    return modified_files

def write_modified_files_list(modified_files, output_file_path):
    try:
        with output_file_path.open('w') as file:
            for modified_file in modified_files:
                file.write(f"{modified_file}\n")
    except Exception as e:
        logging.error(f"Failed to write modified files list: {e}")
        raise

def main():
    # Fixed path for the config file based on the given requirement
    config_file_path = Path('/CONFIG/config.ini')

    # Read config and setup directories
    config = read_config(config_file_path)
    directories_to_scan = config['directories_to_scan'].split(',')
    log_path = Path(config.get('log_path', 'LOG'))
    modified_files_path = Path(config.get('modified_files_path', 'MODIFIED_FILE_LIST'))

    log_path.mkdir(exist_ok=True)
    modified_files_path.mkdir(exist_ok=True)
    configure_logging(log_path)

    cutoff_time = datetime.now() - timedelta(days=1)

    modified_files = find_modified_files(directories_to_scan, cutoff_time)
    if modified_files:
        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        output_filename = f"{timestamp}.txt"
        write_modified_files_list(modified_files, modified_files_path / output_filename)
        logging.info(f"Found and logged {len(modified_files)} modified files.")
    else:
        logging.info("No modified files found.")

if __name__ == "__main__":
    main()
