import logging
from configparser import ConfigParser, NoSectionError
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
    if not config.read(config_file_path):
        error_msg = f"Could not read config file or file is empty: {config_file_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    # Check for the 'Paths' section
    if 'Paths' not in config:
        error_msg = f"'[Paths]' section is missing in the config file: {config_file_path}"
        logging.error(error_msg)
        raise NoSectionError(error_msg)
    return {key: value for key, value in config.items('Paths')}

def find_modified_files(directories, cutoff_time):
    modified_files = []
    for directory in directories:
        for path in Path(directory).rglob('*'):
            if path.suffix in ['.py', '.sh'] and path.stat().st_mtime > cutoff_time.timestamp():
                modified_files.append(path)
    return modified_files

def write_modified_files_list(modified_files, output_file_path):
    with output_file_path.open('w') as file:
        for modified_file in modified_files:
            file.write(f"{modified_file}\n")

def main():
    try:
        config_file_path = Path('/CONFIG/config.ini')
        config = read_config(config_file_path)
        directories_to_scan = config.get('directories_to_scan', '').split(',')
        log_path = Path(config.get('log_path', 'LOG'))
        modified_files_path = Path(config.get('modified_files_path', 'MODIFIED_FILE_LIST'))

        log_path.mkdir(exist_ok=True)
        modified_files_path.mkdir(exist_ok=True)
        configure_logging(log_path)

        if not directories_to_scan:
            logging.warning("No directories specified for scanning. Check your config.ini file.")

        cutoff_time = datetime.now() - timedelta(days=1)
        modified_files = find_modified_files(directories_to_scan, cutoff_time)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise
    finally:
        if 'modified_files' in locals() and modified_files:
            timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            output_filename = f"{timestamp}.txt"
            write_modified_files_list(modified_files, modified_files_path / output_filename)
            logging.info(f"Found and logged {len(modified_files)} modified files.")
        else:
            logging.info("No modified files found or an error occurred before file scanning.")
        logging.info("Script execution completed.")

if __name__ == "__main__":
    main()
