"use client";

import dynamic from "next/dynamic";
import { Outcome } from "@/lib/types";

const JsonViewDynamic = dynamic(() => import("./JsonView"), {
  ssr: false,
});

export default function DebugView({ outcome }: { outcome: Outcome }) {
  return (
    <div className="p-3">
      <JsonViewDynamic outcome={outcome} />
    </div>
  );
}
