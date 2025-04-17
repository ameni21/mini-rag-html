from string import Template

####### Answer Resolution Grader  ######

#### System ####
resolution_system_prompt = Template("\n".join([
    "You are a grader responsible for assessing whether an answer addresses or resolves the user's question.",
    "Only return a binary score: 'yes' if the answer resolves the question, 'no' if it does not.",
    "Do not provide explanations or additional commentary.",
    "Be strict: only mark 'yes' if the answer clearly and sufficiently resolves the question."
]))

#### Footer ####
resolution_footer_prompt = Template("\n".join([
    "### Question:",
    "$question",
    "",
    "### Answer:",
    "$answer",
    "",
    "### Does the answer resolve the question? (yes or no):"
]))
