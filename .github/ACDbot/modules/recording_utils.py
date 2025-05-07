import os
import re
import json
from datetime import datetime
import webvtt

# Dictionary of common corrections for technical terms in transcripts
TRANSCRIPT_CORRECTIONS = {
    # Ethereum terms
    "ether ?am": "Ethereum",
    "ethi ?am": "Ethereum",
    "etherium": "Ethereum",
    "ethereal": "Ethereum",
    "eat ?three ?m": "Ethereum",
    "east ?star": "EastStable",
    "ether ?scan": "Etherscan",
    "gas ?feet": "gas fees",
    "solidity": "Solidity",
    "dev ?ups": "devops",
    "beacon ?chain": "Beacon Chain",
    "b ?cam": "Beacon",
    "east ?port": "EastPort",
    "l two": "L2",
    "l1": "L1",
    "l2": "L2",
    "e ?vm": "EVM",
    "e ?1p": "EIP",
    "e ?ip": "EIP",
    "web three": "web3",
    "proof of stake": "proof-of-stake",
    "pos": "PoS",
    "proof of work": "proof-of-work",
    "pow": "PoW",
    # Names
    "v ?talik": "Vitalik",
    "v ?buterin": "Vitalik Buterin",
    # Technology terms
    "get hub": "GitHub",
    "get lab": "GitLab",
    "java script": "JavaScript",
    "type script": "TypeScript",
    "docker eyes": "dockerize",
    "api": "API",
    "apis": "APIs",
    "rest": "REST",
    "rest ?ful": "RESTful",
    "json": "JSON",
    "http": "HTTP",
    "https": "HTTPS",
    "web socket": "WebSocket",
    "web sockets": "WebSockets",
    # General tech terms
    "cicd": "CI/CD",
    "ai": "AI",
    "m l": "ML",
    "n f ts?": "NFTs",
    
    # Additional Ethereum glossary terms
    # Consensus and blockchain terms
    "fifty ?one percent attack": "51% attack",
    "fifty ?one ?attack": "51% attack",
    "validator?s": "validators",
    "block ?hayder": "block header",
    "block ?header": "block header",
    "block ?time": "block time",
    "byte ?code": "bytecode",
    "by ?zan ?tium": "Byzantium",
    "cas ?per": "Casper FFG",
    "check ?point": "checkpoint",
    "consensus ?layer": "consensus layer",
    "execution ?layer": "execution layer",
    "e ?l": "EL",
    "c ?l": "CL",
    "super ?majority": "supermajority",
    "state ?channel": "state channel",
    "state ?channels": "state channels",
    "syn ?king": "syncing",
    "sink": "sync",
    "sink ?committee": "sync committee",
    "zero ?knowledge ?proof": "zero-knowledge proof",
    "zk ?proof": "zero-knowledge proof",
    "zk ?roll ?up": "zero-knowledge rollup",
    "zk ?roll ?ups": "zero-knowledge rollups",

    # Account and transaction terms
    "gas ?limit": "gas limit", 
    "gas ?price": "gas price",
    "gas ?used": "gas used",
    "private ?key": "private key",
    "public ?key": "public key",
    "nons": "nonce",
    "nahnce": "nonce",
    "transaction ?fee": "transaction fee",
    "mem ?pool": "mempool",
    "meta ?mask": "MetaMask",

    # Technical components
    "a ?b ?i": "ABI",
    "application ?binary ?interface": "Application Binary Interface",
    "application ?programming ?interface": "Application Programming Interface",
    "annual ?percentage ?rate": "APR",
    "application ?specific ?integrated ?circuit": "ASIC",
    "a ?sick": "ASIC",
    "big ?indian": "big-endian",
    "little ?indian": "little-endian",
    "boot ?node": "bootnode",
    "smart ?contract": "smart contract",
    "s ?tark": "STARK",
    
    # Network and scaling terms
    "main ?net": "mainnet",
    "test ?net": "testnet",
    "sepolia": "Sepolia",
    "gorly": "Goerli",
    "gourley": "Goerli",
    "optimistic ?roll ?up": "optimistic rollup",
    "optimistic ?roll ?ups": "optimistic rollups",
    "valid ?e ?um": "validium",
    "shard": "shard",
    "sharding": "sharding",
    "arbitram": "Arbitrum",
    "arbit ?rum": "Arbitrum",
    "opt ?e ?mism": "Optimism",
    "poly ?gone": "Polygon",
    "ave ?lange": "Avalanche",
    "base": "Base",

    # DeFi and application terms
    "stable ?coin": "stablecoin",
    "d ?apps": "dapps",
    "d ?app": "dapp",
    "d ?fight": "DeFi",
    "d ?fi": "DeFi",
    "decentralized ?finance": "decentralized finance",
    "decentralized ?autonomous ?organization": "DAO",
    "dow": "DAO",
    "nft": "NFT",
    "non ?fungible ?token": "non-fungible token",
    "token ?standard": "token standard",
    "e ?r ?c ?twenty": "ERC-20",
    "e ?r ?c ?seven ?twenty ?one": "ERC-721",
    "e ?r ?c ?eleven ?fifty ?five": "ERC-1155",
    "wrapped ?ethereum": "WETH",
    "wrapped ?eth": "WETH",
    "wrapped ?bit ?coin": "WBTC",
    "unit ?swap": "Uniswap",
    "uni ?swap": "Uniswap",
    "sushi ?swap": "SushiSwap",
    "curve": "Curve",
    "a ?ave": "Aave",
    "ah ?ve": "Aave",
    "maker ?dow": "MakerDAO",
    "maker": "Maker",
    
    # Protocol upgrades and forks
    "merge": "The Merge",
    "shanghai": "Shanghai",
    "cancel ?loon": "Cancun", 
    "prague": "Prague",
    "dank ?shard ?en": "Dencun",
    "dan ?sharding": "Dencun",
    "den ?soon": "Dencun",
    "dank ?sharding": "Dencun",
    "den ?con": "Dencun",
    "pectra": "Pectra",
    "peck ?tra": "Pectra",
    "spec ?tra": "Pectra",
    "electra": "Pectra",
    "hard ?fork": "hard fork",
    "soft ?fork": "soft fork",
    "london ?fork": "London fork",
    "berlin ?fork": "Berlin fork",
    "istanbul ?fork": "Istanbul fork",
    "paris ?fork": "Paris",
    "belly ?apple ?fork": "Bellatrix", 
    
    # Technical names
    "geth": "Geth",
    "nethermind": "Nethermind", 
    "besu": "Besu",
    "erigon": "Erigon",
    "arrow ?glacier": "Arrow Glacier",
    "gray ?glacier": "Gray Glacier",
    "prism": "Prysm",
    "lighthouse": "Lighthouse",
    "tek ?u": "Teku",
    "taco": "Teku",
    "nimbus": "Nimbus",
    "lodestar": "Lodestar",
    "load ?star": "Lodestar",
    
    # Additional technical terms
    "finality": "finality",
    "finance ?ation": "finalization",
    "finalizer": "finalizer", 
    "gas ?guzzler": "gas guzzler",
    "dust ?attack": "dust attack",
    "re ?org": "reorg",
    "ree ?organization": "reorganization",
    "slashing": "slashing",
    "eath ?staking": "ETH staking",
    "eth ?staking": "ETH staking",
    "staker": "staker",
    "stakers": "stakers",
    "flash ?loan": "flash loan",
    "flash ?loans": "flash loans",
    "floor ?price": "floor price",
    "v ?m": "VM",
    "s ?crypt": "Scrypt",
    "s ?narks": "SNARKs",
    "s ?tark ?s": "STARKs",
    "chain ?id": "chain ID",
    "hot ?wallet": "hot wallet",
    "cold ?wallet": "cold wallet",
    "hardware ?wallet": "hardware wallet",
    "multisig": "multisig",
    "multi ?sig": "multisig",
    "multi ?signature": "multi-signature",
    "pre ?compile": "precompile",
    "pre ?compiled": "precompiled",
    "airdrop": "airdrop",
    "air ?drop": "airdrop",
    "ice ?age": "Ice Age",
    "difficulty ?bomb": "difficulty bomb",
    "uncle ?block": "uncle block",
    "slip ?page": "slippage",
    "liquidity ?pool": "liquidity pool",
    "impermanent ?loss": "impermanent loss",
    "minting": "minting",
    "mint": "mint",
    "burning": "burning",
    "burn": "burn",
    "all ?time ?high": "all-time high",
    "a ?t ?h": "ATH",
    "white ?list": "whitelist",
    "white ?listing": "whitelisting",
    "taint ?analysis": "taint analysis",
    "time ?lock": "timelock",
    "heisenbugs": "heisenbugs",
    "hayzen ?bugs": "heisenbugs",
    "high ?zen ?bugs": "heisenbugs"
}

