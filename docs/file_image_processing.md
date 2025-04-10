# File and Image Processing with AI QA Agent

This document provides comprehensive documentation for the file and image processing capabilities of the AI QA Agent.

## Overview

The AI QA Agent now supports processing and analyzing various file types, including text files, code files, structured data files, and images. These capabilities enable advanced testing scenarios such as:

- Analyzing code files for quality and potential issues
- Extracting test cases from documentation files
- Processing images for UI testing
- Comparing UI designs with actual implementations
- Detecting visual bugs and UI inconsistencies

## File Processing Capabilities

### Supported File Types

The AI QA Agent supports the following file types:

| Category | File Extensions |
|----------|----------------|
| Text | .txt, .md, .log, .csv |
| Code | .py, .js, .java, .cpp, .cs, .html, .css, .php, .rb, .go, .rs, .ts |
| Structured Data | .json, .yaml, .yml, .xml, .toml |
| Documents | .pdf, .docx |
| Test Files | .feature (Gherkin) |
| Images | .jpg, .jpeg, .png, .gif, .bmp, .webp, .tiff, .svg |

### File Processing API

#### Basic File Processing

```python
from api_enhanced import aiqa

# Process a file with default prompts
result = aiqa.process_file("/path/to/file.txt")

# Process a file with custom prompt
result = aiqa.process_file(
    "/path/to/file.txt",
    prompt="Summarize the key points in this document"
)

# Process a file with custom system prompt
result = aiqa.process_file(
    "/path/to/file.txt",
    prompt="Extract the main arguments from this document",
    system_prompt="You are a document analysis expert. Focus on identifying key arguments and supporting evidence."
)
```

#### Code Analysis

```python
from api_enhanced import aiqa

# Analyze a code file
analysis = aiqa.analyze_code_file("/path/to/code.py")

# The analysis result contains:
# - summary: Brief summary of what the code does
# - complexity: Assessment of code complexity (Low, Medium, High)
# - issues: List of potential issues or bugs
# - suggestions: List of improvement suggestions
# - test_coverage: Assessment of test coverage or testability

print(f"Code complexity: {analysis['complexity']}")
print("Potential issues:")
for issue in analysis['issues']:
    print(f"- {issue}")
```

#### Test Case Extraction

```python
from api_enhanced import aiqa

# Extract test cases from a file
test_cases = aiqa.extract_test_cases_from_file("/path/to/requirements.md")

# Each test case contains:
# - title: Test case title
# - description: Test case description
# - steps: List of test steps
# - expected_results: List of expected results
# - priority: Priority level (Low, Medium, High)

for test_case in test_cases:
    print(f"Test: {test_case['title']} (Priority: {test_case['priority']})")
    print("Steps:")
    for i, step in enumerate(test_case['steps'], 1):
        print(f"{i}. {step}")
```

#### Utility Functions

```python
from api_enhanced import aiqa

# Detect file type
file_type = aiqa.detect_file_type("/path/to/file")
print(f"File type: {file_type}")

# Extract text from file
text = aiqa.extract_text_from_file("/path/to/file.pdf")
print(f"Extracted text: {text[:100]}...")

# Extract structured data from file
data = aiqa.extract_structured_data_from_file("/path/to/config.json")
print(f"Configuration: {data}")
```

## Image Processing Capabilities

### Image Analysis

```python
from api_enhanced import aiqa

# Analyze an image
analysis = aiqa.analyze_image("/path/to/screenshot.png")

# The analysis result contains:
# - overall_assessment: General assessment of the UI
# - usability_issues: List of potential usability issues
# - accessibility_concerns: List of accessibility concerns
# - design_consistency: Evaluation of design consistency
# - improvement_suggestions: List of improvement suggestions

print("Usability issues:")
for issue in analysis['usability_issues']:
    print(f"- {issue}")
```

### UI Comparison

```python
from api_enhanced import aiqa

# Compare UI design with actual implementation
comparison = aiqa.compare_ui_with_design(
    "/path/to/design.png",
    "/path/to/screenshot.png"
)

# The comparison result contains:
# - fidelity_score: Overall assessment of implementation fidelity (0-100)
# - discrepancies: List of specific discrepancies identified
# - missing_elements: List of elements in design but missing in implementation
# - additional_elements: List of elements in implementation but not in design
# - text_differences: List of text content differences
# - layout_issues: List of layout and positioning issues
# - improvement_suggestions: List of improvement suggestions
# - similarity_score: Numerical similarity score (0-1)
# - diff_image_path: Path to difference visualization image

print(f"Implementation fidelity: {comparison['fidelity_score']}%")
print(f"Similarity score: {comparison['similarity_score']:.2f}")
print("Discrepancies:")
for discrepancy in comparison['discrepancies']:
    print(f"- {discrepancy}")

# Display the difference visualization
import matplotlib.pyplot as plt
from PIL import Image
plt.imshow(Image.open(comparison['diff_image_path']))
plt.title("UI Differences")
plt.show()
```

### OCR and Text Extraction

```python
from api_enhanced import aiqa

# Extract text from an image using OCR
text = aiqa.extract_text_from_image("/path/to/screenshot.png")
print(f"Extracted text: {text}")
```

