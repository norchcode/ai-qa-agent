import pdb

from dotenv import load_dotenv

load_dotenv()
import asyncio
import os
import sys
import logging
from pprint import pprint
from uuid import uuid4
from src.utils import utils
from src.agent.custom_agent import CustomAgent
import json
import re
from browser_use.agent.service import Agent
from browser_use.browser.browser import BrowserConfig, Browser
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller, DoneAction
from main_content_extractor import MainContentExtractor
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage
)
from json_repair import repair_json
from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt
from src.controller.custom_controller import CustomController
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import BrowserContextConfig, BrowserContext
from browser_use.browser.context import (
    BrowserContextConfig,
    BrowserContextWindowSize,
)

logger = logging.getLogger(__name__)


async def deep_research(task, llm, agent_state=None, **kwargs):
    task_id = str(uuid4())
    save_dir = kwargs.get("save_dir", os.path.join(f"./tmp/deep_research/{task_id}"))
    logger.info(f"Save Deep Research at: {save_dir}")
    os.makedirs(save_dir, exist_ok=True)

    # max qyery num per iteration
    max_query_num = kwargs.get("max_query_num", 3)

    use_own_browser = kwargs.get("use_own_browser", False)
    extra_chromium_args = []

    if use_own_browser:
        cdp_url = os.getenv("CHROME_CDP", kwargs.get("chrome_cdp", None))
        # TODO: if use own browser, max query num must be 1 per iter, how to solve it?
        max_query_num = 1
        chrome_path = os.getenv("CHROME_PATH", None)
        if chrome_path == "":
            chrome_path = None
        chrome_user_data = os.getenv("CHROME_USER_DATA", None)
        if chrome_user_data:
            extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]

        browser = CustomBrowser(
            config=BrowserConfig(
                headless=kwargs.get("headless", False),
                cdp_url=cdp_url,
                disable_security=kwargs.get("disable_security", True),
                chrome_instance_path=chrome_path,
                extra_chromium_args=extra_chromium_args,
            )
        )
        browser_context = await browser.new_context()
    else:
        browser = None
        browser_context = None

    controller = CustomController()

    @controller.registry.action(
        'Extract page content to get the pure markdown.',
    )
    async def extract_content(browser: BrowserContext):
        page = await browser.get_current_page()
        # use jina reader
        url = page.url

        jina_url = f"https://r.jina.ai/{url}"
        await page.goto(jina_url)
        output_format = 'markdown'
        content = MainContentExtractor.extract(  # type: ignore
            html=await page.content(),
            output_format=output_format,
        )
        # go back to org url
        await page.go_back()
        msg = f'Extracted page content:\n{content}\n'
        logger.info(msg)
        return ActionResult(extracted_content=msg)

    search_system_prompt = f"""
    You are a **Deep Researcher**, an AI agent specializing in in-depth information gathering and research using a web browser with **automated execution capabilities**. Your expertise lies in formulating comprehensive research plans and executing them meticulously to fulfill complex user requests. You will analyze user instructions, devise a detailed research plan, and determine the necessary search queries to gather the required information.

    **Your Task:**

    Given a user's research topic, you will:

    1. **Develop a Research Plan:** Outline the key aspects and subtopics that need to be investigated to thoroughly address the user's request. This plan should be a high-level overview of the research direction.
    2. **Generate Search Queries:** Based on your research plan, generate a list of specific search queries to be executed in a web browser. These queries should be designed to efficiently gather relevant information for each aspect of your plan.

    **Output Format:**

    Your output will be a JSON object with the following structure:

    ```json
    {{
    "plan": "A concise, high-level research plan outlining the key areas to investigate.",
      "queries": [
        "search query 1",
        "search query 2",
        //... up to a maximum of {max_query_num} search queries
      ]
    }}
    ```

    **Important:**

    *   Limit your output to a **maximum of {max_query_num}** search queries.
    *   Make the search queries to help the automated agent find the needed information. Consider what keywords are most likely to lead to useful results.
    *   If you have gathered for all the information you want and no further search queries are required, output queries with an empty list: `[]`
    *   Make sure output search queries are different from the history queries.

    **Inputs:**

    1.  **User Instruction:** The original instruction given by the user.
    2.  **Previous Queries:** History Queries.
    3.  **Previous Search Results:** Textual data gathered from prior search queries. If there are no previous search results this string will be empty.
    """
    search_messages = [SystemMessage(content=search_system_prompt)]

    record_system_prompt = """
    You are an expert information recorder. Your role is to process user instructions, current search results, and previously recorded information to extract, summarize, and record new, useful information that helps fulfill the user's request. Your output will be a JSON formatted list, where each element represents a piece of extracted information and follows the structure: `{"url": "source_url", "title": "source_title", "summary_content": "concise_summary", "thinking": "reasoning"}`.

**Important Considerations:**

1. **Minimize Information Loss:** While concise, prioritize retaining important details and nuances from the sources. Aim for a summary that captures the essence of the information without over-simplification. **Crucially, ensure to preserve key data and figures within the `summary_content`. This is essential for later stages, such as generating tables and reports.**

2. **Avoid Redundancy:** Do not record information that is already present in the Previous Recorded Information. Check for semantic similarity, not just exact matches. However, if the same information is expressed differently in a new source and this variation adds valuable context or clarity, it should be included.

3. **Source Information:** Extract and include the source title and URL for each piece of information summarized. This is crucial for verification and context. **The Current Search Results are provided in a specific format, where each item starts with "Title:", followed by the title, then "URL Source:", followed by the URL, and finally "Markdown Content:", followed by the content. Please extract the title and URL from this structure.** If a piece of information cannot be attributed to a specific source from the provided search results, use `"url": "unknown"` and `"title": "unknown"`.

4. **Thinking and Report Structure:**  For each extracted piece of information, add a `"thinking"` key. This field should contain your assessment of how this information could be used in a report, which section it might belong to (e.g., introduction, background, analysis, conclusion, specific subtopics), and any other relevant thoughts about its significance or connection to other information.

**Output Format:**

Provide your output as a JSON formatted list. Each item in the list must adhere to the following format:

```json
[
  {
    "url": "source_url_1",
    "title": "source_title_1",
    "summary_content": "Concise summary of content. Remember to include key data and figures here.",
    "thinking": "This could be used in the introduction to set the context. It also relates to the section on the history of the topic."
  },
  // ... more entries
  {
    "url": "unknown",
    "title": "unknown",
    "summary_content": "concise_summary_of_content_without_clear_source",
    "thinking": "This might be useful background information, but I need to verify its accuracy. Could be used in the methodology section to explain how data was collected."
  }
]
```

**Inputs:**

1. **User Instruction:** The original instruction given by the user. This helps you determine what kind of information will be useful and how to structure your thinking.
2. **Previous Recorded Information:** Textual data gathered and recorded from previous searches and processing, represented as a single text string.
3. **Current Search Plan:** Research plan for current search.
4. **Current Search Query:** The current search query.
5. **Current Search Results:** Textual data gathered from the most recent search query.
    """
    record_messages = [SystemMessage(content=record_system_prompt)]

    search_iteration = 0
    max_search_iterations = kwargs.get("max_search_iterations", 10)  # Limit search iterations to prevent infinite loop
    use_vision = kwargs.get("use_vision", False)

    history_query = []
    history_infos = []
    try:
        while search_iteration < max_search_iterations:
            search_iteration += 1
            logger.info(f"Start {search_iteration}th Search...")
            history_query_ = json.dumps(history_query, indent=4)
            history_infos_ = json.dumps(history_infos, indent=4)
            query_prompt = f"This is search {search_iteration} of {max_search_iterations} maximum searches allowed.\n User Instruction:{task} \n Previous Queries:\n {history_query_} \n Previous Search Results:\n {history_infos_}\n"
            search_messages.append(HumanMessage(content=query_prompt))
            ai_query_msg = llm.invoke(search_messages[:1] + search_messages[1:][-1:])
            search_messages.append(ai_query_msg)
            if hasattr(ai_query_msg, "reasoning_content"):
                logger.info("🤯 Start Search Deep Thinking: ")
                logger.info(ai_query_msg.reasoning_content)
                logger.info("🤯 End Search Deep Thinking")
            ai_query_content = ai_query_msg.content.replace("```json", "").replace("```", "")
            ai_query_content = repair_json(ai_query_content)
            ai_query_content = json.loads(ai_query_content)
            query_plan = ai_query_content["plan"]
            logger.info(f"Current Iteration {search_iteration} Planing:")
            logger.info(query_plan)
            query_tasks = ai_query_content["queries"]
            if not query_tasks:
                break
            else:
                query_tasks = query_tasks[:max_query_num]
                history_query.extend(query_tasks)
                logger.info("Query tasks:")
                logger.info(query_tasks)

            # 2. Perform Web Search and Auto exec
            # Parallel BU agents
            add_infos = "1. Please click on the most relevant link to get information and go deeper, instead of just staying on the search page. \n" \
                        "2. When opening a PDF file, please remember to extract the content using extract_content instead of simply opening it for the user to view.\n"
            if use_own_browser:
                agent = CustomAgent(
                    task=query_tasks[0],
                    llm=llm,
                    add_infos=add_infos,
                    browser=browser,
                    browser_context=browser_context,
                    use_vision=use_vision,
                    system_prompt_class=CustomSystemPrompt,
                    agent_prompt_class=CustomAgentMessagePrompt,
                    max_actions_per_step=5,
                    controller=controller
                )
                agent_result = await agent.run(max_steps=kwargs.get("max_steps", 10))
                query_results = [agent_result]
                # Manually close all tab
                session = await browser_context.get_session()
                pages = session.context.pages
                await browser_context.create_new_tab()
                for page_id, page in enumerate(pages):
                    await page.close()

            else:
                agents = [CustomAgent(
                    task=task,
                    llm=llm,
                    add_infos=add_infos,
                    browser=browser,
                    browser_context=browser_context,
                    use_vision=use_vision,
                    system_prompt_class=CustomSystemPrompt,
                    agent_prompt_class=CustomAgentMessagePrompt,
                    max_actions_per_step=5,
                    controller=controller,
                ) for task in query_tasks]
                query_results = await asyncio.gather(
                    *[agent.run(max_steps=kwargs.get("max_steps", 10)) for agent in agents])

            if agent_state and agent_state.is_stop_requested():
                # Stop
                break
            # 3. Summarize Search Result
            query_result_dir = os.path.join(save_dir, "query_results")
            os.makedirs(query_result_dir, exist_ok=True)
            for i in range(len(query_tasks)):
                query_result = query_results[i].final_result()
                if not query_result:
                    continue
                querr_save_path = os.path.join(query_result_dir, f"{search_iteration}-{i}.md")
                logger.info(f"save query: {query_tasks[i]} at {querr_save_path}")
                with open(querr_save_path, "w", encoding="utf-8") as fw:
                    fw.write(f"Query: {query_tasks[i]}\n")
                    fw.write(query_result)
                # split query result in case the content is too long
                query_results_split = query_result.split("Extracted page content:")
                for qi, query_result_ in enumerate(query_results_split):
                    if not query_result_:
                        continue
                    else:
                        # TODO: limit content lenght: 128k tokens, ~3 chars per token
                        query_result_ = query_result_[:128000 * 3]
                    history_infos_ = json.dumps(history_infos, indent=4)
                    record_prompt = f"User Instruction:{task}. \nPrevious Recorded Information:\n {history_infos_}\n Current Search Iteration: {search_iteration}\n Current Search Plan:\n{query_plan}\n Current Search Query:\n {query_tasks[i]}\n Current Search Results: {query_result_}\n "
                    record_messages.append(HumanMessage(content=record_prompt))
                    ai_record_msg = llm.invoke(record_messages[:1] + record_messages[-1:])
                    record_messages.append(ai_record_msg)
                    if hasattr(ai_record_msg, "reasoning_content"):
                        logger.info("🤯 Start Record Deep Thinking: ")
                        logger.info(ai_record_msg.reasoning_content)
                        logger.info("🤯 End Record Deep Thinking")
                    record_content = ai_record_msg.content
                    record_content = repair_json(record_content)
                    new_record_infos = json.loads(record_content)
                    history_infos.extend(new_record_infos)
            if agent_state and agent_state.is_stop_requested():
                # Stop
                break

        logger.info("\nFinish Searching, Start Generating Report...")

        # 5. Report Generation in Markdown (or JSON if you prefer)
        return await generate_final_report(task, history_infos, save_dir, llm)

    except Exception as e:
        logger.error(f"Deep research Error: {e}")
        return await generate_final_report(task, history_
(Content truncated due to size limit. Use line ranges to read in chunks)