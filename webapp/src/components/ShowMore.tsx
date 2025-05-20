"use client";

import { cn } from "@/lib/utils";
import useResizeObserver, {
  UseResizeObserverCallback,
} from "@react-hook/resize-observer";
import { useLayoutEffect, useRef, useState } from "react";

class ServerSideResizeObserverPolyfill {
  constructor(callback: ResizeObserverCallback) {}
  observe(target: Element, options?: ResizeObserverOptions) {}
  unobserve(target: Element) {}
}

type Props = {
  lineClampClassName: string;
} & React.HTMLAttributes<HTMLParagraphElement>;

export default function ShowMore({
  lineClampClassName,
  className,
  children,
  ...props
}: Props) {
  const ref = useRef<HTMLParagraphElement>(null);
  const [truncated, setTruncated] = useState<boolean>(false);
  const [expanded, setExpanded] = useState<boolean>(false);

  useLayoutEffect(() => {
    if (ref.current && !expanded) {
      if (ref.current.scrollHeight > ref.current.clientHeight) {
        setTruncated(true);
      } else {
        setTruncated(false);
      }
    }
  }, [ref, expanded]);

  useResizeObserver(
    ref,
    (e) => {
      if (e.target.scrollHeight > e.target.clientHeight) {
        setTruncated(true);
      } else {
        setTruncated(false);
      }
    },
    {
      polyfill:
        typeof window === "undefined" ? ServerSideResizeObserverPolyfill : null,
    },
  );

  return (
    <>
      <p
        ref={ref}
        className={cn(
          "max-w-sm text-sm text-muted-foreground first-letter:capitalize",
          expanded ? undefined : lineClampClassName,
          className,
        )}
        {...props}
      >
        {children}
      </p>
      {truncated || expanded ? (
        <a
          onClick={() => setExpanded((e) => !e)}
          className="text-sm text-slate-700 font-medium hover:underline underline-offset-4 hover:font-semibold"
        >
          {expanded ? "Show less" : "Show more"}
        </a>
      ) : null}
    </>
  );
}
