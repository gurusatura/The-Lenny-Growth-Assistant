# UI/UX Design System Document: The Lenny Growth Assistant

## 1. Design Vision & Philosophy
The user interface of **The Lenny Growth Assistant** is built around an **impeccable split-screen workspace** inspired by modern AI tools such as Claude and ChatGPT. It bridges conversational AI and workspace document creation without interrupting user flow or forcing redirects to external browser tabs.

---

## 2. Design System Tokens & Aesthetics

### Color Palette (Slate Dark Mode)
- **Background Main**: `#0f172a` (Slate 900) - Dark background to minimize visual fatigue.
- **Sidebar & Elevated Surfaces**: `#1e293b` (Slate 800) - Subtle contrast establishing visual hierarchy.
- **User Accent**: `#4f46e5` (Indigo 600) - High-energy focus color for user chat bubbles.
- **Assistant Accent**: `#334155` (Slate 700) - Readable container for assistant responses.
- **Artifact Viewer Background**: `#090d16` (Deep Charcoal) - Editor aesthetic for live UI and document preview.
- **Status Badges**: `#10b981` (Emerald Green) - Live connection status indicator.

### Typography
- **Primary Font**: `Inter` (Google Fonts) - Clean, sans-serif typography optimized for high readability.
- **Monospace Code Font**: System Monospace for raw code view.

---

## 3. Split-Screen Layout Architecture

```text
┌───────────────────────────┬─────────────────────────────────┬─────────────────────────────────────┐
│ Left Sidebar (280px)      │ Main Chat Workspace (Flex)      │ Right Artifact Panel (550px)        │
│                           │                                 │                                     │
│  [+ New Chat]             │  Header: Active Session Title   │  Header: Title & Tab Switcher       │
│                           │                                 │  [ Preview | Code ] [X]             │
│  Session 1          [🗑]  │  User Bubble                    │ ┌─────────────────────────────────┐ │
│  Session 2          [🗑]  │  Assistant Bubble               │ │ Live HTML iFrame / Rendered MD  │ │
│                           │  [Open Artifact Badge]          │ │ Component UI or Document        │ │
│                           │                                 │ └─────────────────────────────────┘ │
│                           │  [ Input Textarea ] [Send]      │                                     │
└───────────────────────────┴─────────────────────────────────┴─────────────────────────────────────┘
```

---

## 4. Claude-Style Artifact Rendering Mechanics

1. **Inline Badge**: When an artifact is generated, an `Open Artifact: [Title]` badge appears inside the assistant chat bubble.
2. **Auto-Slide Panel**: The 550px right panel automatically opens on generation.
3. **Dual View Mode**:
   - **Preview Tab**:
     - *HTML/CSS Artifacts*: Rendered inside a live sandboxed `<iframe>` so users can interact with real UI components.
     - *Markdown Artifacts*: Rendered as formatted HTML using `marked.js`.
   - **Code Tab**: Displays raw monospaced source code for easy copying.
