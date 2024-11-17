import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type Outcome = any;

type Props = {
  outcome: Outcome;
};

const formatJSON = ({ documents, ...outcome }: Outcome): string =>
  JSON.stringify(outcome, null, 2);

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader>
      <CardTitle>{outcome.outcome_title}</CardTitle>
    </CardHeader>
    <CardContent>
      <pre>{formatJSON(outcome)}</pre>
    </CardContent>
  </Card>
);

export default OutcomeCard;
