#!/usr/bin/env python3
"""
Script to update the meeting_topic_mapping.json file with call numbers
extracted from meeting titles and organize them by series (ACDE/ACDC/ACDT).

This script:
1. Loads the mapping file
2. Processes each meeting and occurrence
3. Extracts call numbers from meeting titles
4. Updates the mapping file with these call numbers
5. Commits the changes
"""

import os
import json
import argparse
from datetime import datetime
from github import Github, InputGitAuthor
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules import recording_utils

MAPPING_FILE = "../meeting_topic_mapping.json"

def load_meeting_topic_mapping(file_path):
    """Load the mapping file from the given path"""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                return {}
    else:
        print(f"Mapping file not found at {file_path}")
        return {}

def save_meeting_topic_mapping(mapping, file_path):
    """Save the mapping to the given file path"""
    with open(file_path, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"Saved mapping to {file_path}")

def commit_mapping_file(file_path, commit_message):
    """Commit the mapping file to GitHub"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable not set")
        return False
        
    repo_name = os.environ.get("GITHUB_REPOSITORY", "ethereum/pm")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # Read file content
        with open(file_path, "r") as f:
            file_content = f.read()
        
        # Create author information
        author = InputGitAuthor(
            name="GitHub Actions Bot",
            email="actions@github.com"
        )
        
        # Get the current file to update
        github_path = ".github/ACDbot/meeting_topic_mapping.json"
        try:
            contents = repo.get_contents(github_path, ref=branch)
            # Update the file
            result = repo.update_file(
                path=github_path,
                message=commit_message,
                content=file_content,
                sha=contents.sha,
                branch=branch,
                author=author
            )
            print(f"Committed changes to {github_path}")
            return True
        except Exception as e:
            print(f"Error committing file: {e}")
            return False
    except Exception as e:
        print(f"GitHub API error: {e}")
        return False

def update_mapping_with_call_numbers(mapping, filter_series="all"):
    """
    Process all meetings in the mapping and update with call numbers
    
    Args:
        mapping: The loaded mapping file
        filter_series: Filter to a specific series ('acde', 'acdc', 'acdt', 'all')
        
    Returns:
        Tuple of (updated_mapping, update_count)
    """
    updates = 0
    
    for meeting_id, meeting_data in mapping.items():
        # Get call series from top level
        call_series = meeting_data.get("call_series", "").lower()
        
        # Filter by series if specified
        if filter_series != "all":
            # Skip if call_series doesn't match filter
            if filter_series == "acde" and "acde" not in call_series and "execution" not in call_series:
                continue
            if filter_series == "acdc" and "acdc" not in call_series and "consensus" not in call_series:
                continue
            if filter_series == "acdt" and "test" not in call_series:
                continue
        
        # Process occurrences
        if "occurrences" in meeting_data and isinstance(meeting_data["occurrences"], list):
            for i, occurrence in enumerate(meeting_data["occurrences"]):
                if not isinstance(occurrence, dict):
                    continue
                    
                # Only process if call_number is not already set
                if "call_number" not in occurrence:
                    # Get the title from the occurrence
                    title = occurrence.get("issue_title")
                    if title:
                        # Extract call number
                        call_number = recording_utils.extract_call_number(title, call_series)
                        if call_number:
                            # Update occurrence with call number
                            mapping[meeting_id]["occurrences"][i]["call_number"] = call_number
                            # Determine meeting series
                            series = recording_utils.determine_meeting_series(title, call_series)
                            series_display = {
                                "ACDE": "Execution Layer",
                                "ACDC": "Consensus Layer",
                                "ACDT": "Testing"
                            }.get(series, "Unknown")
                            print(f"Meeting ID: {meeting_id}, Occurrence: {occurrence.get('issue_number')}")
                            print(f"  Title: {title}")
                            print(f"  Extracted: Call #{call_number} ({series_display} series)")
                            updates += 1
    
    return mapping, updates

def main():
    parser = argparse.ArgumentParser(description="Update meeting_topic_mapping.json with call numbers")
    parser.add_argument("--mapping-file", default=MAPPING_FILE, help="Path to mapping file")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without saving/committing")
    parser.add_argument("--series", choices=["acde", "acdc", "acdt", "all"], default="all", 
                      help="Process only specific meeting series (default: all)")
    args = parser.parse_args()
    
    # Load mapping
    mapping = load_meeting_topic_mapping(args.mapping_file)
    if not mapping:
        print("Error: Empty or invalid mapping file")
        return
    
    # Update mapping with call numbers
    updated_mapping, update_count = update_mapping_with_call_numbers(mapping, args.series)
    
    if update_count == 0:
        print("No call numbers to update")
        return
    
    print(f"Updated {update_count} occurrences with call numbers")
    
    # Save and commit changes if not dry run
    if not args.dry_run:
        save_meeting_topic_mapping(updated_mapping, args.mapping_file)
        
        # Only commit if GITHUB_TOKEN is available
        if os.environ.get("GITHUB_TOKEN"):
            series_info = f" for {args.series.upper()} series" if args.series != "all" else ""
            commit_message = f"Update mapping with {update_count} call numbers{series_info} [automated]"
            commit_mapping_file(args.mapping_file, commit_message)
        else:
            print("GITHUB_TOKEN not set, skipping commit")
    else:
        print("Dry run - changes not saved or committed")

if __name__ == "__main__":
    main() 