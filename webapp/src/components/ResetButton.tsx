"use client";

import { XIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { usePathname, useSearchParams, useRouter } from "next/navigation";

type Props = {
  forInput: string;
};
export default function ResetButton({ forInput }: Props) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();

  const reset = () => {
    const p = new URLSearchParams(searchParams);
    p.delete(forInput);
    p.delete("page");
    return router.push(`${pathname}?${p.toString()}`);
  };

  return (
    <Button
      type="reset"
      variant="secondary"
      title="Clear"
      className="aspect-square cursor-pointer"
      onClick={reset}
    >
      <XIcon />
    </Button>
  );
}
