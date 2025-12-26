# VISTA Frontend - Modular Architecture

## 🏗️ Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── AccessibilityAnnouncer.js  # Screen reader announcements
│   ├── Header.js                  # App header with title and shortcuts
│   ├── StatusSection.js           # System status display
│   ├── VisionControls.js          # Vision assistant controls
│   ├── NavigationSection.js       # Navigation interface
│   ├── InfoSection.js             # Information and safety sections
│   └── index.js                   # Component exports
├── hooks/                # Custom React hooks
│   ├── useAccessibility.js        # Accessibility and TTS functionality
│   ├── useVisionAssistant.js      # Vision assistant state management
│   ├── useNavigation.js           # Navigation state and API calls
│   ├── useKeyboardShortcuts.js    # Keyboard shortcut handling
│   └── index.js                   # Hook exports
├── App.js               # Main application component
├── App.css              # Accessible styling
└── index.js             # React entry point
```

## 🎯 Component Architecture

### **Main App Component**
- Orchestrates all hooks and components
- Manages global state coordination
- Handles cross-feature interactions

### **Custom Hooks**

#### `useAccessibility()`
- Manages screen reader announcements
- Provides text-to-speech functionality
- Handles focus management for accessibility

#### `useVisionAssistant(speak)`
- Controls vision assistant start/stop
- Manages system status
- Handles API communication for vision features

#### `useNavigation(speak)`
- Manages navigation state (locations, routes)
- Handles navigation API calls
- Controls location saving functionality

#### `useKeyboardShortcuts(...handlers)`
- Implements keyboard accessibility
- Manages global keyboard shortcuts
- Provides keyboard navigation support

### **UI Components**

#### `AccessibilityAnnouncer`
- Hidden component for screen reader announcements
- Manages aria-live regions
- Handles focus management

#### `Header`
- App title and branding
- Keyboard shortcut information
- Accessibility instructions

#### `StatusSection`
- System status display
- Visual and audio status indicators
- Real-time status updates

#### `VisionControls`
- Start/stop vision assistant
- Loading states and feedback
- Primary action controls

#### `NavigationSection`
- Location selection interface
- Navigation controls
- Route management

#### `InfoSection`
- Feature explanations
- Safety information
- Usage instructions

## 🔧 Key Features

### **Accessibility First**
- Full keyboard navigation support
- Screen reader compatibility
- High contrast design
- Audio feedback for all actions

### **Modular Design**
- Separation of concerns
- Reusable components
- Custom hooks for logic
- Easy testing and maintenance

### **Safety Priority**
- Obstacle detection integration
- Clear safety warnings
- Audio priority management
- Emergency stop functionality

## 🚀 Usage

### **Development**
```bash
cd frontend
npm install
npm start
```

### **Keyboard Shortcuts**
- `Ctrl+V`: Toggle Vision Assistant
- `Ctrl+N`: Navigation Controls
- `Ctrl+S`: Save Current Location

### **Screen Reader Support**
- All components have proper ARIA labels
- Live regions for dynamic content
- Semantic HTML structure
- Focus management

## 🎨 Styling

The CSS follows accessibility guidelines:
- High contrast colors (black/white/bright accents)
- Large, clear fonts
- Keyboard focus indicators
- Responsive design
- Motion sensitivity support

## 🔌 API Integration

The frontend communicates with the backend through:
- `/api/start` - Start vision assistant
- `/api/stop` - Stop vision assistant
- `/api/navigation/start` - Begin navigation
- `/api/navigation/stop` - Stop navigation
- `/api/locations` - Manage saved locations

## 🧪 Testing

Each component and hook can be tested independently:
- Components receive props and render UI
- Hooks manage state and side effects
- Clear separation makes mocking easy
- Accessibility testing supported

## 📱 Responsive Design

The interface adapts to different screen sizes while maintaining accessibility:
- Mobile-friendly touch targets
- Scalable text and controls
- Flexible layouts
- Consistent experience across devices