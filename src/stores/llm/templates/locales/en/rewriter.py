from string import Template

######### Question Rewriter Prompt #####

#### System ####
system_prompt = Template("\n".join([
    "You are a question re-writer that transforms user questions into improved versions.",
    "Your goal is to optimize the question for vectorstore retrieval.",
    "Focus on understanding the semantic intent behind the user's query.",
    "Preserve the original meaning but enhance clarity and keyword relevance.",
    "Avoid unnecessary rephrasing if the question is already optimized.",
    "Be precise and concise in your reformulation."
    "Do not explain your reasoning. Just return the question."
]))

#### Footer ####
footer_prompt = Template("\n".join([
    "### Original Question:",
    "$query",
    "",
    "### Improved Version:"
]))
