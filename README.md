# 🎬 YouTube Agent System - AI-Powered Video Generator

An intelligent, multi-agent system that automatically generates professional YouTube videos with animated slides, topic-specific scripts, and quality validation. Inspired by presentation tools like Gamma, this system uses AI agents to orchestrate the entire video production pipeline.

## ✨ Features

### 🤖 Multi-Agent Architecture
- **Research Agent** - Conducts parallel research on trends, facts, and competition
- **Script Writer Agent** - Creates topic-specific, engaging video scripts with proper pacing
- **Quality Validator Agent** - Validates and iteratively improves content quality
- **Production Team Orchestrator** - Coordinates all agents in a seamless workflow

### 🎨 Animated Slide Generation
- **Gamma-Style Presentations** - Professional animated slides with smooth transitions
- **Dynamic Text Animations** - Typewriter effects, staggered bullet points, fade-ins
- **Visual Effects** - Gradient backgrounds, decorative elements, progress bars
- **Multiple Transitions** - Fade, slide, and wipe effects between slides
- **Professional Polish** - Slide counters, animated underlines, semi-transparent overlays

### 📝 Topic-Specific Content Generation
- **Intelligent Outlining** - Generates detailed outlines based on video topic
- **Adaptive Scripts** - Different content structures for different topics (AI, automation, general)
- **Key Points Extraction** - Automatically extracts and formats important information
- **Proper Pacing** - Distributes content according to video duration

### 📊 Quality Assurance
- **Iterative Validation** - 5-iteration quality improvement loop
- **Component Scoring** - Evaluates script, visuals, and audio quality
- **Automatic Improvements** - Applies fixes and enhancements automatically
- **Quality Metrics** - Generates quality scores (0-1.0) for each video

### 🎯 Session Management
- **Workflow Tracking** - Monitors entire video generation process
- **Session Persistence** - Tracks sessions with unique IDs
- **Error Handling** - Graceful fallbacks and error recovery
- **Performance Metrics** - Logs processing times and quality metrics

### 📡 Observability & Monitoring
- **Structured Logging** - JSON-formatted logs for all operations
- **Distributed Tracing** - Tracks request flow through agent pipeline
- **Metrics Collection** - Performance and quality metrics
- **Debug Information** - Detailed operation logs for troubleshooting

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
cd c:\AI Agent\youtube_agent_system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your configuration:
```env
# API Configuration
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
PEXELS_API_KEY=your_pexels_key
GOOGLE_API_KEY=your_google_key

# Service URLs
MCP_SERVER_URL=http://localhost:3000
YOUTUBE_API_URL=https://www.googleapis.com/youtube/v3

# Feature Flags
USE_VOICE_SYNTHESIS=false
USE_BACKGROUND_MUSIC=false
ENABLE_API_INTEGRATIONS=false

# Video Settings
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
VIDEO_FPS=30
VIDEO_FORMAT=mp4
```

### Usage

#### Interactive Mode (Recommended)
```bash
python main.py
```

The application will present an interactive menu:
```
============================================================
🎬 YouTube Agent System - Video Generator
============================================================

Options:
1. Generate a new video
2. Exit

Select an option (1-2): 1
```

Enter your video topic and desired duration (in seconds). The system will:
1. Research your topic
2. Generate a script with proper structure
3. Create animated slides
4. Validate quality
5. Save the final video

#### Video Output
Generated videos are saved to: `output_videos/output_video.mp4`

## 📁 Project Structure

