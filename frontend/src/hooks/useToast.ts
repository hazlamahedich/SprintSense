import { useToast as useToastUI } from '@/components/ui/use-toast';

type ToastVariant = 'default' | 'success' | 'error' | 'warning';

interface ToastOptions {
  title: string;
  description: string;
  variant?: ToastVariant;
  duration?: number;
}

export const useToast = () => {
  const { toast: baseToast } = useToastUI();

  const toast = ({
    title,
    description,
    variant = 'default',
    duration = 5000,
  }: ToastOptions) => {
    baseToast({
      title,
      description,
      variant,
      duration,
    });
  };

  return { toast };
};

export default useToast;
