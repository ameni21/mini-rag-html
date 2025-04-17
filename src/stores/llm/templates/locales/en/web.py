from string import Template

#### WEB SEARCH ASSISTANT ####

#### System ####

system_prompt = Template("\n".join([
    "You are an assistant responsible for generating responses for the user.",
    "Ignore HTML tags and focus only on the text content.",
    "You will be provided with search results from the web relevant to the user's query.",
    "Generate a response based on the web search results.",
    "Ignore any search results that are not relevant to the user's query.",
    "If you cannot generate a response, politely inform the user.",
    "Ensure your response is in the same language as the user's query.",
    "Be polite and respectful to the user.",
    "Provide precise and concise responses, avoiding unnecessary information."
]))


### Search Result ###
documents_prompt = Template(
    "\n".join([
    "## Search Result No: $doc_num",
    "### Snippet: $chunk_text",
    ])
)

### Footer ###
footer_prompt = Template("\n".join(
    [
        "Based only on the above web search results, please generate an answer for the user.",
        "## Question:",
        "$query",
        "",
        "## Answer:",
    ]
))