```
youtube_agent_system/
├── agents/                          # Multi-agent orchestration
│   ├── base_agent.py               # Base agent class with A2A communication
│   ├── sequential_agents.py         # ScriptWriterAgent
│   ├── parallel_agents.py           # ResearchAgent, ParallelAgentExecutor
│   ├── loop_agents.py               # QualityValidatorAgent
│   └── video_production_team.py     # Main orchestrator
│
├── tools/                           # Tools and utilities
│   ├── custom_tools.py              # VideoEditorTool, AnimatedSlideGenerator
│   ├── builtin_tools.py             # GoogleSearchTool, TextToSpeechTool
│   ├── mcp_tools.py                 # MCP client integration
│   └── openapi_tools.py             # OpenAPI integrations
│
├── memory/                          # Memory and context management
│   ├── session_manager.py           # Session tracking
│   ├── memory_bank.py               # Information storage
│   └── context_engineer.py          # Context optimization
│
├── operations/                      # Workflow orchestration
│   ├── long_running.py              # Long-running operation handling
│   └── workflow_orchestrator.py     # Workflow step management
│
├── observability/                   # Logging and monitoring
│   ├── logger.py                    # Structured logging
│   ├── tracer.py                    # Distributed tracing
│   └── metrics.py                   # Performance metrics
│
├── evaluation/                      # Quality evaluation
│   └── quality_evaluator.py         # Video quality assessment
│
├── protocols/                       # Communication protocols
│   └── a2a_protocol.py              # Agent-to-Agent messaging
│
├── utils/                           # Utility functions
│   ├── file_utils.py                # File operations
│   └── video_assembler.py           # Video assembly utilities
│
├── output_videos/                   # Generated video output
├── config.yaml                      # Configuration file
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🔄 Workflow

### Phase 1: Research (Parallel Execution)
```
Research Agent (Trends) ─┐
Research Agent (Facts)   ├─→ Compiled Research Data
Research Agent (Competition) ─┘
```

### Phase 2: Script Writing (Sequential Execution)
```
Research Data → Script Writer Agent → Detailed Script with:
                                     • Title & Tagline
                                     • Structured Sections
                                     • Key Points
                                     • Conclusion
                                     • Pacing Information
```

### Phase 3: Production (Parallel Execution)
```
Script → Voice Synthesis Tool ─┐
Script → Thumbnail Generator  ├─→ Production Assets
Script → Asset Generation Tool ─┘
```

### Phase 4: Quality Validation (Loop Execution)
```
Production Assets → Quality Validator Agent
                  ↓ (5 iterations)
                  Iterative Improvements
                  ↓
                  Final Quality Score (0-1.0)
```

### Phase 5: Video Assembly
```
Final Assets + Script → Animated Slide Generator → Final MP4 Video
```

## 🎯 Content Generation Examples

### AI/Automation Topics
When you input a topic containing "video generator", "AI agent", or "automation", the system generates:

**Slide 1: Introduction**
- Title: Your topic
- Content: Hook and introduction to the concept

**Slide 2: Multi-Agent Architecture**
- Explains how multiple AI agents work together
- Details specialization and distributed responsibility

**Slide 3: Script Writing & Content Generation**
- Covers how AI creates engaging narratives
- Explains structure, pacing, and audience engagement

**Slide 4: Video Production**
- Details visual creation, animations, and assembly
- Explains quality validation process

**Slide 5: Benefits & Applications**
- Real-world use cases
- Advantages and ROI

**Slide 6: Conclusion**
- Key takeaways
- Call to action

## ⚙️ Configuration Options

### Video Parameters
```python
WIDTH = 1920          # Video width in pixels
HEIGHT = 1080         # Video height in pixels
FPS = 30              # Frames per second
CODEC = 'mp4v'        # Video codec (mp4v or MJPG)
```

### Animation Settings
```python
TRANSITION_TYPES = ['fade', 'slide', 'wipe']
TITLE_ANIMATION = 'typewriter'
BULLET_ANIMATION = 'staggered_fade_in'
DURATION_PER_BULLET = 0.1  # seconds between bullets
```

### Quality Settings
```python
MIN_QUALITY_SCORE = 0.7
VALIDATION_ITERATIONS = 5
COMPONENT_WEIGHTS = {
    'script': 0.4,
    'visuals': 0.3,
    'audio': 0.3
}
```

## 📊 Performance Metrics

### Video Generation Time
- **Short videos (1-2 min)**: 2-5 minutes
- **Medium videos (3-5 min)**: 8-15 minutes
- **Long videos (10+ min)**: 20-40 minutes

*Times vary based on system specifications and topic complexity*

### Quality Scores
- **0.5-0.6**: Basic quality
- **0.6-0.7**: Good quality
- **0.7-0.8**: Very good quality
- **0.8-0.9**: Excellent quality
- **0.9-1.0**: Professional quality

### Processing Breakdown
```
Research Phase:        ~3 seconds (parallel)
Script Writing:        ~2 seconds
Production Setup:      ~1 second
Video Assembly:        ~5-30 minutes (depends on duration)
Quality Validation:    ~5 seconds
Total Time:           5-30 minutes
```

## 🔧 Advanced Usage

### Using the Production Team Directly
```python
from agents.video_production_team import VideoProductionTeam
from memory.session_manager import SessionManager
import asyncio

