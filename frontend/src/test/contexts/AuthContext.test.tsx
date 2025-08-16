import { render, screen, act, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from '../../contexts/AuthContext'

// Mock the API client
vi.mock('../../lib/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

// Test component to access context
const TestComponent = () => {
  const auth = useAuth()
  return (
    <div>
      <div data-testid="is-authenticated">{auth.isAuthenticated.toString()}</div>
      <div data-testid="is-loading">{auth.isLoading.toString()}</div>
      <div data-testid="user">{auth.user ? auth.user.username : 'no-user'}</div>
      <button onClick={() => auth.login('test', 'password', 'tenant')} data-testid="login-btn">
        Login
      </button>
      <button onClick={auth.logout} data-testid="logout-btn">
        Logout
      </button>
    </div>
  )
}

// Wrapper component for testing
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>{children}</AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockReturnValue(undefined)
    localStorageMock.removeItem.mockReturnValue(undefined)
    localStorageMock.clear.mockReturnValue(undefined)
  })

  describe('Initial State', () => {
    it('starts with unauthenticated state', () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
      expect(screen.getByTestId('is-loading')).toHaveTextContent('true')
      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    })

    it('loads user from localStorage on mount', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        tenant_id: 'tenant1',
      }
      const mockToken = 'mock-jwt-token'
      
      localStorageMock.getItem
        .mockReturnValueOnce(mockToken) // access token
        .mockReturnValueOnce(JSON.stringify(mockUser)) // user data

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
        expect(screen.getByTestId('user')).toHaveTextContent('testuser')
      })
    })

    it('handles invalid localStorage data gracefully', async () => {
      localStorageMock.getItem.mockReturnValue('invalid-json')

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })
  })

  describe('Login Functionality', () => {
    it('successfully logs in a user', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        tenant_id: 'tenant1',
      }
      const mockTokens = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user_id: '1',
        tenant_id: 'tenant1',
        permissions: ['read', 'write'],
      }

      // Mock API response
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: mockTokens,
        status: 200,
      })

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'access_token',
          mockTokens.access_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'refresh_token',
          mockTokens.refresh_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'user',
          JSON.stringify(mockUser)
        )
      })
    })

    it('handles login errors gracefully', async () => {
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Login failed'))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })

    it('validates login input', async () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      // Should handle empty credentials gracefully
      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
      })
    })
  })

  describe('Logout Functionality', () => {
    it('successfully logs out a user', async () => {
      // Start with authenticated state
      const mockUser = { username: 'testuser' }
      const mockToken = 'mock-token'
      
      localStorageMock.getItem
        .mockReturnValueOnce(mockToken)
        .mockReturnValueOnce(JSON.stringify(mockUser))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
      })

      const logoutButton = screen.getByTestId('logout-btn')
      
      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
    })

    it('calls logout API endpoint', async () => {
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { message: 'Logged out successfully' },
        status: 200,
      })

      // Start with authenticated state
      localStorageMock.getItem
        .mockReturnValueOnce('mock-token')
        .mockReturnValueOnce(JSON.stringify({ username: 'testuser' }))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
      })

      const logoutButton = screen.getByTestId('logout-btn')
      
      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(apiClient.post).toHaveBeenCalledWith('/auth/logout')
      })
    })
  })

  describe('Token Management', () => {
    it('stores tokens securely', async () => {
      const mockTokens = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user_id: '1',
        tenant_id: 'tenant1',
        permissions: ['read', 'write'],
      }

      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: mockTokens,
        status: 200,
      })

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'access_token',
          mockTokens.access_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'refresh_token',
          mockTokens.refresh_token
        )
      })
    })

    it('retrieves tokens on app initialization', async () => {
      const mockToken = 'mock-jwt-token'
      localStorageMock.getItem.mockReturnValue(mockToken)

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token')
      })
    })
  })

  describe('User State Management', () => {
    it('updates user state after successful login', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        tenant_id: 'tenant1',
      }
      const mockTokens = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user_id: '1',
        tenant_id: 'tenant1',
        permissions: ['read', 'write'],
      }

      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: mockTokens,
        status: 200,
      })

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
        expect(screen.getByTestId('user')).toHaveTextContent('testuser')
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })

    it('clears user state after logout', async () => {
      // Start with authenticated state
      localStorageMock.getItem
        .mockReturnValueOnce('mock-token')
        .mockReturnValueOnce(JSON.stringify({ username: 'testuser' }))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
      })

      const logoutButton = screen.getByTestId('logout-btn')
      
      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
    })
  })

  describe('Error Handling', () => {
    it('handles network errors during login', async () => {
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })

    it('handles API errors during login', async () => {
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockRejectedValueOnce({
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' },
        },
      })

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
      })
    })

    it('handles localStorage errors gracefully', async () => {
      localStorageMock.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded')
      })

      const mockTokens = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
        user_id: '1',
        tenant_id: 'tenant1',
        permissions: ['read', 'write'],
      }

      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: mockTokens,
        status: 200,
      })

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      // Should handle storage errors without crashing
      await waitFor(() => {
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
      })
    })
  })

  describe('Loading States', () => {
    it('shows loading state during authentication', async () => {
      const { apiClient } = await import('../../lib/api')
      let resolveLogin: (value: any) => void
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve
      })
      
      vi.mocked(apiClient.post).mockReturnValueOnce(loginPromise)

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      // Should show loading state
      expect(screen.getByTestId('is-loading')).toHaveTextContent('true')

      // Resolve the promise
      resolveLogin!({
        data: {
          access_token: 'mock-token',
          refresh_token: 'mock-refresh',
          user_id: '1',
          tenant_id: 'tenant1',
          permissions: ['read'],
        },
        status: 200,
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })

    it('resets loading state on error', async () => {
      const { apiClient } = await import('../../lib/api')
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Login failed'))

      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      const loginButton = screen.getByTestId('login-btn')
      
      await act(async () => {
        loginButton.click()
      })

      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
      })
    })
  })

  describe('Context Provider', () => {
    it('provides auth context to children', () => {
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      expect(screen.getByTestId('is-authenticated')).toBeInTheDocument()
      expect(screen.getByTestId('is-loading')).toBeInTheDocument()
      expect(screen.getByTestId('user')).toBeInTheDocument()
      expect(screen.getByTestId('login-btn')).toBeInTheDocument()
      expect(screen.getByTestId('logout-btn')).toBeInTheDocument()
    })

    it('throws error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        render(<TestComponent />)
      }).toThrow()

      consoleSpy.mockRestore()
    })
  })
})
