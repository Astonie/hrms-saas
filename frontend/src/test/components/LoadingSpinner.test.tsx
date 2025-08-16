import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner from '../../components/ui/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('animate-spin')
    expect(spinner).toHaveClass('w-6')
    expect(spinner).toHaveClass('h-6')
  })

  it('renders with custom size', () => {
    render(<LoadingSpinner size="lg" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('w-8')
    expect(spinner).toHaveClass('h-8')
  })

  it('renders with custom color', () => {
    render(<LoadingSpinner color="secondary" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-secondary-600')
  })

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Loading data..." />)
    
    const text = screen.getByText('Loading data...')
    expect(text).toBeInTheDocument()
    expect(text).toHaveClass('text-sm')
    expect(text).toHaveClass('text-gray-600')
  })

  it('renders without text when not provided', () => {
    render(<LoadingSpinner />)
    
    const text = screen.queryByText('Loading...')
    expect(text).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<LoadingSpinner className="custom-class" />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('custom-class')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />)
    
    let spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('w-4')
    expect(spinner).toHaveClass('h-4')
    
    rerender(<LoadingSpinner size="md" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('w-6')
    expect(spinner).toHaveClass('h-6')
    
    rerender(<LoadingSpinner size="lg" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('w-8')
    expect(spinner).toHaveClass('h-8')
    
    rerender(<LoadingSpinner size="xl" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('w-12')
    expect(spinner).toHaveClass('h-12')
  })

  it('renders with different colors', () => {
    const { rerender } = render(<LoadingSpinner color="primary" />)
    
    let spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-primary-600')
    
    rerender(<LoadingSpinner color="secondary" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-secondary-600')
    
    rerender(<LoadingSpinner color="success" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-success-600')
    
    rerender(<LoadingSpinner color="warning" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-warning-600')
    
    rerender(<LoadingSpinner color="error" />)
    spinner = screen.getByRole('status')
    expect(spinner).toHaveClass('text-error-600')
  })

  it('has correct accessibility attributes', () => {
    render(<LoadingSpinner text="Loading data..." />)
    
    const spinner = screen.getByRole('status')
    expect(spinner).toHaveAttribute('aria-label', 'Loading')
    
    const text = screen.getByText('Loading data...')
    expect(text).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders with full screen overlay', () => {
    render(<LoadingSpinner fullScreen />)
    
    const overlay = screen.getByTestId('loading-overlay')
    expect(overlay).toBeInTheDocument()
    expect(overlay).toHaveClass('fixed')
    expect(overlay).toHaveClass('inset-0')
    expect(overlay).toHaveClass('bg-white')
    expect(overlay).toHaveClass('bg-opacity-75')
    expect(overlay).toHaveClass('flex')
    expect(overlay).toHaveClass('items-center')
    expect(overlay).toHaveClass('justify-center')
    expect(overlay).toHaveClass('z-50')
  })

  it('renders without full screen overlay by default', () => {
    render(<LoadingSpinner />)
    
    const overlay = screen.queryByTestId('loading-overlay')
    expect(overlay).not.toBeInTheDocument()
  })

  it('renders with custom overlay background', () => {
    render(<LoadingSpinner fullScreen overlayClassName="custom-overlay" />)
    
    const overlay = screen.getByTestId('loading-overlay')
    expect(overlay).toHaveClass('custom-overlay')
  })

  it('renders with custom spinner container', () => {
    render(<LoadingSpinner containerClassName="custom-container" />)
    
    const container = screen.getByTestId('loading-container')
    expect(container).toHaveClass('custom-container')
  })

  it('renders with custom text styling', () => {
    render(<LoadingSpinner text="Loading..." textClassName="custom-text" />)
    
    const text = screen.getByText('Loading...')
    expect(text).toHaveClass('custom-text')
  })
})