async def generate_video():
    team = VideoProductionTeam()
    manager = SessionManager()
    
    session = manager.create_session("Your Topic", 180)
    result = await team.execute_workflow(session)
    
    print(f"Video: {result['video_url']}")
    print(f"Quality: {result['metadata']['quality_score']}")

asyncio.run(generate_video())
```

### Custom Topic Handling
Add custom outlines in `sequential_agents.py`:
```python
elif "your_topic" in topic_lower:
    hook = "Your custom hook"
    points = [
        {
            "point": "Custom point 1",
            "duration": duration * 0.3,
            "details": "Detailed explanation"
        },
        # ... more points
    ]
```

### Batch Processing
```python
topics = [
    ("Topic 1", 180),
    ("Topic 2", 240),
    ("Topic 3", 300)
]

for topic, duration in topics:
    asyncio.run(generate_video(topic, duration))
```

## 🛠️ Troubleshooting

### Issue: Video not generating
**Solution**: Check logs in console output. Ensure OpenCV (cv2) is installed.
```bash
pip install opencv-python
```

### Issue: Memory/RAM issues with long videos
**Solution**: The system generates frame-by-frame. For very long videos:
- Reduce resolution (modify WIDTH/HEIGHT in tools/custom_tools.py)
- Generate multiple shorter videos and concatenate

### Issue: Slow video generation
**Solution**: Depends on CPU. Options:
- Use faster CPU
- Reduce video duration
- Optimize frame generation code

### Issue: Content not topic-specific
**Solution**: Update the outline generation in `sequential_agents.py` with your topic keywords.

## 📚 Dependencies

- **numpy** - Numerical computations
- **opencv-python (cv2)** - Video generation and frame processing
- **pillow (PIL)** - Image processing
- **pydantic** - Data validation and models
- **python-dotenv** - Environment configuration
- **elevenlabs** (optional) - Voice synthesis
- **requests** (optional) - API calls
- **moviepy** (optional) - Video composition alternatives

See `requirements.txt` for complete list and versions.

## 🎓 Learning Resources

### Understanding Multi-Agent Systems
- Agent architecture patterns
- Parallel vs Sequential execution
- Inter-agent communication protocols

### Video Processing
- OpenCV video writing and frame manipulation
- Video codec selection and optimization
- Frame generation techniques

### AI/LLM Integration
- Prompt engineering for content generation
- Context management for coherent narratives
- Quality metrics for AI outputs

## 🤝 Contributing

To extend this system:

1. **Add new agents** in `agents/` directory
2. **Extend tools** in `tools/` directory
3. **Improve content generation** in `sequential_agents.py`
4. **Add new transitions/animations** in `custom_tools.py`

## 📝 License

This project is provided as-is for educational and commercial use.

## 🎬 Example Output

When you run the system with:
```
Topic: "Explanation of Automated Video Generator Using AI Agents"
Duration: 180 seconds
```

You get:
- ✅ 7 animated slides with topic-specific content
- ✅ 1920x1080 @ 30 FPS MP4 video
- ✅ Smooth transitions and animations
- ✅ Professional presentation format
- ✅ Quality score: 0.75+
- ✅ Total generation time: ~19 minutes

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review log files in console output
3. Check code comments for detailed explanations

## 🚀 Future Enhancements

- [ ] Real stock footage integration (Pexels API)
- [ ] AI-generated background images
- [ ] Voice synthesis with emotion control
- [ ] Background music synchronization
- [ ] Advanced effect library (parallax, 3D transforms)
- [ ] Custom branding and watermarks
- [ ] Export to multiple formats (MP4, WebM, GIF)
- [ ] Real-time preview mode
- [ ] Video analytics and performance tracking

---

**Made with ❤️ using AI Agents and OpenCV**

*Generate professional videos in minutes, not hours.*
