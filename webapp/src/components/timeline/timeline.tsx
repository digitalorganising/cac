"use client";

import dayjs from "dayjs";
import * as React from "react";
import { HTMLProps } from "react";
import { cn } from "@/lib/utils";
import ShowMore from "../ShowMore";
import type { TimelineColor } from "./types";

/**
 * Timeline component props interface
 * @interface TimelineProps
 * @extends {React.HTMLAttributes<HTMLOListElement>}
 */
interface TimelineProps extends React.HTMLAttributes<HTMLOListElement> {
  /** Size of the timeline icons */
  iconsize?: "sm" | "md" | "lg";
}

/**
 * Timeline component for displaying a vertical list of events or items
 * @component
 */
const Timeline = React.forwardRef<HTMLOListElement, TimelineProps>(
  ({ className, iconsize, children, ...props }, ref) => {
    const items = React.Children.toArray(children);

    return (
      <ol
        ref={ref}
        aria-label="Timeline"
        className={cn("relative pt-3", className)}
        {...props}
      >
        {React.Children.map(children, (child, index) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, {
              showConnector: index !== items.length - 1,
            } as React.ComponentProps<typeof TimelineItem>);
          }
          return child;
        })}
      </ol>
    );
  },
);
Timeline.displayName = "Timeline";

/**
 * TimelineItem component props interface
 * @interface TimelineItemProps
 * @extends {Omit<HTMLProps<"li">, "ref">}
 */
export interface TimelineItemProps
  extends Omit<HTMLProps<HTMLLIElement>, "ref" | "title"> {
  timelineId: string;
  /** Date string for the timeline item */
  date?: string;
  /** Title of the timeline item */
  title?: React.ReactNode;
  /** Description text */
  description?: string;
  /** Custom icon element */
  icon?: React.ReactNode;
  /** Color theme for the icon */
  iconColor?: TimelineColor | string;
  /** Current status of the item */
  status?: "completed" | "in-progress" | "pending";
  /** Color theme for the connector line */
  connectorColor?: TimelineColor;
  /** Whether to show the connector line */
  showConnector?: boolean;
  /** Size of the icon */
  iconsize?: "sm" | "md" | "lg";
}

const TimelineItem = React.forwardRef<HTMLLIElement, TimelineItemProps>(
  (
    {
      className,
      date,
      title,
      timelineId,
      description,
      icon,
      iconColor,
      status = "completed",
      connectorColor,
      showConnector = true,
      iconsize,
      ...props
    },
    ref,
  ) => {
    const commonClassName = cn("relative", className);
    const content = (
      <div
        className="flex space-x-4"
        {...(status === "in-progress" ? { "aria-current": "step" } : {})}
      >
        {/* Timeline dot and connector */}
        <div className="flex flex-col items-center pt-1">
          <div className="relative z-10">
            <TimelineIcon
              icon={icon}
              color={iconColor}
              status={status}
              iconSize={iconsize}
            />
          </div>
          {showConnector && (
            <div className="h-full min-h-6 w-0.5 bg-border mt-2" />
          )}
        </div>

        {/* Content */}
        <TimelineContent>
          <TimelineHeader>
            <TimelineTime format="DD/MM/YYYY" date={date} />
            <TimelineTitle className="my-1">{title}</TimelineTitle>
          </TimelineHeader>
          <TimelineDescription>{description}</TimelineDescription>
        </TimelineContent>
      </div>
    );

    return (
      <li ref={ref} className={commonClassName} {...props}>
        {content}
      </li>
    );
  },
);
TimelineItem.displayName = "TimelineItem";

interface TimelineTimeProps extends React.HTMLAttributes<HTMLTimeElement> {
  /** Date string, Date object, or timestamp */
  date?: string | Date | number;
  /** Optional format for displaying the date */
  format?: string;
}

const TimelineTime = React.forwardRef<HTMLTimeElement, TimelineTimeProps>(
  ({ className, date, format, children, ...props }, ref) => {
    const formattedDate = React.useMemo(() => {
      if (!date) return "";
      return dayjs(date).format(format);
    }, [date, format]);

    return (
      <time
        ref={ref}
        dateTime={date ? new Date(date).toISOString() : undefined}
        className={cn(
          "text-sm font-medium tracking-tight text-muted-foreground",
          className,
        )}
        {...props}
      >
        {children || formattedDate}
      </time>
    );
  },
);
TimelineTime.displayName = "TimelineTime";

const TimelineConnector = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    status?: "completed" | "in-progress" | "pending";
    color?: "primary" | "secondary" | "muted" | "accent";
  }
>(({ className, status = "completed", color, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "w-0.5",
      {
        "bg-primary": color === "primary" || (!color && status === "completed"),
        "bg-muted": color === "muted" || (!color && status === "pending"),
        "bg-secondary": color === "secondary",
        "bg-accent": color === "accent",
        "bg-gradient-to-b from-primary to-muted":
          !color && status === "in-progress",
      },
      className,
    )}
    {...props}
  />
));
TimelineConnector.displayName = "TimelineConnector";

const TimelineHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex flex-col", className)} {...props} />
));
TimelineHeader.displayName = "TimelineHeader";

const TimelineTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & {
    children?: React.ReactNode;
  }
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "font-semibold leading-none tracking-tight text-secondary-foreground",
      className,
    )}
    {...props}
  >
    {children}
  </h3>
));
TimelineTitle.displayName = "TimelineTitle";

const TimelineIcon = ({
  icon,
  color = "primary",
  iconSize = "md",
}: {
  icon?: React.ReactNode;
  color?: "primary" | "secondary" | "muted" | "accent" | "destructive" | string;
  status?: "completed" | "in-progress" | "pending" | "error";
  iconSize?: "sm" | "md" | "lg";
}) => {
  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12",
  };

  const iconSizeClasses = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  };

  const colorClasses = {
    primary: "bg-primary text-primary-foreground",
    secondary: "bg-secondary text-secondary-foreground",
    muted: "bg-muted text-muted-foreground",
    accent: "bg-accent text-accent-foreground",
    destructive: "bg-destructive text-destructive-foreground",
  };

  return (
    <div
      className={cn(
        "relative text-primary-foreground flex items-center justify-center rounded-full ring-8 ring-background shadow-sm",
        sizeClasses[iconSize],
        colorClasses[color as keyof typeof colorClasses] ?? color,
      )}
    >
      {icon ? (
        <div
          className={cn(
            "flex items-center justify-center",
            iconSizeClasses[iconSize],
          )}
        >
          {icon}
        </div>
      ) : (
        <div className={cn("rounded-full", iconSizeClasses[iconSize])} />
      )}
    </div>
  );
};

const TimelineDescription = (
  props: React.HTMLAttributes<HTMLParagraphElement>,
) => (
  <ShowMore
    lineClampClassName="line-clamp-5 sm:line-clamp-8"
    className={cn(
      "max-w-sm text-sm text-muted-foreground first-letter:capitalize",
      props.className,
    )}
    {...props}
  />
);
TimelineDescription.displayName = "TimelineDescription";

const TimelineContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col gap-0.5 pl-2 pb-4", className)}
    {...props}
  />
));
TimelineContent.displayName = "TimelineContent";

export {
  Timeline,
  TimelineItem,
  TimelineConnector,
  TimelineHeader,
  TimelineTitle,
  TimelineIcon,
  TimelineDescription,
  TimelineContent,
  TimelineTime,
};
