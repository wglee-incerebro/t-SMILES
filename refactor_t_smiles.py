import os
import re

def to_snake_case(name):
    """Convert CamelCase or ALLCAPS to snake_case"""
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def rename_files_and_dirs(root_dir):
    rename_map = {}

    # Step 1: Rename directories (bottom-up)
    for dirpath, dirnames, _ in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            if re.search(r'[A-Z]', dirname):
                old_dir = os.path.join(dirpath, dirname)
                new_dirname = to_snake_case(dirname)
                new_dir = os.path.join(dirpath, new_dirname)
                if old_dir != new_dir:
                    print(f"[DIR] Renaming: {old_dir} → {new_dir}")
                    os.rename(old_dir, new_dir)
                    rel_old = os.path.relpath(old_dir, root_dir)
                    rel_new = os.path.relpath(new_dir, root_dir)
                    rename_map[rel_old.replace("\\", "/")] = rel_new.replace("\\", "/")

    # Step 2: Rename .py files
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") and re.search(r'[A-Z]', filename):
                old_path = os.path.join(dirpath, filename)
                new_name = to_snake_case(os.path.splitext(filename)[0]) + ".py"
                new_path = os.path.join(dirpath, new_name)
                if old_path != new_path:
                    print(f"[FILE] Renaming: {old_path} → {new_path}")
                    os.rename(old_path, new_path)
                    rel_old = os.path.relpath(old_path, root_dir)
                    rel_new = os.path.relpath(new_path, root_dir)
                    rename_map[rel_old.replace("\\", "/")] = rel_new.replace("\\", "/")

    return rename_map

def path_to_module(path):
    """Convert relative path (with .py) to dotted import path"""
    return path.replace(".py", "").replace("/", ".").replace("\\", ".")

def update_imports(root_dir, rename_map, root_package="t_smiles"):
    module_map = {path_to_module(k): path_to_module(v) for k, v in rename_map.items()}

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            file_path = os.path.join(dirpath, filename)

            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            original_code = code

            # Step 1: Update renamed modules or folders
            for old_mod, new_mod in module_map.items():
                code = re.sub(rf'\bimport\s+{re.escape(old_mod)}\b', f'import {new_mod}', code)
                code = re.sub(rf'\bfrom\s+{re.escape(old_mod)}\b', f'from {new_mod}', code)

            # Step 2: Prefix root_package to any un-prefixed internal imports
            code = re.sub(rf'\bfrom\s+(dataset|tools|mol_utils|third_party)([\. ])',
                          rf'from {root_package}.\1\2', code)
            code = re.sub(rf'\bimport\s+(dataset|tools|mol_utils|third_party)([\. ])',
                          rf'import {root_package}.\1\2', code)

            if code != original_code:
                print(f"[UPDATE] Fixing imports in: {file_path}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)

if __name__ == "__main__":
    ROOT = "t_smiles"
    print(f"🔧 Starting full refactor of {ROOT}")
    rename_map = rename_files_and_dirs(ROOT)
    update_imports(ROOT, rename_map)
    print("✅ Refactoring complete.")
