import asyncio
import os
import re
from datetime import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langchain.tools import tool


llm = ChatOllama(model="qwen2.5:7b")


def extract_conflicts(content: str):
    pattern = r"<<<<<<<.*?=======.*?>>>>>>>.*?"
    return re.findall(pattern, content, re.DOTALL)


async def resolve_conflict_block(file_path: str, conflict_block: str):
    prompt = f"""
You are a senior software engineer.

Resolve this git merge conflict.

Rules:
- Preserve functionality from both sides whenever possible.
- Remove all merge conflict markers.
- Return only the final code.
- No markdown.
- No explanations.

File:
{file_path}

Conflict:
{conflict_block}
"""

    response = await llm.ainvoke(prompt)

    return response.content.strip()


async def resolve_file_conflicts(file_path: str):

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    conflicts = extract_conflicts(content)

    if not conflicts:
        return

    updated_content = content

    for conflict in conflicts:
        resolved = await resolve_conflict_block(
            file_path,
            conflict
        )

        updated_content = updated_content.replace(
            conflict,
            resolved,
            1
        )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)


@tool
async def push_changes(commit_message: str):
    """
    Safely pull latest changes, resolve merge conflicts,
    commit and push code.
    """

    current_dir = os.getcwd()

    mcp_client = MultiServerMCPClient({
        "gitserver": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@cyanheads/git-mcp-server@latest"]
        }
    })

    tools = await mcp_client.get_tools()

    tool_map = {
        tool.name: tool
        for tool in tools
    }

    print("Setting working directory...")

    await tool_map["git_set_working_dir"].ainvoke({
        "path": current_dir
    })

    # =====================================================
    # STEP 1: CREATE BACKUP BRANCH
    # =====================================================

    backup_branch = (
        f"backup_before_pull_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    print(f"Creating backup branch: {backup_branch}")

    try:
        await tool_map["git_branch"].ainvoke({
            "path": current_dir,
            "name": backup_branch
        })
    except Exception as e:
        print("Backup branch creation failed:", e)

    # =====================================================
    # STEP 2: CHECK STATUS
    # =====================================================

    status = await tool_map["git_status"].ainvoke({
        "path": current_dir
    })

    print(status)

    has_local_changes = (
        "modified:" in str(status).lower()
        or "new file:" in str(status).lower()
        or "deleted:" in str(status).lower()
    )

    stash_created = False

    # =====================================================
    # STEP 3: STASH IF NEEDED
    # =====================================================

    if has_local_changes:

        print("Stashing local changes...")

        try:
            await tool_map["git_stash"].ainvoke({
                "path": current_dir
            })

            stash_created = True

        except Exception as e:
            print("Stash failed:", e)

    # =====================================================
    # STEP 4: PULL
    # =====================================================

    print("Pulling latest code...")

    pull_result = await tool_map["git_pull"].ainvoke({
        "path": current_dir
    })

    print(pull_result)

    # =====================================================
    # STEP 5: STASH POP
    # =====================================================

    if stash_created:

        print("Applying stashed changes...")

        try:
            await tool_map["git_stash_pop"].ainvoke({
                "path": current_dir
            })

        except Exception as e:
            print("Stash pop reported issue:", e)

    # =====================================================
    # STEP 6: FIND CONFLICTS
    # =====================================================

    status_after_pop = await tool_map["git_status"].ainvoke({
        "path": current_dir
    })

    print(status_after_pop)

    conflicted_files = []

    for line in str(status_after_pop).splitlines():

        if line.startswith("UU "):
            conflicted_files.append(
                line.replace("UU ", "").strip()
            )

    # =====================================================
    # STEP 7: RESOLVE CONFLICTS
    # =====================================================

    if conflicted_files:

        print(
            f"Found {len(conflicted_files)} "
            f"conflicted files"
        )

        for file in conflicted_files:

            full_path = os.path.join(
                current_dir,
                file
            )

            if os.path.exists(full_path):

                print(
                    f"Resolving conflict in {file}"
                )

                await resolve_file_conflicts(
                    full_path
                )

    # =====================================================
    # STEP 8: VERIFY CONFLICTS GONE
    # =====================================================

    verification_status = await tool_map["git_status"].ainvoke({
        "path": current_dir
    })

    unresolved = []

    for line in str(verification_status).splitlines():

        if line.startswith("UU "):
            unresolved.append(line)

    if unresolved:

        raise Exception(
            "Some merge conflicts could not "
            f"be resolved: {unresolved}"
        )

    # =====================================================
    # STEP 9: ADD
    # =====================================================

    print("Adding files...")

    await tool_map["git_add"].ainvoke({
        "path": current_dir,
        "paths": ["."]
    })

    # =====================================================
    # STEP 10: COMMIT
    # =====================================================

    print("Creating commit...")

    commit_result = await tool_map["git_commit"].ainvoke({
        "path": current_dir,
        "message": commit_message
    })

    print(commit_result)

    # =====================================================
    # STEP 11: PUSH
    # =====================================================

    print("Pushing code...")

    push_result = await tool_map["git_push"].ainvoke({
        "path": current_dir
    })

    print(push_result)

    return (
        f"Successfully pushed code. "
        f"Backup branch: {backup_branch}"
    )


async def main():

    result = await push_changes.ainvoke({
        "commit_message":
        "Added MCP orchestration logic"
    })

    print(result)


if __name__ == "__main__":
    asyncio.run(main())