import { Facets } from "@/lib/queries/facets";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { filterLabels } from "./common";
import { Entries } from "type-fest";
import { FacetSelectMobile } from "./FacetSelect";

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
