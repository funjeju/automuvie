import { cn } from "@/lib/cn";

interface ChipProps {
  active?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Chip({ active, onClick, children }: ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn("chip cursor-pointer select-none", active && "chip-active")}
    >
      {children}
    </button>
  );
}
