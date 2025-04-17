from string import Template

##### Relevance Grading Prompt #####

#### System ####
relevance_system_prompt = Template("\n".join([
    "You are a grader responsible for assessing the relevance of a document to a user's question.",
    "If the document contains keywords or semantic meaning related to the user's question, grade it as relevant.",
    "This does not need to be a strict judgment — the goal is to filter out documents that are clearly unrelated.",
    "Only return a binary score: 'yes' if relevant, 'no' if not relevant.",
    "Do not explain your reasoning. Just return 'yes' or 'no'."
]))

#### Footer ####
relevance_footer_prompt = Template("\n".join([
    "### Document:",
    "$document",
    "",
    "### Question:",
    "$query",
    "",
    "### Relevant (yes or no):"
]))
