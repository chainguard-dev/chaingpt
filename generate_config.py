import os
import shutil
from pathlib import Path


CONFIG_DIR = os.path.join(Path.home(), ".chaingpt")


def main() -> int:
    try:
        import yaml
    except ImportError as e:
        print("This script requires pyyaml. Install with:\n\tpip install pyyaml")
        exit(-1)

    if os.path.exists(CONFIG_DIR):
        shutil.rmtree(CONFIG_DIR)
    os.mkdir(CONFIG_DIR)

    config_path = os.path.join(CONFIG_DIR, "config.yaml")
    
    with open("config_example.yaml", "r", encoding="utf-8") as f_in:
        config_data = yaml.safe_load(f_in)
        
        openai_key = input("Your OpenAI API key: ")
        config_data["secrets"]["openai_api_key"] = openai_key

        pat = input("Your GitHub personal access token: ")
        config_data["secrets"]["github_personal_access_token"] = pat
        
        with open(config_path, "w") as f_out:
            yaml.safe_dump(config_data, f_out, sort_keys=False)
        
        print(f"Configuration successfully generated at {config_path}")


if __name__ == "__main__":
    main()