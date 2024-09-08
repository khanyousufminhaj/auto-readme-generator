import requests
import os
import json

import google.generativeai as genai
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name='gemini-1.5-pro')

def generate_readme_using_llm(prompt):
    response=model.generate_content(prompt)
    return response
# GitHub API and Token
GITHUB_TOKEN = os.getenv('PAT')
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Fetch repositories
with open('repos.json') as f:
    repos = json.load(f)

# Iterate over repositories
for repo in repos:
    repo_name = repo['name']
    owner = repo['owner']['login']

    # Check if README.md exists
    readme_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/README.md"
    response = requests.get(readme_url, headers=HEADERS)
    
    if response.status_code == 404:  # README doesn't exist
        print(f"README not found for {repo_name}. Generating...")

        # Generate README using LLM (GEMINI or OpenAI)
        prompt = f"Generate a README for the repository {repo_name}."
        readme_content = generate_readme_using_llm(prompt)  # Replace with your LLM call

        # Save the README file
        with open(f"{repo_name}_README.md", "w") as readme_file:
            readme_file.write(readme_content)

        # Mark the repo for pushing the new README
        print(f"Generated README for {repo_name}")
    else:
        print(f"README already exists for {repo_name}")
