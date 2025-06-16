import {
  Archive,
  ArchiveX,
  BookOpenCheck,
  BookText,
  BookUp,
  ClipboardX,
  DoorOpen,
  Grid2x2Check,
  Grid2x2X,
  Inbox,
  Mailbox,
  Map,
  Megaphone,
  OctagonX,
  Scale,
  ScrollText,
  Trophy,
  Vote,
} from "lucide-react";
import Link from "next/link";
import { ReactNode } from "react";
import { EventType, OutcomeEvent } from "@/lib/types";
import { TimelineItem, TimelineItemProps } from "../timeline/timeline";

type Props = {
  event: OutcomeEvent;
} & TimelineItemProps;

const getIcon = (eventType: EventType): ReactNode => {
  switch (eventType) {
    case "application_received":
      return <Inbox />;
    case "application_withdrawn":
      return <Archive />;
    case "application_accepted":
      return <BookOpenCheck />;
    case "application_rejected":
      return <ClipboardX />;
    case "bargaining_unit_appropriate":
      return <Grid2x2Check />;
    case "bargaining_unit_inappropriate":
      return <Grid2x2X />;
    case "ballot_requirement_decided":
      return <Vote />;
    case "ballot_not_required":
      return <ScrollText />;
    case "ballot_form_postal":
      return <Mailbox />;
    case "ballot_form_workplace":
      return <Vote />;
    case "ballot_form_combination":
      return <Map />;
    case "ballot_held":
      return <Megaphone />;
    case "unfair_practice_upheld":
      return <Scale />;
    case "unfair_practice_not_upheld":
      return <Scale />;
    case "access_arrangement":
      return <DoorOpen />;
    case "union_recognized":
      return <Trophy />;
    case "union_not_recognized":
      return <OctagonX />;
    case "method_decision":
      return <BookText />;
    case "method_agreed":
      return <BookUp />;
    case "case_closed":
      return <ArchiveX />;
  }
};

const getColor = (eventType: EventType): string => {
  switch (eventType) {
    case "case_closed":
    case "method_decision":
    case "method_agreed":
      return "bg-zinc-400";
    case "application_received":
    case "access_arrangement":
    case "bargaining_unit_appropriate":
    case "ballot_requirement_decided":
    case "ballot_form_postal":
    case "ballot_form_workplace":
    case "ballot_form_combination":
    case "ballot_held":
      return "bg-zinc-500";
    case "unfair_practice_upheld":
    case "unfair_practice_not_upheld":
    case "bargaining_unit_inappropriate":
      return "bg-amber-600";
    case "application_accepted":
    case "ballot_not_required":
    case "union_recognized":
      return "bg-green-600";
    case "application_rejected":
    case "union_not_recognized":
      return "bg-red-600";
    default:
      return "bg-zinc-500";
  }
};
export default function DecisionTimelineItem({ event, ...otherProps }: Props) {
  return (
    <TimelineItem
      date={event.date}
      title={
        <Link
          href={event.sourceDocumentUrl}
          target="_blank"
          className="text-primary hover:underline underline-offset-4"
        >
          {event.type.label}
        </Link>
      }
      description={event.description}
      icon={getIcon(event.type.value)}
      iconColor={getColor(event.type.value)}
      status="completed"
      {...otherProps}
    />
  );
}
