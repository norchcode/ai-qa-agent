# AI QA Agent

An AI-powered QA testing framework with browser automation capabilities.

## Features

- Browser automation for web testing
- Natural language test case generation
- Test case analysis and optimization
- Gherkin format translation
- Visual testing and screenshot comparison
- Report generation
- Web UI for easy interaction

## Installation

1. Clone the repository:
```bash
git clone https://github.com/norchcode/ai-qa-agent.git
cd ai-qa-agent
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
python -m playwright install chromium
```

4. Create a `.env` file with your API keys (see `.env.example` for required variables)

## Usage

### Running with Xvfb (Recommended)

For environments without a display server, use the provided script:

```bash
chmod +x run_with_xvfb.sh
./run_with_xvfb.sh
```

This starts a virtual X server using Xvfb, allowing browser automation to run without headless mode.

### Standard Run

```bash
python -m src.ui.webui_enhanced
```

Then open your browser to http://127.0.0.1:7789

### Example Commands

Try these commands in the web UI:

- "open google.com, search for AI testing tools"
- "open amazon.com, search for headphones, sort by price low to high"
- "analyze this test case: [paste your test case]"
- "translate to Gherkin: User logs in, adds item to cart, proceeds to checkout"

## Project Structure

- `src/core/`: Core components and controller
- `src/tools/`: Testing and analysis tools
- `src/ui/`: Web UI components
- `src/utils/`: Utility functions and helpers

## License

MIT
