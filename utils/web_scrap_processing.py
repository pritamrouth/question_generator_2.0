import re

def process_scraped_data(markdown_text):
    # Split the text into lines
    lines = markdown_text.splitlines()
    
    # Prepare a list to hold the processed lines
    processed_lines = []
    seen_lines = set()  # To track seen lines
    duplicates = set()  # To track duplicate lines
    
    # Define keywords or phrases to filter out promotional content
    promotional_keywords = [
        "promote", "advertisement", "sign up", "subscribe", 
        "follow", "join", "get started", "limited time offer",
        "click here", "check out", "don't miss", "exclusive deal", "free trial",
        "special offer", "Try", "Get", "Buy", "Order", "Shop", "share", "Listen",
        "Watch", "Download", "Learn", "Discover", "Explore", "Read", "Linkedin","Cookie",
        "Terms", "Privacy", "Policy", "FAQ", "Contact", "About", "Cookies","Login","Accept",
        "Reject", "Decline", "Cancel", "Close", "Exit", "Leave","Earn money",
    ]
    
    for line in lines:
        # Remove links using regex
        line = re.sub(r'http[s]?://\S+', '', line)  # Remove links
        line = re.sub(r'\[.*?\]\(.*?\)', '', line)  # Remove markdown links
        
         # Check if the line starts with an uppercase letter and is not a list
        if line and line[0].isupper() and not line.startswith(("-", "*", "+")):
            # Check for promotional content
            if not any(keyword.lower() in line.lower() for keyword in promotional_keywords):
                # Check if the number of words in the line is 5 or more
                if len(line.split()) >= 5:
                    if line in seen_lines:
                        duplicates.add(line)  # Mark as duplicate
                    else:
                        seen_lines.add(line)  # Add to seen lines
                        processed_lines.append(line.strip())
    
    # Remove duplicates from processed_lines
    processed_lines = [line for line in processed_lines if line not in duplicates]
    
    # Join processed lines into a single string
    processed_text = "\n".join(processed_lines)
    
    return processed_text