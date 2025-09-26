import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { ToggleGroup, ToggleGroupItem } from '../ui/toggle-group-core';

describe('ToggleGroup', () => {
  it('renders toggle group items correctly', () => {
    render(
      <ToggleGroup value="option1" onChange={() => {}}>
        <ToggleGroupItem value="option1">Option 1</ToggleGroupItem>
        <ToggleGroupItem value="option2">Option 2</ToggleGroupItem>
        <ToggleGroupItem value="option3">Option 3</ToggleGroupItem>
      </ToggleGroup>
    );

    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
    expect(screen.getByText('Option 3')).toBeInTheDocument();
  });

  it('handles value changes', () => {
    const handleChange = vi.fn();
    render(
      <ToggleGroup value="option1" onChange={handleChange}>
        <ToggleGroupItem value="option1">Option 1</ToggleGroupItem>
        <ToggleGroupItem value="option2">Option 2</ToggleGroupItem>
      </ToggleGroup>
    );

    fireEvent.click(screen.getByText('Option 2'));
    expect(handleChange).toHaveBeenCalledWith('option2');
  });

  it('applies selected state correctly', () => {
    render(
      <ToggleGroup value="option1" onChange={() => {}}>
        <ToggleGroupItem value="option1">Option 1</ToggleGroupItem>
        <ToggleGroupItem value="option2">Option 2</ToggleGroupItem>
      </ToggleGroup>
    );

    const items = screen.getAllByRole('radio');
    expect(items[0]).toHaveClass('bg-white');
    expect(items[1]).not.toHaveClass('bg-white');
  });

  it('applies custom className to group and items', () => {
    render(
      <ToggleGroup value="option1" onChange={() => {}} className="group-class">
        <ToggleGroupItem value="option1" className="item-class">
          Option 1
        </ToggleGroupItem>
      </ToggleGroup>
    );

    expect(screen.getByRole('group')).toHaveClass('group-class');
    expect(screen.getByRole('radio')).toHaveClass('item-class');
  });

  it('handles keyboard navigation', () => {
    const handleChange = vi.fn();
    render(
      <ToggleGroup value="option1" onChange={handleChange}>
        <ToggleGroupItem value="option1">Option 1</ToggleGroupItem>
        <ToggleGroupItem value="option2">Option 2</ToggleGroupItem>
      </ToggleGroup>
    );

    const option2 = screen.getByText('Option 2');
    option2.focus();
    fireEvent.keyDown(option2, { key: 'Enter' });

    expect(handleChange).toHaveBeenCalledWith('option2');
  });

  it('throws error when ToggleGroupItem is used outside ToggleGroup', () => {
    const originalError = console.error;
    console.error = vi.fn();

    expect(() => {
      render(<ToggleGroupItem value="option1">Option 1</ToggleGroupItem>);
    }).toThrow('ToggleGroupItem must be used within a ToggleGroup');

    console.error = originalError;
  });
});