def improve_transcript(transcript_file):
    """
    Improves the transcript by:
    1. Correcting technical terms using the dictionary
    2. Formatting speaker names consistently
    3. Merging consecutive captions from the same speaker
    
    Args:
        transcript_file: Path to the VTT transcript file
    
    Returns:
        Path to the improved transcript file
    """
    try:
        # Load the VTT file
        captions = webvtt.read(transcript_file)
        
        # Parse the captions into a more usable format
        parsed_captions = []
        current_speaker = None
        current_text = []
        current_start = None
        current_end = None
        
        for caption in captions:
            text = caption.text
            
            # Extract speaker name
            speaker_match = re.match(r'^(.+?):\s*(.*)', text)
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                content = speaker_match.group(2).strip()
                
                # If speaker changed, save the previous segment
                if current_speaker and current_speaker != speaker:
                    if current_text:
                        parsed_captions.append({
                            "speaker": current_speaker,
                            "text": " ".join(current_text),
                            "start": current_start,
                            "end": current_end
                        })
                    current_text = [content]
                    current_speaker = speaker
                    current_start = caption.start
                    current_end = caption.end
                else:
                    current_speaker = speaker
                    current_text.append(content)
                    if not current_start:
                        current_start = caption.start
                    current_end = caption.end
            else:
                # Continue with current speaker
                if current_speaker:
                    current_text.append(text.strip())
                    current_end = caption.end
                else:
                    # No speaker identified yet, treat as new segment
                    current_speaker = "Unknown Speaker"
                    current_text = [text.strip()]
                    current_start = caption.start
                    current_end = caption.end
        
        # Add the last segment
        if current_speaker and current_text:
            parsed_captions.append({
                "speaker": current_speaker,
                "text": " ".join(current_text),
                "start": current_start,
                "end": current_end
            })
        
        # Apply corrections to technical terms
        for i, caption in enumerate(parsed_captions):
            text = caption["text"]
            
            # Apply each correction from the dictionary
            for pattern, replacement in TRANSCRIPT_CORRECTIONS.items():
                text = re.sub(r'\b' + pattern + r'\b', replacement, text, flags=re.IGNORECASE)
            
            # Update the caption text
            parsed_captions[i]["text"] = text
        
        # Generate improved transcript in markdown format
        output_filename = os.path.splitext(transcript_file)[0] + "_improved.md"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Meeting Transcript\n\n")
            
            for caption in parsed_captions:
                speaker = caption["speaker"]
                text = caption["text"]
                timestamp = caption["start"]
                
                f.write(f"**{speaker}** ({timestamp}):\n{text}\n\n")
        
        print(f"Improved transcript saved to {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"Error improving transcript: {e}")
        return transcript_file  # Return original file on error

def format_chat_log(chat_file):
    """
    Formats the Zoom chat log into a threaded format, grouping messages by threads.
    
    Args:
        chat_file: Path to the chat log txt file
    
    Returns:
        Path to the formatted chat file
    """
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            chat_content = f.read()
        
        # Parse chat messages
        # Format is typically:
        # HH:MM:SS From Username to Everyone/Someone: Message
        chat_pattern = re.compile(
            r'(\d{2}:\d{2}:\d{2})\s+From\s+(.+?)\s+to\s+(.+?):\s+(.*?)(?=\n\d{2}:\d{2}:\d{2}|\Z)', 
            re.DOTALL
        )
        
        messages = []
        for match in chat_pattern.finditer(chat_content):
            time, sender, recipient, text = match.groups()
            
            # Detect if message is a reply to another message
            reply_to = None
            reply_text = None
            
            if "In reply to" in text:
                # Try to extract the original message and sender
                reply_match = re.search(r'In reply to "(.+?)"\s*(?:from)?\s*(.+?)(?:\s*:|\n)', text)
                if reply_match:
                    reply_text = reply_match.group(1).strip()
                    reply_to = reply_match.group(2).strip()
                    # Remove the reply prefix from the actual message
                    text = text.split('\n', 1)[-1].strip()
            
            messages.append({
                "time": time,
                "sender": sender,
                "recipient": recipient,
                "text": text.strip(),
                "reply_to": reply_to,
                "reply_text": reply_text
            })
        
        # Organize messages into threads
        threads = []
        message_map = {}  # Map of message ID to thread index
        
        for idx, message in enumerate(messages):
            if message["reply_to"] is None:
                # This is a top-level message, create a new thread
                thread_id = len(threads)
                threads.append({
                    "messages": [message],
                    "participants": {message["sender"]}
                })
                message_map[idx] = thread_id
            else:
                # This is a reply, find which thread it belongs to
                found_thread = False
                for thread_id, thread in enumerate(threads):
                    for thread_message in thread["messages"]:
                        if (thread_message["sender"] == message["reply_to"] and 
                            (message["reply_text"] in thread_message["text"])):
                            # Found the thread this message replies to
                            thread["messages"].append(message)
                            thread["participants"].add(message["sender"])
                            message_map[idx] = thread_id
                            found_thread = True
                            break
                    if found_thread:
                        break
                
                # If we didn't find the thread, create a new one
                if not found_thread:
                    thread_id = len(threads)
                    threads.append({
                        "messages": [message],
                        "participants": {message["sender"]}
                    })
                    message_map[idx] = thread_id
        
        # Generate formatted chat in markdown
        output_filename = os.path.splitext(chat_file)[0] + "_threaded.md"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Meeting Chat Log\n\n")
            
            for thread_id, thread in enumerate(threads):
                # Only add thread header if there's more than one message
                if len(thread["messages"]) > 1:
                    participants = ", ".join(thread["participants"])
                    f.write(f"## Thread {thread_id + 1} ({participants})\n\n")
                
                # Sort messages by time
                thread["messages"].sort(key=lambda m: m["time"])
                
                for message in thread["messages"]:
                    time = message["time"]
                    sender = message["sender"]
                    text = message["text"]
                    
                    # Format based on whether it's a reply
                    if message["reply_to"]:
                        reply_text = message["reply_text"]
                        reply_to = message["reply_to"]
                        f.write(f"**{sender}** ({time}, replying to {reply_to}):\n{text}\n\n")
                    else:
                        f.write(f"**{sender}** ({time}):\n{text}\n\n")
                
                f.write("---\n\n")
        
        print(f"Formatted chat log saved to {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"Error formatting chat log: {e}")
        return chat_file  # Return original file on error

def extract_call_number(meeting_title, meeting_series=None):
    """
    Extract the call number from a meeting title.
    
    Args:
        meeting_title: Title of the meeting
        meeting_series: Series of the meeting (ACDE/ACDC) if known
    
    Returns:
        Call number (integer) if found, None otherwise
    """
    if not meeting_title:
        return None
        
    # Try different patterns to extract call number
    
    # Pattern: "Call #X" or "Meeting #X"
    call_number_match = re.search(r'(?:call|meeting)\s*#?\s*(\d+)', meeting_title, re.IGNORECASE)
    if call_number_match:
        try:
            return int(call_number_match.group(1))
        except ValueError:
            pass
    
    # Pattern: "ACDE/ACDC X" or "EL/CL Call X"
    if meeting_series:
        series_pattern = meeting_series
        if meeting_series.lower() == "acde":
            series_pattern = r'(?:ACDE|EL\s+Call)'
        elif meeting_series.lower() == "acdc":
            series_pattern = r'(?:ACDC|CL\s+Call)'
            
        series_match = re.search(f'{series_pattern}\s*#?\s*(\d+)', meeting_title, re.IGNORECASE)
        if series_match:
            try:
                return int(series_match.group(1))
            except ValueError:
                pass
    
    # Last resort: Look for any number after common prefixes
    prefixes = [
        r'ACDE\s*', r'ACDC\s*', r'EL\s+Call\s*', r'CL\s+Call\s*',
        r'All\s+Core\s+Devs\s+Execution\s+Layer\s+Meeting\s*',
        r'All\s+Core\s+Devs\s+Consensus\s+Layer\s+Meeting\s*',
        r'All\s+Core\s+Devs\s+Meeting\s*',
        r'ACD\s+Meeting\s*',
        r'All\s+Core\s+Devs\s+Testing\s*'
    ]
    
    for prefix in prefixes:
        prefix_match = re.search(f'{prefix}#?\s*(\d+)', meeting_title, re.IGNORECASE)
        if prefix_match:
            try:
                return int(prefix_match.group(1))
            except ValueError:
                pass
    
    # If we still don't have a number, try to find any number in the title
    number_match = re.search(r'\b(\d+)\b', meeting_title)
    if number_match:
        try:
            return int(number_match.group(1))
        except ValueError:
            pass
    
    return None

def determine_meeting_series(meeting_title, call_series=None):
    """
    Determine which series (ACDE, ACDC, ACDT) a meeting belongs to.
    
    Args:
        meeting_title: Title of the meeting
        call_series: Call series from the mapping file if available
    
    Returns:
        "ACDE" (Execution Layer), "ACDC" (Consensus Layer), "ACDT" (Testing), or None if undetermined
    """
    if not meeting_title:
        return None
        
    # If call_series is provided, use it to determine the series
    if call_series:
        call_series = call_series.upper()
        if "ACDE" in call_series:
            return "ACDE"
        if "ACDC" in call_series:
            return "ACDC"
        if "TEST" in call_series or "TESTING" in call_series:
            return "ACDT"
    
    # Check for specific markers in the title
    title_upper = meeting_title.upper()
    
    # Testing indicators
    if any(marker in title_upper for marker in ["TESTING", "TEST CALL", "TESTS"]):
        return "ACDT"
    
    # Execution Layer indicators
    if any(marker in title_upper for marker in ["ACDE", "EXECUTION LAYER", "EL CALL"]):
        return "ACDE"
    
    # Consensus Layer indicators
    if any(marker in title_upper for marker in ["ACDC", "CONSENSUS LAYER", "CL CALL"]):
        return "ACDC"
    
    # Look for more generic markers and infer from those
    if "CORE DEVS" in title_upper:
        # Check if it might be a Testing call
        if "TEST" in title_upper:
            return "ACDT"
        # Default to ACDE if no other indicator
        return "ACDE"
    
    # Can't determine
    return None

def get_meeting_path(meeting_id, meeting_title=None, call_series=None, meeting_metadata=None):
    """
    Determine the appropriate path for storing meeting files based on series and call number.
    
    Args:
        meeting_id: Meeting ID
        meeting_title: Meeting title if available
        call_series: Call series from mapping if available
        meeting_metadata: Additional meeting metadata from mapping if available
    
    Returns:
        Tuple of (base_path, call_number)
    """
    # Default path
    base_path = f"Zoom/Meeting_Recordings/{meeting_id}"
    call_number = None
    
    # Try to determine the meeting series
    meeting_series = determine_meeting_series(meeting_title, call_series)
    
    # Extract call number
    call_number = extract_call_number(meeting_title, meeting_series)
    
    # Check metadata for call_number if not found in title
    if not call_number and meeting_metadata and 'call_number' in meeting_metadata:
        try:
            call_number = int(meeting_metadata['call_number'])
        except (ValueError, TypeError):
            pass
    
    # Construct path based on series and call number
    if meeting_series == "ACDE":
        if call_number:
            base_path = f"AllCoreDevs-EL-Meetings/call_{call_number:03d}"
        else:
            base_path = "AllCoreDevs-EL-Meetings"
    elif meeting_series == "ACDC":
        if call_number:
            base_path = f"AllCoreDevs-CL-Meetings/call_{call_number:03d}"
        else:
            base_path = "AllCoreDevs-CL-Meetings"
    elif meeting_series == "ACDT":
        if call_number:
            base_path = f"AllCoreDevs-Testing-meetings/call_{call_number:03d}"
        else:
            base_path = "AllCoreDevs-Testing-meetings"
    
    return base_path, call_number

def commit_to_github(repo, branch, files, commit_message, meeting_id, meeting_title=None, call_series=None, metadata=None):
    """
    Commits files to the GitHub repository
    
    Args:
        repo: GitHub repository object
        branch: Branch name
        files: List of file paths to commit
        commit_message: Commit message
        meeting_id: Meeting ID for path construction
        meeting_title: Meeting title if available
        call_series: Call series from mapping if available
        metadata: Additional meeting metadata from mapping if available
    
    Returns:
        Dictionary with GitHub URLs to the committed files and extracted call number
    """
    # Import modules needed for GitHub operations
    from github import Github, InputGitAuthor
    import base64
    
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        print("GITHUB_TOKEN environment variable not set")
        return None
    
    repo_name = os.environ.get("GITHUB_REPOSITORY", "ethereum/pm")
    
    try:
        # Initialize GitHub client
        g = Github(gh_token)
        repo = g.get_repo(repo_name)
        
        # Determine appropriate path based on meeting series and call number
        base_path, call_number = get_meeting_path(meeting_id, meeting_title, call_series, metadata)
        
        print(f"[DEBUG] Determined base path: {base_path} with call number: {call_number}")
        
        # Create author information
        author = InputGitAuthor(
            name="GitHub Actions Bot",
            email="actions@github.com"
        )
        
        # Track URLs for committed files and metadata
        result = {
            "github_urls": {},
            "call_number": call_number,
            "meeting_series": determine_meeting_series(meeting_title, call_series)
        }
        
        # Commit each file
        for file_path in files:
            # Extract the filename
            file_name = os.path.basename(file_path)
            
            # Create the target path in GitHub
            target_path = f"{base_path}/{file_name}"
            
            # If this is a markdown transcript, try to use simpler naming
            if file_name.endswith("_improved.md") and call_number:
                if "transcript" in file_name.lower():
                    target_path = f"{base_path}/transcript.md"
                elif "chat" in file_name.lower():
                    target_path = f"{base_path}/chat.md"
            
            print(f"[DEBUG] Committing file to path: {target_path}")
            
            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Base64 encode for API
            content_encoded = base64.b64encode(file_content).decode("utf-8")
            
            try:
                # Check if file already exists
                try:
                    contents = repo.get_contents(target_path, ref=branch)
                    # Update existing file
                    result_data = repo.update_file(
                        path=target_path,
                        message=f"{commit_message} - Update {file_name}",
                        content=content_encoded,
                        sha=contents.sha,
                        branch=branch,
                        author=author
                    )
                    result["github_urls"][file_name] = result_data["content"].html_url
                    print(f"Updated {target_path} in repository")
                except Exception as e:
                    if "not found" in str(e).lower() or "404" in str(e):
                        # Create new file
                        result_data = repo.create_file(
                            path=target_path,
                            message=f"{commit_message} - Add {file_name}",
                            content=content_encoded,
                            branch=branch,
                            author=author
                        )
                        result["github_urls"][file_name] = result_data["content"].html_url
                        print(f"Created {target_path} in repository")
                    else:
                        raise e
            except Exception as e:
                print(f"Error committing {file_path}: {str(e)}")
        
        return result
    
    except Exception as e:
        print(f"Error in commit_to_github: {str(e)}")
        return None 