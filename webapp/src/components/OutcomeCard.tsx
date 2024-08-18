import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

type Outcome = {
  title: string;
};

type Props = {
  outcome: Outcome;
};

const OutcomeCard = ({ outcome }: Props) => (
  <Card>
    <CardHeader>
      <CardTitle>{outcome.title}</CardTitle>
    </CardHeader>
    <CardContent>Lorem ipsum dolor sit amet.</CardContent>
  </Card>
);

export default OutcomeCard;
