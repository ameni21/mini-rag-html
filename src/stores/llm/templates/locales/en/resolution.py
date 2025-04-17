from string import Template

####### Answer Resolution Grader  ######

#### System ####
system_prompt = Template("\n".join([
    "You are a grader responsible for assessing whether an answer addresses or resolves the user's question.",
    "Only return a binary score: 'yes' if the answer resolves the question, 'no' if it does not.",
    "Do not provide explanations or additional commentary.",
    "Be strict: only mark 'yes' if the answer clearly and sufficiently resolves the question."
]))

#### Generation ####
generation_prompt = Template("\n".join([
    "### LLM generation:",
    "$generation"
]))

#### Footer ####
footer_prompt = Template("\n".join([
    "",
    "Does the answer resolve the question? (yes or no)"
    "## Question:",
    "$query",
    "",
    "## Answer:",
    
    
]))
