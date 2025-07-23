#!/usr/bin/env python3

# --- INSTRUCTIONS ---
# Set up the ignore file extensions
# Set up patterns, ignore extensions, ignore folder
# Run the following commands
# chmod +x inspect_files_recursive.py
# ./inspect_files_recursive_2.py /...folder....


import re
import argparse
import os

# --- IGNORE FILE TYPES ---
# Ignore any file that has one of the following extensions
IGNORE_FILE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.zip', '.gz', '.tar', 
                          '.exe', '.dll', '.o', '.so', '.class', '.mp3', '.mp4', '.mov', 
                          '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                          '.iso', '.dmg', '.svg', '.webp', '.DS_Store', '.ttf',
                          '.pbxproj', '.xcuserstate', '.resolved']
# ---------------------------------


# --- PATTERNS TO CHECK ---
# Add your regex patterns here.
# Key: descriptive name, Value: raw regex string.
PATTERNS = {
    "Email Address": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IPv4 Address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "8 digit number": r"\\b\\d{8}\\b", # Matches student id
    "authcate": r"\\b\\w{4}\\d{4}\\b",
    "API key": r"\\b[A-Za-z0-9]{32,}\\b",
    "API key 2": r"[\"\']?([A-Za-z0-9_\-]{60,})={0,2}[\"\']?",
    "Credit cards": r"\\b(?:\\d[ -]*?){13,16}\\b",
    "JWT tokens": r"\\b[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\b",
    "Passwords in code": r"\\b(?:password|passwd|pwd|secret|api_key|apikey|token|auth_token|access_token|private_key)\\b",
    # --- ADD MORE PATTERNS BELOW ---
    # "Your Pattern Name": r"your_regex_pattern",
}
# -------------------------

# --- IGNORE PATTERNS FOR MATCHES ---
# For each key from PATTERNS, you can specify a list of regex strings.
# If a string matched by a PATTERN also matches ANY of these ignore regexes,
# that specific match will be discarded.
IGNORE_PATTERNS_FOR_MATCH = {
    "Email Address": [
        r"\.(png|jpg|jpeg|gif|svg|webp)$",  # Ends with common image extensions
        r"dummy@",                          # Contains dummy@
        r"gary@monash.edu",
        r"'Test.Test@idmqat.monash.edu",
        r"johndoe@john.com",
        # Add more ignore patterns specific to "Email Address" matches
    ],
    "URL": [
        r"localhost",                       # Contains "localhost"
        r"127\.0\.0\.1",                     # Contains "127.0.0.1"
        r"\.(png|jpg|jpeg|gif|css|js)$",   # Often, URLs ending in these are not what we're looking for as standalone "URL" findings
        # Add more ignore patterns specific to "URL" matches
    ],
    "API key 2": [
        r"^test_.*"
    ],
    # "PATTERN_NAME_FROM_ABOVE": [ r"ignore_regex1", r"ignore_regex2" ],
}
# ---------------------------------

# --- FOLDERS TO IGNORE ---
# List of folder names or relative paths (from the initial scan root) to completely ignore.
# If a directory's name matches an entry, or its path relative to the
# scan root matches an entry, it and all its contents will be skipped.
# - Use forward slashes '/' for paths; they will be normalized.
# - Examples: "Pods", "build/Release", ".git"
IGNORE_FOLDERS = [
    ".git",
    ".hg",
    "venv",
    "env",
    "Pods",              # Ignores any folder named "Pods"
    "build",             # Ignores any folder named "build"
    "DerivedData",       # Common for Xcode projects
    "xcuserdata",       # Common for Xcode projects
    "project.xcworkspace", # Common for Xcode projects (often a dir)
]
# -------------------------


