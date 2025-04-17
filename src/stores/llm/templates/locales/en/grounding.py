from string import Template

#### LLM Grounding Assessment Prompt ####

#### System ####
system_prompt = Template("\n".join([
    "You are a grader assessing whether an LLM generation is grounded in",
    "supported by a set of retrieved facts. \n ",
    "Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in",
    "supported by the  facts.."
]))





#### Facts ( documents) ####
documents_prompt = Template("\n".join([
    "### facts:",
    "",
    "## Document No: $doc_num",
    "### Content: $chunk_text",
]))

#### Generation ####
generation_prompt = Template("\n".join([
    "### LLM generation:",
    "$generation"
]))

#### Footer ####
footer_prompt = Template("\n".join([
    "",
    "Based only on the above facts, return 'yes' or 'no'.",
    "",
    "## Answer:",
]))
