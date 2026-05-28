import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

const styles = cva(
  "inline-flex items-center justify-center gap-2 rounded-chip text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary: "px-5 py-2.5 text-white bg-brand-gradient shadow-glow hover:opacity-95",
        secondary: "px-5 py-2.5 text-white border border-border hover:bg-white/5",
        ghost: "px-3 py-2 text-muted hover:text-white hover:bg-white/5",
        danger: "px-5 py-2.5 text-white bg-error/90 hover:bg-error",
      },
      size: { sm: "text-xs px-3 py-1.5", md: "", lg: "text-base px-6 py-3" },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
);

type Props = ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof styles>;

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { className, variant, size, ...rest },
  ref
) {
  return <button ref={ref} className={cn(styles({ variant, size }), className)} {...rest} />;
});
