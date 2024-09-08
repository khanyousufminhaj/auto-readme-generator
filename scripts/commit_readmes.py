import os
import subprocess

# Commit and push the README files to each repo
for repo in os.listdir():
    if repo.endswith('_README.md'):
        repo_name = repo.replace('_README.md', '')
        readme_path = f"{repo_name}_README.md"

        # Clone the repository
        subprocess.run(["git", "clone", f"https://{GITHUB_TOKEN}@github.com/your-username/{repo_name}.git"])
        os.chdir(repo_name)

        # Copy the README file and push
        subprocess.run(["cp", f"../{readme_path}", "README.md"])
        subprocess.run(["git", "add", "README.md"])
        subprocess.run(["git", "commit", "-m", "Auto-generate README"])
        subprocess.run(["git", "push"])

        # Return to original directory
        os.chdir("..")