### Image Comparison

```python
from api_enhanced import aiqa

# Compare two images
similarity_score, diff_path = aiqa.compare_images(
    "/path/to/image1.png",
    "/path/to/image2.png"
)

print(f"Similarity score: {similarity_score:.2f}")
print(f"Difference visualization: {diff_path}")
```

### UI Element Detection

```python
from api_enhanced import aiqa

# Detect UI elements in an image
elements = aiqa.detect_ui_elements("/path/to/screenshot.png")

print(f"Detected {len(elements)} UI elements:")
for element in elements:
    print(f"- {element['type']} at position {element['position']}")
    if element['text']:
        print(f"  Text: {element['text']}")
```

## Advanced Usage

### Combining File and Image Processing

```python
from api_enhanced import aiqa
import os

# Analyze a UI test report that includes screenshots
report_analysis = aiqa.process_file("/path/to/test_report.md")

# Extract image paths from the report
image_paths = []
for line in aiqa.extract_text_from_file("/path/to/test_report.md").split("\n"):
    if ".png" in line or ".jpg" in line:
        # Extract image path (simplified example)
        image_path = line.split("(")[1].split(")")[0]
        if os.path.exists(image_path):
            image_paths.append(image_path)

# Analyze each screenshot
for image_path in image_paths:
    print(f"Analyzing image: {image_path}")
    image_analysis = aiqa.analyze_image(image_path)
    print(f"Found {len(image_analysis.get('usability_issues', []))} usability issues")
```

### UI Testing Workflow

```python
from api_enhanced import aiqa

# 1. Compare design with implementation
comparison = aiqa.compare_ui_with_design(
    "/path/to/design.png",
    "/path/to/screenshot.png"
)

# 2. If similarity score is below threshold, analyze the differences
if comparison['similarity_score'] < 0.9:
    print("Significant differences detected between design and implementation")
    
    # 3. Detect UI elements in both images
    design_elements = aiqa.detect_ui_elements("/path/to/design.png")
    ui_elements = aiqa.detect_ui_elements("/path/to/screenshot.png")
    
    # 4. Compare element counts
    print(f"Design has {len(design_elements)} elements")
    print(f"Implementation has {len(ui_elements)} elements")
    
    # 5. Extract text from both images
    design_text = aiqa.extract_text_from_image("/path/to/design.png")
    ui_text = aiqa.extract_text_from_image("/path/to/screenshot.png")
    
    # 6. Check for text differences
    if design_text != ui_text:
        print("Text content differs between design and implementation")
```

## LLM Provider Support

The file and image processing capabilities are supported by different LLM providers with varying levels of functionality:

| Provider | File Processing | Image Analysis | Multimodal Support |
|----------|----------------|----------------|-------------------|
| Groq (Claude 3 Opus/Sonnet) | ✅ | ✅ | ✅ |
| Groq (Other models) | ✅ | ⚠️ Limited | ❌ |
| Hyperbolic.xyz | ✅ | ⚠️ Limited | Depends on model |
| Ollama | ✅ | ⚠️ Limited | Depends on model |
| LM Studio | ✅ | ⚠️ Limited | Depends on model |

For image analysis with non-multimodal models, the system uses OCR and computer vision techniques to extract information from images before sending to the LLM.

## Implementation Details

### File Processing

The file processing functionality is implemented in the `FileProcessor` class, which provides methods for:

- Detecting file types based on extension and content
- Extracting text from various file formats
- Extracting code from files
- Extracting structured data from files

### Image Processing

The image processing functionality is implemented in the `ImageProcessor` class, which provides methods for:

- Extracting text from images using OCR
- Encoding images to base64 for API requests
- Comparing images and generating difference visualizations
- Detecting UI elements in images

### LLM Integration

The LLM integration is implemented in the `LLMProvider` abstract base class and its concrete implementations (e.g., `GroqProvider`). These classes provide methods for:

- Processing files using the LLM
- Analyzing code files
- Extracting test cases from files
- Analyzing images
- Comparing UI designs with implementations

## Requirements

To use the file and image processing capabilities, you need to install the following dependencies:

```bash
# Core dependencies
pip install groq langchain-groq openai ollama

# File processing dependencies
pip install PyPDF2 python-docx beautifulsoup4 chardet pyyaml xmltodict toml

# Image processing dependencies
pip install pillow opencv-python-headless pytesseract scikit-image matplotlib
```

Additionally, for OCR functionality, you need to install Tesseract OCR:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download and install from https://github.com/UB-Mannheim/tesseract/wiki
```

## Limitations

- Large files may exceed token limits of LLM models
- Image analysis quality depends on the capabilities of the selected LLM model
- OCR accuracy varies depending on image quality and text characteristics
- UI element detection is based on computer vision techniques and may not be 100% accurate
- Processing time increases with file size and complexity

## Future Enhancements

- Support for more file formats (e.g., audio, video)
- Improved chunking for large files
- Enhanced UI element detection with machine learning
- Support for more LLM providers with multimodal capabilities
- Integration with popular design tools (e.g., Figma, Sketch)
