import { Entries } from "type-fest";
import { Facets } from "@/lib/queries/facets";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { FacetSelectMobile } from "./FacetSelect";
import { filterLabels } from "./common";

export default async function MobileFacetControls({
  facetsPromise,
}: {
  facetsPromise: Promise<Facets>;
}) {
  const facets = await facetsPromise;
  return (
    <div>
      <Accordion type="multiple">
        {(
          Object.entries(facets.multiSelect) as Entries<Facets["multiSelect"]>
        ).map(([name, buckets]) => (
          <AccordionItem key={name} value={name}>
            <AccordionTrigger>{filterLabels[name] ?? ""}</AccordionTrigger>
            <AccordionContent>
              <FacetSelectMobile
                name={name}
                options={buckets.map((bucket) => ({
                  value: bucket.value.toString(),
                  label: `${bucket.label ?? bucket.value} (${bucket.count})`,
                }))}
              />
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
