"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { useRouter } from "nextjs-toploader/app";
import { useOptimisticFilterRouter } from "@/lib/useOptimisticFilterRouter";

type Props = {
  forInput: string;
};
export default function ResetButton({ forInput }: Props) {
  const filterRouter = useOptimisticFilterRouter({
    resetOnNavigate: new Set(["page"]),
  });

  const reset = () => filterRouter.delete("query");

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
