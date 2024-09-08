import os
import requests
import json
import base64
import google.generativeai as genai

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name='gemini-1.5-pro')

def generate_readme_using_llm(prompt):
    """Generate README using an LLM like Gemini."""
    response = model.generate_content(prompt)
    return response

# GitHub API and Token
GITHUB_TOKEN = os.getenv('PAT')
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_repo_files(owner, repo_name):
    """Fetch all code files in the repository using the GitHub API."""
    files_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/main?recursive=1"
    response = requests.get(files_url, headers=HEADERS)
    
    if response.status_code == 200:
        files = response.json().get('tree', [])
        # Filter to only include code files (e.g., .py, .js, .cpp, etc.)
        code_files = [file['path'] for file in files if file['path'].endswith(('.py', '.js', '.cpp', '.java'))]
        return code_files
    else:
        print(f"Failed to fetch files for {repo_name}. Status Code: {response.status_code}")
        return []

def fetch_file_content(owner, repo_name, file_path):
    """Fetch the content of a file from the repository."""
    file_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
    response = requests.get(file_url, headers=HEADERS)
    
    if response.status_code == 200:
        file_content = base64.b64decode(response.json().get('content', '')).decode('utf-8')
        return file_content
    else:
        print(f"Failed to fetch file: {file_path}")
        return ''

def fetch_readme_content(owner, repo_name):
    """Fetch the content of the README.md file."""
    readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/README.md"
    response = requests.get(readme_url, headers=HEADERS)
    
    if response.status_code == 200:
        readme_data = response.json()
        readme_content = base64.b64decode(readme_data['content']).decode('utf-8').strip()
        return readme_content
    elif response.status_code == 404:
        return None  # README is missing
    else:
        print(f"Failed to check README for {repo_name}. Status Code: {response.status_code}")
        return None

def generate_readme_for_repo(owner, repo_name):
    """Generate a README based on code files in the repository."""
    readme_content = fetch_readme_content(owner, repo_name)
    
    # Check if README is missing, empty, or too short
    if readme_content is None or len(readme_content) == 0 or len(readme_content.split()) < 100:
        print(f"README is missing, empty, or too short for {repo_name}. Generating...")

        # Fetch all code files
        code_files = fetch_repo_files(owner, repo_name)
        
        if not code_files:
            print(f"No code files found for {repo_name}. Skipping README generation.")
            return

        # Collect code contents for the LLM prompt
        code_summary = ""
        for file_path in code_files:
            file_content = fetch_file_content(owner, repo_name, file_path)
            code_summary += f"\n### File: {file_path}\n{file_content[:500]}"  # Limit the content size for LLM

        # Generate a prompt for the LLM
        prompt = f"Generate a detailed README for the repository {repo_name}. Here are some code snippets:\n{code_summary}"
        new_readme_content = generate_readme_using_llm(prompt)

        # Save the new README file locally
        with open(f"{repo_name}_README.md", "w") as readme_file:
            readme_file.write(new_readme_content)
        
        print(f"Generated README for {repo_name}")
    else:
        print(f"README exists and is sufficient for {repo_name} (Word count: {len(readme_content.split())})")

# Fetch the list of repositories
with open('repos.json') as f:
    repos = json.load(f)

# Iterate over repositories and generate README if missing, empty, or too short
for repo in repos:
    repo_name = repo['name']
    owner = repo['owner']['login']
    generate_readme_for_repo(owner, repo_name)
