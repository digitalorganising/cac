import { TimelineItem } from "./timeline/timeline";
import { OutcomeEvent } from "@/lib/types";

type Props = {
  event: OutcomeEvent;
};
export default function DecisionTimelineItem({ event }: Props) {
  return (
    <TimelineItem
      date={event.date}
      title={event.type.label}
      description={event.description}
      status="completed"
    />
  );
}
