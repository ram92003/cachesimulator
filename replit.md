# Interactive Cache Memory Simulator

## Overview
A modern, web-based interactive cache memory simulator with visual animations and educational features for Computer Organization and Architecture (COA) demonstrations. Includes both a modern web interface and the original CLI version.

## Project Purpose
Educational tool for visualizing and understanding cache memory operations:
- **Interactive Learning**: Visual feedback with animations
- **Two Interfaces**: Modern web UI + traditional CLI
- **Complete Coverage**: Direct-Mapped and Fully Associative caches
- **Educational Output**: Step-by-step progress, tooltips, and detailed logs
- **Engaging UX**: Sound effects, hover states, smooth transitions

## Architecture

### Backend (Flask)
1. **app.py**: Flask REST API server
   - `/api/create_cache`: Initialize cache with configuration
   - `/api/access`: Execute memory operations
   - `/api/get_state`: Retrieve current cache state
   - `/api/reset`: Reset cache to initial state

2. **src/cache_engine.py**: Core cache simulation logic
   - `CacheBlock`: Cache line representation
   - `CacheSimulator`: Base class with statistics
   - `DirectMappedCache`: Direct-mapped implementation
   - `FullyAssociativeCache`: Fully associative with LRU

### Frontend (Web Interface)
1. **templates/index.html**: Modern HTML5 structure
   - Configuration panel with tooltips
   - Cache state visualization
   - Real-time statistics dashboard
   - Operation log with auto-scroll
   - Progress indicator
   - Collapsible panels

2. **static/css/style.css**: Modern styling with animations
   - Green glow effect on cache hits
   - Red pulse/shake on cache misses
   - Fade-in animation for block loading
   - Smooth transitions throughout
   - Responsive design
   - Gradient backgrounds

3. **static/js/simulator.js**: Interactive functionality
   - API communication
   - Animation orchestration
   - Event handling
   - Sound effects (Web Audio API)
   - Tooltip system
   - Auto-scrolling logs

### CLI Version
**cache_simulator.py**: Original command-line interface
- Still available for text-based use
- Sample demonstrations
- Interactive mode

## Key Features

### Visual Feedback
- ✅ **Hit Animation**: Green glow effect (1.5s)
- ❌ **Miss Animation**: Red pulse/shake (0.6s)
- 📦 **Load Animation**: Fade-in slide (0.8s)
- 🎯 **Progress Steps**: Animated step indicator
- 🎨 **Hover Effects**: Button states, field tooltips

### Interactive Elements
- **Collapsible Panels**: Click headers to expand/collapse
- **Hover Tooltips**: Explain valid bit, tag, dirty bit, data
- **Sound Toggle**: Optional audio feedback (toggleable)
- **Auto-Scroll Log**: Latest entries highlighted
- **Responsive Buttons**: Hover, active, disabled states

### Educational Output
- Address decomposition visualization
- Step-by-step operation progress
- Real-time statistics updates
- Detailed operation logs
- Cache state table with color coding

## Technical Stack
- **Backend**: Python 3.11 + Flask
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Cache Logic**: Pure Python (no external deps for core)
- **Animations**: CSS keyframes & transitions
- **Sound**: Web Audio API
- **Icons**: Font Awesome 6

## Usage

### Web Interface
1. Run: `python app.py` (auto-configured workflow)
2. Visit webview or `http://localhost:5000`
3. Create cache with configuration
4. Execute memory operations
5. Watch visual feedback!

### CLI Interface
1. Run: `python cache_simulator.py`
2. Choose sample demo or interactive mode
3. See text-based output

## Recent Changes
- **2025-11-19**: Major web interface update + progress indicator fix
  - Created modern Flask-based web application
  - Added CSS animations for hits/misses/loading
  - Implemented 4-step progress indicator with intelligent step mapping
  - Fixed progress indicator to handle variable backend steps (4-5 steps)
  - Backend now includes explicit Hit/Miss step for clarity
  - Frontend maps all steps to 4 indicators: Fetch → Compare → Hit/Miss → Update
  - Added hover tooltips for all cache fields
  - Created responsive button states with ripple effects
  - Implemented auto-scrolling log panel with highlights
  - Added optional toggleable sound effects (Web Audio API)
  - Applied modern design (gradients, shadows, rounded corners, smooth transitions)
  - Created collapsible panel system for all sections
  - Maintained original CLI version for backwards compatibility
  - Removed unused boilerplate files (main.py)

## User Preferences
- Prefers visual, interactive learning tools
- Values modern UI with smooth animations
- Wants educational tooltips and explanations
- Likes optional audio feedback

## Project State
**Status**: Complete with both web and CLI interfaces
**Version**: 2.0 (Web) + 1.0 (CLI)
**Last Updated**: November 19, 2025

## Files
- `app.py` - Flask backend
- `src/cache_engine.py` - Core logic
- `templates/index.html` - Web UI
- `static/css/style.css` - Styling & animations
- `static/js/simulator.js` - Interactivity
- `cache_simulator.py` - CLI version
- `README.md` - Documentation

## Configuration
- **Workflow**: "Cache Simulator Web App"
- **Command**: `python app.py`
- **Port**: 5000
- **Output**: webview
