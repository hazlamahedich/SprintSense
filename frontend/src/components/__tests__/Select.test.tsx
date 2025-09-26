import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Select } from '../ui/select-core';

const defaultOptions = [
  { value: 'option1', label: 'Option 1' },
  { value: 'option2', label: 'Option 2' },
  { value: 'option3', label: 'Option 3' },
];

describe('Select', () => {
  it('renders options correctly', () => {
    render(<Select options={defaultOptions} />);

    defaultOptions.forEach(option => {
      expect(screen.getByText(option.label)).toBeInTheDocument();
    });
  });

  it('handles value changes', () => {
    const handleChange = vi.fn();
    render(<Select options={defaultOptions} onChange={handleChange} />);

    fireEvent.change(screen.getByRole('combobox'), {
      target: { value: 'option2' }
    });
    expect(handleChange).toHaveBeenCalled();
  });

  it('displays error message', () => {
    render(<Select options={defaultOptions} error="Please select an option" />);
    expect(screen.getByText('Please select an option')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toHaveClass('border-red-500');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLSelectElement>();
    render(<Select ref={ref} options={defaultOptions} />);
    expect(ref.current).toBeInstanceOf(HTMLSelectElement);
  });

  it('handles disabled state', () => {
    render(<Select options={defaultOptions} disabled />);
    expect(screen.getByRole('combobox')).toBeDisabled();
  });

  it('applies custom className', () => {
    render(<Select options={defaultOptions} className="custom-class" />);
    expect(screen.getByRole('combobox')).toHaveClass('custom-class');
  });

  it('handles focus and blur events', () => {
    const handleFocus = vi.fn();
    const handleBlur = vi.fn();

    render(
      <Select
        options={defaultOptions}
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.focus(select);
    expect(handleFocus).toHaveBeenCalledTimes(1);

    fireEvent.blur(select);
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('renders with a default selected value', () => {
    render(
      <Select
        options={defaultOptions}
        value="option2"
      />
    );

    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('option2');
  });
});
