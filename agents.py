import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import web_search , scrape_url 
from dotenv import load_dotenv
load_dotenv()

# Check for API keys
if "OPEN_API_KEY" in os.environ and "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["OPEN_API_KEY"]

# Model setup: prioritize Gemini if GOOGLE_API_KEY is available (or fallback to OpenAI)
if os.getenv("GOOGLE_API_KEY"):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
else:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#FIRST AGENT
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

#second agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )    

#third agent
 
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research writer producing evidence-based reports.

STRICT RULES:
- Only use facts, statistics, and claims that appear in the provided research material.
- Always cite the source URL inline when referencing a specific fact (e.g. "According to [Source Title](URL), ...").
- If the research material lacks sufficient evidence on a point, explicitly state: "Insufficient evidence was found on this aspect."
- Clearly distinguish verified facts from predictions or opinions.
- Never invent statistics, percentages, study names, or citations.
- If a URL was provided in the research but the page could not be scraped, note it as "[Source not fully accessible]".
- Write the entire report in this language/style: {language}.
- If language is "Auto", use the same language as the topic. If it mixes Hindi and English, use natural Hinglish."""),
    ("human", """Write a detailed, evidence-based research report on the topic below.

Topic: {topic}

Research Material (search results and scraped content):
{research}

Structure the report with these sections:
1. **Introduction** — Brief overview of the topic and why it matters.
2. **Key Findings** — Minimum 3 well-explained findings, each supported by evidence from the research material. Cite the source URL for each claim.
3. **Limitations & Counterarguments** — Acknowledge gaps in evidence, opposing viewpoints, or areas where research is inconclusive.
4. **Conclusion** — Summarize key takeaways based strictly on available evidence.
5. **References** — List every source URL used, with its title.

Important: If the research material is insufficient to fully cover the topic, state this clearly rather than fabricating content."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()   

#fourth agent


critic_prompt = ChatPromptTemplate.from_messages([
     ("system", """You are a rigorous research quality reviewer. Evaluate reports objectively using the weighted criteria below.

Scoring Criteria (total = 10):
- Source Reliability (20%): Are sources from credible, authoritative origins? Are URLs real and verifiable?
- Evidence & Factual Support (25%): Are claims backed by specific data, statistics, or cited findings from the research? Or are they vague generalizations?
- Research Depth (15%): Does the report cover multiple dimensions of the topic with sufficient detail?
- Citations & References (15%): Are sources cited inline and listed in a references section? Are URLs present and correctly attributed?
- Critical Analysis (15%): Does the report include limitations, counterarguments, or areas of uncertainty?
- Structure & Clarity (10%): Is the report well-organized, readable, and logically structured?

STRICT RULES:
- A report with zero source URLs must score no higher than 3/10 regardless of writing quality.
- A report that invents statistics or citations not found in research material should be penalized.
- Do not inflate scores to be encouraging. Be accurate.
- Keep the required section headings in English.
- Write the content under each heading in this language/style: {language}.
- If language is "Auto", use the same language as the report."""),
    ("human", """Review the research report below using the weighted evaluation criteria.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Weaknesses:
- ...
- ...

Missing Information:
- ...

Unsupported Claims:
- ... (list any claims that lack evidence or citation, or write "None identified")

Recommendations:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()


# Revision chain — used to improve a report based on critic feedback
revision_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research writer revising a report based on peer review feedback.

STRICT RULES:
- Address the specific weaknesses and recommendations raised by the reviewer.
- Add inline source citations where the reviewer noted they were missing, using URLs from the research material.
- Add a Limitations section if the reviewer flagged its absence.
- Do NOT invent new facts, statistics, or URLs that are not in the original research material.
- If the research material is insufficient to address a criticism, explicitly state that more research is needed rather than fabricating content.
- Preserve the overall structure and any strengths noted by the reviewer.
- Write the complete revised report in this language/style: {language}.
- If language is "Auto", preserve the report's existing language."""),
    ("human", """Revise the research report below based on the critic's feedback.

ORIGINAL REPORT:
{report}

CRITIC FEEDBACK:
{feedback}

ORIGINAL RESEARCH MATERIAL (use this for citations):
{research}

Produce the complete revised report with all sections. Cite sources inline using URLs from the research material."""),
])

revision_chain = revision_prompt | llm | StrOutputParser()