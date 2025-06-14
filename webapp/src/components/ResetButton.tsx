"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { ButtonHTMLAttributes } from "react";
import { Button } from "@/components/ui/button";
import { useAppQueryState } from "@/lib/app-query-state";
import { cn } from "@/lib/utils";

type Props = {
  forInput: string;
} & ButtonHTMLAttributes<HTMLButtonElement>;

export default function ResetButton({ forInput, className, ...props }: Props) {
  const [_, setQuery] = useAppQueryState("query");

  const reset = () => {
    setQuery(null);
  };

  return (
    <Button
      type="reset"
      variant="secondary"
      title="Clear"
      className={cn("aspect-square cursor-pointer", className)}
      onClick={reset}
      {...props}
    >
      <Cross2Icon />
    </Button>
  );
}
