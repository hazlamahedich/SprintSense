import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Button } from '../ui/button'

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    const { rerender } = render(<Button variant="default">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('bg-blue-600');

    rerender(<Button variant="outline">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('border-gray-300');

    rerender(<Button variant="destructive">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('bg-red-600');
  });

  it('applies size styles correctly', () => {
    const { rerender } = render(<Button size="sm">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('h-8');

    rerender(<Button size="md">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('h-10');

    rerender(<Button size="lg">Button</Button>);
    expect(screen.getByText('Button')).toHaveClass('h-12');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Button</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('handles disabled state', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByText('Disabled')).toBeDisabled();
  });
});
