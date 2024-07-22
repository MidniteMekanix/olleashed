import os
import requests
from bs4 import BeautifulSoup
from ollama import Client
import pyperclip
import usb.core
import usb.util
import duckduckgo_search
import logging
from configparser import ConfigParser
import subprocess
import shlex

# Initialize configuration
config = ConfigParser()
config.read('config.ini')

# Set up logging
logging.basicConfig(filename='olleashed.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Ollama Client
client = Client(host=config.get('Ollama', 'host', fallback='http://localhost:11434'))

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return f"Error reading file: {e}"

def web_search(query):
    try:
        return duckduckgo_search.query(query, num_results=5)
    except Exception as e:
        logging.error(f"Error performing web search: {e}")
        return f"Error performing web search: {e}"

def web_scrape(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.text
    except Exception as e:
        logging.error(f"Error scraping web page: {e}")
        return f"Error scraping web page: {e}"

def list_usb_devices():
    try:
        devices = usb.core.find(find_all=True)
        return [usb.util.get_string(dev, 256, dev.iProduct) for dev in devices]
    except Exception as e:
        logging.error(f"Error listing USB devices: {e}")
        return f"Error listing USB devices: {e}"

def create_and_run_python_code(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        return exec_globals.get('result', 'Code executed successfully.')
    except Exception as e:
        logging.error(f"Error executing Python code: {e}")
        return f"Error executing Python code: {e}"

def interact_with_files(command):
    parts = command.split(' ')
    if parts[0] == '/file':
        file_path = ' '.join(parts[1:])
        return read_file(file_path)
    elif parts[0] == '/search':
        query = ' '.join(parts[1:])
        return web_search(query)
    elif parts[0] == '/web':
        url = ' '.join(parts[1:])
        return web_scrape(url)
    elif parts[0] == '/usb':
        return list_usb_devices()
    elif parts[0] == '/generate':
        prompt = ' '.join(parts[1:])
        return client.generate(model=config.get('Ollama', 'model', fallback='llama3-groq-tool-use:latest'), prompt=prompt)
    elif parts[0] == '/chat':
        message = ' '.join(parts[1:])
        return client.chat(model=config.get('Ollama', 'model', fallback='llama3-groq-tool-use:latest'), messages=[{'role': 'user', 'content': message}])
    elif parts[0] == '/embeddings':
        prompt = ' '.join(parts[1:])
        return client.embeddings(model=config.get('Ollama', 'model', fallback='llama3-groq-tool-use:latest'), prompt=prompt)
    elif parts[0] == '/list':
        return client.list()
    elif parts[0] == '/show':
        model = parts[1]
        return client.show(model)
    elif parts[0] == '/create':
        modelfile = ' '.join(parts[1:])
        return client.create(model='example', modelfile=modelfile)
    elif parts[0] == '/copy':
        src_model, dest_model = parts[1], parts[2]
        return client.copy(src_model, dest_model)
    elif parts[0] == '/delete':
        model = parts[1]
        return client.delete(model)
    elif parts[0] == '/pull':
        model = parts[1]
        return client.pull(model)
    elif parts[0] == '/push':
        model = parts[1]
        return client.push(model)
    elif parts[0] == '/ps':
        return client.ps()
    elif parts[0] == '/run':
        code = ' '.join(parts[1:])
        return create_and_run_python_code(code)
    elif parts[0] == '/exec':
        command_to_exec = ' '.join(parts[1:])
        return execute_shell_command(command_to_exec)
    elif parts[0] == '/help':
        return display_help()
    else:
        return "Error: Unknown command. Type '/help' for a list of available commands."

def execute_shell_command(command):
    try:
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        logging.error(f"Error executing shell command '{command}': {e}")
        return f"Error executing shell command: {e}"

def display_help():
    help_text = """
    Available Commands:
    /file <path>: Reads and displays the content of the specified file.
    /search <query>: Performs a web search using DuckDuckGo.
    /web <url>: Scrapes the title from the specified URL.
    /usb: Lists connected USB devices.
    /generate <prompt>: Generates text based on the provided prompt using the specified model.
    /chat <message>: Engages in a conversational interaction with the model.
    /embeddings <prompt>: Retrieves embeddings for a given prompt.
    /list: Lists available models.
    /show <model>: Shows details about a specific model.
    /create <modelfile>: Creates a new model from a model file.
    /copy <src_model> <dest_model>: Copies a model.
    /delete <model>: Deletes a model.
    /pull <model>: Pulls a model from a remote repository.
    /push <model>: Pushes a model to a remote repository.
    /ps: Lists running processes.
    /run <code>: Creates and runs Python code.
    /exec <command>: Executes a shell command.
    /help: Displays this help message.
    /exit: Exits the application.
    """
    return help_text

def main():
    print("Welcome to the CLI application using llama3-groq-tool-use:latest model!")
    while True:
        command = input("Enter command: ")
        if command == '/exit':
            break
        response = interact_with_files(command)
        if response:
            print(response)

if __name__ == '__main__':
    main()

