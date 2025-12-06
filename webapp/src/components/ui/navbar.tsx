import Link from "next/link";
import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "./button";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";

// Hamburger icon component
const HamburgerIcon = ({
  className,
  ...props
}: React.SVGAttributes<SVGElement>) => (
  <svg
    className={cn("pointer-events-none", className)}
    width={16}
    height={16}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path
      d="M4 12L24 12"
      className="origin-center -translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-x-0 group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[315deg]"
    />
    <path
      d="M0 12H24"
      className="origin-center translate-x-[4px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.8)] group-aria-expanded:rotate-45 group-aria-expanded:translate-x-0"
    />
    <path
      d="M4 12H24"
      className="origin-center translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[135deg]"
    />
  </svg>
);

type NavbarLink = {
  href: string;
  label: React.ReactNode;
};

export interface NavbarProps extends React.HTMLAttributes<HTMLElement> {
  navigationLinks: NavbarLink[];
}

function Navbar({ className, navigationLinks }: NavbarProps) {
  return (
    <nav className="p-0.5 xs:p-1 sm:p-3">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            className="sm:hidden group h-9 w-9 hover:bg-accent hover:text-accent-foreground"
            variant="ghost"
            size="icon"
          >
            <HamburgerIcon />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="start" className="w-fit p-2 flex flex-col gap-2">
          {navigationLinks.map((link) => (
            <Button
              asChild
              key={link.href}
              variant="ghost"
              className="justify-start"
            >
              <Link href={link.href}>{link.label}</Link>
            </Button>
          ))}
        </PopoverContent>
      </Popover>
      <div className="hidden sm:block">
        {navigationLinks.map((link) => (
          <Button asChild key={link.href} variant="ghost">
            <Link href={link.href}>{link.label}</Link>
          </Button>
        ))}
      </div>
    </nav>
  );
}

export default Navbar;
