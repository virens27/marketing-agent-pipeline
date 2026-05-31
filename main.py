import sys
import logging
import subprocess
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

def run_agent(module: str, name: str):
    logger.info(f"{'='*50}")
    logger.info(f"Running {name}...")
    logger.info(f"{'='*50}")
    result = subprocess.run(
        [sys.executable, "-m", module],
        capture_output=False
    )
    if result.returncode != 0:
        logger.error(f"{name} failed with return code {result.returncode}")
        sys.exit(1)
    logger.info(f"{name} completed successfully.")
    time.sleep(1)

def main():
    logger.info("Starting Marketing Agent Pipeline...")
    logger.info("="*50)

    run_agent("agents.research_agent", "Agent 1 - Research Agent")
    run_agent("agents.analysis_agent", "Agent 2 - Analysis Agent")
    run_agent("agents.content_agent",  "Agent 3 - Content Agent")

    logger.info("="*50)
    logger.info("Agents 1-3 complete. Starting Review UI...")
    logger.info("Open http://localhost:8000 to review and approve campaigns.")
    logger.info("Press Ctrl+C to stop the server after reviewing.")
    logger.info("="*50)

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "api.main:app", "--port", "8000"],
            capture_output=False
        )
    except KeyboardInterrupt:
        logger.info("Review UI stopped.")

    logger.info("="*50)
    logger.info("Running Agent 5 - Execution Agent...")
    run_agent("agents.execution_agent", "Agent 5 - Execution Agent")

    logger.info("="*50)
    logger.info("Pipeline complete! Check your Google Sheet for all outputs.")
    logger.info("="*50)

if __name__ == "__main__":
    main()