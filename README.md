# Interactive Cache Memory Simulator 🎯

A modern, visual, and interactive web-based tool for understanding cache memory operations in Computer Architecture. Perfect for COA demonstrations, learning, and exploring cache behavior!

## ✨ Features

### 🎨 Modern Interactive UI
- **Smooth Animations**: Visual feedback for every operation
  - ✅ Green glow effect on cache hits
  - ❌ Red pulse/shake effect on cache misses
  - 📦 Fade-in animation when loading blocks into cache
- **Progress Indicator**: Step-by-step visualization of each operation:
  - Fetch → Compare Tag → Hit/Miss Decision → Update Cache
- **Collapsible Panels**: Organize your workspace by expanding/collapsing sections
- **Hover Tooltips**: Learn what each field means (valid bit, tag, dirty bit, data)
- **Auto-Scrolling Log**: Latest operations highlighted and automatically visible
- **Sound Effects**: Optional audio feedback for hits and misses (toggleable)

### 🧠 Cache Simulation Features
- **Two Cache Types**:
  - Direct-Mapped Cache (fixed mapping)
  - Fully Associative Cache with LRU replacement
- **Write Policies**:
  - Write-Through (immediate memory updates)
  - Write-Back (deferred updates with dirty bit)
- **Real-Time Statistics**:
  - Total accesses, hits, misses
  - Hit ratio and miss ratio
  - Memory reads and writes tracking
- **Educational Output**:
  - Address decomposition (tag, index, offset)
  - Detailed operation logs
  - Cache state visualization

### 💎 Modern Design
- Gradient backgrounds and smooth transitions
- Rounded corners and elegant shadows
- Responsive button states (hover, active, disabled)
- Clean, professional color scheme
- Mobile-responsive layout

## 🚀 Quick Start

### Run the Web Application

The application is already configured and running! Simply open the webview to access the interactive simulator.

Or manually run:
```bash
python app.py
```

Then visit: `http://localhost:5000`

## 📖 How to Use

### 1. Create a Cache
1. Select your cache configuration:
   - **Cache Size**: Total size in bytes (16, 32, 64, or 128)
   - **Block Size**: Size of each block (4, 8, or 16 bytes)
   - **Cache Type**: Direct-Mapped or Fully Associative
   - **Write Policy**: Write-Through or Write-Back
2. Click **"Create Cache"**
3. Watch the cache table appear with initial state

### 2. Execute Memory Operations
1. Enter a **Memory Address** (decimal or hex)
2. Choose **Operation Type**: Read or Write
3. Click **"Execute Operation"**
4. Watch the magic happen:
   - ✨ Progress indicator shows each step
   - 🎯 Cache line highlights in green (hit) or red (miss)
   - 📊 Statistics update in real-time
   - 📝 Operation logged with full details

### 3. Explore Interactive Features
- **Hover over cache fields** to see tooltips explaining each component
- **Toggle sound effects** using the switch in the operation panel
- **Collapse/expand panels** by clicking on panel headers
- **View detailed logs** showing address decomposition and results
- **Reset cache** to start fresh experiments
- **Clear logs** to declutter the operation history

## 🎓 Educational Use Cases

### Demo 1: Understanding Cache Hits vs Misses
```
Configuration: 16-byte cache, 4-byte blocks, Direct-Mapped, Write-Back
Sequence: 0, 4, 8, 12, 0, 4, 8, 12
Result: Shows how repeated addresses create hits after initial misses
```

### Demo 2: Conflict Misses in Direct-Mapped
```
Configuration: 16-byte cache, 4-byte blocks, Direct-Mapped
Sequence: 0, 16, 32, 0, 16, 32
Result: Addresses map to same line, causing conflicts (0% hit rate!)
```

### Demo 3: LRU Benefits in Fully Associative
```
Configuration: 16-byte cache, 4-byte blocks, Fully Associative
Sequence: 0, 16, 32, 0, 16, 32
Result: No conflicts! LRU allows all blocks to coexist (62.5% hit rate)
```

### Demo 4: Write-Through vs Write-Back
```
Configuration: Same cache, different write policies
Operations: All writes to addresses 0, 4, 8, 12, 0, 4, 8, 12
Comparison:
  - Write-Through: 8 memory writes
  - Write-Back: 0 memory writes (100% reduction!)
```

