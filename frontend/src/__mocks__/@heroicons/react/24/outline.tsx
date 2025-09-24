import React from 'react';

// Create a mock component that renders a basic SVG
const MockIcon = (props: any) => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    {...props}
  >
    <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" />
  </svg>
);

// Export all icons from @heroicons/react/24/outline as mock components
export const ArrowPathIcon = MockIcon;
export const ArrowRightIcon = MockIcon;
export const ArrowLeftIcon = MockIcon;
export const CheckIcon = MockIcon;
export const ChevronDownIcon = MockIcon;
export const ChevronUpIcon = MockIcon;
export const PlusIcon = MockIcon;
export const RefreshIcon = MockIcon;
export const XMarkIcon = MockIcon;
export const TrashIcon = MockIcon;
export const PencilIcon = MockIcon;
export const EyeIcon = MockIcon;
export const StarIcon = MockIcon;
export const ClockIcon = MockIcon;
export const CalendarIcon = MockIcon;
export const UserIcon = MockIcon;
export const UsersIcon = MockIcon;
export const TagIcon = MockIcon;
export const FlagIcon = MockIcon;
export const ExclamationTriangleIcon = MockIcon;
export const CheckCircleIcon = MockIcon;
export const DocumentIcon = MockIcon;
