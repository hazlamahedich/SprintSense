import { SVGProps } from 'react'

const mockIconComponent = (props: SVGProps<SVGSVGElement>) => {
  return <svg {...props} />
}

export const ExclamationTriangleIcon = mockIconComponent
export const ArrowPathIcon = mockIconComponent
export const TrashIcon = mockIconComponent
export const MinusIcon = mockIconComponent
export const ArrowUpIcon = mockIconComponent
// Add other icons as needed
