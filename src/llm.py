import config
import re
from openai import OpenAI

async def generate_website(task):

    ai_config:config.Config = config.load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key= config.get_key(),
        )

    content = task["content"]
    print(f"Generating Website~\n\n Prompt: {content}")
    
    completion = client.chat.completions.create(
    model=ai_config.base_llm,
    messages=[
        {
        "role": "system",
        "content": ai_config.system_note
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


