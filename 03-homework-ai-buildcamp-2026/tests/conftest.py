from tests.patch_agent import patch_agent, tracker, unpatch_agent


def pytest_configure(config):
    patch_agent()


def pytest_unconfigure(config):
    unpatch_agent()


def pytest_terminal_summary(terminalreporter):
    terminalreporter.section("LLM usage")
    terminalreporter.write_line(
        f"runs: {tracker.runs} | requests: {tracker.requests} | "
        f"input tokens: {tracker.input_tokens} | output tokens: {tracker.output_tokens}"
    )
    terminalreporter.write_line(f"total cost: ${tracker.cost:.6f}")
