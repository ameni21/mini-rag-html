from string import Template

#### LLM Grounding Assessment Prompt ####

#### System ####
grounding_system_prompt = Template("\n".join([
    "You are a grader responsible for evaluating whether an LLM-generated answer is grounded in a provided set of retrieved facts.",
    "Grounded means that the answer is directly supported by or consistent with the facts.",
    "Only return a binary score: 'yes' if grounded, 'no' if not grounded.",
    "Do not explain your reasoning. Just return 'yes' or 'no'."
]))

#### Footer ####
grounding_footer_prompt = Template("\n".join([
    "### Retrieved Facts:",
    "$facts",
    "",
    "### LLM-Generated Answer:",
    "$answer",
    "",
    "### Grounded in Facts? (yes or no):"
]))