## 🏗️ Architecture

```
cache-simulator/
├── app.py                  # Flask backend API
├── src/
│   └── cache_engine.py     # Core cache simulation logic
├── templates/
│   └── index.html          # Modern HTML UI
├── static/
│   ├── css/
│   │   └── style.css       # Animations & modern styling
│   ├── js/
│   │   └── simulator.js    # Interactive functionality
│   └── sounds/
│       └── (optional sound files)
├── cache_simulator.py      # Original CLI version (still available!)
└── README.md
```

## 🎨 UI Components

### Cache State Panel
- **Bit Breakdown**: Shows tag, index (if applicable), and offset bits
- **Cache Table**: Visual representation of all cache lines
- **Color-Coded Fields**:
  - 🟢 Green: Valid bit set
  - 🔴 Red: Invalid or dirty bit unset
  - 🔵 Blue: Tag and data values
  - 🟡 Yellow: Dirty bit set

### Statistics Dashboard
- **6 Key Metrics** displayed in cards:
  - Total Accesses
  - Cache Hits (green theme)
  - Cache Misses (red theme)
  - Hit Ratio
  - Memory Reads
  - Memory Writes

### Operation Log
- Chronological list of all operations
- Latest entry highlighted
- Shows:
  - Timestamp
  - Address and operation type
  - Hit/Miss status
  - Address decomposition
  - Eviction warnings
  - Dirty block writebacks

## 🎯 Key Concepts Visualized

### Address Decomposition
See exactly how addresses are split into tag, index, and offset bits based on your cache configuration.

### Cache Hit (Green Glow)
- Valid bit = 1
- Tag matches
- Data retrieved from cache (fast!)

### Cache Miss (Red Pulse)
- Invalid block OR tag mismatch
- Must fetch from memory (slow)
- May trigger eviction

### LRU Replacement
Cache table shows current LRU order (top = least recent, bottom = most recent) for Fully Associative mode.

### Write Policies
- **Write-Through**: Every write updates both cache AND memory
- **Write-Back**: Writes update cache only; memory updated on eviction (dirty bit tracking)

## 🔧 Technical Details

- **Frontend**: HTML5, CSS3 (with animations), Vanilla JavaScript
- **Backend**: Python Flask REST API
- **Cache Engine**: Pure Python (no external dependencies for core logic)
- **Animations**: CSS keyframes and transitions
- **Sound**: Web Audio API (browser-generated tones)

## 📱 Responsive Design

The interface automatically adapts to different screen sizes:
- Desktop: Side-by-side panels
- Tablet/Mobile: Stacked panels
- All features remain accessible

## 🎵 Sound Effects

Optional audio feedback helps reinforce learning:
- **High beep (800Hz)**: Cache hit ✅
- **Low beep (200Hz)**: Cache miss ❌
- Toggle on/off anytime with the sound switch

## 🆚 CLI vs Web Interface

Both versions are included!

**Web Interface** (app.py):
- Modern visual design
- Animations and tooltips
- Interactive exploration
- Best for: Learning, demos, visual learners

**CLI Version** (cache_simulator.py):
- Text-based output
- Sample demonstrations
- Batch operations
- Best for: Scripts, automation, text-only environments

Run CLI version:
```bash
python cache_simulator.py
```

## 🎓 For Educators

Perfect for:
- Computer Architecture courses
- Cache memory lectures
- COA lab demonstrations
- Student assignments
- Self-paced learning

Students can:
- Visualize abstract concepts
- Experiment with different configurations
- See immediate feedback
- Understand trade-offs between cache types
- Compare write policies

## 🐛 Troubleshooting

**Browser console errors?**
- Refresh the page
- Ensure JavaScript is enabled

**Animations not smooth?**
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- Close other resource-intensive tabs

**Sound not working?**
- Check browser audio permissions
- Try clicking the page first (some browsers require user interaction)

## 📜 License

Educational use - Free to use and modify for learning purposes.

## 👥 Credits

Created for Computer Organization and Architecture (COA) education and demonstrations.

---

## 🚀 Try It Now!

1. Open the webview or visit `http://localhost:5000`
2. Create a cache with your preferred settings
3. Execute memory operations
4. Watch the visual feedback in action
5. Learn and experiment!

**Happy Cache Simulating!** 🎉
