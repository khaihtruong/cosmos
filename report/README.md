# Report System

This folder contains the modular report generation system for chat sessions. The code is organized into focused modules with clear responsibilities.

## 📁 Folder Structure

```
report/
├── generator.py          # Main orchestrator (start here!)
├── base.py              # Abstract base classes
├── components/          # Data generators
│   ├── ai_summary.py
│   ├── saved_messages.py
│   ├── descriptive_stats.py
│   └── nlp_analysis.py
├── analyzers/           # Pure analysis functions
│   ├── sentiment.py
│   ├── voice_analysis.py
│   └── keyword_extraction.py
├── renderers/           # Output formatters
│   ├── html_renderer.py
│   └── pdf_renderer.py
└── styles/              # CSS styling
    ├── base_styles.py
    └── pdf_styles.py
```

## 🎯 How It Works

The report system follows a simple pipeline:

```
ChatSession → Components → Analyzers → Renderers → HTML/PDF
```

### 1. **generator.py** - The Orchestrator
- **What it does**: Coordinates everything
- **When to edit**: Changing the overall report generation flow
- **Example**: Adding a new output format or changing how components are executed

### 2. **components/** - Data Generators
- **What they do**: Load data from the database and prepare it for display
- **When to edit**:
  - Adding new sections to reports (create new component)
  - Changing what data appears in existing sections
- **Examples**:
  - `ai_summary.py`: Generates AI-powered summaries using Gemini
  - `saved_messages.py`: Retrieves user's saved messages
  - `descriptive_stats.py`: Calculates conversation statistics
  - `nlp_analysis.py`: Orchestrates NLP analyzers

### 3. **analyzers/** - Pure Analysis
- **What they do**: Perform calculations on text (no database access)
- **When to edit**: Changing how sentiment, voice, or keywords are analyzed
- **Examples**:
  - `sentiment.py`: Uses TextBlob to analyze positive/negative tone
  - `voice_analysis.py`: Detects active vs passive voice using spaCy
  - `keyword_extraction.py`: Finds emotional keywords and questions

### 4. **renderers/** - Output Formatters
- **What they do**: Convert data into HTML or PDF format
- **When to edit**:
  - Changing the HTML structure
  - Rearranging sections
  - Adding new display formats
- **Examples**:
  - `html_renderer.py`: Generates web-ready HTML
  - `pdf_renderer.py`: Generates print-optimized HTML

### 5. **styles/** - Visual Appearance
- **What they do**: Define colors, fonts, layouts (CSS only)
- **When to edit**:
  - Changing colors, fonts, spacing
  - Adjusting print layout
  - Making reports match brand guidelines
- **Examples**:
  - `base_styles.py`: Core styling for all reports
  - `pdf_styles.py`: Print-specific overrides

## 🛠️ Common Tasks

### Adding a New Report Section

1. **Create a component** in `components/my_section.py`:
```python
from report.base import ReportComponent

class MySection(ReportComponent):
    def generate(self):
        # Load data from database
        data = self.session.some_data
        return {'title': 'My Section', 'data': data}
```

2. **Register it** in `components/__init__.py`:
```python
from .my_section import MySection

COMPONENT_REGISTRY['my_section'] = MySection
```

3. **Add rendering logic** in `renderers/html_renderer.py`:
```python
def render_component(self, component_name, data):
    if component_name == 'my_section':
        return self._render_my_section(data)
    # ... existing code
```

4. **Style it** in `styles/base_styles.py`:
```css
.unified-report .my-section {
    background: #f0f8ff;
    padding: 1rem;
}
```

### Changing Colors or Fonts

Edit `styles/base_styles.py` - all visual styling is in one place!

### Adjusting Print Layout

Edit `styles/pdf_styles.py` - controls page breaks, margins, print colors.

### Modifying AI Summary Prompts

Edit the `_build_prompt()` method in `components/ai_summary.py`.

### Changing What Statistics Are Shown

Edit the `generate()` method in `components/descriptive_stats.py`.

## 🔍 Understanding the Architecture

### Separation of Concerns

Each type of module has a specific job:

| Module Type | Responsibility | Database Access? | Returns |
|-------------|---------------|------------------|---------|
| **Components** | Load & prepare data | ✅ Yes | Dictionary |
| **Analyzers** | Pure computation | ❌ No | Dictionary |
| **Renderers** | Format output | ❌ No | HTML string |
| **Stylers** | Visual appearance | ❌ No | CSS string |

### Base Classes

All modules inherit from abstract base classes in `base.py`:

- `ReportComponent`: Interface for components (must implement `generate()`)
- `Analyzer`: Interface for analyzers (must implement `analyze()`)
- `Renderer`: Interface for renderers (must implement `render_component()`)

This ensures consistency and makes the code easier to test.

## 📝 Example Usage

```python
from llm_chat.models.session import ChatSession
from report.generator import ReportGenerator

# Get a session
session = ChatSession.query.get(session_id)

# Create generator
generator = ReportGenerator(session)

# Export to HTML
html_path = generator.save_report(format='html')

# Or get HTML string directly
html_string = generator.export_html(standalone=True)
```

## 🚀 Adding New Features

1. **New analysis type** (e.g., readability score):
   - Create analyzer in `analyzers/readability.py`
   - Use it in `components/nlp_analysis.py`

2. **New output format** (e.g., Markdown):
   - Create renderer in `renderers/markdown_renderer.py`
   - Add method in `generator.py`

3. **New data source** (e.g., user feedback):
   - Create component in `components/feedback.py`
   - Register in `components/__init__.py`

## 💡 Tips

- **Start with `generator.py`** to understand the flow
- **Components** are independent - they don't talk to each other
- **Analyzers** are pure functions - easy to test!
- **Renderers** just format data - no business logic
- **Styles** are scoped to `.unified-report` to avoid conflicts

## ❓ Questions?

- "Where do I change report colors?" → `styles/base_styles.py`
- "How do I add a new section?" → Create component, register, render
- "Where's the AI summary logic?" → `components/ai_summary.py`
- "How do sentiment scores work?" → `analyzers/sentiment.py`
- "Can I customize the PDF layout?" → `styles/pdf_styles.py`

---

**Last Updated**: Post-refactoring from 1,124-line monolith to modular structure
