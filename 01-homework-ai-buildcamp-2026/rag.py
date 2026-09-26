import argparse
import json
from pathlib import Path
from typing import Literal, Union

from minsearch import Index
from openai import OpenAI
from pydantic import BaseModel, Field

from index_books import BACKENDS, DEFAULT_BACKEND, index_path_for

INSTRUCTIONS = """
You're a course assistant, your task is to answer the QUESTION from the
course students using the provided CONTEXT
"""


class RAGResponse(BaseModel):
    answer: str = Field(description="The main answer to the user's question in markdown")
    found_answer: bool = Field(description="True if relevant information was found in the documentation")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    confidence_explanation: str = Field(description="Explanation about the confidence level")
    answer_type: Literal["how-to", "explanation", "troubleshooting", "comparison", "reference"] = Field(
        description="The category of the answer"
    )
    followup_questions: list[str] = Field(description="Suggested follow-up questions")

PROMPT_TEMPLATE = """
<QUESTION>
{question}
</QUESTION>

<CONTEXT>
{context}
</CONTEXT>
""".strip()

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_NUM_RESULTS = 5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Answer a question using RAG over the indexed book chunks")
    parser.add_argument("query", help="Question to ask")
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=DEFAULT_NUM_RESULTS,
        help=f"Number of chunks to retrieve for context (default: {DEFAULT_NUM_RESULTS})",
    )
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=DEFAULT_BACKEND,
        help=f"Which index to use, by the backend used to build it (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=None,
        help="Path to a specific index file (overrides --backend)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--structured",
        action="store_true",
        help="Use structured outputs (RAGResponse) instead of plain text",
    )
    return parser.parse_args()


def build_prompt(
        question: str,
        search_results: list[dict],) -> str:
    context = json.dumps(search_results, indent=2)
    prompt = PROMPT_TEMPLATE.format(
        question=question,
        context=context
    ).strip()
    return prompt


def search(
        index: Index,
        question: str,
        num_results: int = DEFAULT_NUM_RESULTS,) -> list[dict]:
    return index.search(question, num_results=num_results)


def llm(
        openai_client: OpenAI,
        user_prompt: str,
        instructions: str = INSTRUCTIONS,
        model: str = DEFAULT_MODEL,
        structured: bool = False,
        ) -> tuple[Union[str, RAGResponse], int, int]:
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]

    if structured:
        response = openai_client.responses.parse(
            model=model,
            input=messages,
            text_format=RAGResponse,
        )
        return response.output_parsed, response.usage.input_tokens, response.usage.output_tokens

    response = openai_client.responses.create(
        model=model,
        input=messages
    )

    return response.output_text, response.usage.input_tokens, response.usage.output_tokens


def rag(
        query: str,
        backend: str = DEFAULT_BACKEND,
        index_path: Path | None = None,
        num_results: int = DEFAULT_NUM_RESULTS,
        model: str = DEFAULT_MODEL,
        structured: bool = False,
        ) -> tuple[Union[str, RAGResponse], int, int]:
    index_path = index_path or index_path_for(backend)
    index = Index.load(index_path)
    openai_client = OpenAI()

    search_results = search(index, query, num_results)
    prompt = build_prompt(query, search_results)
    return llm(openai_client, prompt, INSTRUCTIONS, model, structured)


def main() -> None:
    args = parse_args()
    answer, input_tokens, output_tokens = rag(
        args.query,
        args.backend,
        args.index_path,
        args.num_results,
        args.model,
        args.structured,
    )

    if isinstance(answer, RAGResponse):
        print(answer.model_dump_json(indent=2))
    else:
        print(answer)

    print()
    print(f"input_tokens={input_tokens}, output_tokens={output_tokens}")


if __name__ == "__main__":
    main()
