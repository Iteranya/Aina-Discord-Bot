import config
import re

async def generate_website(task):
    content = task["content"]
    print(f"Generating Website~\n\n Prompt: {content}")
    
    completion = config.client.chat.completions.create(
    model=config.base_llm,
    messages=[
        {
        "role": "system",
        "content": "ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE"
        },
        {
        "role": "user",
        "content": f"Make me a website with the following description: {content}"
        },
        {
        "role": "assistant",
        "content": "Understood, here's the requested site: ```html\n"
        }
    ]
    )
    result = completion.choices[0].message.content
    print(result)
    return regex_html(result)

def regex_html(text):
    # Try to find complete HTML document with doctype
    doctype_pattern = re.compile(r'<!DOCTYPE\s+html[^>]*>.*?</html>', re.DOTALL | re.IGNORECASE)
    match = doctype_pattern.search(text)
    if match:
        return match.group(0)
    
    # Try to find HTML without doctype but with html tags
    html_pattern = re.compile(r'<html[^>]*>.*?</html>', re.DOTALL | re.IGNORECASE)
    match = html_pattern.search(text)
    if match:
        return match.group(0)
    
    return None


