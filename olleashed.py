import os
import requests
from bs4 import BeautifulSoup
from ollama import Client  # Correct import
import pyperclip
import usb.core
import usb.util
import duckduckgo_search

# Initialize Ollama Client
client = Client(host='http://localhost:11434')  # Adjust host if necessary

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def web_search(query):
    return duckduckgo_search.query(query, num_results=5)

def web_scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.title.text

def list_usb_devices():
    devices = usb.core.find(find_all=True)
    return [dev for dev in devices]

def interact_with_files(command):
    if command.startswith('/file'):
        file_path = command.split(' ')[1]
        return read_file(file_path)
    elif command.startswith('/search'):
        query = ' '.join(command.split(' ')[1:])
        return web_search(query)
    elif command.startswith('/web'):
        url = command.split(' ')[1]
        return web_scrape(url)
    elif command.startswith('/usb'):
        return list_usb_devices()

def main():
    print("Welcome to the CLI application using llama3-groq-tool-use:latest model!")
    while True:
        command = input("Enter command: ")
        if command == '/exit':
            break
        response = interact_with_files(command)
        if response:
            print(response)
        else:
            # Interact with Ollama model
            response = client.generate(model='llama3-groq-tool-use:latest', prompt=command)
            print(response)

if __name__ == '__main__':
    main()
