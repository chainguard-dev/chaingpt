# ChainGPT

### Overview
---
An LLM chatbot connected to your GitHub repository of choice. Use ChainGPT to explore directories, read files, execute shell code and more!

### Setup
---

1. Clone the repository
```
git clone https://github.com/paulgibert/chaingpt.git
```

2. Run `generate_config.py` and specify your [OpenAI API key](https://platform.openai.com/docs/quickstart?context=python) and [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). The API key is used to access GPT-4 and the token is used for GitHub's API.
```
cd chaingpt
python3 generate_config.py
Your OpenAI API key: [OPENAI API KEY]
Your GitHub personal access token: [GITHUB PAT]
Configuration successfully generated at .../chaingpt/config.yaml
```

3. Install the package

Globally:
```
pip install .
```

Virtual Environment:
```
pip install venv
python -m venv env
source env/bin/activate
pip install .
```

### Usage
```
chaingpt [GITHUB REPO]
```

### Quickstart
Let's use ChainGPT to analyze the [Grype](https://github.com/anchore/grype.git) repository.

Follow the setup instructions to install ChainGPT, then launch the application with Grype's URL:

```
python -m chaingpt https://github.com/anchore/grype.git
Building local Wolfi package index: 100%|█████████████████████████████████████| 2386/2386 [00:10<00:00, 217.06it/s]

Welcome to ChainGPT! Provide a prompt or type `exit` to quit.
Enter a prompt > |
```

Let's ask ChainGPT to describe the project:

```
Enter a prompt > Describe this project.
📄 Analyzing README.md: What is this project about?
Processing large file in chunks: 100%|█████████████████████████████████████████████████| 3/3 [01:18<00:00, 26.23s/it]
```

ChainGPT uses the `file_qa` tool to analyze the `README.md`. The file is large, so ChainGPT processes it in chunks. We receive a response in green:

```
The project is about Grype, a customizable vulnerability scanner.
It can be configured to exit with an error if any vulnerabilities are
reported at or above a specified severity level, and can ignore certain
matches based on various criteria. Grype can report only vulnerabilities
that have a confirmed fix or those that do not have a confirmed fix.
It uses a local database to perform vulnerability scans and supports
shell completion. It can pull images from private registries using
configured credentials and can be configured to access private registries
without the need for a docker daemon. Future plans for Grype include the
development of support for allowlist and package mapping.
```

ChainGPT has several tools that allow for powerful repository interactions.
Feel free to explore!