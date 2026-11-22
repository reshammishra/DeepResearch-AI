import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, revision_chain

def _extract_text(content) -> str:
    """Helper to ensure agent message content is always formatted as clean string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        extracted = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                extracted.append(item["text"])
            elif isinstance(item, str):
                extracted.append(item)
            else:
                extracted.append(str(item))
        return "\n".join(extracted)
    return str(content)


def _extract_tool_outputs(messages) -> str:
    """Extract raw tool call outputs from the agent message chain.

    LangGraph agents return a list of messages:
      HumanMessage -> AIMessage(tool_calls) -> ToolMessage(raw output) -> AIMessage(summary)
    The ToolMessage objects contain the raw tool output (with URLs intact),
    which the agent's final summary often drops.
    """
    tool_texts = []
    for msg in messages:
        # ToolMessage from langchain / langgraph
        msg_type = getattr(msg, "type", None)
        if msg_type == "tool":
            tool_texts.append(_extract_text(getattr(msg, "content", "")))
    return "\n\n".join(tool_texts)


def _extract_urls(text: str) -> list:
    """Extract all HTTP/HTTPS URLs from text."""
    return re.findall(r'https?://[^\s\)\]\"\'>]+', text)


def _build_url_block(text: str) -> str:
    """Build a structured URL list from text for the Reader Agent."""
    urls = _extract_urls(text)
    if not urls:
        return ""
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    lines = [f"  {i}. {u}" for i, u in enumerate(unique[:8], 1)]
    return "\n".join(lines)


def run_research_pipeline(topic: str, on_step=None, language: str = "Auto") -> dict:
    state = {}

    # ── Step 1: Search ──────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("step-1 search agent is working...")
    print("=" * 50)
    if on_step:
        on_step("search", "Search Agent is querying the web for reliable sources...")

    raw_tool_output = ""
    try:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        # Capture the agent's summary (last message)
        agent_summary = _extract_text(search_result['messages'][-1].content)
        # Also capture raw tool outputs which contain the actual URLs and snippets
        raw_tool_output = _extract_tool_outputs(search_result['messages'])
        # Combine both: raw tool data (with URLs) + agent analysis
        if raw_tool_output.strip():
            state["search_results"] = (
                f"=== RAW SEARCH DATA ===\n{raw_tool_output}\n\n"
                f"=== AGENT ANALYSIS ===\n{agent_summary}"
            )
        else:
            state["search_results"] = agent_summary
    except Exception as e:
        state["search_results"] = f"Search Agent encountered an error: {str(e)}"
        print(f"Search error: {e}")

    if not state["search_results"].strip() or "No search results" in state["search_results"]:
        state["search_results"] = "No search results were found for this topic."

    print("\n search result ", state['search_results'][:500])

    # ── Step 2: Reader Agent ────────────────────────────────────────
    print("\n" + "=" * 50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("=" * 50)
    if on_step:
        on_step("reader", "Reader Agent is extracting in-depth content from sources...")

    # Extract URLs from BOTH raw tool output and agent summary
    combined_for_urls = raw_tool_output + "\n" + state['search_results']
    url_block = _build_url_block(combined_for_urls)

    if url_block:
        reader_prompt = (
            f"You have the following URLs from web search results about '{topic}'.\n\n"
            f"URLs to scrape:\n{url_block}\n\n"
            f"Scrape the top 3 most relevant URLs using the scrape_url tool. "
            f"For each URL, call scrape_url with the exact URL. "
            f"Return all scraped content with the source URL clearly labeled."
        )
    else:
        reader_prompt = (
            f"The search results about '{topic}' did not contain usable URLs. "
            f"Report that no URLs were available to scrape."
        )

    try:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user", reader_prompt)]
        })
        # Get agent summary AND raw scraped tool outputs
        reader_summary = _extract_text(reader_result['messages'][-1].content)
        reader_tool_output = _extract_tool_outputs(reader_result['messages'])
        # Combine: raw scraped data has the actual page content with URLs
        if reader_tool_output.strip():
            state['scraped_content'] = (
                f"=== SCRAPED PAGE CONTENT ===\n{reader_tool_output}\n\n"
                f"=== READER ANALYSIS ===\n{reader_summary}"
            )
        else:
            state['scraped_content'] = reader_summary
    except Exception as e:
        state['scraped_content'] = f"Reader Agent encountered an error: {str(e)}"
        print(f"Reader error: {e}")

    if not state['scraped_content'].strip():
        state['scraped_content'] = "No content was successfully scraped from any sources."

    print("\nscraped content: \n", state['scraped_content'][:500])

    # ── Step 3: Writer Chain ────────────────────────────────────────
    print("\n" + "=" * 50)
    print("step 3 - Writer is drafting the report ...")
    print("=" * 50)
    if on_step:
        on_step("writer", "Writer Agent is synthesizing structured research report...")

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    try:
        state["report"] = _extract_text(writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
            "language": language,
        }))
    except Exception as e:
        state["report"] = f"Writer Chain encountered an error: {str(e)}"
        print(f"Writer error: {e}")

    if not state["report"].strip():
        state["report"] = "The Writer Agent was unable to generate a report from the available research material."

    print("\n Final Report\n", state['report'][:500])

    # ── Step 4: Critic Chain ────────────────────────────────────────
    print("\n" + "=" * 50)
    print("step 4 - critic is reviewing the report ")
    print("=" * 50)
    if on_step:
        on_step("critic", "Critic Agent is reviewing quality, structure & citations...")

    try:
        state["feedback"] = _extract_text(critic_chain.invoke({
            "report": state['report'],
            "language": language,
        }))
    except Exception as e:
        state["feedback"] = f"Critic Chain encountered an error: {str(e)}"
        print(f"Critic error: {e}")

    print("\n critic report \n", state['feedback'][:500])

    # ── Step 5: Revision Loop (max 2 attempts) ─────────────────────
    # Only revise if the critic gave a score and it's below 7/10
    score_match = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", state.get("feedback", ""))
    initial_score = float(score_match.group(1)) if score_match else None

    max_revisions = 2
    revision_count = 0

    if initial_score is not None and initial_score < 7:
        for attempt in range(1, max_revisions + 1):
            print(f"\n{'=' * 50}")
            print(f"Revision {attempt} — Score was {initial_score}/10, attempting improvement...")
            print("=" * 50)
            if on_step:
                on_step("writer", f"Revision {attempt}: Writer is improving the report based on critic feedback...")

            try:
                revised_report = _extract_text(revision_chain.invoke({
                    "report": state["report"],
                    "feedback": state["feedback"],
                    "research": research_combined,
                    "language": language,
                }))

                if revised_report.strip():
                    state["report"] = revised_report
            except Exception as e:
                print(f"Revision error: {e}")
                break

            # Re-evaluate with Critic
            if on_step:
                on_step("critic", f"Revision {attempt}: Critic is re-evaluating the revised report...")

            try:
                state["feedback"] = _extract_text(critic_chain.invoke({
                    "report": state["report"],
                    "language": language,
                }))
            except Exception as e:
                print(f"Critic re-evaluation error: {e}")
                break

            # Check new score
            new_match = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", state["feedback"])
            new_score = float(new_match.group(1)) if new_match else None
            revision_count += 1

            print(f"\n Revised critic score: {new_score}/10")

            if new_score is not None and new_score >= 7:
                print("Score meets threshold. Stopping revisions.")
                break
            elif new_score is not None:
                initial_score = new_score

    if revision_count > 0:
        state["revisions"] = revision_count

    if on_step:
        on_step("complete", "All research agents completed successfully!")

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
