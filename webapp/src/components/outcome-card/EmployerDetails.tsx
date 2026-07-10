import { ExternalLinkIcon } from "@radix-ui/react-icons";
import Link from "next/link";
import { companiesHouseUrl, getEntityTypeLabel } from "@/lib/company";
import {
  addParamValue,
  appSearchParamsCache,
  appSearchParamsSerializer,
} from "@/lib/search-params";
import { Outcome, OutcomeCompanySic } from "@/lib/types";

type Props = {
  employer: Outcome["parties"]["employer"];
  company?: Outcome["company"];
};

const typeBadgeClass = "rounded-md px-2.5 py-0.5 inline-block bg-slate-200";
const typeBadgeLinkClass = `${typeBadgeClass} hover:bg-slate-300`;

const filterLinkClass =
  "text-primary underline underline-offset-4 hover:font-medium";

const sectionClass = "font-medium text-muted-foreground";

const descriptionListClass = "list-none mt-1 space-y-1.5";

const descriptionItemClass = "border-l border-slate-300 pl-2 leading-snug";

const groupSicsBySection = (
  sics: OutcomeCompanySic[],
): [string, OutcomeCompanySic[]][] => {
  const groups = new Map<string, OutcomeCompanySic[]>();
  for (const sic of sics) {
    const existing = groups.get(sic.section) ?? [];
    existing.push(sic);
    groups.set(sic.section, existing);
  }
  return [...groups.entries()];
};

const NatureOfBusiness = ({ sics }: { sics: OutcomeCompanySic[] }) => {
  if (sics.length === 0) {
    return null;
  }

  if (sics.length === 1) {
    const sic = sics[0];
    return (
      <p data-sic-code={sic.code}>
        <span className={sectionClass}>{sic.section}</span>: {sic.description}
      </p>
    );
  }

  const sections = groupSicsBySection(sics);

  if (sections.length === 1) {
    const [section, entries] = sections[0];
    return (
      <div>
        <p className={sectionClass}>{section}</p>
        <ul className={descriptionListClass}>
          {entries.map((sic) => (
            <li
              key={sic.code}
              className={descriptionItemClass}
              data-sic-code={sic.code}
            >
              {sic.description}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <ul className="list-none space-y-2.5">
      {sections.map(([section, entries]) => (
        <li key={section}>
          <span className={sectionClass}>{section}</span>
          <ul className={descriptionListClass}>
            {entries.map((sic) => (
              <li
                key={sic.code}
                className={descriptionItemClass}
                data-sic-code={sic.code}
              >
                {sic.description}
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
};

const EmployerDetails = ({ employer, company }: Props) => {
  const params = appSearchParamsCache.all();
  const filterHref = appSearchParamsSerializer(
    addParamValue(params, "parties.employer", employer),
  );

  if (!company) {
    return (
      <Link href={filterHref} className={filterLinkClass}>
        {employer}
      </Link>
    );
  }

  return (
    <div className="flex flex-col gap-y-2">
      <Link href={filterHref} className={filterLinkClass}>
        {company.name}
      </Link>
      <div className="pt-0.5">
        {company.type === "identified" && company.number ? (
          <Link
            href={companiesHouseUrl(company.number)}
            target="_blank"
            className={`${typeBadgeLinkClass} inline-flex items-center gap-x-1`}
            aria-label={`View ${company.name} on Companies House`}
          >
            Companies House
            <ExternalLinkIcon className="size-3" />
          </Link>
        ) : (
          <span className={typeBadgeClass}>
            {getEntityTypeLabel(company)}
          </span>
        )}
      </div>
      <NatureOfBusiness sics={company.sics} />
    </div>
  );
};

export default EmployerDetails;
