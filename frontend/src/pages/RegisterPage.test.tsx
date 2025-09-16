import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import { RegisterPage } from './RegisterPage'
import { userApi } from '../services/api'

// Mock the API
vi.mock('../services/api', () => ({
  userApi: {
    register: vi.fn(),
  },
}));

// Mock the Zustand store
const mockSetUser = vi.fn();
const mockSetAccessToken = vi.fn();
const mockSetError = vi.fn();

vi.mock('../store/appStore', () => ({
  useAppStore: () => ({
    setUser: mockSetUser,
    setAccessToken: mockSetAccessToken,
    setError: mockSetError,
  }),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

describe('RegisterPage', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    vi.clearAllMocks();
    user = userEvent.setup();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );
  };

  it('renders the registration form correctly', () => {
    renderComponent();
    expect(screen.getByRole('heading', { name: /create account/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText('Password', { exact: true })).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password', { exact: true })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('shows validation errors when fields are touched then cleared', async () => {
    renderComponent();
    const fullNameField = screen.getByLabelText(/full name/i);
    const emailField = screen.getByLabelText(/email address/i);
    const passwordField = screen.getByLabelText('Password', { exact: true });
    const confirmPasswordField = screen.getByLabelText('Confirm Password', { exact: true });

    // Type something then clear each field to trigger validation
    await user.type(fullNameField, 'Test');
    await user.clear(fullNameField);
    
    await user.type(emailField, 'test');
    await user.clear(emailField);
    
    await user.type(passwordField, 'test');
    await user.clear(passwordField);
    
    await user.type(confirmPasswordField, 'test');
    await user.clear(confirmPasswordField);

    await waitFor(async () => {
        expect(fullNameField).toHaveAttribute('aria-invalid', 'true');
        expect(emailField).toHaveAttribute('aria-invalid', 'true');
        expect(passwordField).toHaveAttribute('aria-invalid', 'true');
        expect(confirmPasswordField).toHaveAttribute('aria-invalid', 'true');
    });
  });

  it('shows validation error for mismatched passwords', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true });
    const confirmPasswordField = screen.getByLabelText('Confirm Password', { exact: true });
    
    // Fill valid data first, then change confirm password to trigger mismatch
    await user.type(screen.getByLabelText(/full name/i), 'Test User');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(passwordField, 'Password123');
    await user.type(confirmPasswordField, 'Password123');
    
    // Now change confirm password to create mismatch
    await user.clear(confirmPasswordField);
    await user.type(confirmPasswordField, 'Password456');
    
    // Tab away to trigger validation
    await user.tab();

    await waitFor(async () => {
        expect(await screen.findByLabelText('Confirm Password', { exact: true })).toHaveAttribute('aria-invalid', 'true');
    });
  });

  it('submits the form successfully with valid data', async () => {
    const mockResponse = {
      message: 'User registered successfully',
      user: { id: '1', email: 'test@example.com', full_name: 'Test User', is_active: true, created_at: new Date().toISOString() },
      access_token: 'fake-token',
      token_type: 'bearer',
    };
    vi.mocked(userApi.register).mockResolvedValue(mockResponse);

    renderComponent();

    await user.type(screen.getByLabelText(/full name/i), 'Test User');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText('Password', { exact: true }), 'Password123');
    await user.type(screen.getByLabelText('Confirm Password', { exact: true }), 'Password123');

    await user.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(userApi.register).toHaveBeenCalledWith({
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'Password123',
      });
      expect(mockSetUser).toHaveBeenCalledWith(mockResponse.user);
      expect(mockSetAccessToken).toHaveBeenCalledWith(mockResponse.access_token);
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });
  });

  it('handles 409 conflict error (email already exists)', async () => {
    const error = { response: { status: 409 } };
    vi.mocked(userApi.register).mockRejectedValue(error);

    renderComponent();

    await user.type(screen.getByLabelText(/full name/i), 'Test User');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText('Password', { exact: true }), 'Password123');
    await user.type(screen.getByLabelText('Confirm Password', { exact: true }), 'Password123');

    await user.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(async () => {
        expect(await screen.findByLabelText(/email address/i)).toHaveAttribute('aria-invalid', 'true');
    });
  });

  it('handles generic API error on submission', async () => {
    const error = { response: { data: { detail: 'A generic error occurred' } } };
    vi.mocked(userApi.register).mockRejectedValue(error);

    renderComponent();

    await user.type(screen.getByLabelText(/full name/i), 'Test User');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText('Password', { exact: true }), 'Password123');
    await user.type(screen.getByLabelText('Confirm Password', { exact: true }), 'Password123');

    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });

  it('shows validation error for invalid email format', async () => {
    renderComponent();
    const emailField = screen.getByLabelText(/email address/i);
    
    await user.type(emailField, 'invalid-email');
    await user.tab(); // Trigger blur validation
    
    await waitFor(() => {
      expect(emailField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for weak password', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true });
    
    await user.type(passwordField, 'weak');
    await user.tab(); // Trigger blur validation
    
    await waitFor(() => {
      expect(passwordField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for password without uppercase letter', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true });
    
    await user.type(passwordField, 'password123');
    await user.tab();
    
    await waitFor(() => {
      expect(passwordField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/password must contain at least one uppercase letter/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for password without lowercase letter', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true });
    
    await user.type(passwordField, 'PASSWORD123');
    await user.tab();
    
    await waitFor(() => {
      expect(passwordField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/password must contain at least one lowercase letter/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for password without number', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true });
    
    await user.type(passwordField, 'Password');
    await user.tab();
    
    await waitFor(() => {
      expect(passwordField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/password must contain at least one number/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for invalid full name with numbers', async () => {
    renderComponent();
    const fullNameField = screen.getByLabelText(/full name/i);
    
    await user.type(fullNameField, 'John123');
    await user.tab();
    
    await waitFor(() => {
      expect(fullNameField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/full name can only contain letters/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for too short full name', async () => {
    renderComponent();
    const fullNameField = screen.getByLabelText(/full name/i);
    
    await user.type(fullNameField, 'A');
    await user.tab();
    
    await waitFor(() => {
      expect(fullNameField).toHaveAttribute('aria-invalid', 'true');
      expect(screen.getByText(/full name must be at least 2 characters/i)).toBeInTheDocument();
    });
  });

  it('enables submit button when all fields are valid', async () => {
    renderComponent();
    const submitButton = screen.getByRole('button', { name: /create account/i });
    
    // Initially disabled
    expect(submitButton).toBeDisabled();
    
    // Fill all fields with valid data
    await user.type(screen.getByLabelText(/full name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email address/i), 'john@example.com');
    await user.type(screen.getByLabelText('Password', { exact: true }), 'Password123');
    await user.type(screen.getByLabelText('Confirm Password', { exact: true }), 'Password123');
    
    await waitFor(() => {
      expect(submitButton).toBeEnabled();
    });
  });

  it('toggles password visibility', async () => {
    renderComponent();
    const passwordField = screen.getByLabelText('Password', { exact: true }) as HTMLInputElement;
    const toggleButton = screen.getByLabelText('toggle password visibility');
    
    expect(passwordField.type).toBe('password');
    
    await user.click(toggleButton);
    expect(passwordField.type).toBe('text');
    
    await user.click(toggleButton);
    expect(passwordField.type).toBe('password');
  });

  it('toggles confirm password visibility', async () => {
    renderComponent();
    const confirmPasswordField = screen.getByLabelText('Confirm Password', { exact: true }) as HTMLInputElement;
    const toggleButton = screen.getByLabelText('toggle confirm password visibility');
    
    expect(confirmPasswordField.type).toBe('password');
    
    await user.click(toggleButton);
    expect(confirmPasswordField.type).toBe('text');
    
    await user.click(toggleButton);
    expect(confirmPasswordField.type).toBe('password');
  });
});
