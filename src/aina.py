import config
from src import llm


def save_html(html_content, file_name):
    output_path = f"sites/drafts/{file_name}"
    # Open file in text write mode (not binary)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"HTML successfully saved to {output_path}")

async def work() -> None:
    # Aina-chan Will Do Her Best!!!
    while True:
        task = await config.queue_to_process_everything.get()
        new_site = await llm.generate_website(task)
        name = title_to_filename(task["title"])
        save_html(new_site,f"{name}.html")
        config.queue_to_process_everything.task_done()

def title_to_filename(title):
    # Convert to lowercase
    filename = title.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '-')
    
    # Remove special characters
    import re
    filename = re.sub(r'[^\w\s_-]', '', filename)
    
    return filename