def inspect_file(filepath, relative_path_for_display=None):
    """
    Inspects a single file for predefined regex patterns, filters matches
    using ignore patterns, and logs valid matches.
    """
    # This function remains largely the same as the previous version
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'") # Should be rare if called by os.walk
        return
    if not os.path.isfile(filepath):
        print(f"Error: '{filepath}' is not a file.") # Should be rare
        return

    display_name = relative_path_for_display if relative_path_for_display else os.path.basename(filepath)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file '{display_name}': {e}")
        return

    if not content.strip():
        return

    found_any_valid_match_in_file = False

    for pattern_name, regex_pattern in PATTERNS.items():
        try:
            compiled_regex = re.compile(regex_pattern)
        except re.error as e:
            print(f"Error compiling primary regex for '{pattern_name}': {e}. Skipping this pattern.")
            continue

        initial_matches = []
        try:
            for match_obj in compiled_regex.finditer(content):
                initial_matches.append(match_obj.group(0))
        except Exception as e:
            print(f"Error during regex search for '{pattern_name}' in '{display_name}': {e}")
            continue

        if not initial_matches:
            continue

        final_matches_for_this_pattern = []
        ignore_regex_list_for_current_pattern = IGNORE_PATTERNS_FOR_MATCH.get(pattern_name, [])

        for matched_string in initial_matches:
            should_be_ignored = False
            for ignore_regex_str in ignore_regex_list_for_current_pattern:
                try:
                    compiled_ignore_regex = re.compile(ignore_regex_str)
                    if compiled_ignore_regex.search(matched_string):
                        should_be_ignored = True
                        break
                except re.error as e:
                    print(f"Warning: Invalid ignore regex '{ignore_regex_str}' for pattern '{pattern_name}': {e}.")
            
            if not should_be_ignored:
                final_matches_for_this_pattern.append(matched_string)

        if final_matches_for_this_pattern:
            if not found_any_valid_match_in_file:
                print(f"\n--- Matches found in File: '{display_name}' ---")
                found_any_valid_match_in_file = True

            print(f"  Pattern: '{pattern_name}'")
            for valid_match_string in final_matches_for_this_pattern:
                print(f"    Matched String: '{valid_match_string}'")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect files for regex patterns, with filtering and folder ignoring."
    )
    parser.add_argument(
        "target_path",
        help="The path to the file or directory to inspect."
    )
    parser.add_argument(
        "--skip-ext",
        nargs='*',
        default=IGNORE_FILE_EXTENSIONS,
        help="List of file extensions to skip. Provide space-separated values."
    )
    args = parser.parse_args()

    target_path = os.path.abspath(os.path.expanduser(args.target_path)) # Normalize and expand ~
    skip_extensions = [ext.lower() for ext in args.skip_ext] if args.skip_ext else []
    
    # Normalize IGNORE_FOLDERS for consistent matching.
    # Store both original (for printing) and normalized (for matching).
    normalized_ignore_folders = [os.path.normpath(p) for p in IGNORE_FOLDERS]


    if not os.path.exists(target_path):
        print(f"Error: Path not found: '{target_path}'")
        return

    if os.path.isfile(target_path):
        # For a single file, we generally don't apply folder ignore logic unless it's explicitly requested.
        # The current IGNORE_FOLDERS logic is primarily for pruning directory traversal.
        # If you want to check if a single file is within an "ignored path structure", that's more complex.
        # For now, we process it if its extension isn't skipped.
        file_ext = os.path.splitext(target_path)[1].lower()
        if file_ext in skip_extensions:
            print(f"Skipping single file '{target_path}' due to its extension ('{file_ext}').")
            return

        print(f"Inspecting single file: '{target_path}'")
        inspect_file(target_path)

    elif os.path.isdir(target_path):
        print(f"\nInspecting directory (and subdirectories): '{target_path}'")
        if IGNORE_FOLDERS: # Only print if there are folders to ignore
             print(f"Ignoring folders matching patterns: {', '.join(IGNORE_FOLDERS)}")
        if skip_extensions:
            print(f"Skipping files with extensions: {', '.join(skip_extensions)}")

        files_processed_count = 0
        for dirpath, dirnames_original, filenames in os.walk(target_path, topdown=True):
            # `topdown=True` is default, but explicit. Allows modifying `dirnames` to prune search.

            # --- Filter dirnames to prevent descending into ignored folders ---
            # `dirnames_original` is the list of subdirectories in `dirpath` from `os.walk`.
            # We modify `dirnames` (which `os.walk` uses for further recursion) in-place.
            
            dirs_to_visit_after_filtering = []
            for d_name in dirnames_original:
                full_subdir_path = os.path.join(dirpath, d_name)
                # Path of the subdirectory relative to the initial `target_path` (scan root)
                relative_subdir_path_from_scan_root = os.path.normpath(os.path.relpath(full_subdir_path, target_path))

                should_skip_this_subdir = False
                for ignore_pattern in normalized_ignore_folders:
                    # Check 1: Is the directory name itself an explicitly ignored name? (e.g., "Pods")
                    if d_name == ignore_pattern:
                        should_skip_this_subdir = True
                        break
                    # Check 2: Is the directory's path (relative to scan root) an ignored path pattern?
                    # (e.g., ignore_pattern "build/frameworks", relative_subdir_path_from_scan_root is "build/frameworks")
                    if relative_subdir_path_from_scan_root == ignore_pattern:
                        should_skip_this_subdir = True
                        break
                
                if not should_skip_this_subdir:
                    dirs_to_visit_after_filtering.append(d_name)
            
            dirnames_original[:] = dirs_to_visit_after_filtering # Crucial: modify in-place
            # --- End of dirname filtering ---

            # Now process files in the current (potentially non-ignored) dirpath
            for filename in filenames:
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in skip_extensions:
                    continue

                filepath = os.path.join(dirpath, filename)
                relative_filepath_for_display = os.path.relpath(filepath, start=target_path)
                inspect_file(filepath, relative_path_for_display=relative_filepath_for_display)
                files_processed_count += 1
        
        print(f"\nFinished inspecting directory. Processed {files_processed_count} applicable file(s).")
    else:
        print(f"Error: '{target_path}' is not a valid file or directory.")

if __name__ == "__main__":
    main()