import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the hooks to avoid API calls during testing
jest.mock('./hooks', () => ({
  useAccessibility: () => ({
    announcements: [],
    announcementRef: { current: null },
    speak: jest.fn()
  }),
  useVisionAssistant: () => ({
    isRunning: false,
    loading: false,
    status: 'Vision Assistant Ready',
    handleToggleVision: jest.fn()
  }),
  useNavigation: () => ({
    navigationActive: false,
    setNavigationActive: jest.fn(),
    startLocation: '',
    setStartLocation: jest.fn(),
    destination: '',
    setDestination: jest.fn(),
    savedLocations: [],
    loading: false,
    handleStartNavigation: jest.fn(),
    handleStopNavigation: jest.fn(),
    handleSaveLocation: jest.fn()
  }),
  useKeyboardShortcuts: jest.fn()
}));

test('renders VISTA Vision Assistant', () => {
  render(<App />);
  const linkElement = screen.getByText(/VISTA - Vision Assistant/i);
  expect(linkElement).toBeInTheDocument();
});

test('renders system status section', () => {
  render(<App />);
  const statusElement = screen.getByText(/System Status/i);
  expect(statusElement).toBeInTheDocument();
});

test('renders main controls', () => {
  render(<App />);
  const controlsElement = screen.getByText(/Main Controls/i);
  expect(controlsElement).toBeInTheDocument();
});

test('renders start vision button', () => {
  render(<App />);
  const startButton = screen.getByText(/START VISION/i);
  expect(startButton).toBeInTheDocument();
});

test('renders accessibility features', () => {
  render(<App />);
  const shortcutsElement = screen.getByText(/Ctrl\+V: Toggle Vision/i);
  expect(shortcutsElement).toBeInTheDocument();
});