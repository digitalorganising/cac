"use client";

import { Cross2Icon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";
import { useRouter } from "nextjs-toploader/app";
import { useFilterHref } from "@/lib/useFilterHref";

type Props = {
  forInput: string;
};
export default function ResetButton({ forInput }: Props) {
  const filterHref = useFilterHref({ resetOnNavigate: new Set(["page"]) });
  const router = useRouter();

  const reset = () => {
    return router.push(filterHref.delete("query").urlString);
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
