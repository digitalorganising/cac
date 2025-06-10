"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { useAppQueryState } from "@/lib/app-query-state";

type Props = {
  forInput: string;
};

export default function ResetButton({ forInput }: Props) {
  const [_, setQuery] = useAppQueryState("query");

  const reset = () => {
    setQuery(null);
  };

  return (
    <Button
      type="reset"
      variant="secondary"
      title="Clear"
      className="aspect-square cursor-pointer"
      onClick={reset}
    >
      <Cross2Icon />
    </Button>
  );
}
